import { motion } from 'framer-motion';
import { apiFetch } from '../services/api';
import type { Event } from '../services/api';

const statItems = (events: Event[]) => [
  { label: 'Total Events', value: events.length, icon: '📅' },
  {
    label: 'Total Guests',
    value: events.reduce((a, e) => a + (e.Guests?.length ?? 0), 0),
    icon: '👥',
  },
  {
    label: 'Avg Accuracy',
    value: events.length > 0 
      ? (events.reduce((a, e) => a + (e.Accuracy ?? 0), 0) / events.length).toFixed(1) + '%' 
      : '0%',
    icon: '🎯',
  },
  { label: 'Messages Sent', value: '—', icon: '💬' },
];

import { useEffect, useState } from 'react';

export default function Dashboard() {
  const [events, setEvents] = useState<Event[]>([]);

  useEffect(() => {
    apiFetch<Event[]>('/events').then(setEvents).catch(console.error);
  }, []);

  const stats = statItems(events);
  const recentEvents = events.slice(-5).reverse();

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <h1 className="page-title">Dashboard</h1>
      <p className="page-subtitle">Platform overview and session metrics</p>

      {/* Stat Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px', marginBottom: '36px' }}>
        {stats.map((s, i) => (
          <motion.div
            key={s.label}
            className="stat-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.08 }}
          >
            <div className="stat-card-number">{s.value}</div>
            <div className="stat-card-label">{s.label}</div>
          </motion.div>
        ))}
      </div>

      {/* Recent Events Table */}
      <div className="glass-card" style={{ padding: '24px' }}>
        <h2 style={{ fontFamily: 'var(--font-brand)', fontSize: '1.8rem', marginBottom: '20px', color: 'var(--color-text-primary)' }}>
          Recent Events
        </h2>
        {recentEvents.length === 0 ? (
          <p style={{ color: 'var(--color-text-muted)', fontFamily: 'var(--font-elegant)', fontStyle: 'italic', textAlign: 'center', padding: '40px' }}>
            No sessions recorded yet.
          </p>
        ) : (
          <table className="glass-table">
            <thead>
              <tr>
                <th>Event Name</th>
                <th>Date</th>
                <th>Accuracy</th>
                <th>Guests</th>
              </tr>
            </thead>
            <tbody>
              {recentEvents.map((e) => (
                <tr key={e['Event Name']}>
                  <td style={{ color: 'var(--color-text-primary)', fontWeight: 500 }}>{e['Event Name']}</td>
                  <td>{e['Event Date']}</td>
                  <td>
                    <span style={{ color: (e.Accuracy ?? 0) > 80 ? '#4ecd70' : (e.Accuracy ?? 0) > 50 ? 'var(--color-accent-gold)' : '#f06292' }}>
                      {e.Accuracy ? `${e.Accuracy}%` : 'N/A'}
                    </span>
                  </td>
                  <td>
                    <span className="badge badge-info">{e.Guests?.length ?? 0}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </motion.div>
  );
}
