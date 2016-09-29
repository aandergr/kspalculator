# -*- coding: utf-8 -*-

"""Technology Tree"""

# Source: http://wiki.kerbalspaceprogram.com/wiki/Parts, as well as in-game info

from enum import Enum, unique

@unique
class Node(Enum):
    """Node of technology tree.

    Not all nodes of the tree are necessary to be present for this tool."""

    Start = 11
    BasicRocketry = 21
    Engineering101 = 22
    GeneralRocketry = 31
    Stability = 32
    AdvancedRocketry = 41
    FlightControl = 42
    HeavyRocketry = 51
    PropulsionSystems = 52
    Aerodynamics = 53
    AdvancedFlightControl = 54
    HeavierRocketry = 61
    PrecisionPropulsion = 62
    AdvancedFuelSystems = 63
    SupersonicFlight = 64
    SpecializedControl = 65
    NuclearPropulsion = 71
    HighAltitudeFlight = 72
    VeryHeavyRocketry = 81
    HypersonicFlight = 82
    IonPropulsion = 83
    AerospaceTech = 91

    def depends_on(self, other):
        """Returns true if other must have been researched when self is researched.

        Note that x.depends_on(x) is False.

        >>> Node.Start.depends_on(Node.Start)
        False
        >>> Node.NuclearPropulsion.depends_on(Node.HeavyRocketry)
        True
        >>> Node.VeryHeavyRocketry.depends_on(Node.HeavyRocketry)
        False"""
        # OR-branches are skipped until their merge. Fortunately, this is not a limitation.
        DEPCHAINS = [ [ Node.Start, Node.BasicRocketry, Node.GeneralRocketry,
                        Node.AdvancedRocketry, Node.HeavyRocketry, Node.HeavierRocketry,
                        Node.NuclearPropulsion ],
                      [ Node.Start, Node.BasicRocketry, Node.GeneralRocketry, Node.AdvancedRocketry,
                        Node.PropulsionSystems, Node.PrecisionPropulsion ],
                      [ Node.Start, Node.AdvancedFuelSystems, Node.NuclearPropulsion ],
                      [ Node.Start, Node.VeryHeavyRocketry ],
                      [ Node.Start, Node.Aerodynamics, Node.SupersonicFlight,
                        Node.HighAltitudeFlight, Node.HypersonicFlight, Node.AerospaceTech ],
                      [ Node.Start, Node.Engineering101, Node.IonPropulsion ],
                      [ Node.Start, Node.Stability ],
                      [ Node.Start, Node.FlightControl, Node.AdvancedFlightControl, Node.SpecializedControl ] ]
        for depchain in DEPCHAINS:
            try:
                if depchain.index(other) < depchain.index(self):
                    return True
            except ValueError:
                pass
        return False

class NodeSet:
    """Set of Nodes.

    With depends_on as order relation, only maximum nodes are stored in the set.

    Does not inherit from set, as doing so would require us to properly implement all functions,
    which is not what we want.
    """

    def __init__(self):
        self.nodes = set()

    def add(self, newnode):
        """Add newnode to set.

        >>> N = NodeSet()
        >>> N.add(Node.BasicRocketry)
        >>> len(N.nodes) == 1 and Node.BasicRocketry in N.nodes
        True
        >>> N.add(Node.Start)
        >>> len(N.nodes) == 1 and Node.BasicRocketry in N.nodes
        True
        >>> N.add(Node.GeneralRocketry)
        >>> len(N.nodes) == 1 and Node.GeneralRocketry in N.nodes
        True
        >>> N.add(Node.IonPropulsion)
        >>> len(N.nodes) == 2 and Node.IonPropulsion in N.nodes and Node.GeneralRocketry in N.nodes
        True
        >>> N.add(Node.Start)
        >>> len(N.nodes) == 2 and Node.IonPropulsion in N.nodes and Node.GeneralRocketry in N.nodes
        True
        >>> N.add(Node.AdvancedRocketry)
        >>> len(N.nodes) == 2 and Node.IonPropulsion in N.nodes and Node.AdvancedRocketry in N.nodes
        True"""

        # remove nodes which are prerequisites for newnode
        for node in self.nodes.copy():
            if newnode.depends_on(node):
                self.nodes.remove(node)

        # add newnode if it is not a prerequisite of all other nodes
        for node in self.nodes:
            if not node.depends_on(newnode):
                self.nodes.add(newnode)
                return
        if len(self.nodes) == 0:
            self.nodes.add(newnode)

    def is_easier_than(self, other):
        """Returns true if all our nodes have to be researched for other to be researched.

        A is easier than B <=> for all nodes a from A there is a node b from B such that
        b.depends_on(a), or A ⊊ B. (Note that x.depends_on(x) is False)

        >>> N = NodeSet()
        >>> M = NodeSet()
        >>> N.add(Node.BasicRocketry)
        >>> M.add(Node.GeneralRocketry)
        >>> N.is_easier_than(M)
        True
        >>> M.is_easier_than(N)
        False
        >>> N.add(Node.AerospaceTech)
        >>> N.is_easier_than(M)
        False
        >>> M.is_easier_than(N)
        False
        >>> N = NodeSet(); N.add(Node.BasicRocketry); N.add(Node.Engineering101)
        >>> M = NodeSet(); M.add(Node.BasicRocketry)
        >>> N.is_easier_than(M)
        False
        >>> M.is_easier_than(N)
        True
        """

        if self.nodes < other.nodes:
            return True

        for a in self.nodes:
            for b in other.nodes:
                if b.depends_on(a):
                    break
            else:
                return False
        return True
