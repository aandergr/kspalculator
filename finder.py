from design import FindDesigns


class Finder(object):
    def __init__(self, payload, preferred_radial_size, delta_vs, accelerations, pressures, gimbal,
                 boosters, electricity, length):
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

    def Find(self, best_only=True, order_by_cost=False):
        all_designs = FindDesigns(self.payload,
                                  self.pressures,
                                  self.delta_vs,
                                  self.accelerations,
                                  self.preferred_radial_size,
                                  self.gimbal,
                                  self.boosters,
                                  self.electricity,
                                  self.length)

        if best_only:
            designs = [d for d in all_designs if d.IsBest]
        else:
            designs = all_designs

        if order_by_cost:
            return sorted(designs, key=lambda dsg: dsg.cost)
        return sorted(designs, key=lambda dsg: dsg.mass)
