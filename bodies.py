# Python 2.7 support.
from __future__ import division
from enum import Enum, unique

@unique
class CelestialBody(Enum):
    """The celestial bodies in the Kerbol system."""
    Kerbol = (1.746, 0.157908, 600)
    Moho = (0.275)
    Eve = (1.7, 5, 90)
    Gilly = (0.005)
    Kerbin = (1, 1, 70)
    Mun = (0.166)
    Minmus = (0.05)
    Duna = (0.3, 0.066667, 50)
    Ike = (0.112)
    Dres = (0.115)
    Jool = (0.8, 15, 200)
    Laythe = (0.8, 0.6, 50)
    Vall = (0.235)
    Tylo = (0.8)
    Bop = (0.06)
    Pol = (0.038)
    Eeloo = (0.172)

    def __init__(self, gravity, pressure=None, atmospheric_height=None):
        self.gravity = gravity
        self.pressure_at_sealevel = pressure
        self.atmospheric_height = atmospheric_height

@unique
class Location(Enum):
    Surface = 0
    Orbit = 1
    Stationary = 2
    SOI = 3
    Intercept = 4


class DeltaVEdge(object):
    def __init__(self, delta_v, start, start_location, end_location, end=None, plane_change=0):
        self.delta_v = delta_v
        self.start = start
        self.start_location = start_location
        self.end_location = end_location
        if not end:
            self.end = self.start
        else:
            self.end = end
        self.plane_change = plane_change


