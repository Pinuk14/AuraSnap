import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { apiFetch } from '../services/api';
import type { Event } from '../services/api';
import toast from 'react-hot-toast';
import LiquidButton from '../components/LiquidButton';

export default function UpdateEvents() {
  const [events, setEvents] = useState<Event[]>([]);
  const [edits, setEdits] = useState<Record<string, Partial<Event>>>({});
  const [loading, setLoading] = useState(true);

  const load = () => {
    setLoading(true);
    apiFetch<Event[]>('/events').then((ev) => { setEvents(ev); setLoading(false); }).catch(console.error);
  };

  useEffect(() => { load(); }, []);

  const setField = (name: string, field: keyof Event, val: string) => {
    setEdits((e) => ({ ...e, [name]: { ...e[name], [field]: val } }));
  };

  const get = (ev: Event, field: keyof Event) =>
    (edits[ev['Event Name']]?.[field] as string | undefined) ?? (ev[field] as string);

  const saveEvent = async (ev: Event) => {
    const merged = { ...ev, ...edits[ev['Event Name']] };
    try {
      await apiFetch(`/events/${encodeURIComponent(ev['Event Name'])}`, {
        method: 'PUT',
        body: JSON.stringify({
          event_name: merged['Event Name'],
          event_date: merged['Event Date'],
          event_owner: merged['Event Owner'],
          contact_number: merged['Contact Number'],
          file_location: merged['File Location'],
        }),
      });
      toast.success('Event updated!');
      load();
    } catch (err: any) { toast.error(err.message); }
  };

  const deleteEvent = async (name: string) => {
    if (!confirm(`Delete event "${name}"? This will remove the folder too.`)) return;
    try {
      await apiFetch(`/events/${encodeURIComponent(name)}`, { method: 'DELETE' });
      toast.success('Event deleted');
      load();
    } catch (err: any) { toast.error(err.message); }
  };

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
      <h1 className="page-title">Manage Events</h1>
      <p className="page-subtitle">Edit or remove registered events</p>

      {loading ? (
        <p style={{ color: 'var(--color-text-muted)', fontFamily: 'var(--font-elegant)', fontStyle: 'italic' }}>Loading events...</p>
      ) : events.length === 0 ? (
        <div className="glass-card" style={{ padding: '60px', textAlign: 'center' }}>
          <p style={{ color: 'var(--color-text-muted)', fontFamily: 'var(--font-elegant)', fontStyle: 'italic', fontSize: '1.1rem' }}>No events found. Add one first!</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {events.map((ev, i) => (
            <motion.div
              key={ev['Event Name']}
              className="glass-card"
              style={{ padding: '24px' }}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.05 }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '16px' }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: '14px', flex: 1 }}>
                  {[
                    { label: 'Event Name', field: 'Event Name' as keyof Event },
                    { label: 'Date', field: 'Event Date' as keyof Event },
                    { label: 'Owner', field: 'Event Owner' as keyof Event },
                    { label: 'Contact', field: 'Contact Number' as keyof Event },
                  ].map(({ label, field }) => (
                    <div key={field}>
                      <label className="form-label">{label}</label>
                      <input
                        className="form-input"
                        value={get(ev, field)}
                        onChange={(e) => setField(ev['Event Name'], field, e.target.value)}
                      />
                    </div>
                  ))}
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', flexShrink: 0 }}>
                  <LiquidButton size="sm" onClick={() => saveEvent(ev)}>
                    Save
                  </LiquidButton>
                  <button className="btn-danger" style={{ fontSize: '0.8rem', padding: '8px' }} onClick={() => deleteEvent(ev['Event Name'])}>
                    Remove
                  </button>
                </div>
              </div>

              <div style={{ marginTop: '10px', display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
                <span className="badge badge-info">{ev.Guests?.length ?? 0} guests</span>
                <span className="badge" style={{ background: 'rgba(78,205,112,0.15)', color: '#4ecd70' }}>
                  Accuracy: {ev.Accuracy ? `${ev.Accuracy}%` : 'N/A'}
                </span>
                <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', fontFamily: 'var(--font-elegant)' }}>
                  Location: {ev['File Location']}
                </span>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </motion.div>
  );
}
