/**
 * magicService.ts
 * Manages the long-running "Magic" process so it survives page navigation.
 */

export type MagicPhase = 'idle' | 'running' | 'done' | 'error';

interface ProgressMsg {
  type: 'progress' | 'done' | 'error';
  phase?: string;
  current?: number;
  total?: number;
  percent?: number;
  message?: string;
}

export interface MagicState {
  phase: MagicPhase;
  statusText: string;
  percent: number;
  eventName: string;
}

let state: MagicState = {
  phase: 'idle',
  statusText: '',
  percent: 0,
  eventName: ''
};

type Listener = (s: MagicState) => void;
const listeners = new Set<Listener>();

export const magicService = {
  getState: () => state,
  
  subscribe: (l: Listener) => {
    listeners.add(l);
    return () => listeners.delete(l);
  },

  run: async (eventName: string, customPath: string, tasks: string[]) => {
    if (state.phase === 'running') return;
    
    state = { ...state, phase: 'running', eventName, percent: 0, statusText: 'Starting…' };
    notify();

    try {
      const res = await fetch('/api/magic/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ event_name: eventName, custom_path: customPath, tasks }),
      });

      if (!res.body) throw new Error("No response body");

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() ?? '';
        
        for (const line of lines) {
          if (!line.startsWith('data:')) continue;
          try {
            const msg: ProgressMsg = JSON.parse(line.slice(5).trim());
            if (msg.type === 'progress') {
              state = { ...state, statusText: msg.phase ?? '', percent: msg.percent ?? 0 };
              notify();
            } else if (msg.type === 'done') {
              state = { ...state, phase: 'done', statusText: msg.message ?? 'Complete!', percent: 100 };
              notify();
              return;
            } else if (msg.type === 'error') {
              state = { ...state, phase: 'error', statusText: msg.message ?? 'An error occurred.' };
              notify();
              return;
            }
          } catch { /* skip malformed */ }
        }
      }
    } catch (err: any) {
      state = { ...state, phase: 'error', statusText: err.message || 'Connection failed.' };
      notify();
    }
  },

  reset: () => {
    state = { phase: 'idle', statusText: '', percent: 0, eventName: '' };
    notify();
  }
};

function notify() {
  listeners.forEach(l => l(state));
}

export default magicService;
