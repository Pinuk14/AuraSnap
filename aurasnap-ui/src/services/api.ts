// Shared API helper
const BASE = '/api';

export async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Request failed');
  }
  return res.json();
}

export async function selectFolder(): Promise<string> {
  const r = await apiFetch<{ path: string }>('/utils/select-folder');
  return r.path;
}

export interface Event {
  'Event Name': string;
  'Event Date': string;
  'Event Owner': string;
  'Contact Number': string;
  'File Location': string;
  'Accuracy': number;
  'Guests': Guest[];
}

export interface Guest {
  name: string;
  'whatsapp Number': string;
  photos: string[];
}

export interface Settings {
  Number: string;
  Whatsapp: string;
  Camera: string;
  'Processing Mode': string;
  'WhatsApp Delivery Method': string;
  'WaterMark Image'?: string;
  'WaterMark Location'?: string;
  'WaterMark Opacity'?: number;
  'WaterMark Scale'?: number;
}
