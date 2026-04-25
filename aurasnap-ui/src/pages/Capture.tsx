import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { apiFetch } from '../api';
import type { Event } from '../api';
import toast from 'react-hot-toast';
import LiquidButton from '../components/LiquidButton';
import LiquidInput from '../components/LiquidInput';


export default function Capture() {
  const [events, setEvents] = useState<Event[]>([]);
  const [eventName, setEventName] = useState('');
  const [userName, setUserName] = useState('');
  const [phone, setPhone] = useState('');
  const [streaming, setStreaming] = useState(false);
  const [capturing, setCapturing] = useState(false);
  const [captureCount, setCaptureCount] = useState(0);

  const MAX_FRAMES = 100;
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  useEffect(() => {
    apiFetch<Event[]>('/events').then(setEvents).catch(console.error);
  }, []);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 1280, height: 720 } });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
        setStreaming(true);
      }
    } catch (err) {
      toast.error('Could not access camera');
    }
  };

  const stopCamera = () => {
    streamRef.current?.getTracks().forEach(t => t.stop());
    setStreaming(false);
  };

  const captureAll = async () => {
    if (!eventName || !userName || !phone) return toast.error('Fill all details');

    // Clear folder first to overwrite instead of append
    try {
      await apiFetch(`/capture/clear/${encodeURIComponent(eventName)}/${encodeURIComponent(phone)}`, { method: 'DELETE' });
    } catch (err) {
      console.error('Failed to clear folder', err);
    }

    setCapturing(true);
    setCaptureCount(0);

    for (let i = 0; i < MAX_FRAMES; i++) {
      await new Promise(r => setTimeout(r, 400));
      if (!videoRef.current || !canvasRef.current) break;

      const video = videoRef.current;
      const canvas = canvasRef.current;
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext('2d');
      ctx?.drawImage(video, 0, 0);

      const b64 = canvas.toDataURL('image/jpeg', 0.85);
      await apiFetch('/capture/frame', {
        method: 'POST',
        body: JSON.stringify({ event_name: eventName, user_name: userName, phone_number: phone, frame_b64: b64 }),
      });
      setCaptureCount(i + 1);
    }

    setCapturing(false);
    toast.success('Capture complete');
    setUserName('');
    setPhone('');
  };

  const valid = eventName && userName && phone.length >= 10;

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
      <h1 className="page-title">Capture</h1>
      <p className="page-subtitle">Training Data Acquisition</p>

      <div className="form-grid-2" style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: '24px' }}>
        <div className="glass-card" style={{ padding: '28px' }}>
          <div className="form-group">
            <label className="form-label">Select Event</label>
            <select className="form-input form-select" value={eventName} onChange={e => setEventName(e.target.value)}>
              <option value="">Choose event...</option>
              {events.map(ev => <option key={ev['Event Name']} value={ev['Event Name']}>{ev['Event Name']}</option>)}
            </select>
          </div>
          <div className="form-group">
            <LiquidInput label="Guest Name" placeholder="Full Name" value={userName} onChange={e => setUserName(e.target.value)} />
          </div>
          <div className="form-group">
            <LiquidInput label="WhatsApp Number" placeholder="e.g. 9876543210" value={phone} onChange={e => setPhone(e.target.value)} />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {!streaming
              ? <LiquidButton onClick={startCamera} fullWidth>Open Camera</LiquidButton>
              : <LiquidButton onClick={stopCamera} fullWidth>Stop Camera</LiquidButton>
            }
            <LiquidButton disabled={!streaming || !valid || capturing} onClick={captureAll} fullWidth>
              {capturing ? `Capturing ${captureCount}/${MAX_FRAMES}...` : `Capture (${MAX_FRAMES} frames)`}
            </LiquidButton>
          </div>
          {capturing && (
            <div style={{ marginTop: '16px' }}>
              <div className="progress-track">
                <div className="progress-fill" style={{ width: `${(captureCount / MAX_FRAMES) * 100}%` }} />
              </div>
            </div>
          )}
        </div>
        <div className="glass-card" style={{ padding: '20px' }}>
          <p style={{ fontFamily: 'var(--font-elegant)', color: 'var(--color-text-muted)', marginBottom: '12px' }}>Live Camera Feed</p>
          <video ref={videoRef} autoPlay playsInline className="camera-feed" style={{ display: streaming ? 'block' : 'none' }} />
          {!streaming && (
            <div className="camera-feed" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '300px', color: 'var(--color-text-muted)', fontStyle: 'italic' }}>
              Camera not active
            </div>
          )}
          <canvas ref={canvasRef} style={{ display: 'none' }} />
        </div>
      </div>
    </motion.div>
  );
}
