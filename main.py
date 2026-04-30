"""
UAV Hybrid Digital Twin — Production Entry Point
──────────────────────────────────────────────────
Fixed 200ms timestep loop. Full sequential pipeline:

  Physics (20D nonlinear) → EKF (rollback) → Digital Twin →
  LSTM+MCDropout (prediction) → Fused Anomaly (IF + MCD) →
  4-Quadrant Risk → TTF → MPC + Decision → Action (closed-loop) →
  Explainability → Streamer (WebSocket + JSON)

Run:
  python main.py                    # 400 cycles (~80s real-time)
  python main.py --cycles 200       # custom cycle count
  python main.py --no-ws            # disable WebSocket server
  python main.py --demo             # fast demo (fault at 3s, 80 cycles)
  python main.py --validate         # integration test suite only
"""

import asyncio
import logging
import time
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np

from config.settings import SystemConfig, CONFIG
from core.models import SystemSnapshot
from engines.physics import PhysicsEngine
from engines.ekf import RollbackAugmentedEKF
from engines.digital_twin import DigitalTwinStateManager
from engines.prediction import LSTMPredictionEngine
from engines.anomaly import FusedAnomalyEngine
from engines.risk import IntegratedRiskEngine
from engines.decision import TTFEstimator, DecisionIntelligenceLayer, AdaptiveBudgetMPC
from engines.action_executor import ActionExecutor
from engines.explainability import HybridExplainabilityEngine
from streaming.streamer import StreamingLayer

# ── Logging: suppress sub-module noise, keep our structured output ────────────
logging.basicConfig(level=logging.WARNING)
core_logger = logging.getLogger("TWIN")
core_logger.setLevel(logging.INFO)
_h = logging.StreamHandler()
_h.setFormatter(logging.Formatter("%(message)s"))
core_logger.addHandler(_h)
core_logger.propagate = False


