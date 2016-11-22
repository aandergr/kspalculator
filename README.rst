kspalculator
============

**kspalculator** is a tool which determines the **best** rocket
propulsion designs for one stage of a rocket, given a set of
**constraints** and **preferences**.

*Constraints* are properties of the spacecraft which have to be
fulfilled. These are the possible payload and the Delta-v as well as the
minimum acceleration which is reached in an environment with given air
pressure. *Preferences* are further properties a propulsion design might
fulfil in order to be preferred. Examples for preferences are the thrust
vectoring angle, the radial size, whether the engine is able to generate
electric power, etc.

Which is the *best* design depends heavily on the specific application.
A design might be better than another one, if it is cheaper or has a
lower mass, but it might also be considered better if it is buildable
using less technology or if it better fulfills some of the given
preferences. Obviously, it is impossible to sort all propulsion designs
by their "goodness", so there might be more than one which is the best
at least by some criteria. This tool presents exactly *all* best
designs.

There is an official web frontend for kspalculator at:
https://kspalculator.appspot.com/.

Features
--------

kspalculator evaluates all possible designs, checks whether they fulfil
the user's requirements, and then checks whether it is the best design
using the relation "*A* is better than *B* iff *A* is better than *B* by
*any* of the user's criteria". Only the **best designs** are then
presented to the user. This way, the user has maximum flexibility to use
the type of propulsion which serves best his needs, still without being
spammed by non-optimal solutions.

The stage might have different requirements for minimum acceleration for
**different *flight phases*** through different air pressures and
different Delta-v requirements. For example you might require the vessel
accelerating by 1000 m/s with an acceleration of 3 m/s², and later 500
m/s with an acceleration of 7 m/s².

Besides considering the **classic liquid fuel engines** as well as
**solid fuel boosters**, kspalculator also considers using the **LV-N
Nerv Atomic Rocket Motor**, the **IX-6315 Dawn Electric Propulsion** and
the **O-10 Puff MonoPropellant Engine**.

Considered criteria to decide whether a design is better than another
one are

- Mass,
- Cost,
- Whether it is buildable with easier
  available technology,
- Whether gimbal (thrust vectoring) is available,
  or Thrust Vectoring Range,
- Whether it uses MonoPropellant as fuel,
  which is also used by Reaction Control System (RCS) thrusters,
- Whether its engine generates electric power,
- The length of the
  engine, as might be meaningful when building landers,
- Whether it
  meets user's radial size preference.

Even though calculating this sounds highly sophisticated, the best
designs are presented to the user usually within **less than a second**.
The information shown about each design includes a detailed listing of
the **performance characteristics**, i.e. the **actually reachable
Delta-v** (which might be slightly more than required, because of
rounding to tank sizes), the **acceleration at full thrust** as well as
the **mass** at beginning and end of each *flight phase*.

(By the way, we are talking about Kerbal Space Program, version 1.2.1)

Usage
-----

GUI
~~~

There is an official web frontend for kspalculator at:
https://kspalculator.appspot.com/.

Here we explain how to use the kspalculator command line tool, but the
basic concepts don't vary.

Installation
~~~~~~~~~~~~

Make sure you have `Python <https://www.python.org/>`__, at least
version 3.4 installed. Fetch the most recent version of kspalculator at
https://github.com/aandergr/kspalculator/releases. Installation is then
done by unzipping the archive and calling

::

    python3 setup.py install

Basic Usage
~~~~~~~~~~~

kspalculator is invoked on the command line. Syntax is

::

    kspalculator [--boosters] [--cost] [preferences] <payload> <Delta-v[:acceleration[:pressure]] [...]>

where ``payload`` is the payload in kg and
``Delta-v[:acceleration[:pressure]]`` are tuples of required Delta-v in
m/s, acceleration in m/s² and environment pressure in ATM (0.0 = vacuum,
1.0 = kerbin sea level pressure) for each flight phase. You have to
specify at least one of these tuples. Acceleration and pressure are
optional and default to zero.

If you add ``--bosters``, kspalculator will consider adding solid fuel
boosters. This is very useful for launcher stages.

Options for ``preferences`` are:

- ``--preferred-radius {tiny,small,large,extralarge}``: Preferred radius
  of the stage. Tiny = 0.625 m, Small = 1.25 m, Large = 2.5 m (Rockomax),
  ExtraLarge = 3.75 m (Kerbodyne),
- ``--electricity``: Prefer engines
  generating electricity,
- ``--length`` or ``--lander``: Prefer engines
  which are short or radially mounted,
- ``--gimbal``: Prefer engines
  having gimbal. If you specify this option twice, a higher gimbal range
  is considered better.
