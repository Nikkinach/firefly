import React from 'react';

interface Props {
  size?: number;
  showText?: boolean;
}

export const FireflyLogo: React.FC<Props> = ({
  size = 40,
  showText = true
}) => {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
      <img
        src="/assets/firefly-logo.png"
        alt="Firefly"
        style={{
          width: size,
          height: size,
          objectFit: 'contain',
          filter: 'drop-shadow(0 0 8px rgba(252, 211, 77, 0.5))',
        }}
      />
      {showText && (
        <span
          style={{
            fontSize: size * 0.55,
            fontWeight: 600,
            color: '#FFFFFF',
            letterSpacing: '0.5px',
          }}
        >
          Firefly
        </span>
      )}
    </div>
  );
};
