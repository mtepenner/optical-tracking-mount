import React from 'react';

interface ErrorGraphsProps {
  errorHistory: number[];
  currentError: number;
}

const ErrorGraphs: React.FC<ErrorGraphsProps> = ({ errorHistory, currentError }) => {
  const maxError = Math.max(10, ...errorHistory);
  const graphHeight = 120;
  const graphWidth = 280;

  const points = errorHistory.map((err, i) => {
    const x = (i / Math.max(1, errorHistory.length - 1)) * graphWidth;
    const y = graphHeight - (err / maxError) * graphHeight;
    return `${x},${y}`;
  }).join(' ');

  const errorColor = currentError < 2 ? '#00ff88' : currentError < 5 ? '#ffaa00' : '#ff4444';

  return (
    <div style={styles.container} data-testid="error-graphs">
      <div style={styles.header}>TRACKING ERROR</div>
      <div style={styles.currentError}>
        <span style={{ color: errorColor, fontSize: '24px', fontWeight: 'bold' }}>
          {currentError.toFixed(2)}
        </span>
        <span style={{ fontSize: '12px', marginLeft: '4px' }}>arcsec</span>
      </div>
      <div style={styles.graphContainer}>
        <svg width={graphWidth} height={graphHeight} style={styles.graph}>
          {/* Grid lines */}
          {[0.25, 0.5, 0.75].map(frac => (
            <line
              key={frac}
              x1={0} y1={graphHeight * frac}
              x2={graphWidth} y2={graphHeight * frac}
              stroke="#1a1a4a" strokeWidth="1" strokeDasharray="4,4"
            />
          ))}
          {/* Error trace */}
          {errorHistory.length > 1 && (
            <polyline
              points={points}
              fill="none"
              stroke={errorColor}
              strokeWidth="1.5"
            />
          )}
        </svg>
        <div style={styles.yAxis}>
          <span>{maxError.toFixed(0)}&quot;</span>
          <span>{(maxError / 2).toFixed(0)}&quot;</span>
          <span>0&quot;</span>
        </div>
      </div>
      <div style={styles.stats}>
        <div>
          Avg: {errorHistory.length > 0
            ? (errorHistory.reduce((a, b) => a + b, 0) / errorHistory.length).toFixed(2)
            : '0.00'}&quot;
        </div>
        <div>
          Peak: {errorHistory.length > 0
            ? Math.max(...errorHistory).toFixed(2)
            : '0.00'}&quot;
        </div>
        <div>Samples: {errorHistory.length}</div>
      </div>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  container: {
    border: '1px solid #1a1a4a',
    borderRadius: '4px',
    padding: '12px',
    flex: 1,
  },
  header: {
    color: '#7090ff',
    fontSize: '10px',
    letterSpacing: '2px',
    marginBottom: '8px',
  },
  currentError: {
    marginBottom: '12px',
  },
  graphContainer: {
    display: 'flex',
    gap: '4px',
  },
  graph: {
    backgroundColor: '#050515',
    borderRadius: '4px',
  },
  yAxis: {
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'space-between',
    fontSize: '9px',
    opacity: 0.5,
  },
  stats: {
    marginTop: '8px',
    fontSize: '11px',
    display: 'flex',
    justifyContent: 'space-between',
    opacity: 0.7,
  },
};

export default ErrorGraphs;
