/**
 * LiquidToggle.tsx
 * TypeScript port of Modular-UIcomponents/components/LiquidToggle.jsx
 */
import { useState } from 'react';
import type { ReactNode } from 'react';

const SunIcon = () => (
  <svg width={13} height={13} viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth={2.5} strokeLinecap="round">
    <circle cx={12} cy={12} r={4} />
    <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41" />
  </svg>
);

const MoonIcon = () => (
  <svg width={13} height={13} viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z" />
  </svg>
);

const sizeTokens = {
  sm: { trackW: '52px', trackH: '28px', thumbSize: '20px', thumbInset: '4px', iconSize: 10, gap: '8px', labelSize: '0.85rem' },
  md: { trackW: '68px', trackH: '36px', thumbSize: '26px', thumbInset: '5px', iconSize: 13, gap: '10px', labelSize: '1rem' },
  lg: { trackW: '84px', trackH: '44px', thumbSize: '32px', thumbInset: '6px', iconSize: 16, gap: '12px', labelSize: '1.1rem' },
};

interface LiquidToggleProps {
  checked?: boolean;
  defaultChecked?: boolean;
  onChange?: (val: boolean) => void;
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  iconOn?: ReactNode;
  iconOff?: ReactNode;
  label?: string;
  labelPosition?: 'left' | 'right';
}

export default function LiquidToggle({
  checked: controlledChecked,
  defaultChecked = false,
  onChange,
  size = 'md',
  disabled = false,
  iconOn,
  iconOff,
  label,
  labelPosition = 'right',
}: LiquidToggleProps) {
  const isControlled = controlledChecked !== undefined;
  const [internalChecked, setInternalChecked] = useState(defaultChecked);
  const [hovered, setHovered] = useState(false);
  const checked = isControlled ? controlledChecked! : internalChecked;
  const sz = sizeTokens[size];

  const handleToggle = () => {
    if (disabled) return;
    const next = !checked;
    if (!isControlled) setInternalChecked(next);
    onChange?.(next);
  };

  const thumbIcon = checked ? (iconOn ?? <SunIcon />) : (iconOff ?? <MoonIcon />);

  return (
    <>
      <style>{`
        @keyframes lg-toggle-pop {
          0% { transform: scale(1); }
          40% { transform: scale(1.18); }
          100% { transform: scale(1); }
        }
      `}</style>
      <div
        onClick={handleToggle}
        onMouseEnter={() => !disabled && setHovered(true)}
        onMouseLeave={() => setHovered(false)}
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: sz.gap,
          flexDirection: labelPosition === 'left' ? 'row-reverse' : 'row',
          cursor: disabled ? 'not-allowed' : 'pointer',
          opacity: disabled ? 0.45 : 1,
          userSelect: 'none',
          transform: hovered ? 'scale(1.05)' : 'scale(1)',
          transition: 'transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 2.2)',
        }}
      >
        {/* Track */}
        <div style={{
          position: 'relative',
          width: sz.trackW, height: sz.trackH,
          borderRadius: '9999px', overflow: 'hidden',
          boxShadow: hovered
            ? '0 8px 24px rgba(0,0,0,0.3), 0 0 0 1.5px rgba(255,255,255,0.4)'
            : '0 4px 12px rgba(0,0,0,0.2), 0 0 20px rgba(0,0,0,0.1)',
          transition: 'box-shadow 0.4s cubic-bezier(0.175, 0.885, 0.32, 2.2)',
          flexShrink: 0,
        }}>
          {/* Glass blur */}
          <div style={{ position: 'absolute', inset: 0, zIndex: 0, backdropFilter: 'blur(3px)', WebkitBackdropFilter: 'blur(3px)', filter: 'url(#glass-distortion)', isolation: 'isolate', borderRadius: 'inherit' }} />
          {/* Tint */}
          <div style={{ position: 'absolute', inset: 0, zIndex: 1, background: hovered ? 'rgba(255,255,255,0.4)' : checked ? 'rgba(255,255,255,0.32)' : 'rgba(255,255,255,0.18)', transition: 'background 0.4s cubic-bezier(0.175, 0.885, 0.32, 2.2)', borderRadius: 'inherit' }} />
          {/* Edge shine */}
          <div style={{ position: 'absolute', inset: 0, zIndex: 2, borderRadius: 'inherit', boxShadow: hovered ? 'inset 2px 2px 2px 0 rgba(255,255,255,0.7), inset -1px -1px 2px 1px rgba(255,255,255,0.5)' : 'inset 2px 2px 1px 0 rgba(255,255,255,0.5), inset -1px -1px 1px 1px rgba(255,255,255,0.3)', transition: 'box-shadow 0.4s cubic-bezier(0.175, 0.885, 0.32, 2.2)' }} />

          {/* Thumb */}
          <div style={{
            position: 'absolute',
            top: sz.thumbInset,
            left: checked ? `calc(100% - ${sz.thumbSize} - ${sz.thumbInset})` : sz.thumbInset,
            width: sz.thumbSize, height: sz.thumbSize,
            borderRadius: '50%', zIndex: 10, overflow: 'hidden',
            boxShadow: '0 2px 8px rgba(0,0,0,0.3), 0 0 0 1px rgba(255,255,255,0.4)',
            transition: 'left 0.4s cubic-bezier(0.175, 0.885, 0.32, 2.2)',
            animation: 'lg-toggle-pop 0.4s cubic-bezier(0.175, 0.885, 0.32, 2.2)',
          }}>
            <div style={{ position: 'absolute', inset: 0, backdropFilter: 'blur(6px)', WebkitBackdropFilter: 'blur(6px)', filter: 'url(#glass-distortion)', isolation: 'isolate', borderRadius: '50%' }} />
            <div style={{ position: 'absolute', inset: 0, background: checked ? 'rgba(255,255,255,0.5)' : 'rgba(255,255,255,0.35)', transition: 'background 0.4s ease', borderRadius: '50%' }} />
            <div style={{ position: 'absolute', inset: 0, borderRadius: '50%', boxShadow: 'inset 1px 1px 1px rgba(255,255,255,0.8), inset -1px -1px 1px rgba(255,255,255,0.3)' }} />
            <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 5 }}>
              {thumbIcon}
            </div>
          </div>
        </div>

        {label && (
          <span style={{ color: 'inherit', opacity: 0.85, fontFamily: 'var(--font-ui)', fontWeight: 500, fontSize: sz.labelSize, letterSpacing: '0.01em' }}>
            {label}
          </span>
        )}
      </div>
    </>
  );
}