# 1.1.2 map from
# http://forum.kerbalspaceprogram.com/index.php?/topic/87463-105-112-community-delta-v-map-22-nov-17th-opm-update/
DeltaVGraph = [
    DeltaVEdge(3400, CelestialBody.Kerbin, Location.Surface, Location.Orbit),
    DeltaVEdge(1115, CelestialBody.Kerbin, Location.Orbit, Location.Stationary),

    DeltaVEdge(860, CelestialBody.Kerbin, Location.Orbit, Location.Intercept, CelestialBody.Mun),
    DeltaVEdge(310, CelestialBody.Mun, Location.Intercept, Location.Orbit),
    DeltaVEdge(580, CelestialBody.Mun, Location.Orbit, Location.Surface),

    DeltaVEdge(930, CelestialBody.Kerbin, Location.Orbit, Location.Intercept,
               CelestialBody.Minmus, 340),
    DeltaVEdge(160, CelestialBody.Minmus, Location.Intercept, Location.Orbit),
    DeltaVEdge(180, CelestialBody.Minmus, Location.Orbit, Location.Surface),

    DeltaVEdge(950, CelestialBody.Kerbin, Location.Orbit, Location.SOI),

    DeltaVEdge(6000, CelestialBody.Kerbin, Location.SOI, Location.SOI,
               CelestialBody.Kerbol),
    DeltaVEdge(13700, CelestialBody.Kerbol, Location.SOI, Location.Orbit),
    DeltaVEdge(67000, CelestialBody.Kerbol, Location.Orbit, Location.Surface),

    DeltaVEdge(760, CelestialBody.Kerbin, Location.SOI, Location.Intercept,
               CelestialBody.Moho, 2520),
    DeltaVEdge(2410, CelestialBody.Moho, Location.Intercept, Location.Orbit),
    DeltaVEdge(870, CelestialBody.Moho, Location.Orbit, Location.Surface),

    DeltaVEdge(90, CelestialBody.Kerbin, Location.SOI, Location.Intercept,
               CelestialBody.Eve, 430),
    DeltaVEdge(80, CelestialBody.Eve, Location.Intercept, Location.SOI),
    DeltaVEdge(1330, CelestialBody.Eve, Location.SOI, Location.Orbit),
    DeltaVEdge(8000, CelestialBody.Eve, Location.Orbit, Location.Surface),
    DeltaVEdge(60, CelestialBody.Eve, Location.SOI, Location.Intercept,
               CelestialBody.Gilly),
    DeltaVEdge(410, CelestialBody.Gilly, Location.Intercept, Location.Orbit),
    DeltaVEdge(30, CelestialBody.Gilly, Location.Orbit, Location.Surface),

    DeltaVEdge(130, CelestialBody.Kerbin, Location.SOI, Location.Intercept,
               CelestialBody.Duna, 10),
    DeltaVEdge(250, CelestialBody.Duna, Location.Intercept, Location.SOI),
    DeltaVEdge(360, CelestialBody.Duna, Location.SOI, Location.Orbit),
    DeltaVEdge(1450, CelestialBody.Duna, Location.Orbit, Location.Surface),
    DeltaVEdge(30, CelestialBody.Duna, Location.SOI, Location.Intercept,
               CelestialBody.Ike),
    DeltaVEdge(180, CelestialBody.Ike, Location.Intercept, Location.Orbit),
    DeltaVEdge(390, CelestialBody.Ike, Location.Orbit, Location.Surface),

    DeltaVEdge(610, CelestialBody.Kerbin, Location.SOI, Location.Intercept,
               CelestialBody.Dres, 1010),
    DeltaVEdge(1290, CelestialBody.Dres, Location.Intercept, Location.Orbit),
    DeltaVEdge(430, CelestialBody.Dres, Location.Orbit, Location.Surface),

    DeltaVEdge(980, CelestialBody.Kerbin, Location.SOI, Location.Intercept,
               CelestialBody.Jool, 270),
    DeltaVEdge(160, CelestialBody.Jool, Location.Intercept, Location.SOI),
    DeltaVEdge(2810, CelestialBody.Jool, Location.SOI, Location.Orbit),
    DeltaVEdge(14000, CelestialBody.Jool, Location.Orbit, Location.Surface),
    DeltaVEdge(160, CelestialBody.Jool, Location.SOI, Location.Intercept,
               CelestialBody.Pol, 700),
    DeltaVEdge(820, CelestialBody.Pol, Location.Intercept, Location.Orbit),
    DeltaVEdge(130, CelestialBody.Pol, Location.Orbit, Location.Surface),
    DeltaVEdge(220, CelestialBody.Jool, Location.SOI, Location.Intercept,
               CelestialBody.Bop, 2440),
    DeltaVEdge(900, CelestialBody.Bop, Location.Intercept, Location.Orbit),
    DeltaVEdge(220, CelestialBody.Bop, Location.Orbit, Location.Surface),
    DeltaVEdge(400, CelestialBody.Jool, Location.SOI, Location.Intercept,
               CelestialBody.Tylo),
    DeltaVEdge(1100, CelestialBody.Tylo, Location.Intercept, Location.Orbit),
    DeltaVEdge(2270, CelestialBody.Tylo, Location.Orbit, Location.Surface),
    DeltaVEdge(620, CelestialBody.Jool, Location.SOI, Location.Intercept,
               CelestialBody.Vall),
    DeltaVEdge(910, CelestialBody.Vall, Location.Intercept, Location.Orbit),
    DeltaVEdge(860, CelestialBody.Vall, Location.Orbit, Location.Surface),
    DeltaVEdge(930, CelestialBody.Jool, Location.SOI, Location.Intercept,
               CelestialBody.Laythe),
    DeltaVEdge(1070, CelestialBody.Laythe, Location.Intercept, Location.Orbit),
    DeltaVEdge(2900, CelestialBody.Laythe, Location.Orbit, Location.Surface),

    DeltaVEdge(1140, CelestialBody.Kerbin, Location.SOI, Location.Intercept,
               CelestialBody.Eeloo, 1330),
    DeltaVEdge(1370, CelestialBody.Eeloo, Location.Intercept, Location.Orbit),
    DeltaVEdge(620, CelestialBody.Eeloo, Location.Orbit, Location.Surface),
]


def _BuildStageGraph():
    return {}
_graph = _BuildStageGraph()


def CalculateCost(start_body, start_location, end_body, end_location):
    return [1000], [0], [0]
