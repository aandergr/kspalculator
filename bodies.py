# Python 2.7 support.
from __future__ import division
from enum import Enum, unique

from collections import defaultdict
from math import exp

from physics import g_0

@unique
class CelestialBody(Enum):
    """The celestial bodies in the Kerbol system."""
    Kerbol = (1.746, 610, 0.157908, 600, 43429)
    Moho = (0.275, 50)
    Eve = (1.7, 100, 5, 90, 7200)
    Gilly = (0.005, 10)
    Kerbin = (1, 80, 1, 70, 5600)
    Mun = (0.166, 14)
    Minmus = (0.05, 10)
    Duna = (0.3, 60, 0.066667, 50, 5700)
    Ike = (0.112, 10)
    Dres = (0.115, 12)
    Jool = (0.8, 210, 15, 200, 30000)
    Laythe = (0.8, 60, 0.6, 50, 8000)
    Vall = (0.235, 15)
    Tylo = (0.8, 10)
    Bop = (0.06, 10)
    Pol = (0.038, 10)
    Eeloo = (0.172, 10)

    def __init__(self, gravity, orbital_height, pressure=0, atmospheric_height=0, scale_height=0):
        self.gravity = gravity
        self.orbital_height = orbital_height
        self.pressure_at_sealevel = pressure
        self.atmospheric_height = atmospheric_height
        self.scale_height = scale_height

@unique
class Location(Enum):
    Surface = 0
    Orbit = 1
    Stationary = 2
    Soi = 3
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

        self.start_node = (self.start, self.start_location)
        self.end_node = (self.end, self.end_location)

    def CostAccelerationPressure(self):
        """Returns (dV, acceleration, pressure) triplets needed to traverse this edge."""
        acceleration_required = 0
        pressure = 0

        # Generate multiple tuples to estimate pressure changes for bodies with atmosphere.
        if self.start.pressure_at_sealevel or self.end.pressure_at_sealevel:
            # Takeoffs require 2g, landings require 1.5g.
            if self.start_location is Location.Surface:
                costs, pressures = self._CostsAndPressuresFromAtmosphericSurfaceToOrbit()
                acceleration_required = 2 * self.start.gravity * g_0

                return costs, [acceleration_required] * len(costs), pressures
            elif self.end_location is Location.Surface:
                acceleration_required = 1.5 * self.end.gravity * g_0
                # TODO - model aerobraking.
                #pressure = self.end.pressure_at_sealevel

        return [self.delta_v], [acceleration_required], [pressure]

    def _CostsAndPressuresFromAtmosphericSurfaceToOrbit(self):
        # From http://wiki.kerbalspaceprogram.com/wiki/Atmosphere:
        #   pressure = p_0 * e ^ (-altitude / H)
        # where H = the scale height for the body, p_0 = the surface pressure.
        p_0 = self.start.pressure_at_sealevel
        H = self.start.scale_height
        atmospheric_height = self.start.atmospheric_height * 1000
        orbit = self.start.orbital_height * 1000
        total_delta_v = self.delta_v

        # For each increment of scale height, add a delta_v cost and instantaneous pressure at the
        # current altitude.
        # TODO - The linear attribution of delta_v is almost certainly incorrect.
        costs = []
        pressures = []
        # Add a safety factor by considering everything up until 2.5 H as surface atmospheric
        # pressure.
        altitude = 2 * H
        exponent = 0
        last_delta_v = 0
        while altitude < atmospheric_height:
            pressure = p_0 * exp(-exponent)
            altitude += H
            delta_v_to_new_altitude = total_delta_v * (altitude / orbit)
            delta_v = delta_v_to_new_altitude - last_delta_v
            last_delta_v = delta_v_to_new_altitude
            exponent += 1

            costs.append(delta_v)
            pressures.append(pressure)

        # Add the remaining delta_v to orbit outside of the atmosphere.
        costs.append(self.delta_v - last_delta_v)
        pressures.append(0)

        return costs, pressures


