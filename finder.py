from design import FindDesigns


class Finder(object):
    def __init__(self, payload, preferred_radial_size, delta_vs, gimbal, boosters, electricity,
                 length):
        """Initializes this finder.

        Args:
            payload (Int) - Payload size in kilograms.
            preferred_radial_size (RadialSize) - The preferred radial size.
            delta_vs ([(delta_v, acceleration, pressure)]) - Array of delta-V requirements.
            gimbal (boolean) - Whether or not to prefer thrust vectoring engines.
            boosters (boolean) - Whether or not to include solid boosters.
            electricity (boolean) - Whether or not to prefer engines that generate power.
            length (boolean) - Whether or not to prefer shorter engines.
        """
        self.payload = payload
        self.preferred_radial_size = preferred_radial_size
        self.delta_vs = delta_vs
        self.gimbal = gimbal
        self.boosters = boosters
        self.electricity = electricity
        self.length = length

    def FindDesigns(self, best_only=True, order_by_cost=False):
        dv, ac, pr = zip(*self.delta_vs)
        all_designs = FindDesigns(self.payload, pr, dv, ac, self.preferred_radial_size,
                                  self.gimbal, self.boosters, self.electricity, self.length)

        if best_only:
            designs = [d for d in all_designs if d.IsBest]
        else:
            designs = all_designs

        if order_by_cost:
            return sorted(designs, key=lambda dsg: dsg.cost)
        return sorted(D, key=lambda dsg: dsg.mass)
