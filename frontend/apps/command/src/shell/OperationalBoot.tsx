import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const BOOT_SEQUENCE = [
  '[SYS] INITIATING PLANETARY COGNITION KERNEL...',
  '[HW]  VERIFYING PX4 / MAVSDK TELEMETRY LINKS... OK',
  '[HW]  JETSON ORIN SURVIVABILITY ENGINE... ONLINE',
  '[NET] ESTABLISHING SWARM TOPOLOGY MESH... SECURED',
  '[AI]  CALIBRATING WORLD MODEL UNCERTAINTY FIELDS...',
  '[AI]  SEMANTIC MISSION ORCHESTRATOR... STANDBY',
  '[SYS] OPERATIONAL CONSCIOUSNESS... ONLINE',
];

export function OperationalBoot() {
  const [visible, setVisible] = useState(true);
  const [lines, setLines] = useState<string[]>([]);

  useEffect(() => {
    let currentLine = 0;
    
    const interval = setInterval(() => {
      if (currentLine < BOOT_SEQUENCE.length) {
        setLines(prev => [...prev, BOOT_SEQUENCE[currentLine]]);
        currentLine++;
      } else {
        clearInterval(interval);
        setTimeout(() => setVisible(false), 1200);
      }
    }, 350); // Fast, tactical progression

    return () => clearInterval(interval);
  }, []);

  if (!visible) return null;

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ opacity: 1 }}
          exit={{ opacity: 0, filter: 'blur(10px)', scale: 1.05 }}
          transition={{ duration: 0.8, ease: "easeInOut" }}
          className="fixed inset-0 z-[100] flex flex-col items-center justify-center bg-[#010409] ops-crt-flicker"
        >
          {/* Subtle neural scan overlay */}
          <div className="ops-neural-scan opacity-20" />
          
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="flex flex-col items-center"
          >
            <div className="mb-8 font-mono text-3xl font-bold tracking-[0.4em] text-teal-400 ops-hud-glow">
              ALTARIA
            </div>
            
            <div className="h-px w-64 bg-gradient-to-r from-transparent via-teal-500/80 to-transparent mb-8" />
            
            <div className="w-[450px] font-mono text-[11px] leading-loose tracking-widest text-slate-400 text-left">
              {lines.map((line, i) => (
                <motion.div 
                  key={i}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className={i === BOOT_SEQUENCE.length - 1 ? "text-teal-400 font-bold ops-hud-glow mt-4" : ""}
                >
                  {line}
                </motion.div>
              ))}
              {lines.length < BOOT_SEQUENCE.length && (
                <motion.div 
                  animate={{ opacity: [1, 0] }} 
                  transition={{ repeat: Infinity, duration: 0.8 }}
                  className="inline-block w-2 h-3 bg-teal-500 ml-1 translate-y-0.5"
                />
              )}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
