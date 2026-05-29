import { useEffect, useRef } from 'react';
import { useCognitionStore } from '../stores/cognitionStore';

export function useTacticalAudio() {
  const audioCtx = useRef<AudioContext | null>(null);
  const humOsc = useRef<OscillatorNode | null>(null);
  const humGain = useRef<GainNode | null>(null);
  const initialized = useRef(false);

  const connected = useCognitionStore((s) => s.connection === 'connected');
  const threatLevel = useCognitionStore(
    (s) => s.envelope?.adversarial?.attack_confidence ?? 0
  ) as number;

  useEffect(() => {
    const initAudio = () => {
      if (initialized.current) return;
      
      const CtxClass = window.AudioContext || (window as any).webkitAudioContext;
      if (!CtxClass) return;
      
      audioCtx.current = new CtxClass();
      
      // Deep operational hum (non-intrusive)
      humOsc.current = audioCtx.current.createOscillator();
      humGain.current = audioCtx.current.createGain();
      
      humOsc.current.type = 'sine';
      humOsc.current.frequency.value = 55; // Low atmospheric hum
      
      humGain.current.gain.value = 0; // Start silent
      
      humOsc.current.connect(humGain.current);
      humGain.current.connect(audioCtx.current.destination);
      
      humOsc.current.start();
      initialized.current = true;
    };

    // Browsers require interaction to start audio
    window.addEventListener('click', initAudio, { once: true });
    window.addEventListener('keydown', initAudio, { once: true });
    
    return () => {
      window.removeEventListener('click', initAudio);
      window.removeEventListener('keydown', initAudio);
      
      if (humOsc.current) {
        try { humOsc.current.stop(); } catch {}
        humOsc.current.disconnect();
      }
      if (humGain.current) {
        humGain.current.disconnect();
      }
      if (audioCtx.current && audioCtx.current.state !== 'closed') {
        audioCtx.current.close();
      }
      initialized.current = false;
    };
  }, []);

  // Modulate atmospheric hum based on connection and threat level
  useEffect(() => {
    if (!initialized.current || !humGain.current || !audioCtx.current || !humOsc.current) return;
    
    const now = audioCtx.current.currentTime;
    
    if (!connected) {
      // Fade out smoothly if offline
      humGain.current.gain.setTargetAtTime(0, now, 0.5);
    } else {
      // Base volume + escalation for threat (very subtle)
      const targetVolume = 0.015 + (threatLevel * 0.03); 
      // Base frequency + subtle tension rise
      const targetFreq = 55 + (threatLevel * 15);
      
      humGain.current.gain.setTargetAtTime(targetVolume, now, 2.0);
      humOsc.current.frequency.setTargetAtTime(targetFreq, now, 2.0);
    }
  }, [connected, threatLevel]);
}
