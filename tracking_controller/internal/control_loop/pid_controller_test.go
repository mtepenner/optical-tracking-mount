package controlloop

import (
"math"
"testing"
"time"
)

func TestNewPIDController(t *testing.T) {
pid := NewPIDController()
if pid == nil {
t.Fatal("NewPIDController returned nil")
}
if pid.PanGains.Kp != 2.0 {
t.Errorf("Expected Kp=2.0, got %f", pid.PanGains.Kp)
}
}

func TestPIDZeroError(t *testing.T) {
pid := NewPIDController()
now := time.Now()
cmd := pid.Update(0, 0, now)
if cmd.PanSpeed != 0 || cmd.TiltSpeed != 0 {
t.Errorf("Expected zero output for zero error, got pan=%f tilt=%f", cmd.PanSpeed, cmd.TiltSpeed)
}
}

func TestPIDDeadZone(t *testing.T) {
pid := NewPIDController()
pid.DeadZone = 5.0
now := time.Now()
// Error within dead zone
cmd := pid.Update(3.0, 3.0, now)
if cmd.PanSpeed != 0 || cmd.TiltSpeed != 0 {
t.Errorf("Expected zero output within dead zone, got pan=%f tilt=%f", cmd.PanSpeed, cmd.TiltSpeed)
}
}

func TestPIDPositiveError(t *testing.T) {
pid := NewPIDController()
now := time.Now()
// Large positive error should produce positive output
cmd := pid.Update(100.0, 100.0, now)
if cmd.PanSpeed <= 0 {
t.Errorf("Expected positive pan speed for positive error, got %f", cmd.PanSpeed)
}
if cmd.TiltSpeed <= 0 {
t.Errorf("Expected positive tilt speed for positive error, got %f", cmd.TiltSpeed)
}
}

func TestPIDOutputClamped(t *testing.T) {
pid := NewPIDController()
pid.MaxOutput = 3.0
now := time.Now()
// Very large error
cmd := pid.Update(1e6, 1e6, now)
if math.Abs(cmd.PanSpeed) > 3.0+1e-10 {
t.Errorf("Pan speed exceeds max: %f", cmd.PanSpeed)
}
if math.Abs(cmd.TiltSpeed) > 3.0+1e-10 {
t.Errorf("Tilt speed exceeds max: %f", cmd.TiltSpeed)
}
}

func TestPIDReset(t *testing.T) {
pid := NewPIDController()
now := time.Now()
pid.Update(100, 100, now)
pid.Reset()
// After reset, state should be cleared
cmd := pid.Update(0, 0, now.Add(time.Second))
if cmd.PanSpeed != 0 || cmd.TiltSpeed != 0 {
t.Errorf("After reset and zero error, expected zero output")
}
}