# 1.1.2 map from
# http://forum.kerbalspaceprogram.com/index.php?/topic/87463-105-112-community-delta-v-map-22-nov-17th-opm-update/
DeltaVEdges = [
    DeltaVEdge(3400, CelestialBody.Kerbin, Location.Surface, Location.Orbit),
    DeltaVEdge(1115, CelestialBody.Kerbin, Location.Orbit, Location.Stationary),

    DeltaVEdge(860, CelestialBody.Kerbin, Location.Orbit, Location.Intercept, CelestialBody.Mun),
    DeltaVEdge(310, CelestialBody.Mun, Location.Intercept, Location.Orbit),
    DeltaVEdge(580, CelestialBody.Mun, Location.Orbit, Location.Surface),

    DeltaVEdge(930, CelestialBody.Kerbin, Location.Orbit, Location.Intercept,
               CelestialBody.Minmus, 340),
    DeltaVEdge(160, CelestialBody.Minmus, Location.Intercept, Location.Orbit),
    DeltaVEdge(180, CelestialBody.Minmus, Location.Orbit, Location.Surface),

    DeltaVEdge(950, CelestialBody.Kerbin, Location.Orbit, Location.Soi),

    DeltaVEdge(6000, CelestialBody.Kerbin, Location.Soi, Location.Soi,
               CelestialBody.Kerbol),
    DeltaVEdge(13700, CelestialBody.Kerbol, Location.Soi, Location.Orbit),
    DeltaVEdge(67000, CelestialBody.Kerbol, Location.Orbit, Location.Surface),

    DeltaVEdge(760, CelestialBody.Kerbin, Location.Soi, Location.Intercept,
               CelestialBody.Moho, 2520),
    DeltaVEdge(2410, CelestialBody.Moho, Location.Intercept, Location.Orbit),
    DeltaVEdge(870, CelestialBody.Moho, Location.Orbit, Location.Surface),

    DeltaVEdge(90, CelestialBody.Kerbin, Location.Soi, Location.Intercept,
               CelestialBody.Eve, 430),
    DeltaVEdge(80, CelestialBody.Eve, Location.Intercept, Location.Soi),
    DeltaVEdge(1330, CelestialBody.Eve, Location.Soi, Location.Orbit),
    DeltaVEdge(8000, CelestialBody.Eve, Location.Orbit, Location.Surface),
    DeltaVEdge(60, CelestialBody.Eve, Location.Soi, Location.Intercept,
               CelestialBody.Gilly),
    DeltaVEdge(410, CelestialBody.Gilly, Location.Intercept, Location.Orbit),
    DeltaVEdge(30, CelestialBody.Gilly, Location.Orbit, Location.Surface),

    DeltaVEdge(130, CelestialBody.Kerbin, Location.Soi, Location.Intercept,
               CelestialBody.Duna, 10),
    DeltaVEdge(250, CelestialBody.Duna, Location.Intercept, Location.Soi),
    DeltaVEdge(360, CelestialBody.Duna, Location.Soi, Location.Orbit),
    DeltaVEdge(1450, CelestialBody.Duna, Location.Orbit, Location.Surface),
    DeltaVEdge(30, CelestialBody.Duna, Location.Soi, Location.Intercept,
               CelestialBody.Ike),
    DeltaVEdge(180, CelestialBody.Ike, Location.Intercept, Location.Orbit),
    DeltaVEdge(390, CelestialBody.Ike, Location.Orbit, Location.Surface),

    DeltaVEdge(610, CelestialBody.Kerbin, Location.Soi, Location.Intercept,
               CelestialBody.Dres, 1010),
    DeltaVEdge(1290, CelestialBody.Dres, Location.Intercept, Location.Orbit),
    DeltaVEdge(430, CelestialBody.Dres, Location.Orbit, Location.Surface),

    DeltaVEdge(980, CelestialBody.Kerbin, Location.Soi, Location.Intercept,
               CelestialBody.Jool, 270),
    DeltaVEdge(160, CelestialBody.Jool, Location.Intercept, Location.Soi),
    DeltaVEdge(2810, CelestialBody.Jool, Location.Soi, Location.Orbit),
    DeltaVEdge(14000, CelestialBody.Jool, Location.Orbit, Location.Surface),
    DeltaVEdge(160, CelestialBody.Jool, Location.Soi, Location.Intercept,
               CelestialBody.Pol, 700),
    DeltaVEdge(820, CelestialBody.Pol, Location.Intercept, Location.Orbit),
    DeltaVEdge(130, CelestialBody.Pol, Location.Orbit, Location.Surface),
    DeltaVEdge(220, CelestialBody.Jool, Location.Soi, Location.Intercept,
               CelestialBody.Bop, 2440),
    DeltaVEdge(900, CelestialBody.Bop, Location.Intercept, Location.Orbit),
    DeltaVEdge(220, CelestialBody.Bop, Location.Orbit, Location.Surface),
    DeltaVEdge(400, CelestialBody.Jool, Location.Soi, Location.Intercept,
               CelestialBody.Tylo),
    DeltaVEdge(1100, CelestialBody.Tylo, Location.Intercept, Location.Orbit),
    DeltaVEdge(2270, CelestialBody.Tylo, Location.Orbit, Location.Surface),
    DeltaVEdge(620, CelestialBody.Jool, Location.Soi, Location.Intercept,
               CelestialBody.Vall),
    DeltaVEdge(910, CelestialBody.Vall, Location.Intercept, Location.Orbit),
    DeltaVEdge(860, CelestialBody.Vall, Location.Orbit, Location.Surface),
    DeltaVEdge(930, CelestialBody.Jool, Location.Soi, Location.Intercept,
               CelestialBody.Laythe),
    DeltaVEdge(1070, CelestialBody.Laythe, Location.Intercept, Location.Orbit),
    DeltaVEdge(2900, CelestialBody.Laythe, Location.Orbit, Location.Surface),

    DeltaVEdge(1140, CelestialBody.Kerbin, Location.Soi, Location.Intercept,
               CelestialBody.Eeloo, 1330),
    DeltaVEdge(1370, CelestialBody.Eeloo, Location.Intercept, Location.Orbit),
    DeltaVEdge(620, CelestialBody.Eeloo, Location.Orbit, Location.Surface),
]


