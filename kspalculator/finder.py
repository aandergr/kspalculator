# -*- coding: utf-8 -*-

from .design import find_designs


class Finder(object):
    def __init__(self, payload, preferred_radial_size, delta_vs, accelerations, pressures, gimbal,
                 boosters, electricity, length, monopropellant):
        """Initializes this finder.

        Args:
            payload (Int) - Payload size in kilograms.
            preferred_radial_size (RadialSize) - The preferred radial size.
            delta_vs ([float]) - Array of delta-V requirements.
            accelerations ([float]) - Array of acceleration requirements.
            pressures ([float]) - Array of pressure requirements.
            gimbal (boolean) - Whether or not to prefer thrust vectoring engines.
            boosters (boolean) - Whether or not to include solid boosters.
            electricity (boolean) - Whether or not to prefer engines that generate power.
            length (boolean) - Whether or not to prefer shorter engines.
        """
        if payload < 0.0:
            raise ValueError("Invalid payload")
        for i in range(len(delta_vs)):
            # because of Eve, we have to support up to 5 ATM
            if delta_vs[i] <= 0.0 or accelerations[i] < 0.0 or \
                    pressures[i] < 0.0 or pressures[i] > 5.0:
                raise ValueError("Invalid Delta-v tuple")
        self.payload = payload
        self.preferred_radial_size = preferred_radial_size
        self.delta_vs = delta_vs
        self.accelerations = accelerations
        self.pressures = pressures
        self.gimbal = gimbal
        self.boosters = boosters
        self.electricity = electricity
        self.length = length
        self.monopropellant = monopropellant

    def lint(self):
        """Check input values for common mistakes and return a list of warnings."""
        warnings = []
        # if these conditions are given, we assume the ship is going to be a kerbin launcher
        kerbin_launcher = sum(self.delta_vs) >= 3400 and 1.0 in self.pressures and \
                max(self.accelerations) > 9.8

        if max(self.accelerations) == 0.0:
            warnings.append("No minimum acceleration in any phase given. Very weak engines could "
                    "be presented.")
        elif max(self.accelerations) > 22.3:
            warnings.append("Very high minimum acceleration required. Overthink whether you really "
                    "need such a strong engine.")
        if max(self.pressures) > 2.5:
            warnings.append("Very high pressure required. If you are going to land on Eve, "
                    "consider landing on a mountain.")
        if self.payload > 115500:
            # 2/3 * ((670000*8 * 195/220) / 13 - 8*24000)
            # Two thirds of maximum weight for eight kickbacks to accelerate with 13 m/s² at 1 ATM
            warnings.append("Your rocket is very heavy.")
        if sum(self.delta_vs) > 7300:
            warnings.append("You require too much Delta-v for most conventional engines. Overthink "
                    "your mission planning.")
        elif sum(self.delta_vs) > 4600:
            warnings.append("As you require much Delta-v, consider splitting the ship into "
                    "multiple stages to carry fewer empty tanks.")
        if kerbin_launcher and not self.boosters:
            warnings.append("Enable solid fuel boosters if you are building a launcher.")
        if kerbin_launcher and max(self.accelerations) <= 10.0:
            warnings.append("To launch from Kerbin, your minimum acceleration should be actually "
                    "higher than the surface gravity.")

        return warnings

    def find(self, best_only=True, order_by_cost=False):
        all_designs = find_designs(self.payload,
                                   self.pressures,
                                   self.delta_vs,
                                   self.accelerations,
                                   self.preferred_radial_size,
                                   self.gimbal,
                                   self.boosters,
                                   self.electricity,
                                   self.length,
                                   self.monopropellant)

        if best_only:
            designs = [d for d in all_designs if d.is_best]
        else:
            designs = all_designs

        if order_by_cost:
            return sorted(designs, key=lambda dsg: dsg.get_cost())
        return sorted(designs, key=lambda dsg: dsg.get_mass())
