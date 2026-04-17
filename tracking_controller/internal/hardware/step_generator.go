// Package hardware provides stepper motor pulse generation.
package hardware

import (
"log"
"math"
"sync"
"time"
)

// StepperConfig holds configuration for a stepper motor axis.
type StepperConfig struct {
StepsPerRevolution int     // Full steps per revolution (e.g., 200 for 1.8° motor)
MicrostepDivision  int     // Microstepping divisor (e.g., 16, 32, 64)
GearRatio          float64 // Gear reduction ratio
MaxStepsPerSec     int     // Maximum stepping frequency
StepPin            int     // GPIO pin for step signal
DirPin             int     // GPIO pin for direction signal
}

// StepGenerator sends high-frequency step/dir pulses to stepper motor drivers.
type StepGenerator struct {
PanConfig  StepperConfig
TiltConfig StepperConfig
mu         sync.Mutex
panRate    float64 // current pan step rate (steps/sec)
tiltRate   float64 // current tilt step rate (steps/sec)
running    bool
simulate   bool
panSteps   int64 // total pan steps taken (for simulation tracking)
tiltSteps  int64 // total tilt steps taken
}

// NewStepGenerator creates a new step generator.
func NewStepGenerator(simulate bool) *StepGenerator {
return &StepGenerator{
PanConfig: StepperConfig{
StepsPerRevolution: 200,
MicrostepDivision:  32,
GearRatio:          100.0,
MaxStepsPerSec:     50000,
StepPin:            17,
DirPin:             27,
},
TiltConfig: StepperConfig{
StepsPerRevolution: 200,
MicrostepDivision:  32,
GearRatio:          100.0,
MaxStepsPerSec:     50000,
StepPin:            22,
DirPin:             23,
},
simulate: simulate,
}
}

// DegreesToSteps converts a rotation in degrees to motor steps.
func (sg *StepGenerator) DegreesToSteps(config StepperConfig, degrees float64) int64 {
stepsPerDeg := float64(config.StepsPerRevolution*config.MicrostepDivision) * config.GearRatio / 360.0
return int64(math.Round(degrees * stepsPerDeg))
}

// StepsToDegrees converts motor steps to degrees of rotation.
func (sg *StepGenerator) StepsToDegrees(config StepperConfig, steps int64) float64 {
stepsPerDeg := float64(config.StepsPerRevolution*config.MicrostepDivision) * config.GearRatio / 360.0
return float64(steps) / stepsPerDeg
}

// SetSpeed sets the motor speeds in degrees per second for both axes.
func (sg *StepGenerator) SetSpeed(panDegPerSec, tiltDegPerSec float64) {
sg.mu.Lock()
defer sg.mu.Unlock()

panStepsPerDeg := float64(sg.PanConfig.StepsPerRevolution*sg.PanConfig.MicrostepDivision) * sg.PanConfig.GearRatio / 360.0
tiltStepsPerDeg := float64(sg.TiltConfig.StepsPerRevolution*sg.TiltConfig.MicrostepDivision) * sg.TiltConfig.GearRatio / 360.0

sg.panRate = clampFloat(panDegPerSec*panStepsPerDeg, float64(-sg.PanConfig.MaxStepsPerSec), float64(sg.PanConfig.MaxStepsPerSec))
sg.tiltRate = clampFloat(tiltDegPerSec*tiltStepsPerDeg, float64(-sg.TiltConfig.MaxStepsPerSec), float64(sg.TiltConfig.MaxStepsPerSec))
}

// Start begins the step generation loop.
func (sg *StepGenerator) Start() {
sg.mu.Lock()
if sg.running {
sg.mu.Unlock()
return
}
sg.running = true
sg.mu.Unlock()

go sg.stepLoop()
log.Println("StepGenerator started")
}

// Stop halts step generation.
func (sg *StepGenerator) Stop() {
sg.mu.Lock()
sg.running = false
sg.panRate = 0
sg.tiltRate = 0
sg.mu.Unlock()
log.Println("StepGenerator stopped")
}

// GetStepCounts returns the cumulative step counts for both axes.
func (sg *StepGenerator) GetStepCounts() (pan int64, tilt int64) {
sg.mu.Lock()
defer sg.mu.Unlock()
return sg.panSteps, sg.tiltSteps
}

func (sg *StepGenerator) stepLoop() {
ticker := time.NewTicker(time.Millisecond)
defer ticker.Stop()

for range ticker.C {
sg.mu.Lock()
if !sg.running {
sg.mu.Unlock()
return
}
panRate := sg.panRate
tiltRate := sg.tiltRate
sg.mu.Unlock()

// Calculate steps for this tick interval (1ms)
panSteps := int64(math.Round(panRate / 1000.0))
tiltSteps := int64(math.Round(tiltRate / 1000.0))

if sg.simulate {
sg.mu.Lock()
sg.panSteps += panSteps
sg.tiltSteps += tiltSteps
sg.mu.Unlock()
} else {
// In production: send GPIO pulses
sg.sendPulses(sg.PanConfig, panSteps)
sg.sendPulses(sg.TiltConfig, tiltSteps)
sg.mu.Lock()
sg.panSteps += panSteps
sg.tiltSteps += tiltSteps
sg.mu.Unlock()
}
}
}

func (sg *StepGenerator) sendPulses(config StepperConfig, steps int64) {
// In production: set direction pin based on sign, then pulse step pin
// This is a placeholder for actual GPIO control via /dev/gpiochip0
_ = config
_ = steps
}

// IsRunning returns whether the step generator is active.
func (sg *StepGenerator) IsRunning() bool {
sg.mu.Lock()
defer sg.mu.Unlock()
return sg.running
}

func clampFloat(v, min, max float64) float64 {
if v < min {
return min
}
if v > max {
return max
}
return v
}
