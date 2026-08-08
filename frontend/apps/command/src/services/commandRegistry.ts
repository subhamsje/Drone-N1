/**
 * Unified Command Registry System.
 * Connects ⌘K Command Palette, Top Navigation, Panel Action Buttons, and Keybindings
 * into a single deterministic command execution pipeline.
 */

import { useUiStore, WorkspaceMode } from '../global/uiState';
import { useFleetStore, FlightMode } from '../global/fleetState';
import { useMissionStore } from '../global/missionState';
import { useWorkspaceLayoutStore } from '../layout';
import { apiClient } from './api/client';

export interface CommandItem {
  id: string;
  title: string;
  category: 'NAVIGATION' | 'FLIGHT_CONTROL' | 'MISSION' | 'SIMULATION' | 'WORKSPACE' | 'SAFETY';
  shortcut?: string;
  description?: string;
  execute: () => Promise<void> | void;
}

class CommandRegistry {
  private commands: Map<string, CommandItem> = new Map();

  constructor() {
    this.registerDefaultCommands();
  }

  public register(cmd: CommandItem) {
    this.commands.set(cmd.id, cmd);
  }

  public get(id: string): CommandItem | undefined {
    return this.commands.get(id);
  }

  public getAll(): CommandItem[] {
    return Array.from(this.commands.values());
  }

  public async execute(id: string) {
    const cmd = this.commands.get(id);
    if (!cmd) {
      console.warn(`[CommandRegistry] Command ${id} not found.`);
      return;
    }
    try {
      await cmd.execute();
    } catch (err) {
      console.error(`[CommandRegistry] Error executing ${id}:`, err);
    }
  }

  private registerDefaultCommands() {
    // 1. Navigation Commands
    this.register({
      id: 'nav.ops',
      title: 'Go to Operations Dashboard',
      category: 'NAVIGATION',
      shortcut: '⌘1',
      description: 'Switch workspace to fleet operations and mission queue',
      execute: () => useUiStore.getState().setWorkspaceMode('ops_center'),
    });

    this.register({
      id: 'nav.globe',
      title: 'Go to 3D Planetary Globe',
      category: 'NAVIGATION',
      shortcut: '⌘2',
      description: 'Switch workspace to photorealistic Cesium 3D globe',
      execute: () => useUiStore.getState().setWorkspaceMode('command_globe'),
    });

    this.register({
      id: 'nav.studio',
      title: 'Go to Node Mission Studio IDE',
      category: 'NAVIGATION',
      shortcut: '⌘3',
      description: 'Open spatial DAG editor, corridor sculptor, and survey raster',
      execute: () => useUiStore.getState().setWorkspaceMode('mission_studio'),
    });

    this.register({
      id: 'nav.twin',
      title: 'Go to Digital Twin Physics Sandbox',
      category: 'NAVIGATION',
      shortcut: '⌘4',
      description: 'Open R3F physics twin and counterfactual predictive sandbox',
      execute: () => useUiStore.getState().setWorkspaceMode('twin_workbench'),
    });

    // 2. Flight Control Commands
    this.register({
      id: 'flight.toggle_arm',
      title: 'Toggle Arm / Disarm State',
      category: 'FLIGHT_CONTROL',
      shortcut: '⇧A',
      description: 'Send arming command to Pixhawk 6X FMU flight stack',
      execute: async () => {
        await useFleetStore.getState().toggleArm();
      },
    });

    this.register({
      id: 'flight.mode_offboard',
      title: 'Set Flight Mode: OFFBOARD (AI Autonomous)',
      category: 'FLIGHT_CONTROL',
      description: 'Engage MPC autonomous trajectory setpoints',
      execute: async () => {
        await useFleetStore.getState().setFlightMode('OFFBOARD');
      },
    });

    this.register({
      id: 'flight.mode_hold',
      title: 'Set Flight Mode: HOLD (Loiter)',
      category: 'FLIGHT_CONTROL',
      description: 'Command vehicle to loiter at current GPS coordinates',
      execute: async () => {
        await useFleetStore.getState().setFlightMode('HOLD');
      },
    });

    this.register({
      id: 'flight.mode_rtl',
      title: 'Command Return to Base (RTL)',
      category: 'FLIGHT_CONTROL',
      shortcut: '⇧R',
      description: 'Climb to 60m AGL safe altitude and return to launch base',
      execute: async () => {
        await useFleetStore.getState().setFlightMode('RTL');
      },
    });

    this.register({
      id: 'flight.emergency_land',
      title: 'EMERGENCY: Immediate Auto-Flare Touchdown',
      category: 'SAFETY',
      shortcut: '⇧E',
      description: 'Abort all corridors and execute deterministic ground effect flare',
      execute: async () => {
        await useFleetStore.getState().setFlightMode('EMERGENCY');
        await apiClient.post('/api/v1/bounded-contexts/flight/abort', { uav_id: 'Altaria-Alpha' });
      },
    });

    // 3. Mission & Simulation Commands
    this.register({
      id: 'mission.compile_graph',
      title: 'Compile MAVSDK Waypoint Graph',
      category: 'MISSION',
      shortcut: '⌘B',
      description: 'Validate DAG dependencies and compile trajectory splines',
      execute: async () => {
        await useMissionStore.getState().compileGraph();
      },
    });

    this.register({
      id: 'sim.inject_gps_fault',
      title: 'Inject Simulation Fault: GPS Jamming Spike',
      category: 'SIMULATION',
      description: 'Test automatic ORB-SLAM3 visual inertial odometry handover',
      execute: async () => {
        await apiClient.post('/api/v1/bounded-contexts/simulation/inject-fault', {
          type: 'GPS_LOSS',
          target_uav: 'Altaria-Alpha',
        });
      },
    });

    // 4. Workspace Layout Commands
    this.register({
      id: 'layout.preset_tactical',
      title: 'Load Preset: Tactical Cockpit',
      category: 'WORKSPACE',
      description: 'Restore default tactical multi-panel split view',
      execute: () => useWorkspaceLayoutStore.getState().loadPreset('tactical'),
    });

    this.register({
      id: 'layout.preset_fpv',
      title: 'Load Preset: FPV Vision & Photogrammetry',
      category: 'WORKSPACE',
      description: 'Expand primary video viewport to 72% width',
      execute: () => useWorkspaceLayoutStore.getState().loadPreset('fpv'),
    });

    this.register({
      id: 'layout.reset',
      title: 'Reset Workspace Layout to Factory Default',
      category: 'WORKSPACE',
      description: 'Clear local persistence and restore canonical tree',
      execute: () => useWorkspaceLayoutStore.getState().resetLayout(),
    });
  }
}

export const commandRegistry = new CommandRegistry();
