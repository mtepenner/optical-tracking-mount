package ephemeris

import (
"math"
"testing"
"time"
)

func TestNewSGP4Target(t *testing.T) {
elements := DefaultISSTLE()
target := NewSGP4Target(elements)
if target == nil {
t.Fatal("NewSGP4Target returned nil")
}
if target.Elements.Name != "ISS (ZARYA)" {
t.Errorf("Expected ISS name, got %s", target.Elements.Name)
}
}

func TestCalculatePosition(t *testing.T) {
target := NewSGP4Target(DefaultISSTLE())
now := time.Date(2024, 6, 15, 12, 0, 0, 0, time.UTC)
pos := target.CalculatePosition(now)

// RA should be in range 0-360
if pos.RA < 0 || pos.RA > 360 {
t.Errorf("RA out of range: %f", pos.RA)
}
// Dec should be within orbital inclination
if math.Abs(pos.Dec) > 60 {
t.Errorf("Dec out of expected range: %f", pos.Dec)
}
// ISS altitude ~400km
if pos.Range < 100 || pos.Range > 1000 {
t.Errorf("Range unexpected: %f km", pos.Range)
}
// ISS velocity ~7.7 km/s
if pos.Velocity < 5 || pos.Velocity > 10 {
t.Errorf("Velocity unexpected: %f km/s", pos.Velocity)
}
}

func TestPositionChangesOverTime(t *testing.T) {
target := NewSGP4Target(DefaultISSTLE())
t1 := time.Date(2024, 6, 15, 12, 0, 0, 0, time.UTC)
t2 := t1.Add(10 * time.Minute)

pos1 := target.CalculatePosition(t1)
pos2 := target.CalculatePosition(t2)

// Position should change over 10 minutes
if pos1.RA == pos2.RA && pos1.Dec == pos2.Dec {
t.Error("Position did not change over 10 minutes")
}
}

func TestSolveKepler(t *testing.T) {
// For circular orbit (e=0), E should equal M
M := 1.0
E := solveKepler(M, 0.0, 1e-12)
if math.Abs(E-M) > 1e-10 {
t.Errorf("For e=0, E should equal M. Got E=%f, M=%f", E, M)
}
}

func TestNormalizeAngle(t *testing.T) {
tests := []struct {
input, expected float64
}{
{0, 0},
{math.Pi, math.Pi},
{3 * math.Pi, math.Pi},
{-math.Pi, math.Pi},
}
for _, tc := range tests {
result := normalizeAngle(tc.input)
if math.Abs(result-tc.expected) > 1e-10 {
t.Errorf("normalizeAngle(%f) = %f, want %f", tc.input, result, tc.expected)
}
}
}