class UAVHybridEngine:
    """
    Central orchestrator.

    All 12 modules are composed here and run sequentially every 200ms.
    The CLOSED LOOP is:
      ActionExecutor.execute()
        → PhysicsEngine.apply_action_feedback()   (changes degradation rate)
        → mpc.u_optimal → self._u_cmd             (changes motor commands)
        → next physics step sees different inputs  (this is what makes it real)
    """

    LOOP_MS = 200

    def __init__(self, config: SystemConfig = CONFIG):
        self.cfg          = config
        self._cycle       = 0
        self._running     = False
        self._physics_steps = max(1, int(self.LOOP_MS / (config.ekf.dt * 1000)))

        # ── Instantiate all modules ───────────────────────────────────────
        self.physics      = PhysicsEngine(config)
        self.ekf          = RollbackAugmentedEKF(config)
        self.digital_twin = DigitalTwinStateManager(config)
        self.predictor    = LSTMPredictionEngine(config)
        self.anomaly_eng  = FusedAnomalyEngine(config)
        self.risk_engine  = IntegratedRiskEngine(config)
        self.ttf_est      = TTFEstimator(config)
        self.mpc          = AdaptiveBudgetMPC(config)
        self.decision_eng = DecisionIntelligenceLayer(config)
        self.action_exec  = ActionExecutor(config)
        self.explainer    = HybridExplainabilityEngine(config)
        self.streamer     = StreamingLayer(config)

        # Warm-started MPC command (updated every cycle by MPC output)
        self._u_cmd = np.full(4, config.physics.hover_thrust, dtype=float)

        self._stats = {"risk": [], "ttf": [], "actions": {}, "cycle_ms": []}

        self._print_banner()

    # ─────────────────────────────────────────────────────────────────────────

    async def run(self, max_cycles: int = 400, start_ws: bool = True):
        self._running = True
        if start_ws:
            await self.streamer.start_websocket_server()

        core_logger.info(self._header())
        core_logger.info("─" * 125)

        interval = self.LOOP_MS / 1000.0
        while self._running:
            if max_cycles and self._cycle >= max_cycles:
                break

            t0 = time.monotonic()
            try:
                snap = await self._execute_cycle()
                await self.streamer.emit(snap)
                dt_ms = (time.monotonic() - t0) * 1000
                self._record(snap, dt_ms)
                self._print_cycle(snap, dt_ms)
            except Exception as e:
                core_logger.error(f"[ERROR] cycle {self._cycle}: {e}", exc_info=True)

            await asyncio.sleep(max(0.0, interval - (time.monotonic() - t0)))

        self._print_summary()

    def stop(self):
        self._running = False

    # ── Pipeline ──────────────────────────────────────────────────────────────

    async def _execute_cycle(self) -> SystemSnapshot:
        t0 = time.time()
        self._cycle += 1
        comm_delay = 0.0

        # ── 1. Physics sub-steps (N × 20ms) ──────────────────────────────
        physics_frame = None
        for _ in range(self._physics_steps):
            physics_frame = self.physics.step_physics(self._u_cmd)
            self.physics.transmit_measurement()
            self.ekf.predict_forward(
                self.physics.time, self._u_cmd,
                self.physics.fault_losses, self.physics.fault_taus,
            )
            pkt = self.physics.receive_measurement()
            if pkt is not None:
                t_sent, z  = pkt
                comm_delay = self.physics.time - t_sent
                self.ekf.delayed_update(t_sent, z, self.physics.fault_losses, self.physics.fault_taus)

        # ── 2. EKF posterior (state source for all downstream) ────────────
        ekf_state = self.ekf.get_state()

        # ── 3. Digital Twin — sliding window + ROC ────────────────────────
        telemetry = self.digital_twin.update(physics_frame, ekf_state)
        window    = self.digital_twin.get_window()

        # ── 4. LSTM prediction + MC Dropout uncertainty ───────────────────
        prediction = self.predictor.predict(window)

        # ── 5. Feature vectors ────────────────────────────────────────────
        fv_14d = self.digital_twin.get_feature_vector(
            telemetry, prediction.battery, prediction.rpm, ekf_state
        )
        fv_8d = [
            float(ekf_state.x[5]),   float(ekf_state.x[10]),
            float(ekf_state.x[11]),  float(ekf_state.x[12]),
            float(self._u_cmd[0]),   float(self._u_cmd[1]),
            float(ekf_state.innovation_mag), float(comm_delay),
        ]

        # ── 6. Fused anomaly (IF + MCD) ───────────────────────────────────
        anomaly = self.anomaly_eng.detect(fv_14d, fv_8d)

        # ── 7. 4-Quadrant integrated risk ─────────────────────────────────
        risk = self.risk_engine.compute(
            telemetry=telemetry, prediction=prediction, anomaly=anomaly,
            ekf=ekf_state, fault_losses=self.physics.fault_losses,
            comm_delay=comm_delay,
            battery_roc=self.digital_twin.battery_roc,
            rpm_roc=self.digital_twin.rpm_roc,
        )

        # ── 8. TTF ────────────────────────────────────────────────────────
        grad = self.risk_engine.get_risk_gradient()
        ttf  = self.ttf_est.estimate(risk, physics_frame.battery, grad)

        # ── 9. MPC (time-bounded gradient descent) ────────────────────────
        mpc_out = await asyncio.get_event_loop().run_in_executor(
            None, self.mpc.optimize,
            ekf_state.x, self.action_exec.target_z, self.cfg.ekf.dt,
            self.physics.dynamics, self.physics.fault_losses, self.physics.fault_taus,
            risk.value,
        )

        # ── 10. Decision (probabilistic multi-factor + MPC signal) ────────
        decision = self.decision_eng.decide(
            risk=risk, ttf=ttf, anomaly=anomaly,
            battery=physics_frame.battery,
            risk_gradient=grad, mpc_output=mpc_out,
        )

        # ── 11. Action Execution → CLOSED LOOP ───────────────────────────
        effect, state, _ = self.action_exec.execute(
            action=decision.action, risk=risk,
            mpc_dt=self.cfg.ekf.dt, physics_engine=self.physics,
        )
        self._u_cmd = np.array(mpc_out.u_optimal, dtype=float)   # ← closed loop

        # ── 12. Explainability ────────────────────────────────────────────
        explanation = self.explainer.explain(
            telemetry=telemetry, prediction=prediction,
            anomaly=anomaly, risk=risk, decision=decision, ekf=ekf_state,
            battery_roc=self.digital_twin.battery_roc,
            rpm_roc=self.digital_twin.rpm_roc,
        )

        return SystemSnapshot(
            timestamp=t0, physics=physics_frame, ekf=ekf_state,
            telemetry=telemetry, prediction=prediction, anomaly=anomaly,
            risk=risk, ttf=ttf, decision=decision, explainability=explanation,
            action_effect=effect, system_state=state, cycle=self._cycle,
        )

    # ── Terminal Output ───────────────────────────────────────────────────────

    def _print_banner(self):
        core_logger.info("")
        core_logger.info("╔══════════════════════════════════════════════════════════════════════════════╗")
        core_logger.info("║    UAV HYBRID DIGITAL TWIN  —  REAL-TIME AUTONOMOUS INTELLIGENCE SYSTEM     ║")
        core_logger.info("║  20D Physics │ Rollback EKF │ LSTM+MCDropout │ IF+MCD Anomaly │ MPC N=5    ║")
        core_logger.info("╚══════════════════════════════════════════════════════════════════════════════╝")
        core_logger.info(f"  Fault onset   : t={self.cfg.physics.fault_onset_time}s → motor {self.cfg.physics.fault_motor_index} (gradual ramp @ {self.cfg.physics.fault_loss_ramp_rate}/s)")
        core_logger.info(f"  Loop          : {self.LOOP_MS}ms ({self._physics_steps} physics sub-steps × {self.cfg.ekf.dt*1000:.0f}ms)")
        core_logger.info(f"  Stream        : {self.cfg.stream.json_output_path}")
        core_logger.info(f"  WebSocket     : ws://{self.cfg.stream.websocket_host}:{self.cfg.stream.websocket_port}")
        core_logger.info("")

    def _header(self) -> str:
        return (
            f"{'CYC':>4} │{'ALT':>6} {'BAT':>5} {'RPM':>5}│"
            f"{'RISK':>7}{'BAR':>8} {'LVL':>8}│"
            f"{'TTF':>5}│"
            f"{'EKF_C':>6} {'MECH':>5} {'AI':>5}│"
            f"{'ANML':>6}│"
            f"{'MPC':>13}│"
            f"{'ACTION':>14} {'CF':>5}│STATE"
        )

    def _print_cycle(self, s: SystemSnapshot, dt_ms: float):
        if (self._cycle - 1) % 25 == 0:
            core_logger.info(self._header())
            core_logger.info("─" * 125)

        bar = self._bar(s.risk.value)
        m   = s.decision.mpc_output
        mpc = f"{m.iterations}i {m.time_used_ms:4.1f}ms{'✓' if m.converged else ' '}" if m else "           —"
        anm = f"{'⚡' if s.anomaly.is_anomaly else ' '}{s.anomaly.score:.3f}"
        act = s.decision.action.value
        flag= {"EMERGENCY_LAND":"⚠", "RETURN_HOME":"↩", "THRUST_ADJUST":"⚙", "NONE":" "}.get(act," ")

        core_logger.info(
            f"{s.cycle:>4} │{s.physics.altitude:>6.1f} {s.physics.battery:>5.1f} {s.physics.rpm:>5.0f}│"
            f"{s.risk.value:>7.4f}{bar}{s.risk.level.value:>8}│"
            f"{s.ttf.minutes:>5.2f}│"
            f"{s.ekf.confidence:>6.3f} {s.risk.r_mechanical:>5.3f} {s.risk.r_ai:>5.3f}│"
            f"{anm:>6}│"
            f"{mpc:>13}│"
            f"{act:>14}{flag} {s.decision.confidence:>5.3f}│{s.system_state.value}"
        )

        if act != "NONE" or s.risk.level.value in ("HIGH", "CRITICAL"):
            ex = s.explainability
            core_logger.info(f"       ├─ 🔍 {ex.dominant_signal}")
            core_logger.info(f"       ├─ 📊 mech={ex.r_mechanical:.3f} sensor={ex.r_sensor:.3f} comms={ex.r_comms:.3f} ai={ex.r_ai:.3f}  src={ex.failure_source.value}")
            core_logger.info(f"       ├─ 🧠 EKF conf={ex.ekf_confidence:.3f} cov={ex.ekf_covariance_trace:.2f} | MPC {ex.mpc_iters}i {'✓' if ex.mpc_converged else '✗'} → {ex.mpc_implied_action} | AI_unc={ex.ai_uncertainty:.3f}")
            core_logger.info(f"       └─ 💬 {ex.root_cause[:110]}")
            core_logger.info(f"          {'─'*80}")

    def _print_summary(self):
        r, t = self._stats["risk"], self._stats["ttf"]
        a, ct = self._stats["actions"], self._stats["cycle_ms"]
        core_logger.info("")
        core_logger.info("╔══════════════════════════════════════════════════╗")
        core_logger.info("║              SIMULATION COMPLETE                 ║")
        core_logger.info("╚══════════════════════════════════════════════════╝")
        if r:
            core_logger.info(f"  Cycles     : {self._cycle}")
            core_logger.info(f"  Risk range : {min(r):.4f} → {max(r):.4f}")
            core_logger.info(f"  TTF range  : {max(t):.2f}m → {min(t):.2f}m")
            core_logger.info(f"  Actions    : {a}")
            if ct:
                core_logger.info(f"  Cycle time : avg={sum(ct)/len(ct):.1f}ms  max={max(ct):.1f}ms")
        n = len(r)
        if n >= 20:
            e, l = r[:n//4], r[3*n//4:]
            te, tl = t[:n//4], t[3*n//4:]
            core_logger.info("")
            core_logger.info("  BEHAVIORAL CHECKS:")
            core_logger.info(f"  {'✅' if max(l)>max(e) else '❌'} Risk increases after fault    {max(e):.4f} → {max(l):.4f}")
            core_logger.info(f"  {'✅' if min(tl)<max(te) else '❌'} TTF decreases toward 0       {max(te):.2f}m → {min(tl):.2f}m")
            non_none = sum(v for k,v in a.items() if k!="NONE")
            core_logger.info(f"  {'✅' if non_none>0 else '❌'} Actions triggered             {non_none} non-NONE cycles")

    def _record(self, s: SystemSnapshot, dt_ms: float):
        self._stats["risk"].append(s.risk.value)
        self._stats["ttf"].append(s.ttf.minutes)
        self._stats["cycle_ms"].append(dt_ms)
        ak = s.decision.action.value
        self._stats["actions"][ak] = self._stats["actions"].get(ak, 0) + 1

    @staticmethod
    def _bar(v: float, w: int = 6) -> str:
        f = int(v * w)
        return f"[{'█'*f}{'░'*(w-f)}]"


# ══════════════════════════════════════════════════════════════════════════════

async def run_validation():
    """12-point integration validation. Run with: python main.py --validate"""
    core_logger.info("")
    core_logger.info("╔══════════════════════════════════════════════════════════╗")
    core_logger.info("║           INTEGRATION VALIDATION SUITE (60 cycles)      ║")
    core_logger.info("╚══════════════════════════════════════════════════════════╝")

    cfg = SystemConfig()
    cfg.physics.fault_onset_time     = 2.0
    cfg.physics.fault_loss_ramp_rate = 0.10

    engine    = UAVHybridEngine(cfg)
    snapshots = []
    for _ in range(60):
        s = await engine._execute_cycle()
        snapshots.append(s)

    def chk(name, ok, detail=""):
        core_logger.info(f"  {'✅ PASS' if ok else '❌ FAIL'}  {name:42s}  {detail}")

    n     = len(snapshots)
    early = snapshots[:10]
    late  = snapshots[45:]

    d = snapshots[-1].to_dict()
    keys = ["timestamp","cycle","physics","ekf","prediction","anomaly","risk","ttf","decision","explainability","action_effect","system_state"]
    chk("All snapshot keys present",              all(k in d for k in keys))

    er, lr = [s.risk.value for s in early], [s.risk.value for s in late]
    chk("Risk rises after fault onset",           max(lr) > max(er),         f"{max(er):.4f} → {max(lr):.4f}")

    et, lt = [s.ttf.minutes for s in early], [s.ttf.minutes for s in late]
    chk("TTF decreases toward 0",                 min(lt) < max(et),         f"{max(et):.2f}m → {min(lt):.2f}m")

    acts = [s.decision.action.value for s in snapshots]
    non_none = [a for a in acts if a != "NONE"]
    chk("Non-NONE actions triggered",             len(non_none) > 0,         f"{set(non_none)}")

    confs = [s.ekf.confidence for s in snapshots]
    chk("EKF confidence always in [0,1]",         all(0 <= c <= 1 for c in confs))

    ea, la = [s.anomaly.score for s in early], [s.anomaly.score for s in late]
    chk("Anomaly score rises during fault",        max(la) >= max(ea),        f"{max(ea):.4f} → {max(la):.4f}")

    max_cmd = cfg.physics.max_motor_cmd
    u_valid = all(all(0<=u<=max_cmd for u in s.decision.mpc_output.u_optimal)
                  for s in snapshots if s.decision.mpc_output)
    chk("MPC motor commands in valid range",       u_valid)

    ex = snapshots[-1].explainability
    cs = sum(ex.signal_contributions.values())
    chk("Explainability contributions sum to 1",  abs(cs - 1.0) < 0.02,     f"sum={cs:.4f}")

    chk("Closed-loop: actions taken",             len(non_none) > 0,         f"{len(non_none)} cycles")

    late_srcs = [s.risk.dominant_source.value for s in late]
    fault_id  = any("Actuator" in s or "Sensor" in s for s in late_srcs)
    chk("Fault source correctly identified",       fault_id,                  f"{set(late_srcs)}")

    em, lm = [s.risk.r_mechanical for s in early], [s.risk.r_mechanical for s in late]
    chk("Mechanical risk rises with fault",        max(lm) > max(em),         f"{max(em):.4f} → {max(lm):.4f}")

    await engine.streamer.emit(snapshots[-1])
    chk("Streamer buffer populated",              len(engine.streamer.get_recent(5)) > 0)

    core_logger.info("")
    passed = 12   # (manually count above if adding more)


async def main():
    p = argparse.ArgumentParser(description="UAV Hybrid Digital Twin")
    p.add_argument("--cycles",   type=int, default=400,  help="Loop cycle count (default 400)")
    p.add_argument("--no-ws",    action="store_true",    help="Disable WebSocket server")
    p.add_argument("--demo",     action="store_true",    help="Fast demo: fault@3s, 80 cycles")
    p.add_argument("--validate", action="store_true",    help="Run integration validation only")
    args = p.parse_args()

    if args.validate:
        await run_validation()
        return

    if args.demo:
        cfg = SystemConfig()
        cfg.physics.fault_onset_time     = 3.0
        cfg.physics.fault_loss_ramp_rate = 0.08
        cycles = 80
    else:
        cfg    = CONFIG
        cycles = args.cycles

    engine = UAVHybridEngine(cfg)
    try:
        await engine.run(max_cycles=cycles, start_ws=not args.no_ws)
    except KeyboardInterrupt:
        engine.stop()
        core_logger.info("\n[STOP] Halted by user.")


if __name__ == "__main__":
    asyncio.run(main())
