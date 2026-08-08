import React, { useState } from 'react';
import { useFleetStore } from '../global/fleetState';
import { useUiStore } from '../global/uiState';
import { Plane, Box, Cpu, CheckCircle2, X, ShieldCheck, Zap, Radio, Layers, Eye } from 'lucide-react';
import { Button } from '../components/primitives/Button';
import { Badge } from '../components/primitives/Badge';

export interface AirframeOption {
  id: string;
  name: string;
  category: string;
  wingspan: string;
  maxPayload: string;
  endurance: string;
  propulsion: string;
  description: string;
  icon: any;
}

export const AIRFRAME_CATALOG: AirframeOption[] = [
  {
    id: 'VTOL_PUSHER',
    name: 'Hybrid VTOL Fixed-Wing Pusher',
    category: 'Long-Range BVLOS Cruiser',
    wingspan: '2.8m Carbon Composite',
    maxPayload: '3.5 kg',
    endurance: '3.5 Hours',
    propulsion: '4x VTOL Lift + 1x Rear Pusher Motor',
    description: 'Long-range perimeter patrol and linear corridor inspection combining vertical takeoff with high-speed 85km/h cruise.',
    icon: Plane,
  },
  {
    id: 'QUAD_ISR',
    name: 'Tactical Quad-X Heavy Scout',
    category: 'Urban ISR & Inspection',
    wingspan: '750mm Wheelbase',
    maxPayload: '2.2 kg',
    endurance: '48 Mins',
    propulsion: '4x High-Torque Brushless Outrunners',
    description: 'High-agility carbon-fiber quadrotor equipped with tubular landing skids, dual RTK GNSS masts, and 3-axis EO/IR gimbal.',
    icon: Box,
  },
  {
    id: 'HEXA_HEAVY',
    name: 'Heavy-Lift Industrial Hexacopter',
    category: 'Industrial Cargo & LiDAR Survey',
    wingspan: '1200mm Hexagonal Hub',
    maxPayload: '15.0 kg',
    endurance: '42 Mins',
    propulsion: '6x Redundant Heavy-Lift Stators',
    description: 'Six-rotor industrial powerhouse designed for heavy payloads, multispectral cameras, and automatic single-motor failure compensation.',
    icon: Layers,
  },
  {
    id: 'OCTO_X8',
    name: 'Octocopter Coaxial X8 Defense',
    category: 'Heavy Tactical Defense & Cinema',
    wingspan: '950mm Coaxial Carbon',
    maxPayload: '18.5 kg',
    endurance: '38 Mins',
    propulsion: '8x Coaxial Top/Bottom Stators',
    description: 'Eight-motor coaxial powertrain providing extreme thrust-to-weight ratio and survivability in extreme wind conditions.',
    icon: Zap,
  },
];

export interface WizardProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectAirframe: (airframeId: 'VTOL_PUSHER' | 'QUAD_ISR' | 'HEXA_HEAVY' | 'OCTO_X8') => void;
}

