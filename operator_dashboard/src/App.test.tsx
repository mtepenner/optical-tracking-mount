import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from './App.tsx';
import ViewfinderHUD from './components/ViewfinderHUD.tsx';
import TargetSelector from './components/TargetSelector.tsx';
import ErrorGraphs from './components/ErrorGraphs.tsx';
import ManualOverride from './components/ManualOverride.tsx';

describe('App', () => {
  test('renders the main title', () => {
    render(<App />);
    expect(screen.getByText('Optical Tracking Mount')).toBeInTheDocument();
  });

  test('shows IDLE status initially', () => {
    render(<App />);
    expect(screen.getByText(/IDLE/)).toBeInTheDocument();
  });

  test('shows default target name', () => {
    render(<App />);
    const elements = screen.getAllByText('ISS (ZARYA)');
    expect(elements.length).toBeGreaterThanOrEqual(1);
  });
});

describe('ViewfinderHUD', () => {
  test('renders viewfinder', () => {
    render(<ViewfinderHUD isTracking={false} trackingError={0} />);
    expect(screen.getByTestId('viewfinder-hud')).toBeInTheDocument();
  });

  test('displays VIEWFINDER label', () => {
    render(<ViewfinderHUD isTracking={true} trackingError={2.5} />);
    expect(screen.getByText('VIEWFINDER')).toBeInTheDocument();
  });

  test('displays tracking error', () => {
    render(<ViewfinderHUD isTracking={true} trackingError={3.7} />);
    expect(screen.getByText(/3\.7/)).toBeInTheDocument();
  });
});

describe('TargetSelector', () => {
  test('renders target list', () => {
    const onSelect = jest.fn();
    render(<TargetSelector onSelect={onSelect} />);
    expect(screen.getByTestId('target-selector')).toBeInTheDocument();
    expect(screen.getByText('ISS (ZARYA)')).toBeInTheDocument();
  });

  test('filters targets by search query', () => {
    const onSelect = jest.fn();
    render(<TargetSelector onSelect={onSelect} />);
    const input = screen.getByTestId('target-search');
    fireEvent.change(input, { target: { value: 'Jupiter' } });
    expect(screen.getByText('Jupiter')).toBeInTheDocument();
    expect(screen.queryByText('Saturn')).not.toBeInTheDocument();
  });

  test('calls onSelect when target is clicked', () => {
    const onSelect = jest.fn();
    render(<TargetSelector onSelect={onSelect} />);
    fireEvent.click(screen.getByText('Jupiter'));
    expect(onSelect).toHaveBeenCalledWith('Jupiter');
  });
});

describe('ErrorGraphs', () => {
  test('renders with no history', () => {
    render(<ErrorGraphs errorHistory={[]} currentError={0} />);
    expect(screen.getByTestId('error-graphs')).toBeInTheDocument();
    expect(screen.getByText('TRACKING ERROR')).toBeInTheDocument();
  });

  test('displays current error value', () => {
    render(<ErrorGraphs errorHistory={[1, 2, 3]} currentError={2.5} />);
    expect(screen.getByText('2.50')).toBeInTheDocument();
  });

  test('shows statistics', () => {
    render(<ErrorGraphs errorHistory={[1, 2, 3]} currentError={2} />);
    expect(screen.getByText(/Samples: 3/)).toBeInTheDocument();
  });
});

describe('ManualOverride', () => {
  test('renders in disabled state', () => {
    const onJog = jest.fn();
    render(<ManualOverride onJog={onJog} />);
    expect(screen.getByText('DISABLED')).toBeInTheDocument();
  });

  test('toggles to enabled state', () => {
    const onJog = jest.fn();
    render(<ManualOverride onJog={onJog} />);
    fireEvent.click(screen.getByTestId('override-toggle'));
    expect(screen.getByText('ENABLED')).toBeInTheDocument();
  });

  test('jog buttons are disabled when not active', () => {
    const onJog = jest.fn();
    render(<ManualOverride onJog={onJog} />);
    const upBtn = screen.getByTestId('jog-up');
    expect(upBtn).toBeDisabled();
  });
});
