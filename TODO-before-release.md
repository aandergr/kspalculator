**Things which should be done before releasing this software, in order of
their priority.**

* Review and test IsBest algorithm.

* Verify parts.py correctness for current KSP version

* Documentation and User Interface.
 * Write good README.md with examples.
 * Let kspalculator.py print all constraints for double-checking, unless
   --quiet option is given.
 * Rework --help.
 * Check validity of given options.

* One more time: Test and review code.

**Scheduled for later (after first release):**

* Consider adapters between different radial sizes.
 * There should be an option for upper radial size.
 * There should be an option for not using smaller sizes than upper
   radial size.
 * There should be an option to disable usage of adapters (but still
   changing size, as preferrence of keeping size can be expressed using
   --preferred-size option)

* Consider mounting multiple small engines on bi-coupler, tri-coupler,
  etc.. This option should be disable-able.
