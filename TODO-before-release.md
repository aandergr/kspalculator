*Things which should be done before releasing this software, in order of
their priority.*

* Consider remaining types of engines, i.e.
 * Nuclear fission motor,
 * Ion propulsion,
 * Monopropellant engines,
 * Twin-Boar, having tank included.

* Consider that engines with low height as well as radially mounted engines
  might be advantageous (e.g. for landers)

* Consider that engines generating electricity might be advantageous.

* Review and test IsBest algorithm.

* Verify parts.py correctness for current KSP version

* Documentation and User Interface.
 * Write good README.md with examples.
 * Let kspalculator.py print all constraints for double-checking, unless
   --quiet option is given.
 * Rework --help.
 * --version, also showing KSP version of parts.py
 * Check validity of given options.

* One more time: Test and review code.

*Scheduled for later (after first release):*

* Consider adapters between different radial sizes.
 * There should be an option for upper radial size.
 * There should be an option for not using smaller sizes than upper
   radial size.
 * There should be an option to disable usage of adapters (but still
   changing size, as preferrence of keeping size can be expressed using
   --preferred-size option)

* Consider mounting multiple small engines on bi-coupler, tri-coupler,
  etc.. This option should be disable-able.
