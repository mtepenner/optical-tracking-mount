// Package main is the entry point for the tracking controller.
package main

import (
"log"
"os"
"os/signal"
"syscall"
"time"

"github.com/mtepenner/optical-tracking-mount/tracking_controller/internal/control_loop"
"github.com/mtepenner/optical-tracking-mount/tracking_controller/internal/ephemeris"
"github.com/mtepenner/optical-tracking-mount/tracking_controller/internal/hardware"
"github.com/mtepenner/optical-tracking-mount/tracking_controller/internal/kinematics"
)

func main() {
log.Println("Optical Tracking Mount - Tracking Controller starting...")

// Observer location (configurable via environment)
observer := kinematics.ObserverLocation{
Latitude:  51.0447, // Calgary, AB
Longitude: -114.0719,
}

// Initialize subsystems
target := ephemeris.NewSGP4Target(ephemeris.DefaultISSTLE())
transformer := kinematics.NewCoordinateTransformer(observer)
pid := controlloop.NewPIDController()
stepGen := hardware.NewStepGenerator(true) // simulate mode

stepGen.Start()
defer stepGen.Stop()

// Graceful shutdown
sigChan := make(chan os.Signal, 1)
signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

ticker := time.NewTicker(100 * time.Millisecond) // 10 Hz control loop
defer ticker.Stop()

log.Println("Control loop running at 10 Hz. Press Ctrl+C to stop.")

// Simulated current mount position
currentAltAz := kinematics.AltAz{Altitude: 45.0, Azimuth: 180.0}

for {
select {
case <-sigChan:
log.Println("Shutdown signal received")
return
case now := <-ticker.C:
// 1. Calculate where the target should be
targetPos := target.CalculatePosition(now)

// 2. Convert RA/Dec to Alt/Az (using simplified LST)
lst := computeLST(now, observer.Longitude)
targetAltAz := transformer.EquatorialToHorizontal(targetPos.RA, targetPos.Dec, lst)

// 3. Compute tracking error
panError := (targetAltAz.Azimuth - currentAltAz.Azimuth) * 3600.0    // arcsec
tiltError := (targetAltAz.Altitude - currentAltAz.Altitude) * 3600.0 // arcsec

// 4. PID controller update
cmd := pid.Update(panError, tiltError, now)

// 5. Send to step generator
stepGen.SetSpeed(cmd.PanSpeed, cmd.TiltSpeed)

// 6. Simulate mount movement
currentAltAz.Azimuth += cmd.PanSpeed * 0.1   // 100ms tick
currentAltAz.Altitude += cmd.TiltSpeed * 0.1

errorArcsec := kinematics.ComputeTrackingErrorArcsec(currentAltAz, targetAltAz)

log.Printf("Target: Az=%.2f° Alt=%.2f° | Current: Az=%.2f° Alt=%.2f° | Error: %.1f arcsec | Motor: Pan=%.4f°/s Tilt=%.4f°/s",
targetAltAz.Azimuth, targetAltAz.Altitude,
currentAltAz.Azimuth, currentAltAz.Altitude,
errorArcsec, cmd.PanSpeed, cmd.TiltSpeed)
}
}
}

// computeLST computes a simplified Local Sidereal Time in degrees.
func computeLST(t time.Time, longitude float64) float64 {
// Julian date
y := float64(t.Year())
m := float64(t.Month())
d := float64(t.Day()) + float64(t.Hour())/24.0 + float64(t.Minute())/1440.0 + float64(t.Second())/86400.0

if m <= 2 {
y--
m += 12
}

A := float64(int(y / 100))
B := 2 - A + float64(int(A/4))
JD := float64(int(365.25*(y+4716))) + float64(int(30.6001*(m+1))) + d + B - 1524.5

// Greenwich Mean Sidereal Time
T := (JD - 2451545.0) / 36525.0
GMST := 280.46061837 + 360.98564736629*(JD-2451545.0) + 0.000387933*T*T

// Local Sidereal Time
LST := GMST + longitude

// Normalize to 0-360
for LST < 0 {
LST += 360
}
for LST >= 360 {
LST -= 360
}
return LST
}
