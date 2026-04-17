import React, { useState, useCallback } from 'react';

interface ManualOverrideProps {
  onJog: (pan: number, tilt: number) => void;
}

const ManualOverride: React.FC<ManualOverrideProps> = ({ onJog }) => {
  const [isActive, setIsActive] = useState(false);

  const handleDirection = useCallback((pan: number, tilt: number) => {
    onJog(pan, tilt);
  }, [onJog]);

  return (
    <div style={styles.container} data-testid="manual-override">
      <div style={styles.header}>
        <span>MANUAL OVERRIDE</span>
        <button
          onClick={() => setIsActive(!isActive)}
          style={{
            ...styles.toggleBtn,
            backgroundColor: isActive ? '#1a4a1a' : '#4a1a1a',
            borderColor: isActive ? '#00ff88' : '#ff4444',
          }}
          data-testid="override-toggle"
        >
          {isActive ? 'ENABLED' : 'DISABLED'}
        </button>
      </div>
      <div style={{ ...styles.joystickArea, opacity: isActive ? 1 : 0.3 }}>
        <div style={styles.joystickGrid}>
          <div />
          <button
            style={styles.jogBtn}
            disabled={!isActive}
            onMouseDown={() => handleDirection(0, 1)}
            onMouseUp={() => handleDirection(0, 0)}
            data-testid="jog-up"
          >
            &#9650;
          </button>
          <div />
          <button
            style={styles.jogBtn}
            disabled={!isActive}
            onMouseDown={() => handleDirection(-1, 0)}
            onMouseUp={() => handleDirection(0, 0)}
            data-testid="jog-left"
          >
            &#9664;
          </button>
          <div style={styles.centerDot}>&#9679;</div>
          <button
            style={styles.jogBtn}
            disabled={!isActive}
            onMouseDown={() => handleDirection(1, 0)}
            onMouseUp={() => handleDirection(0, 0)}
            data-testid="jog-right"
          >
            &#9654;
          </button>
          <div />
          <button
            style={styles.jogBtn}
            disabled={!isActive}
            onMouseDown={() => handleDirection(0, -1)}
            onMouseUp={() => handleDirection(0, 0)}
            data-testid="jog-down"
          >
            &#9660;
          </button>
          <div />
        </div>
      </div>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  container: {
    border: '1px solid #1a1a4a',
    borderRadius: '4px',
    padding: '12px',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '12px',
    color: '#7090ff',
    fontSize: '10px',
    letterSpacing: '2px',
  },
  toggleBtn: {
    padding: '4px 12px',
    border: '1px solid',
    borderRadius: '4px',
    color: '#e0e0ff',
    fontFamily: "'Courier New', monospace",
    fontSize: '10px',
    cursor: 'pointer',
    letterSpacing: '1px',
  },
  joystickArea: {
    display: 'flex',
    justifyContent: 'center',
    transition: 'opacity 0.3s',
  },
  joystickGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 48px)',
    gridTemplateRows: 'repeat(3, 48px)',
    gap: '4px',
    placeItems: 'center',
  },
  jogBtn: {
    width: '44px',
    height: '44px',
    backgroundColor: '#0d0d35',
    border: '1px solid #1a1a4a',
    borderRadius: '4px',
    color: '#7090ff',
    fontSize: '16px',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  centerDot: {
    color: '#7090ff',
    fontSize: '12px',
  },
};

export default ManualOverride;
