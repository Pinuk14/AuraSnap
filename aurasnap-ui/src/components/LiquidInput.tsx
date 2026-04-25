/**
 * LiquidInput.tsx
 * TypeScript port of Modular-UIcomponents/components/LiquidInput.jsx
 * Uses lighter glass-distortion-input SVG filter.
 */
import { useState, useRef } from 'react';
import type { ReactNode, CSSProperties, InputHTMLAttributes } from 'react';

const EyeIcon = ({ open }: { open: boolean }) => (
  <svg width={16} height={16} viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,0.7)" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
    {open ? (
      <><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" /><circle cx={12} cy={12} r={3} /></>
    ) : (
      <><path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19M1 1l22 22" /></>
    )}
  </svg>
);

const sizeTokens = {
  sm:  { fontSize: '0.85rem', padV: '0.5rem',  padH: '0.9rem', radius: '1rem',  labelSize: '0.75rem', iconPad: '0.75rem', gapAfterIcon: '0.4rem' },
  md:  { fontSize: '0.95rem', padV: '0.75rem', padH: '1.1rem', radius: '1.4rem', labelSize: '0.8rem',  iconPad: '1rem',    gapAfterIcon: '0.5rem' },
  lg:  { fontSize: '1.05rem', padV: '1rem',    padH: '1.3rem', radius: '1.8rem', labelSize: '0.85rem', iconPad: '1.1rem',  gapAfterIcon: '0.6rem' },
};

interface LiquidInputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'size'> {
  label?: string;
  size?: 'sm' | 'md' | 'lg';
  error?: string;
  hint?: string;
  iconLeft?: ReactNode;
  iconRight?: ReactNode;
  onIconRightClick?: () => void;
  fullWidth?: boolean;
  wrapperStyle?: CSSProperties;
}

export default function LiquidInput({
  label,
  size = 'md',
  error,
  hint,
  iconLeft,
  iconRight,
  onIconRightClick,
  fullWidth = true,
  wrapperStyle = {},
  type = 'text',
  disabled = false,
  ...rest
}: LiquidInputProps) {
  const [focused, setFocused] = useState(false);
  const [hovered, setHovered] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const isPassword = type === 'password';
  const inputType = isPassword ? (showPassword ? 'text' : 'password') : type;
  const sz = sizeTokens[size];
  const hasError = Boolean(error);

  const resolvedIconRight = isPassword ? (
    <div onClick={() => setShowPassword(v => !v)} style={{ cursor: 'pointer', display: 'flex' }}>
      <EyeIcon open={showPassword} />
    </div>
  ) : iconRight;

  return (
    <>
      <style>{`.lg-input-real::placeholder { color: rgba(255,255,255,0.45); } .lg-input-real { caret-color: rgba(255,255,255,0.9); }`}</style>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', width: fullWidth ? '100%' : 'auto', ...wrapperStyle }}>
        {label && (
          <label style={{
            color: hasError ? 'rgba(255,160,160,0.9)' : 'rgba(255,255,255,0.65)',
            fontSize: sz.labelSize,
            fontFamily: 'var(--font-elegant)',
            letterSpacing: '0.08em',
            textTransform: 'uppercase',
            paddingLeft: '4px',
          }}>{label}</label>
        )}

        <div
          onClick={() => inputRef.current?.focus()}
          onMouseEnter={() => !disabled && setHovered(true)}
          onMouseLeave={() => setHovered(false)}
          style={{
            position: 'relative', display: 'flex', alignItems: 'center',
            borderRadius: sz.radius, overflow: 'hidden',
            boxShadow: hasError
              ? '0 4px 16px rgba(255,100,100,0.25), 0 0 0 1.5px rgba(255,120,120,0.5)'
              : focused
                ? '0 8px 28px rgba(0,0,0,0.3), 0 0 0 2px rgba(255,255,255,0.45)'
                : hovered
                  ? '0 8px 24px rgba(0,0,0,0.2), 0 0 0 1.5px rgba(255,255,255,0.3)'
                  : '0 4px 12px rgba(0,0,0,0.2)',
            transform: focused ? 'scale(1.02)' : hovered ? 'scale(1.01)' : 'scale(1)',
            transition: 'transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 2.2), box-shadow 0.4s ease',
            cursor: disabled ? 'not-allowed' : 'text',
            opacity: disabled ? 0.45 : 1,
          }}
        >
          {/* Glass blur distortion layer */}
          <div style={{
            position: 'absolute', inset: 0, zIndex: 0,
            backdropFilter: focused ? 'blur(5px)' : 'blur(3px)',
            WebkitBackdropFilter: focused ? 'blur(5px)' : 'blur(3px)',
            filter: 'url(#glass-distortion-input)',
            isolation: 'isolate', borderRadius: 'inherit',
          }} />
          {/* Tint */}
          <div style={{
            position: 'absolute', inset: 0, zIndex: 1,
            background: focused ? 'rgba(255,255,255,0.28)' : hovered ? 'rgba(255,255,255,0.22)' : 'rgba(255,255,255,0.15)',
            transition: 'background 0.3s ease', borderRadius: 'inherit',
          }} />
          {/* Edge shine */}
          <div style={{
            position: 'absolute', inset: 0, zIndex: 2, borderRadius: 'inherit',
            boxShadow: focused || hovered
              ? 'inset 2px 2px 2px 0 rgba(255,255,255,0.6), inset -1px -1px 2px 1px rgba(255,255,255,0.4)'
              : 'inset 2px 2px 1px 0 rgba(255,255,255,0.4), inset -1px -1px 1px 1px rgba(255,255,255,0.2)',
            transition: 'box-shadow 0.3s ease',
          }} />

          {/* Left icon */}
          {iconLeft && (
            <div style={{ position: 'relative', zIndex: 3, paddingLeft: sz.iconPad, display: 'flex', alignItems: 'center', flexShrink: 0 }}>
              {iconLeft}
            </div>
          )}

          {/* Input */}
          <input
            ref={inputRef}
            type={inputType}
            onFocus={() => setFocused(true)}
            onBlur={() => setFocused(false)}
            disabled={disabled}
            className="lg-input-real"
            style={{
              position: 'relative', zIndex: 3, flex: 1,
              background: 'transparent', border: 'none', outline: 'none',
              color: 'rgba(255,255,255,0.95)',
              textShadow: '0 1px 3px rgba(0,0,0,0.3)',
              fontFamily: 'var(--font-ui)', fontWeight: 500,
              fontSize: sz.fontSize,
              padding: iconLeft
                ? `${sz.padV} ${resolvedIconRight ? sz.iconPad : sz.padH} ${sz.padV} ${sz.gapAfterIcon}`
                : `${sz.padV} ${resolvedIconRight ? sz.iconPad : sz.padH} ${sz.padV} ${sz.padH}`,
              width: '100%',
            }}
            {...rest}
          />

          {/* Right icon */}
          {resolvedIconRight && (
            <div onClick={onIconRightClick} style={{ position: 'relative', zIndex: 3, paddingRight: sz.iconPad, display: 'flex', alignItems: 'center', flexShrink: 0, cursor: onIconRightClick || isPassword ? 'pointer' : 'default' }}>
              {resolvedIconRight}
            </div>
          )}
        </div>

        {(error || hint) && (
          <span style={{ color: hasError ? 'rgba(255,160,160,0.9)' : 'rgba(255,255,255,0.4)', fontSize: '0.75rem', fontFamily: 'var(--font-ui)', paddingLeft: '4px' }}>
            {error || hint}
          </span>
        )}
      </div>
    </>
  );
}
