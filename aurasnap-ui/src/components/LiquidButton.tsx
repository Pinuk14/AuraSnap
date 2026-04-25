/**
 * LiquidButton.tsx
 * Direct TypeScript port of Modular-UIcomponents/components/LiquidButton.jsx
 * Uses SVG feTurbulence + feDisplacementMap distortion + specular lighting.
 */
import { useState } from 'react';
import type { ReactNode, CSSProperties } from 'react';

interface LiquidButtonProps {
  children: ReactNode;
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
  onClick?: () => void;
  disabled?: boolean;
  icon?: ReactNode;
  iconRight?: ReactNode;
  type?: 'button' | 'submit' | 'reset';
  style?: CSSProperties;
}

const sizeMap = {
  sm: { fontSize: '0.85rem', borderRadius: '2rem',   paddingInline: '1.4rem', paddingBlock: '0.6rem' },
  md: { fontSize: '0.95rem', borderRadius: '2.5rem', paddingInline: '1.8rem', paddingBlock: '0.85rem' },
  lg: { fontSize: '1.05rem', borderRadius: '3rem',   paddingInline: '2.4rem', paddingBlock: '1.1rem' },
};

export default function LiquidButton({
  children,
  size = 'md',
  fullWidth = false,
  onClick,
  disabled = false,
  icon,
  iconRight,
  type = 'button',
  style = {},
}: LiquidButtonProps) {
  const [hovered, setHovered] = useState(false);
  const [pressed, setPressed] = useState(false);
  const sz = sizeMap[size];

  return (
    <button
      type={type}
      onClick={disabled ? undefined : onClick}
      onMouseEnter={() => !disabled && setHovered(true)}
      onMouseLeave={() => { setHovered(false); setPressed(false); }}
      onMouseDown={() => !disabled && setPressed(true)}
      onMouseUp={() => setPressed(false)}
      disabled={disabled}
      style={{
        position: 'relative',
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        cursor: disabled ? 'not-allowed' : 'pointer',
        overflow: 'hidden',
        border: 'none',
        background: 'transparent',
        padding: 0,
        width: fullWidth ? '100%' : 'auto',
        ...sz,
        boxShadow: '0 6px 6px rgba(0,0,0,0.2), 0 0 20px rgba(0,0,0,0.1)',
        transform: pressed ? 'scale(0.92)' : hovered ? 'scale(1.05)' : 'scale(1)',
        transition: 'transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 2.2), box-shadow 0.4s cubic-bezier(0.175, 0.885, 0.32, 2.2)',
        opacity: disabled ? 0.45 : 1,
        ...style,
      }}
    >
      {/* Layer 1 — glass distortion + blur */}
      <div style={{
        position: 'absolute', inset: 0,
        backdropFilter: 'blur(3px)', WebkitBackdropFilter: 'blur(3px)',
        filter: 'url(#glass-distortion)',
        overflow: 'hidden', isolation: 'isolate',
        zIndex: 0, borderRadius: 'inherit',
      }} />
      {/* Layer 2 — white tint */}
      <div style={{
        position: 'absolute', inset: 0,
        background: 'rgba(255,255,255,0.25)',
        zIndex: 1, borderRadius: 'inherit',
      }} />
      {/* Layer 3 — edge shine */}
      <div style={{
        position: 'absolute', inset: 0,
        zIndex: 2, borderRadius: 'inherit',
        boxShadow: 'inset 2px 2px 1px 0 rgba(255,255,255,0.5), inset -1px -1px 1px 1px rgba(255,255,255,0.5)',
      }} />
      {/* Layer 4 — content */}
      <span style={{
        position: 'relative', zIndex: 3,
        color: 'inherit',
        fontFamily: 'var(--font-ui)',
        fontWeight: 600, letterSpacing: '0.01em',
        userSelect: 'none',
        display: 'flex', alignItems: 'center', gap: '8px',
        transform: hovered && !pressed ? 'scale(0.95)' : 'scale(1)',
        transition: 'transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 2.2)',
      }}>
        {icon && <span style={{ display: 'flex', alignItems: 'center' }}>{icon}</span>}
        {children}
        {iconRight && <span style={{ display: 'flex', alignItems: 'center' }}>{iconRight}</span>}
      </span>
    </button>
  );
}
