import React from 'react';

interface ViewfinderHUDProps {
  isTracking: boolean;
  trackingError: number;
}

const ViewfinderHUD: React.FC<ViewfinderHUDProps> = ({ isTracking, trackingError }) => {
  const crosshairColor = isTracking ? '#00ff88' : '#ff4444';
  const errorColor = trackingError < 2 ? '#00ff88' : trackingError < 5 ? '#ffaa00' : '#ff4444';

  return (
    <div style={styles.container} data-testid="viewfinder-hud">
      <div style={styles.viewport}>
        {/* Simulated star field background */}
        <div style={styles.starField}>
          {Array.from({ length: 20 }, (_, i) => (
            <div
              key={i}
              style={{
                ...styles.star,
                left: `${(i * 37 + 13) % 100}%`,
                top: `${(i * 53 + 7) % 100}%`,
                width: `${1 + (i % 3)}px`,
                height: `${1 + (i % 3)}px`,
                opacity: 0.3 + (i % 5) * 0.15,
              }}
            />
          ))}
        </div>

        {/* Digital crosshair */}
        <svg style={styles.crosshair} viewBox="0 0 200 200">
          {/* Outer circle */}
          <circle cx="100" cy="100" r="60" fill="none" stroke={crosshairColor} strokeWidth="1" opacity="0.5" />
          {/* Inner circle */}
          <circle cx="100" cy="100" r="20" fill="none" stroke={crosshairColor} strokeWidth="1" opacity="0.7" />
          {/* Crosshair lines */}
          <line x1="100" y1="30" x2="100" y2="80" stroke={crosshairColor} strokeWidth="1" />
          <line x1="100" y1="120" x2="100" y2="170" stroke={crosshairColor} strokeWidth="1" />
          <line x1="30" y1="100" x2="80" y2="100" stroke={crosshairColor} strokeWidth="1" />
          <line x1="120" y1="100" x2="170" y2="100" stroke={crosshairColor} strokeWidth="1" />
          {/* Center dot */}
          <circle cx="100" cy="100" r="2" fill={crosshairColor} />
        </svg>

        {/* HUD overlay info */}
        <div style={styles.hudInfo}>
          <div style={styles.hudLabel}>VIEWFINDER</div>
          <div style={{ color: errorColor }}>
            Error: {trackingError.toFixed(1)}&quot;
          </div>
        </div>
      </div>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  container: {
    flex: 1,
    border: '1px solid #1a1a4a',
    borderRadius: '4px',
    overflow: 'hidden',
    position: 'relative',
  },
  viewport: {
    width: '100%',
    height: '100%',
    minHeight: '300px',
    backgroundColor: '#050515',
    position: 'relative',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  starField: {
    position: 'absolute',
    inset: 0,
  },
  star: {
    position: 'absolute',
    backgroundColor: '#ffffff',
    borderRadius: '50%',
  },
  crosshair: {
    width: '60%',
    height: '60%',
    zIndex: 1,
  },
  hudInfo: {
    position: 'absolute',
    bottom: '8px',
    left: '8px',
    fontSize: '11px',
  },
  hudLabel: {
    color: '#7090ff',
    fontSize: '10px',
    letterSpacing: '2px',
    marginBottom: '4px',
  },
};

export default ViewfinderHUD;
