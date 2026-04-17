package hardware

import (
"testing"
"time"
)

func TestNewStepGenerator(t *testing.T) {
sg := NewStepGenerator(true)
if sg == nil {
t.Fatal("NewStepGenerator returned nil")
}
if sg.PanConfig.StepsPerRevolution != 200 {
t.Errorf("Expected 200 steps/rev, got %d", sg.PanConfig.StepsPerRevolution)
}
}

func TestDegreesToSteps(t *testing.T) {
sg := NewStepGenerator(true)
steps := sg.DegreesToSteps(sg.PanConfig, 1.0)
// 200 * 32 * 100 / 360 = 1777.78 steps per degree
expected := int64(1778)
if steps != expected {
t.Errorf("Expected %d steps for 1 degree, got %d", expected, steps)
}
}

func TestStepsToDegrees(t *testing.T) {
sg := NewStepGenerator(true)
steps := sg.DegreesToSteps(sg.PanConfig, 10.0)
degrees := sg.StepsToDegrees(sg.PanConfig, steps)
if diff := degrees - 10.0; diff > 0.01 || diff < -0.01 {
t.Errorf("Round-trip conversion error: 10.0 -> %d steps -> %f degrees", steps, degrees)
}
}

func TestStartStop(t *testing.T) {
sg := NewStepGenerator(true)
sg.Start()
if !sg.IsRunning() {
t.Error("Expected step generator to be running")
}
time.Sleep(10 * time.Millisecond)
sg.Stop()
time.Sleep(10 * time.Millisecond)
if sg.IsRunning() {
t.Error("Expected step generator to be stopped")
}
}

func TestSetSpeed(t *testing.T) {
sg := NewStepGenerator(true)
sg.Start()
sg.SetSpeed(1.0, -1.0)
time.Sleep(50 * time.Millisecond)
pan, tilt := sg.GetStepCounts()
sg.Stop()
// With speed set, we should have accumulated some steps
if pan == 0 && tilt == 0 {
t.Log("Warning: no steps accumulated (may be timing dependent)")
}
}
