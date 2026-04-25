import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { apiFetch } from '../api';
import type { Settings } from '../api';
import toast from 'react-hot-toast';
import LiquidButton from '../components/LiquidButton';

const POSITIONS = [
  'top-left', 'top-center', 'top-right',
  'center-left', 'center', 'center-right',
  'bottom-left', 'bottom-center', 'bottom-right',
];

export default function Watermark() {
  const [opacity, setOpacity] = useState(1.0);
  const [scale, setScale] = useState(0.2);
  const [position, setPosition] = useState('bottom-right');
  const [wmB64, setWmB64] = useState<string | null>(null);
  const [previewSrc, setPreviewSrc] = useState<string | null>(null);
  const [loadingPreview, setLoadingPreview] = useState(false);

  useEffect(() => {
    apiFetch<Settings>('/settings').then(s => {
      if (s['WaterMark Opacity']) setOpacity(Number(s['WaterMark Opacity']));
      if (s['WaterMark Scale']) setScale(Number(s['WaterMark Scale']));
      if (s['WaterMark Location']) setPosition(s['WaterMark Location']);
    });
  }, []);

  const refreshPreview = async (op = opacity, sc = scale, pos = position, b64 = wmB64) => {
    setLoadingPreview(true);
    try {
      const r = await apiFetch<{ image_b64: string }>('/watermark/preview', {
        method: 'POST',
        body: JSON.stringify({ wm_image_b64: b64, opacity: op, scale: sc, position: pos }),
      });
      setPreviewSrc(`data:image/jpeg;base64,${r.image_b64}`);
    } catch { /* silent */ }
    setLoadingPreview(false);
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      const result = ev.target?.result as string;
      const b64 = result.split(',')[1];
      setWmB64(b64);
      refreshPreview(opacity, scale, position, b64);
    };
    reader.readAsDataURL(file);
  };

  const saveSettings = async () => {
    try {
      await apiFetch('/watermark/save', {
        method: 'POST',
        body: JSON.stringify({ wm_image_b64: wmB64, opacity, scale, position }),
      });
      toast.success('Watermark settings saved!');
    } catch (err: any) { toast.error(err.message); }
  };

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
      <h1 className="page-title">Watermark</h1>
      <p className="page-subtitle">Configure & preview your watermark overlay</p>

      <div style={{ display: 'grid', gridTemplateColumns: '300px 1fr', gap: '24px', alignItems: 'start' }}>
        {/* Controls */}
        <div className="glass-card" style={{ padding: '28px' }}>
          <div className="form-group">
            <label className="form-label">Watermark Image</label>
            <input type="file" accept="image/*" onChange={handleImageUpload} style={{ display: 'none' }} id="wm-file" />
            <label htmlFor="wm-file" className="btn-secondary" style={{ display: 'flex', justifyContent: 'center', cursor: 'pointer' }}>
              Choose Image
            </label>
            {wmB64 && <p style={{ fontSize: '0.75rem', color: '#4ecd70', marginTop: '6px', textAlign: 'center' }}>Image loaded</p>}
          </div>

          <div className="form-group">
            <label className="form-label">Opacity: {opacity.toFixed(2)}</label>
            <input type="range" min={0.1} max={1} step={0.05} value={opacity}
              onChange={e => { setOpacity(Number(e.target.value)); refreshPreview(Number(e.target.value), scale, position); }} />
          </div>

          <div className="form-group">
            <label className="form-label">Size (Scale): {(scale * 100).toFixed(0)}%</label>
            <input type="range" min={0.05} max={0.8} step={0.05} value={scale}
              onChange={e => { setScale(Number(e.target.value)); refreshPreview(opacity, Number(e.target.value), position); }} />
          </div>

          <div className="form-group">
            <label className="form-label">Position</label>
            <div className="radio-grid">
              {POSITIONS.map(p => (
                <button key={p} className={`radio-grid-btn${position === p ? ' selected' : ''}`}
                  onClick={() => { setPosition(p); refreshPreview(opacity, scale, p); }}>
                  {p.replace('-', ' ')}
                </button>
              ))}
            </div>
          </div>

          <LiquidButton onClick={saveSettings} fullWidth style={{ marginBottom: '10px' }}>
            Save Settings
          </LiquidButton>
          <LiquidButton size="sm" fullWidth onClick={() => refreshPreview()}>
            Refresh Preview
          </LiquidButton>
        </div>

        {/* Live Preview */}
        <div className="glass-card" style={{ padding: '20px' }}>
          <p style={{ fontFamily: 'var(--font-elegant)', color: 'var(--color-text-muted)', marginBottom: '12px' }}>Live Preview</p>
          {loadingPreview ? (
            <div style={{ minHeight: '400px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--color-text-muted)' }}>
              Loading preview...
            </div>
          ) : previewSrc ? (
            <div className="wm-preview-container">
              <img src={previewSrc} alt="Watermark preview" style={{ width: '100%', display: 'block' }} />
            </div>
          ) : (
            <div style={{ minHeight: '400px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: 'var(--color-text-muted)', fontFamily: 'var(--font-elegant)', fontStyle: 'italic' }}>
              <p>Upload a watermark image and click</p>
              <LiquidButton size="sm" style={{ marginTop: '12px' }} onClick={() => refreshPreview()}>
                Generate Preview
              </LiquidButton>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}
