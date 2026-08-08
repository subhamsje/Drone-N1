/**
 * Silent Tactical Audio & Telemetry Stub (Voice Disabled).
 */

class TacticalAudioEngine {
  public playChirp(_freq: number = 880, _durationMs: number = 80) {
    // Silent mode
  }

  public speak(_text: string, _priority: 'NORMAL' | 'CRITICAL' = 'NORMAL') {
    // Voice disabled per user request
  }

  public alertGpsLoss() {}
  public alertMotorRamp() {}
  public alertEcdsaVerified() {}
  public alertHandover() {}
}

export const tacticalAudio = new TacticalAudioEngine();
