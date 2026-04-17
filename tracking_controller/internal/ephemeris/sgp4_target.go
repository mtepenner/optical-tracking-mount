// Package ephemeris provides satellite position calculations using simplified SGP4.
package ephemeris

import (
"math"
"time"
)

// OrbitalElements represents the Two-Line Element (TLE) orbital parameters.
type OrbitalElements struct {
Name          string
Inclination   float64 // degrees
RAAN          float64 // Right Ascension of Ascending Node (degrees)
Eccentricity  float64
ArgPerigee    float64 // Argument of Perigee (degrees)
MeanAnomaly   float64 // degrees
MeanMotion    float64 // revolutions per day
Epoch         time.Time
}

// TargetPosition represents a celestial target's position.
type TargetPosition struct {
RA          float64 // Right Ascension in degrees (0-360)
Dec         float64 // Declination in degrees (-90 to +90)
Altitude    float64 // Above horizon in degrees
Azimuth     float64 // Compass bearing in degrees
Range       float64 // Distance in km
Velocity    float64 // Velocity in km/s
Timestamp   time.Time
}

// SGP4Target calculates satellite positions using simplified perturbation model.
type SGP4Target struct {
Elements OrbitalElements
}

// NewSGP4Target creates a new target calculator from orbital elements.
func NewSGP4Target(elements OrbitalElements) *SGP4Target {
return &SGP4Target{Elements: elements}
}

// DefaultISSTLE returns approximate ISS orbital elements.
func DefaultISSTLE() OrbitalElements {
return OrbitalElements{
Name:         "ISS (ZARYA)",
Inclination:  51.6416,
RAAN:         247.4627,
Eccentricity: 0.0006703,
ArgPerigee:   130.5360,
MeanAnomaly:  325.0288,
MeanMotion:   15.72125391,
Epoch:        time.Date(2024, 1, 1, 0, 0, 0, 0, time.UTC),
}
}

// CalculatePosition computes the satellite position at a given time.
func (s *SGP4Target) CalculatePosition(t time.Time) TargetPosition {
// Time since epoch in minutes
deltaMinutes := t.Sub(s.Elements.Epoch).Minutes()

// Mean motion in radians per minute
n := s.Elements.MeanMotion * 2.0 * math.Pi / (24.0 * 60.0)

// Current mean anomaly
M := degToRad(s.Elements.MeanAnomaly) + n*deltaMinutes
M = normalizeAngle(M)

// Solve Kepler's equation: E - e*sin(E) = M  (Newton's method)
E := solveKepler(M, s.Elements.Eccentricity, 1e-10)

// True anomaly
e := s.Elements.Eccentricity
sinV := math.Sqrt(1-e*e) * math.Sin(E) / (1 - e*math.Cos(E))
cosV := (math.Cos(E) - e) / (1 - e*math.Cos(E))
trueAnomaly := math.Atan2(sinV, cosV)

// Argument of latitude
u := trueAnomaly + degToRad(s.Elements.ArgPerigee)

// Simplified position in orbital plane
inc := degToRad(s.Elements.Inclination)
raan := degToRad(s.Elements.RAAN)

// Earth rotation rate (rad/min)
earthRotRate := 2.0 * math.Pi / (23.0*60.0 + 56.0 + 4.09/60.0)
raanCorrected := raan - earthRotRate*deltaMinutes

// Convert to equatorial coordinates (simplified)
x := math.Cos(u)*math.Cos(raanCorrected) - math.Sin(u)*math.Sin(raanCorrected)*math.Cos(inc)
y := math.Cos(u)*math.Sin(raanCorrected) + math.Sin(u)*math.Cos(raanCorrected)*math.Cos(inc)
z := math.Sin(u) * math.Sin(inc)

// Convert to RA/Dec
ra := math.Atan2(y, x)
if ra < 0 {
ra += 2 * math.Pi
}
dec := math.Atan2(z, math.Sqrt(x*x+y*y))

// Semi-major axis (km) from mean motion
mu := 398600.4418 // Earth gravitational parameter km^3/s^2
nRadPerSec := n / 60.0
a := math.Pow(mu/(nRadPerSec*nRadPerSec), 1.0/3.0)

// Velocity (vis-viva, simplified circular)
velocity := math.Sqrt(mu / a)

return TargetPosition{
RA:        radToDeg(ra),
Dec:       radToDeg(dec),
Range:     a - 6371.0, // approximate altitude
Velocity:  velocity, // km/s
Timestamp: t,
}
}

// solveKepler solves Kepler's equation using Newton's method.
func solveKepler(M, e, tolerance float64) float64 {
E := M
for i := 0; i < 50; i++ {
dE := (E - e*math.Sin(E) - M) / (1 - e*math.Cos(E))
E -= dE
if math.Abs(dE) < tolerance {
break
}
}
return E
}

func degToRad(d float64) float64 { return d * math.Pi / 180.0 }
func radToDeg(r float64) float64 { return r * 180.0 / math.Pi }

func normalizeAngle(a float64) float64 {
a = math.Mod(a, 2*math.Pi)
if a < 0 {
a += 2 * math.Pi
}
return a
}
