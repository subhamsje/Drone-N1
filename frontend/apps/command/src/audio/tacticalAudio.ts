/**
 * Tactical Aerospace Procedural Voice & Audio Synthesizer.
 */

// Web Audio API & SpeechSynthesis for military/aerospace tactical feedback
class TacticalAudioEngine {
  private synth: SpeechSynthesis | null = null;
  private voice: SpeechSynthesisVoice | null = null;
  private audioCtx: AudioContext | null = null;

  constructor() {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      this.synth = window.speechSynthesis;
      this.initVoice();
    }
  }

  private initVoice() {
    if (!this.synth) return;
    const loadVoices = () => {
      const voices = this.synth!.getVoices();
      // Select a crisp English voice
      this.voice = voices.find(v => v.lang.startsWith('en') && v.name.includes('Natural')) || voices.find(v => v.lang.startsWith('en')) || null;
    };
    loadVoices();
    if (this.synth.onvoiceschanged !== undefined) {
      this.synth.onvoiceschanged = loadVoices;
    }
  }

  public playChirp(freq: number = 880, durationMs: number = 80) {
    try {
      if (!this.audioCtx) {
        this.audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)();
      }
      const osc = this.audioCtx.createOscillator();
      const gain = this.audioCtx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(freq, this.audioCtx.currentTime);
      gain.gain.setValueAtTime(0.08, this.audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, this.audioCtx.currentTime + durationMs / 1000);
      osc.connect(gain);
      gain.connect(this.audioCtx.destination);
      osc.start();
      osc.stop(this.audioCtx.currentTime + durationMs / 1000);
    } catch (e) {
      // AudioContext fallback
    }
  }

  public speak(text: string, priority: 'NORMAL' | 'CRITICAL' = 'NORMAL') {
    if (!this.synth) return;
    this.playChirp(priority === 'CRITICAL' ? 1200 : 880, 100);
    
    if (priority === 'CRITICAL') {
      this.synth.cancel(); // Interrupt existing speech for emergency
    }

    const utter = new SpeechSynthesisUtterance(text);
    if (this.voice) utter.voice = this.voice;
    utter.rate = 1.1; // Crisp aerospace cadence
    utter.pitch = 0.95;
    this.synth.speak(utter);
  }

  public alertGpsLoss() {
    this.speak("Warning: GPS signal lost. ORB-SLAM3 visual inertial odometry engaged.", "CRITICAL");
  }

  public alertMotorRamp() {
    this.speak("Caution: Motor thermal degradation detected. Diverting to Emergency Landing Zone Alpha.", "CRITICAL");
  }

  public alertEcdsaVerified() {
    this.speak("Zero trust command signature validated.", "NORMAL");
  }

  public alertHandover() {
    this.speak("Control handover acknowledged. Swarm mesh leader synced.", "NORMAL");
  }
}

export const tacticalAudio = new TacticalAudioEngine();
