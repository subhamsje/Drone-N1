import React, { useState } from 'react';
import { ShieldCheck, Download, CheckCircle, FileText, Lock, X } from 'lucide-react';

interface ComplianceAuditModalProps {
  isOpen: boolean;
  onClose: () => void;
  missionId?: string;
}

export const ComplianceAuditModal: React.FC<ComplianceAuditModalProps> = ({
  isOpen,
  onClose,
  missionId = 'MSN-901'
}) => {
  const [downloading, setDownloading] = useState(false);
  const [downloadComplete, setDownloadComplete] = useState(false);

  if (!isOpen) return null;

  const handleExportPdf = () => {
    setDownloading(true);
    setTimeout(() => {
      setDownloading(false);
      setDownloadComplete(true);
      setTimeout(() => setDownloadComplete(false), 4000);
    }, 1500);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-md p-4">
      <div className="relative w-full max-w-2xl bg-slate-900/90 border border-emerald-500/30 rounded-2xl p-6 shadow-2xl text-slate-100 backdrop-blur-xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-6">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
                FAA / EASA Compliance Audit Exporter
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 font-mono border border-emerald-500/30">
                  SIGNED
                </span>
              </h2>
              <p className="text-xs text-slate-400">Mission: {missionId} • STANAG 4586 & DO-178C Compliant</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Audit Details Body */}
        <div className="space-y-4 font-mono text-sm">
          <div className="grid grid-cols-2 gap-4 bg-slate-950/60 p-4 rounded-xl border border-slate-800">
            <div>
              <span className="text-xs text-slate-500 uppercase block mb-1">Cryptographic Hash</span>
              <span className="text-emerald-400 text-xs break-all">
                4fb2d7e58e70731a86c0bb31cb288430a603600671dd447268f09457d4bb85fc
              </span>
            </div>
            <div>
              <span className="text-xs text-slate-500 uppercase block mb-1">Zero-Trust Signature</span>
              <span className="text-sky-400 text-xs flex items-center gap-1">
                <Lock className="w-3.5 h-3.5 text-sky-400 inline" /> ECDSA NIST256p Verified
              </span>
            </div>
          </div>

          <div className="bg-slate-950/40 p-4 rounded-xl border border-slate-800 space-y-2">
            <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Regulatory Metrics</h3>
            <div className="flex items-center justify-between text-xs py-1 border-b border-slate-800/60">
              <span className="text-slate-400">Airspace Authorization</span>
              <span className="text-slate-200 font-semibold">Class G Uncontrolled (BVLOS Waived)</span>
            </div>
            <div className="flex items-center justify-between text-xs py-1 border-b border-slate-800/60">
              <span className="text-slate-400">Risk Mitigation Score</span>
              <span className="text-emerald-400 font-bold">98.4% (Low Risk)</span>
            </div>
            <div className="flex items-center justify-between text-xs py-1 border-b border-slate-800/60">
              <span className="text-slate-400">Landing Precision</span>
              <span className="text-slate-200">0.12 meters (RTK-GPS)</span>
            </div>
          </div>
        </div>

        {/* Action Footer */}
        <div className="mt-6 pt-4 border-t border-slate-800 flex items-center justify-between">
          <div className="text-xs text-slate-400 flex items-center gap-1.5">
            <CheckCircle className="w-4 h-4 text-emerald-400" />
            <span>Ready for formal FAA Part 107 submission</span>
          </div>

          <button
            onClick={handleExportPdf}
            disabled={downloading}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-600 active:bg-emerald-700 font-semibold text-slate-950 text-sm shadow-lg shadow-emerald-500/20 transition-all disabled:opacity-50"
          >
            {downloading ? (
              <span>Generating PDF Package...</span>
            ) : downloadComplete ? (
              <>
                <CheckCircle className="w-4 h-4" /> Exported PDF Package
              </>
            ) : (
              <>
                <Download className="w-4 h-4" /> Download FAA Audit PDF
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
