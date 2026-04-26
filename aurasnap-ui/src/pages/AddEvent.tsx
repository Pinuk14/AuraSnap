import { useState } from 'react';
import { motion } from 'framer-motion';
import { apiFetch, selectFolder } from '../services/api';
import toast from 'react-hot-toast';
import LiquidInput from '../components/LiquidInput';
import LiquidButton from '../components/LiquidButton';

export default function AddEvent() {
  const [form, setForm] = useState({
    event_name: '',
    event_date: '',
    event_owner: '',
    contact_number: '',
    base_path: '',
  });
  const [loading, setLoading] = useState(false);

  const set = (key: string) => (e: any) => setForm(f => ({ ...f, [key]: e.target.value }));

  const todayStr = () => new Date().toISOString().split('T')[0];

  const handleBrowse = async () => {
    const path = await selectFolder();
    if (path) setForm(f => ({ ...f, base_path: path }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.base_path) return toast.error('Select a folder location');
    setLoading(true);
    try {
      await apiFetch('/events', {
        method: 'POST',
        body: JSON.stringify({ ...form, file_location: '' }),
      });
      toast.success('Event created');
      setForm({ event_name: '', event_date: '', event_owner: '', contact_number: '', base_path: '' });
    } catch (err: any) {
      toast.error(err.detail || 'Error creating event');
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
      <h1 className="page-title">Add Event</h1>
      <p className="page-subtitle">Set up a new photography workflow session</p>

      <div className="glass-card" style={{ padding: '36px', maxWidth: '640px', margin: '0 auto' }}>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <LiquidInput label="Event Name" placeholder="e.g. Rahul & Priya Wedding" value={form.event_name} onChange={set('event_name')} required />
          </div>

          <div className="form-grid-2">
            <div className="form-group">
              <label className="form-label">Event Date</label>
              <div style={{ display: 'flex', gap: '8px' }}>
                <LiquidInput type="date" value={form.event_date} onChange={set('event_date')} required />
                <LiquidButton type="button" size="sm" onClick={() => setForm((f) => ({ ...f, event_date: todayStr() }))}>Today</LiquidButton>
              </div>
            </div>
            <div className="form-group">
              <LiquidInput label="Event Owner" placeholder="Organiser name" value={form.event_owner} onChange={set('event_owner')} required />
            </div>
          </div>

          <div className="form-group">
            <LiquidInput label="Contact Number" placeholder="10-digit phone number" value={form.contact_number} onChange={set('contact_number')} required />
          </div>

          <div className="form-group">
            <label className="form-label">Folder Location</label>
            <div style={{ display: 'flex', gap: '8px' }}>
              <input className="form-input" placeholder="Path where photos are stored" value={form.base_path} onChange={set('base_path')} required />
              <LiquidButton type="button" size="sm" onClick={handleBrowse}>Browse</LiquidButton>
            </div>
            <p className="form-hint">The event folder will be created inside this location.</p>
          </div>

          <LiquidButton type="submit" fullWidth disabled={loading} style={{ marginTop: '8px' }}>
            {loading ? 'Processing...' : 'Create Event'}
          </LiquidButton>
        </form>
      </div>
    </motion.div>
  );
}
