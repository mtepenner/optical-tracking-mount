package kinematics

import (
"math"
"testing"
)

func TestEquatorialToHorizontal(t *testing.T) {
ct := NewCoordinateTransformer(ObserverLocation{Latitude: 51.0, Longitude: -114.0})
altaz := ct.EquatorialToHorizontal(180.0, 45.0, 90.0)

// Basic sanity: altitude should be finite
if math.IsNaN(altaz.Altitude) || math.IsNaN(altaz.Azimuth) {
t.Errorf("Got NaN: alt=%f, az=%f", altaz.Altitude, altaz.Azimuth)
}
// Altitude should be in range -90 to 90
if altaz.Altitude < -90 || altaz.Altitude > 90 {
t.Errorf("Altitude out of range: %f", altaz.Altitude)
}
}

func TestHorizontalToMountAngles(t *testing.T) {
ct := NewCoordinateTransformer(ObserverLocation{Latitude: 0, Longitude: 0})
altaz := AltAz{Altitude: 45.0, Azimuth: 180.0}
angles := ct.HorizontalToMountAngles(altaz)
if angles.Pan != 180.0 || angles.Tilt != 45.0 {
t.Errorf("Expected Pan=180, Tilt=45, got Pan=%f, Tilt=%f", angles.Pan, angles.Tilt)
}
}

func TestComputeTrackingErrorSamePoint(t *testing.T) {
a := AltAz{Altitude: 45.0, Azimuth: 180.0}
err := ComputeTrackingError(a, a)
if math.Abs(err) > 1e-10 {
t.Errorf("Expected zero error for same point, got %f", err)
}
}

func TestComputeTrackingErrorArcsec(t *testing.T) {
current := AltAz{Altitude: 45.0, Azimuth: 180.0}
target := AltAz{Altitude: 45.001, Azimuth: 180.001}
errArcsec := ComputeTrackingErrorArcsec(current, target)
// Should be a small positive number (a few arcseconds)
if errArcsec <= 0 || errArcsec > 100 {
t.Errorf("Unexpected error: %f arcsec", errArcsec)
}
}

func TestTrackingErrorSymmetry(t *testing.T) {
a := AltAz{Altitude: 30.0, Azimuth: 100.0}
b := AltAz{Altitude: 31.0, Azimuth: 101.0}
err1 := ComputeTrackingError(a, b)
err2 := ComputeTrackingError(b, a)
if math.Abs(err1-err2) > 1e-10 {
t.Errorf("Tracking error not symmetric: %f vs %f", err1, err2)
}
}
