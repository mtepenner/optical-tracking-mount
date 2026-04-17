// Package kinematics provides coordinate transformations between celestial and mount frames.
package kinematics

import "math"

// ObserverLocation represents the observer's position on Earth.
type ObserverLocation struct {
Latitude  float64 // degrees North
Longitude float64 // degrees East
}

// AltAz represents Altitude/Azimuth (horizontal) coordinates.
type AltAz struct {
Altitude float64 // degrees above horizon
Azimuth  float64 // degrees from North, clockwise
}

// MountAngles represents the physical pan/tilt angles of the telescope mount.
type MountAngles struct {
Pan  float64 // horizontal rotation in degrees
Tilt float64 // vertical angle in degrees
}

// CoordinateTransformer converts between celestial and mount coordinate systems.
type CoordinateTransformer struct {
Location ObserverLocation
}

// NewCoordinateTransformer creates a transformer for the given observer location.
func NewCoordinateTransformer(loc ObserverLocation) *CoordinateTransformer {
return &CoordinateTransformer{Location: loc}
}

// EquatorialToHorizontal converts RA/Dec to Altitude/Azimuth.
// hourAngle is the local hour angle in degrees.
func (ct *CoordinateTransformer) EquatorialToHorizontal(raDeg, decDeg, lstDeg float64) AltAz {
// Local Hour Angle
ha := degToRad(lstDeg - raDeg)
dec := degToRad(decDeg)
lat := degToRad(ct.Location.Latitude)

// Altitude
sinAlt := math.Sin(dec)*math.Sin(lat) + math.Cos(dec)*math.Cos(lat)*math.Cos(ha)
alt := math.Asin(clamp(sinAlt, -1, 1))

// Azimuth
cosAz := (math.Sin(dec) - math.Sin(alt)*math.Sin(lat)) / (math.Cos(alt) * math.Cos(lat))
cosAz = clamp(cosAz, -1, 1)
az := math.Acos(cosAz)

if math.Sin(ha) > 0 {
az = 2*math.Pi - az
}

return AltAz{
Altitude: radToDeg(alt),
Azimuth:  radToDeg(az),
}
}

// HorizontalToMountAngles converts Alt/Az coordinates to physical mount angles.
func (ct *CoordinateTransformer) HorizontalToMountAngles(altaz AltAz) MountAngles {
return MountAngles{
Pan:  altaz.Azimuth,
Tilt: altaz.Altitude,
}
}

// ComputeTrackingError calculates the angular error between current and target positions.
func ComputeTrackingError(current, target AltAz) float64 {
// Great-circle distance in degrees
altC := degToRad(current.Altitude)
altT := degToRad(target.Altitude)
dAz := degToRad(target.Azimuth - current.Azimuth)

cosD := math.Sin(altC)*math.Sin(altT) + math.Cos(altC)*math.Cos(altT)*math.Cos(dAz)
cosD = clamp(cosD, -1, 1)
return radToDeg(math.Acos(cosD))
}

// ComputeTrackingErrorArcsec returns tracking error in arcseconds.
func ComputeTrackingErrorArcsec(current, target AltAz) float64 {
return ComputeTrackingError(current, target) * 3600.0
}

func degToRad(d float64) float64 { return d * math.Pi / 180.0 }
func radToDeg(r float64) float64 { return r * 180.0 / math.Pi }

func clamp(v, min, max float64) float64 {
if v < min {
return min
}
if v > max {
return max
}
return v
}