def _BuildStageGraph():
    graph = defaultdict(list)
    for edge in DeltaVEdges:
        graph[(edge.start, edge.start_location)].append(edge)
        graph[(edge.end, edge.end_location)].append(edge)
    return graph
_stage_graph = _BuildStageGraph()


def CalculateCost(start_body, start_location, end_body, end_location):
    """Returns [deltav], [acceleration], [pressure] lists for the given location transfer."""
    path = _ExpandTripEdges((start_body, start_location), (end_body, end_location))
    if not path:
        return [0], [0], [0]

    deltavs = []
    accelerations = []
    pressures = []
    for edge in path:
        print('%r -> %r' % ((edge.start, edge.start_location), (edge.end, edge.end_location)))
        edge_deltavs, edge_accelerations, edge_pressures = edge.CostAccelerationPressure()
        deltavs.extend(edge_deltavs)
        accelerations.extend(edge_accelerations)
        pressures.extend(edge_pressures)

    return deltavs, accelerations, pressures


def _ExpandTripEdges(start_node, end_node, path_edges=list(), visited_nodes=set()):
    """Returns a list of edges traversing from start_node to end_node."""

    visited_nodes.add(start_node)
    if start_node == end_node:
        return path_edges

    out_edges = _stage_graph[start_node]
    for e in out_edges:
        if e.end_node not in visited_nodes:
            p = _ExpandTripEdges(e.end_node, end_node, path_edges + [e], visited_nodes)
            if p:
                return p
    return None
