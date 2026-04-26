import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { apiFetch } from '../services/api';
import type { Settings } from '../services/api';
import toast from 'react-hot-toast';
import LiquidButton from '../components/LiquidButton';

export default function SettingsPage() {
  const [form, setForm] = useState<Partial<Settings>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch<Settings>('/settings').then(s => { setForm(s); setLoading(false); }).catch(console.error);
  }, []);

  const set = (k: keyof Settings) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) =>
    setForm(f => ({ ...f, [k]: e.target.value }));

  const save = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiFetch('/settings', {
        method: 'POST',
        body: JSON.stringify({
          phone_number: form['Number'] ?? '',
          whatsapp_message: form['Whatsapp'] ?? '',
          camera: form['Camera'] ?? 'Camera 0',
          processing_mode: form['Processing Mode'] ?? 'CPU',
          whatsapp_delivery: form['WhatsApp Delivery Method'] ?? 'PyAutoGUI',
        }),
      });
      toast.success('Settings saved!');
    } catch (err: any) { toast.error(err.message); }
  };

  if (loading) return <p style={{ color: 'var(--color-text-muted)' }}>Loading settings…</p>;

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
      <h1 className="page-title">Settings</h1>
      <p className="page-subtitle">Configure your account & automation preferences</p>

      <div className="glass-card" style={{ padding: '36px', maxWidth: '640px' }}>
        <form onSubmit={save}>
          <div className="form-group">
            <label className="form-label">WhatsApp Phone Number</label>
            <input className="form-input" placeholder="+91XXXXXXXXXX" value={form['Number'] ?? ''} onChange={set('Number')} />
          </div>

          <div className="form-group">
            <label className="form-label">WhatsApp Message Template</label>
            <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: '6px' }}>
              Use <code style={{ background: 'rgba(176,110,243,0.15)', padding: '1px 5px', borderRadius: '4px' }}>@USERNAME</code> to insert the guest's name.
            </p>
            <textarea className="form-input form-textarea" value={form['Whatsapp'] ?? ''} onChange={set('Whatsapp')} rows={4} />
          </div>

          <div className="form-group">
            <label className="form-label">Camera</label>
            <select className="form-input form-select" value={form['Camera'] ?? 'Camera 0'} onChange={set('Camera')}>
              {[0, 1, 2, 3, 4].map(i => <option key={i} value={`Camera ${i}`}>Camera {i}</option>)}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Processing Mode</label>
            <div style={{ display: 'flex', gap: '16px', marginTop: '8px' }}>
              {['CPU', 'GPU'].map(m => (
                <label key={m} style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', color: 'var(--color-text-secondary)' }}>
                  <input type="radio" name="proc" value={m} checked={form['Processing Mode'] === m} onChange={set('Processing Mode')} />
                  {m}
                </label>
              ))}
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">WhatsApp Delivery Method</label>
            <div style={{ display: 'flex', gap: '16px', marginTop: '8px' }}>
              {['PyAutoGUI', 'Selenium'].map(m => (
                <label key={m} style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', color: 'var(--color-text-secondary)' }}>
                  <input type="radio" name="delivery" value={m} checked={form['WhatsApp Delivery Method'] === m} onChange={set('WhatsApp Delivery Method')} />
                  {m}
                </label>
              ))}
            </div>
          </div>

          <LiquidButton type="submit" fullWidth style={{ marginTop: '12px' }}>
            Save Settings
          </LiquidButton>

        </form>
      </div>
    </motion.div>
  );
}
