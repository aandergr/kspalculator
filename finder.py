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
        self.payload = payload
        self.preferred_radial_size = preferred_radial_size
        self.delta_vs = delta_vs
        self.accelerations = accelerations
        self.pressures = pressures
        self.gimbal = gimbal
        self.boosters = boosters
        self.electricity = electricity
        self.length = length

    def FindDesigns(self, best_only=True, order_by_cost=False):
        print('%r ' % self.payload)
        print('%r ' % self.delta_vs)
        print('%r ' % self.accelerations)
        print('%r ' % self.pressures)
        print('%r ' % self.preferred_radial_size)
        print('G: %r ' % self.gimbal)
        print('B: %r ' % self.boosters)
        print('E: %r ' % self.electricity)
        print('L: %r ' % self.length)
        all_designs = FindDesigns(self.payload, self.delta_vs, self.accelerations, self.pressures,
                                  self.preferred_radial_size, self.gimbal, self.boosters,
                                  self.electricity, self.length)

        if best_only:
            designs = [d for d in all_designs if d.IsBest]
        else:
            designs = all_designs

        print('%s' % str(all_designs))

        if order_by_cost:
            return sorted(designs, key=lambda dsg: dsg.cost)
        return sorted(designs, key=lambda dsg: dsg.mass)
