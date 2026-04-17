import React, { useState, useCallback } from 'react';
import ViewfinderHUD from './components/ViewfinderHUD';
import TargetSelector from './components/TargetSelector';
import ErrorGraphs from './components/ErrorGraphs';
import ManualOverride from './components/ManualOverride';

export interface TrackingState {
  targetName: string;
  ra: string;
  dec: string;
  trackingErrorArcsec: number;
  isTracking: boolean;
  panSpeed: number;
  tiltSpeed: number;
}

const initialState: TrackingState = {
  targetName: 'ISS (ZARYA)',
  ra: '14h 15m 39.7s',
  dec: "+19° 10' 56.7\"",
  trackingErrorArcsec: 0,
  isTracking: false,
  panSpeed: 0,
  tiltSpeed: 0,
};

const App: React.FC = () => {
  const [state, setState] = useState<TrackingState>(initialState);
  const [errorHistory, setErrorHistory] = useState<number[]>([]);

  const handleTargetSelect = useCallback((name: string) => {
    setState(prev => ({ ...prev, targetName: name, isTracking: true }));
  }, []);

  const handleJog = useCallback((pan: number, tilt: number) => {
    setState(prev => ({ ...prev, panSpeed: pan, tiltSpeed: tilt }));
  }, []);

  // Simulate tracking updates
  React.useEffect(() => {
    if (!state.isTracking) return;
    const interval = setInterval(() => {
      const newError = Math.random() * 5;
      setState(prev => ({ ...prev, trackingErrorArcsec: newError }));
      setErrorHistory(prev => [...prev.slice(-99), newError]);
    }, 1000);
    return () => clearInterval(interval);
  }, [state.isTracking]);

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <h1 style={styles.title}>Optical Tracking Mount</h1>
        <div style={styles.statusBar}>
          <span style={styles.statusItem}>
            Target: <strong>{state.targetName}</strong>
          </span>
          <span style={styles.statusItem}>
            RA: {state.ra} | Dec: {state.dec}
          </span>
          <span style={{
            ...styles.statusItem,
            color: state.isTracking ? '#00ff88' : '#ff4444'
          }}>
            {state.isTracking ? '● TRACKING' : '○ IDLE'}
          </span>
        </div>
      </header>

      <main style={styles.main}>
        <div style={styles.leftPanel}>
          <ViewfinderHUD
            isTracking={state.isTracking}
            trackingError={state.trackingErrorArcsec}
          />
          <ManualOverride onJog={handleJog} />
        </div>
        <div style={styles.rightPanel}>
          <TargetSelector onSelect={handleTargetSelect} />
          <ErrorGraphs errorHistory={errorHistory} currentError={state.trackingErrorArcsec} />
        </div>
      </main>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  container: {
    minHeight: '100vh',
    backgroundColor: '#0a0a2a',
    color: '#e0e0ff',
    fontFamily: "'Courier New', monospace",
  },
  header: {
    padding: '16px 24px',
    borderBottom: '1px solid #1a1a4a',
    background: 'linear-gradient(180deg, #0d0d35 0%, #0a0a2a 100%)',
  },
  title: {
    margin: 0,
    fontSize: '20px',
    color: '#7090ff',
    letterSpacing: '2px',
  },
  statusBar: {
    display: 'flex',
    gap: '24px',
    marginTop: '8px',
    fontSize: '13px',
  },
  statusItem: { opacity: 0.9 },
  main: {
    display: 'flex',
    padding: '16px',
    gap: '16px',
    height: 'calc(100vh - 100px)',
  },
  leftPanel: {
    flex: 2,
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },
  rightPanel: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },
};

export default App;
