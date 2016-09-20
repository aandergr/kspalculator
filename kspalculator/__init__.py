"""Determine the best rocket propulsion designs for one stage of a rocket, given a set of
constraints and preferences (Kerbal Space Program)."""

def __version__():
    try:
        import pkg_resources
        try:
            # pylint:disable=no-member
            return pkg_resources.get_distribution('kspalculator').version
        except pkg_resources.DistributionNotFound:
            return '?'
    except ImportError:
        return '?'