export const DroneIntegrationWizardModal: React.FC<WizardProps> = ({
  isOpen,
  onClose,
  onSelectAirframe,
}) => {
  const [selectedId, setSelectedId] = useState<string>('VTOL_PUSHER');
  const [protocol, setProtocol] = useState<string>('PX4_FMUV6X');
  const [sensorSuite, setSensorSuite] = useState<string[]>(['RTK_GPS', 'EO_IR_GIMBAL', 'LIDAR_TOF']);
  const [vehicleCallsign, setVehicleCallsign] = useState<string>('TITAN-VTOL-01');
  const [step, setStep] = useState<number>(1);
  const [integrating, setIntegrating] = useState<boolean>(false);

  const { addFleetUnit, setFocusedUavId } = useFleetStore();

  if (!isOpen) return null;

  const toggleSensor = (s: string) => {
    if (sensorSuite.includes(s)) {
      setSensorSuite(sensorSuite.filter((item) => item !== s));
    } else {
      setSensorSuite([...sensorSuite, s]);
    }
  };

  const handleCompleteIntegration = () => {
    setIntegrating(true);
    setTimeout(() => {
      // Add newly integrated drone into active fleet state
      addFleetUnit({
        id: vehicleCallsign,
        battery: 100,
        voltage: 16.8,
        role: 'WINGMAN',
        status: 'READY',
      });

      setFocusedUavId(vehicleCallsign);
      onSelectAirframe(selectedId as any);
      setIntegrating(false);
      onClose();
    }, 600);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md animate-fadeIn select-none font-mono text-xs">
      <div className="w-full max-w-2xl rounded-2xl bg-[#0d131f] border border-slate-800 shadow-2xl shadow-black/90 overflow-hidden flex flex-col">
        {/* Header */}
        <div className="h-12 px-5 bg-[#111827] border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <Cpu className="w-4 h-4 text-sky-400" />
            <h3 className="font-bold text-slate-100 text-sm tracking-tight">
              Universal Drone Integration & Airframe Binding Wizard
            </h3>
          </div>
          <button onClick={onClose} className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-white">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Wizard Steps Content */}
        <div className="p-6 overflow-y-auto max-h-[75vh] space-y-6">
          {step === 1 && (
            <div className="space-y-4">
              <div>
                <h4 className="font-bold text-white text-sm">Step 1: Select Drone Airframe Architecture</h4>
                <p className="text-slate-400 text-xs mt-0.5">
                  Choose your hardware configuration to bind high-fidelity 4K physics and aerodynamic profiles.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {AIRFRAME_CATALOG.map((air) => {
                  const Icon = air.icon;
                  const active = selectedId === air.id;
                  return (
                    <div
                      key={air.id}
                      onClick={() => setSelectedId(air.id)}
                      className={`p-4 rounded-xl border cursor-pointer transition-all flex flex-col justify-between ${
                        active
                          ? 'bg-slate-900 border-sky-500 shadow-md shadow-sky-500/10 ring-1 ring-sky-500/40'
                          : 'bg-slate-950/70 border-slate-800 hover:border-slate-700'
                      }`}
                    >
                      <div className="space-y-1.5">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <Icon className={`w-4 h-4 ${active ? 'text-sky-400' : 'text-slate-500'}`} />
                            <span className="font-bold text-slate-100">{air.name}</span>
                          </div>
                          {active && <CheckCircle2 className="w-4 h-4 text-sky-400" />}
                        </div>
                        <p className="text-[11px] text-slate-400 leading-relaxed">{air.description}</p>
                      </div>

                      <div className="mt-3 pt-2.5 border-t border-slate-800/80 flex justify-between text-[10px] text-slate-500">
                        <span>Payload: <strong className="text-slate-300">{air.maxPayload}</strong></span>
                        <span>Endurance: <strong className="text-sky-400">{air.endurance}</strong></span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-5">
              <div>
                <h4 className="font-bold text-white text-sm">Step 2: Flight Controller Protocol & Sensor Binding</h4>
                <p className="text-slate-400 text-xs mt-0.5">
                  Configure hardware protocol endpoints and active telemetry sensor suite.
                </p>
              </div>

              {/* Vehicle Callsign Input */}
              <div className="space-y-1.5">
                <label className="text-slate-400 text-[11px] font-bold uppercase">Assigned Fleet Callsign</label>
                <input
                  type="text"
                  value={vehicleCallsign}
                  onChange={(e) => setVehicleCallsign(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-white font-mono focus:border-sky-500 focus:outline-none"
                />
              </div>

              {/* Protocol Selector */}
              <div className="space-y-1.5">
                <label className="text-slate-400 text-[11px] font-bold uppercase">Autopilot Protocol Stack</label>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { id: 'PX4_FMUV6X', label: 'PX4 FMUv6X (Micro-XRCE-DDS)' },
                    { id: 'ARDUPILOT_CUBE', label: 'ArduPilot Cube Orange+ (MAVLink 2)' },
                    { id: 'DJI_ONBOARD_SDK', label: 'DJI Matrice Onboard SDK' },
                  ].map((p) => (
                    <button
                      key={p.id}
                      onClick={() => setProtocol(p.id)}
                      className={`p-2.5 rounded-lg border text-[10px] font-bold text-left transition-all ${
                        protocol === p.id
                          ? 'bg-slate-800 text-sky-400 border-sky-500'
                          : 'bg-slate-950 text-slate-400 border-slate-800 hover:border-slate-700'
                      }`}
                    >
                      {p.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Sensor Payload Suite */}
              <div className="space-y-1.5">
                <label className="text-slate-400 text-[11px] font-bold uppercase">Hardware Sensor Payload Suite</label>
                <div className="grid grid-cols-2 gap-2">
                  {[
                    { id: 'RTK_GPS', label: 'Dual RTK-GNSS Heading Masts (Sub-cm)' },
                    { id: 'EO_IR_GIMBAL', label: '3-Axis 4K EO / Radiometric FLIR Gimbal' },
                    { id: 'LIDAR_TOF', label: 'Optical Flow & Downward LiDAR ToF' },
                    { id: 'PARACHUTE', label: 'Autonomous Pyrotechnic Rescue Parachute' },
                  ].map((s) => {
                    const active = sensorSuite.includes(s.id);
                    return (
                      <div
                        key={s.id}
                        onClick={() => toggleSensor(s.id)}
                        className={`p-2.5 rounded-lg border cursor-pointer flex items-center justify-between text-[11px] ${
                          active
                            ? 'bg-slate-900 border-sky-500 text-sky-300'
                            : 'bg-slate-950 border-slate-800 text-slate-400'
                        }`}
                      >
                        <span>{s.label}</span>
                        {active && <CheckCircle2 className="w-3.5 h-3.5 text-sky-400" />}
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer Navigation */}
        <div className="h-14 px-6 bg-[#111827] border-t border-slate-800 flex items-center justify-between shrink-0">
          {step === 1 ? (
            <div />
          ) : (
            <Button size="sm" variant="secondary" onClick={() => setStep(1)}>
              &larr; Back to Airframes
            </Button>
          )}

          {step === 1 ? (
            <Button size="sm" variant="primary" onClick={() => setStep(2)}>
              Configure Protocol & Sensor Suite &rarr;
            </Button>
          ) : (
            <Button
              size="sm"
              variant="cyber"
              loading={integrating}
              onClick={handleCompleteIntegration}
            >
              {integrating ? 'Binding Hardware Telemetry...' : 'Deploy & Bind to 4K Digital Twin'}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};