- ``--rcs`` or ``--monopropellant``: Prefer
  engines using RCS fuel (monopropellant), i.e. prefer the O-10 Puff
  engine.

In contrast to the constraints, preferences aren't hard requirements for
a design suggestion to be shown up. Adding preferences only adds
criteria under which designs may be considered better than others. This
means, specifying more preferences, *more* designs will be suggested.

If you specify ``--cost``, results will be sorted by their cost instead
of their mass.

For a brief reference for options, call ``kspalculator --help``. To
display the version of the tool as well as the corresponding version of
Kerbal Space Program, call ``kspalculator --version``.

Note that kspalculator calculates optimal designs for one stage only (or
two if you allow boosters, where the first is a stage only utilizing
solid fuel boosters). It will never split up your design into multiple
stages.

Example
~~~~~~~

Imagine we build a light Mun lander, having a payload of 1320 kg. That
is a Mk1 Command Pod, four LT-05 Landing Struts, a Parachute, a Heat
Shield, a Stack Decoupler and Solar Panels. We want to have two stages:
the upper one flying from Low Kerbin Orbit to Mun, landing there, and
then flying back to Kerbin; and the lower one launching the lander stage
from Kerbin Space Center to Low Kerbin Orbit.

After having determined the payload of the stage, we need to figure out
Delta-v requirements, acceleration requirements and air pressure at the
different flight phases.

In this case air pressure is easy: As the Mun does not have any
atmosphere and the stage starts its way already being in orbit, it is
clear that the lander will be designed to fly through vacuum only.

Needed Delta-v can be easily read at Delta-v maps or calculated by
calculation tools found in the internet (see links section later in this
document). We find out, that we need 1170 m/s from Low Kerbin Orbit to
Low Mun Orbit, then 580 m/s for landing at Mun, 580 m/s for starting at
Mun and later 310 m/s for returning to Kerbin. Additionally, in this
example we want to have 700 m/s Delta-v as a reserve.

Now let's think about acceleration. As we land and start on Mun, we
indeed have constraints regarding minimum acceleration, because we need
to counteract Mun's gravity. In this example, we want to have at least
2\ *g* = 3.3 m/s² acceleration when starting to land at Mun (i.e. when
having reached Low Mun Orbit), and 3\ *g* = 5.0 m/s² to launch at Mun,
*g* being Mun's surface gravity, which is about 1.65 m/s² as can be
found out in the in-game knowledge base.

Do we have any preferences? Yes we do. We're building a lander utilizing
LT-05 Micro Landing Struts, which are quite bad, so it would be nice to
prefer engines which have a short length. Thus, we add ``--length`` flag
to kspalculator invocation. Additionally, our Payload has radial size
*small*, so it would be cool if the propulsion system also had this
radius. We add ``-R small``. Note that adding preferences does *not*
prevent the listing of solutions which do not meet these preferences,
i.e. adding preferences always leads to more output.

Doing so, we get:

::

    $ kspalculator 1320 -R small --length 1170 580:3.3 580:5.0 310 700
    48-7S Spark
        Total Mass: 6145 kg (including payload and full tanks)
        Cost: 1670
        Liquid fuel: 840 units (4725 kg full tank mass)
        Requires: PropulsionSystems
        Radial size: Tiny
        Gimbal: 3.0 °
        Engine is short enough to be used with LT-05 Micro Landing Struts
        Performance:
        [...]

    LV-909 Terrier
        Total Mass: 6320 kg (including payload and full tanks)
        Cost: 1190
        Liquid fuel: 800 units (4500 kg full tank mass)
        Requires: AdvancedRocketry
        Radial size: Small
        Gimbal: 4.0 °
        Engine is short enough to be used with LT-05 Micro Landing Struts
        Performance:
          1:  1170 m/s @ vacuum     9.49 m/s² - 13.42 m/s²    6.3 t -   4.5 t
          2:   580 m/s @ vacuum    13.42 m/s² - 15.92 m/s²    4.5 t -   3.8 t
          3:   580 m/s @ vacuum    15.92 m/s² - 18.90 m/s²    3.8 t -   3.2 t
          4:   310 m/s @ vacuum    18.90 m/s² - 20.72 m/s²    3.2 t -   2.9 t
          5:   700 m/s @ vacuum    20.72 m/s² - 25.48 m/s²    2.9 t -   2.4 t
          6:    51 m/s @ vacuum    25.48 m/s² - 25.86 m/s²    2.4 t -   2.3 t

    [...]

    LV-T30 Reliant
        Total Mass: 11008 kg (including payload and full tanks)
        Cost: 2825
        Liquid fuel: 1500 units (8438 kg full tank mass)
        Requires: GeneralRocketry
        Radial size: Small
        Engine generates electricity
        Engine is short enough to be used with LT-2 Landing Struts
        Performance:
        [...]

    [...]

