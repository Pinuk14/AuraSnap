
import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { apiFetch, selectFolder } from '../services/api';
import type { Event } from '../services/api';
import toast from 'react-hot-toast';
import LiquidButton from '../components/LiquidButton';
import magicService from '../magicService';

export default function Magic() {
  const [events, setEvents] = useState<Event[]>([]);
  const [eventName, setEventName] = useState('');
  const [customPath, setCustomPath] = useState('');
  const [tasks, setTasks] = useState<string[]>(['train', 'sort', 'send']);
  const [modelExists, setModelExists] = useState(false);
  
  // State from magicService
  const [ms, setMs] = useState(magicService.getState());

  useEffect(() => {
    apiFetch<Event[]>('/events').then(setEvents).catch(console.error);
    const unsubscribe = magicService.subscribe(setMs);
    return () => { unsubscribe(); };
  }, []);

  useEffect(() => {
    if (!eventName) {
      setModelExists(false);
      return;
    }
    apiFetch<{ exists: boolean }>('/magic/check-model', {
      method: 'POST',
      body: JSON.stringify({ event_name: eventName, tasks: [] }),
    }).then(r => setModelExists(r.exists)).catch(() => setModelExists(false));
  }, [eventName]);

  const toggleTask = (task: string) => {
    setTasks(prev => prev.includes(task) ? prev.filter(t => t !== task) : [...prev, task]);
  };

  const handleBrowse = async () => {
    const path = await selectFolder();
    if (path) setCustomPath(path);
  };

  const runMagic = async () => {
    if (!eventName) return toast.error('Select an event first.');
    if (tasks.length === 0) return toast.error('Select at least one task.');
    await magicService.run(eventName, customPath, tasks);
  };

  const isRunning = ms.phase === 'running';

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
      <h1 className="page-title">Magic</h1>
      <p className="page-subtitle">Selective Automation Pipeline</p>

      <div className="glass-card" style={{ padding: '36px', maxWidth: '640px', margin: '0 auto' }}>
        <div className="form-group">
          <label className="form-label">Select Event</label>
          <select className="form-input form-select" value={eventName} onChange={e => setEventName(e.target.value)} disabled={isRunning}>
            <option value="">Choose event...</option>
            {events.map(ev => <option key={ev['Event Name']} value={ev['Event Name']}>{ev['Event Name']}</option>)}
          </select>
        </div>

        <div className="form-group">
          <label className="form-label">Photos Path Override</label>
          <div style={{ display: 'flex', gap: '8px' }}>
            <input className="form-input" placeholder="Default: Event folder" value={customPath} onChange={e => setCustomPath(e.target.value)} disabled={isRunning} />
            <LiquidButton type="button" size="sm" disabled={isRunning} onClick={handleBrowse}>
              Browse
            </LiquidButton>
          </div>
        </div>

        <div className="form-group">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <label className="form-label">Tasks to Execute</label>
            {eventName && (
              <span style={{ fontSize: '0.75rem', color: modelExists ? '#4ecd70' : 'var(--color-text-muted)', fontFamily: 'var(--font-elegant)' }}>
                {modelExists ? '✓ Model Detected' : '× No Model'}
              </span>
            )}
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '16px', marginTop: '8px' }}>
            {['train', 'sort', 'send'].map(t => (
              <label key={t} style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', color: 'var(--color-text-secondary)', textTransform: 'capitalize' }}>
                <input type="checkbox" checked={tasks.includes(t)} onChange={() => toggleTask(t)} disabled={isRunning} style={{ width: '18px', height: '18px' }} />
                {t}
              </label>
            ))}
          </div>
        </div>

        <LiquidButton onClick={runMagic} disabled={isRunning || !eventName || tasks.length === 0} fullWidth style={{ marginTop: '16px', fontSize: '1rem', padding: '14px 0' }}>
          {isRunning ? 'Running Tasks...' : 'Execute Magic'}
        </LiquidButton>

        {ms.phase !== 'idle' && (
          <div style={{ marginTop: '28px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span style={{ fontSize: '0.875rem', color: ms.phase === 'error' ? '#f06292' : ms.phase === 'done' ? '#4ecd70' : 'var(--color-accent-2)', fontFamily: 'var(--font-ui)' }}>
                {ms.statusText}
              </span>
              <span style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)' }}>{ms.percent.toFixed(0)}%</span>
            </div>
            <div className="progress-track">
              <div className="progress-fill" style={{ width: `${ms.percent}%`, background: ms.phase === 'error' ? 'linear-gradient(90deg,#f06292,#e91e63)' : undefined }} />
            </div>
            {ms.phase === 'done' && (
              <LiquidButton size="sm" style={{ marginTop: '16px' }} onClick={() => magicService.reset()}>Dismiss</LiquidButton>
            )}
          </div>
        )}
      </div>
    </motion.div>
  );
}
