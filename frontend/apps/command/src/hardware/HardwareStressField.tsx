import { Panel } from '@altaria/ui';
import { useCognitionStore } from '../stores/cognitionStore';
import { cognitionEngine } from '../config/runtime';
import { cognitionBreath } from '../runtime/cognitionClock';

const MOTORS = ['M0', 'M1', 'M2', 'M3'];

export function HardwareCognition() {
  const h = useCognitionStore((s) => s.envelope?.hardware) as Record<string, number | string> | undefined;
  const stress = cognitionEngine().renderState.twin.motorStress;
  const breath = cognitionBreath();

  if (!h) {
    return (
      <Panel title="Embodied Self-Awareness" className="ops-panel-accent">
        <p className="text-[10px] text-slate-600">Awaiting hardware cognition…</p>
      </Panel>
    );
  }

  return (
    <Panel title="Embodied Self-Awareness" className="ops-panel-accent">
      <div className="mb-3 grid grid-cols-4 gap-2">
        {MOTORS.map((label, i) => {
          const s = stress[i] ?? 0;
          const hue = 45 - s * 45;
          return (
            <div key={label} className="flex flex-col items-center gap-1">
              <div
                className="relative h-14 w-full overflow-hidden rounded border border-slate-800"
                style={{
                  background: `linear-gradient(180deg, hsla(${hue}, 90%, 50%, ${0.15 + s * 0.5 + breath * 0.05}) 0%, transparent 100%)`,
                  boxShadow: s > 0.4 ? `0 0 12px hsla(${hue}, 90%, 45%, 0.35)` : undefined,
                }}
              >
                <div
                  className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-amber-600/80 to-transparent"
                  style={{ height: `${s * 100}%`, opacity: 0.5 + breath * 0.2 }}
                />
              </div>
              <span className="font-mono text-[8px] text-slate-500">{label}</span>
            </div>
          );
        })}
      </div>
      <div className="space-y-1 font-mono text-[9px] text-slate-500">
        <p>VIB {Number(h.vibration_evolution ?? 0).toFixed(2)} · ESC {Number(h.esc_wear_prediction ?? 0).toFixed(2)}</p>
        <p>FATIGUE {Number(h.structural_fatigue_risk ?? 0).toFixed(2)} · BAT {((Number(h.battery_chemistry_health ?? 1)) * 100).toFixed(0)}%</p>
      </div>
    </Panel>
  );
}
