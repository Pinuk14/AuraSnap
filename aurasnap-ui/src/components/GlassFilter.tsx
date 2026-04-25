/**
 * GlassFilter.tsx
 * Shared SVG filter definitions used across all Liquid Glass components.
 * Render this ONCE at the root of the app.
 * Ported from Modular-UIcomponents/components/LiquidButton.jsx & LiquidNavbar.jsx
 */
export default function GlassFilter() {
  return (
    <svg style={{ position: 'absolute', width: 0, height: 0, overflow: 'hidden' }}>
      <defs>
        {/* Heavy distortion — buttons, toggles, cards */}
        <filter id="glass-distortion" x="0%" y="0%" width="100%" height="100%" filterUnits="objectBoundingBox">
          <feTurbulence type="fractalNoise" baseFrequency="0.01 0.01" numOctaves={1} seed={5} result="turbulence" />
          <feComponentTransfer in="turbulence" result="mapped">
            <feFuncR type="gamma" amplitude={1} exponent={10} offset={0.5} />
            <feFuncG type="gamma" amplitude={0} exponent={1} offset={0} />
            <feFuncB type="gamma" amplitude={0} exponent={1} offset={0.5} />
          </feComponentTransfer>
          <feGaussianBlur in="turbulence" stdDeviation={3} result="softMap" />
          <feSpecularLighting in="softMap" surfaceScale={5} specularConstant={1} specularExponent={100} lightingColor="white" result="specLight">
            <fePointLight x={-200} y={-200} z={300} />
          </feSpecularLighting>
          <feComposite in="specLight" operator="arithmetic" k1={0} k2={1} k3={1} k4={0} result="litImage" />
          <feDisplacementMap in="SourceGraphic" in2="softMap" scale={150} xChannelSelector="R" yChannelSelector="G" />
        </filter>

        {/* Lighter distortion — inputs */}
        <filter id="glass-distortion-input" x="0%" y="0%" width="100%" height="100%" filterUnits="objectBoundingBox">
          <feTurbulence type="fractalNoise" baseFrequency="0.015 0.015" numOctaves={1} seed={5} result="turbulence" />
          <feComponentTransfer in="turbulence" result="mapped">
            <feFuncR type="gamma" amplitude={1} exponent={10} offset={0.5} />
            <feFuncG type="gamma" amplitude={0} exponent={1} offset={0} />
            <feFuncB type="gamma" amplitude={0} exponent={1} offset={0.5} />
          </feComponentTransfer>
          <feGaussianBlur in="turbulence" stdDeviation={3} result="softMap" />
          <feSpecularLighting in="softMap" surfaceScale={3} specularConstant={1} specularExponent={100} lightingColor="white" result="specLight">
            <fePointLight x={-200} y={-200} z={300} />
          </feSpecularLighting>
          <feComposite in="specLight" operator="arithmetic" k1={0} k2={1} k3={1} k4={0} result="litImage" />
          <feDisplacementMap in="SourceGraphic" in2="softMap" scale={30} xChannelSelector="R" yChannelSelector="G" />
        </filter>

        {/* Navbar bubble distortion */}
        <filter id="liquid-glass-distortion" x="-20%" y="-20%" width="140%" height="140%" colorInterpolationFilters="sRGB">
          <feTurbulence type="fractalNoise" baseFrequency="0.01 0.01" numOctaves={1} seed={4} result="noise" />
          <feGaussianBlur in="noise" stdDeviation={3} result="blur" />
          <feDisplacementMap in="SourceGraphic" in2="blur" scale={70} xChannelSelector="R" yChannelSelector="G" />
        </filter>
      </defs>
    </svg>
  );
}
