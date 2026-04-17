import React, { useState } from 'react';

interface TargetSelectorProps {
  onSelect: (name: string) => void;
}

const TARGETS = [
  { name: 'ISS (ZARYA)', type: 'Satellite', ra: '14h 15m', dec: "+19° 10'" },
  { name: 'Hubble Space Telescope', type: 'Satellite', ra: '18h 36m', dec: "+38° 47'" },
  { name: 'Jupiter', type: 'Planet', ra: '02h 15m', dec: "+12° 30'" },
  { name: 'Saturn', type: 'Planet', ra: '22h 40m', dec: "-10° 15'" },
  { name: 'Mars', type: 'Planet', ra: '06h 20m', dec: "+24° 05'" },
  { name: 'M31 Andromeda', type: 'Deep Sky', ra: '00h 42m', dec: "+41° 16'" },
  { name: 'M42 Orion Nebula', type: 'Deep Sky', ra: '05h 35m', dec: "-05° 23'" },
  { name: 'M45 Pleiades', type: 'Deep Sky', ra: '03h 47m', dec: "+24° 07'" },
];

const TargetSelector: React.FC<TargetSelectorProps> = ({ onSelect }) => {
  const [query, setQuery] = useState('');
  const [selectedTarget, setSelectedTarget] = useState<string | null>(null);

  const filtered = TARGETS.filter(t =>
    t.name.toLowerCase().includes(query.toLowerCase()) ||
    t.type.toLowerCase().includes(query.toLowerCase())
  );

  const handleSelect = (name: string) => {
    setSelectedTarget(name);
    onSelect(name);
  };

  return (
    <div style={styles.container} data-testid="target-selector">
      <div style={styles.header}>TARGET SELECTOR</div>
      <input
        type="text"
        placeholder="Search satellites, planets, DSOs..."
        value={query}
        onChange={e => setQuery(e.target.value)}
        style={styles.searchInput}
        data-testid="target-search"
      />
      <div style={styles.list}>
        {filtered.map(target => (
          <div
            key={target.name}
            onClick={() => handleSelect(target.name)}
            style={{
              ...styles.targetItem,
              backgroundColor: selectedTarget === target.name ? '#1a2a5a' : 'transparent',
              borderColor: selectedTarget === target.name ? '#4060cc' : '#1a1a4a',
            }}
            data-testid={`target-${target.name}`}
          >
            <div style={styles.targetName}>{target.name}</div>
            <div style={styles.targetMeta}>
              <span style={styles.targetType}>{target.type}</span>
              <span>RA {target.ra} | Dec {target.dec}</span>
            </div>
          </div>
        ))}
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
    color: '#7090ff',
    fontSize: '10px',
    letterSpacing: '2px',
    marginBottom: '8px',
  },
  searchInput: {
    width: '100%',
    padding: '8px 12px',
    backgroundColor: '#0d0d35',
    border: '1px solid #1a1a4a',
    borderRadius: '4px',
    color: '#e0e0ff',
    fontFamily: "'Courier New', monospace",
    fontSize: '13px',
    outline: 'none',
    boxSizing: 'border-box',
  },
  list: {
    marginTop: '8px',
    maxHeight: '200px',
    overflowY: 'auto',
  },
  targetItem: {
    padding: '8px',
    border: '1px solid #1a1a4a',
    borderRadius: '4px',
    marginBottom: '4px',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
  },
  targetName: {
    fontSize: '13px',
    fontWeight: 'bold',
  },
  targetMeta: {
    fontSize: '11px',
    opacity: 0.7,
    marginTop: '2px',
    display: 'flex',
    justifyContent: 'space-between',
  },
  targetType: {
    color: '#7090ff',
  },
};

export default TargetSelector;
