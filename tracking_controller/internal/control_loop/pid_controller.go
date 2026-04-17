// Package controlloop implements PID control for telescope tracking.
package controlloop

import (
"math"
"time"
)

// PIDGains holds the PID controller tuning parameters.
type PIDGains struct {
Kp float64 // Proportional gain
Ki float64 // Integral gain
Kd float64 // Derivative gain
}

// PIDState holds the internal state of the PID controller.
type PIDState struct {
LastError    float64
Integral     float64
LastTime     time.Time
Initialized  bool
}

// MotorCommand represents the output speeds for pan and tilt motors.
type MotorCommand struct {
PanSpeed  float64 // degrees per second
TiltSpeed float64 // degrees per second
}

// PIDController calculates motor speeds to minimize tracking error.
type PIDController struct {
PanGains  PIDGains
TiltGains PIDGains
panState  PIDState
tiltState PIDState
MaxOutput float64 // Maximum motor speed (degrees/sec)
DeadZone  float64 // Error below which no correction is applied (arcsec)
}

// NewPIDController creates a new PID controller with default gains.
func NewPIDController() *PIDController {
return &PIDController{
PanGains:  PIDGains{Kp: 2.0, Ki: 0.1, Kd: 0.5},
TiltGains: PIDGains{Kp: 2.0, Ki: 0.1, Kd: 0.5},
MaxOutput: 5.0,    // max 5 degrees/sec
DeadZone:  1.0,    // 1 arcsecond dead zone
}
}

// Update computes the motor command given current tracking errors.
// panError and tiltError are in arcseconds.
func (pid *PIDController) Update(panErrorArcsec, tiltErrorArcsec float64, now time.Time) MotorCommand {
panSpeed := pid.computeAxis(&pid.panState, pid.PanGains, panErrorArcsec, now)
tiltSpeed := pid.computeAxis(&pid.tiltState, pid.TiltGains, tiltErrorArcsec, now)

return MotorCommand{
PanSpeed:  panSpeed,
TiltSpeed: tiltSpeed,
}
}

func (pid *PIDController) computeAxis(state *PIDState, gains PIDGains, errorArcsec float64, now time.Time) float64 {
// Convert to degrees for motor output
errorDeg := errorArcsec / 3600.0

// Dead zone: ignore very small errors
if math.Abs(errorArcsec) < pid.DeadZone {
state.Integral = 0
return 0
}

if !state.Initialized {
state.LastError = errorDeg
state.LastTime = now
state.Initialized = true
return clamp(gains.Kp * errorDeg, -pid.MaxOutput, pid.MaxOutput)
}

dt := now.Sub(state.LastTime).Seconds()
if dt <= 0 {
return 0
}

// PID terms
p := gains.Kp * errorDeg
state.Integral += errorDeg * dt
// Anti-windup: clamp integral
maxIntegral := pid.MaxOutput / (gains.Ki + 1e-10)
state.Integral = clamp(state.Integral, -maxIntegral, maxIntegral)
i := gains.Ki * state.Integral
d := gains.Kd * (errorDeg - state.LastError) / dt

state.LastError = errorDeg
state.LastTime = now

output := p + i + d
return clamp(output, -pid.MaxOutput, pid.MaxOutput)
}

// Reset clears the PID controller state.
func (pid *PIDController) Reset() {
pid.panState = PIDState{}
pid.tiltState = PIDState{}
}

func clamp(v, min, max float64) float64 {
if v < min {
return min
}
if v > max {
return max
}
return v
}