(Output was shortened)

Of the suggested designs, all are the best by some criteria. The first
one, using Spark engine, is the one having the lowest total mass, but in
this example we do not want to use it, for example because we did not
research "Propulsion Systems" yet. We choose the Terrier design as we
think it serves best our needs. Note that the tool also suggests the
Reliant because of lower technology requirements, as well as some other
nice designs which we skipped in this document to save space.

Now build the stage adding the 800 Unit Fuel Tank and the Terrier engine
under your payload. Then add a stack decoupler (which weights 50 kg) as
we're building the launcher stage.

The payload for the launcher stage is 6370 kg (i.e. the lander stage
plus 50 kg stack decoupler). Safe Delta-v and acceleration requirements
for a launch to Low Kerbin Orbit have been found out to be 905 m/s with
13 m/s² at 1 ATM and then 3650 m/s with 13 m/s² at 0.18 ATM.

We want to use solid fuel boosters for the launch, so we add
``--boosters``. Additionally, we prefer engines with thrust vectoring as
it may be helpful to counteract turbulences during launch, so we add
``--gimbal``. *Small* is still our preferred radial size. Now we
determine best launcher designs:

::

    $ kspalculator 6370 --boosters --gimbal -R small 905:13:1 3650:13:0.18
    RE-I5 Skipper
        Total Mass: 89320 kg (including payload and full tanks)
        Cost: 18258
        Liquid fuel: 5600 units (31500 kg full tank mass)
        Requires: HeavyRocketry
        Radial size: Large
        Gimbal: 2.0 °
        Engine generates electricity
        Radially attached 2 * S1 Kickback SFB
        SFBs mounted on TT-70 Radial Decoupler, Advanced Nose Cone, 2 * EAS-4 Strut Connector each
        Performance:
         *1:   905 m/s @ 1.00 atm  13.30 m/s² - 21.35 m/s²   89.3 t -  55.6 t
         *2:   213 m/s @ 0.18 atm  23.59 m/s² - 26.08 m/s²   55.6 t -  50.3 t
          3:  3437 m/s @ 0.18 atm  15.55 m/s² - 47.68 m/s²   40.9 t -  13.3 t
          4:   107 m/s @ 0.18 atm  47.68 m/s² - 49.37 m/s²   13.3 t -  12.9 t

    4 * Mk-55 Thud, radially mounted
        Total Mass: 108520 kg (including payload and full tanks)
        Cost: 19467
        Liquid fuel: 4600 units (25875 kg full tank mass)
        Requires: HeavyRocketry
        Radial size: Small
        Gimbal: 8.0 °
        Engine is short enough to be used with LT-05 Micro Landing Struts
        Radially attached 3 * S1 Kickback SFB
        SFBs mounted on TT-70 Radial Decoupler, Advanced Nose Cone, 2 * EAS-4 Strut Connector each
        You might limit SFB thrust to 79.5 %
        Performance:
         *1:   905 m/s @ 1.00 atm  16.42 m/s² - 26.35 m/s²  108.5 t -  67.6 t
         *2:   637 m/s @ 0.18 atm  29.12 m/s² - 39.36 m/s²   67.6 t -  50.0 t
          3:  3013 m/s @ 0.18 atm  13.15 m/s² - 36.68 m/s²   35.8 t -  12.9 t
          4:     2 m/s @ 0.18 atm  36.68 m/s² - 36.71 m/s²   12.9 t -  12.8 t

    [...]

(Output was shortened)

The asterisks in the performance tables indicate that the phase of
flight is done by solid fuel boosters. The SFB thrust limit suggestion
is the minimum thrust required to fulfil your acceleration constraints.

Now build one of the launchers being suggested by kspalculator and we're
ready to do a giant leap for kerbinkind.

Helpful Links
-------------

Official web frontend for kspalculator:
https://kspalculator.appspot.com/.

Nice cheat sheet, especially containing maps with required Delta-v:
http://wiki.kerbalspaceprogram.com/wiki/Cheat\_sheet

There is a `thread in the Kerbal Space Program
forums <http://forum.kerbalspaceprogram.com/index.php?/topic/140434-kspalculator-determine-best-rocket-propulsion-designs-ie-engine-and-fuel-quantity-for-given-constraints/>`__
about kspalculator.

In case you find any problems or have suggestions, please help us
improving this tool by reporting them at:
https://github.com/aandergr/kspalculator/issues
