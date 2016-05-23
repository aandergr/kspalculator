# kspalculator

**kspalculator** is a tool which determines the **best** rocket propulsion designs for one stage of a rocket,
given a set of **constraints** and **preferences**.

*Constraints* are properties of the spacecraft which have to be fulfilled. These are the possible payload and the
Delta-v as well as the minimum acceleration which is reached in an environment with given air pressure.
*Preferences* are further properties a propulsion design might fulfil in order to be preferred. Examples for
preferences are the thrust vectoring angle, the radial size, whether the engine is able to generate electric
power, etc.

Which is the *best* design depends heavily on the specific application. A design might be better than another one,
if it is cheaper or has a lower mass, but it might also be considered better if it is buildable using less
technology or if it better fulfills some of the given preferences. Obviously, it is impossible to sort all
propulsion designs by their "goodness", so there might be more than one which is the best at least by some
criteria. This tool presents exactly *all* best designs.

## Features

kspalculator evaluates all possible designs, checks whether they fulfil the user's requirements, and then checks
whether it is the best design using the relation "*A* is better than *B* iff *A* is better than *B* by *any* of
the user's criteria". Only the **best designs** are then presented to the user. This way, the user has maximum
flexibility to use the type of propulsion which serves best his needs.

The stage might have different requirements for minimum acceleration for **different _flight phases_** through
different air pressures and different Delta-v requirements. For example you might require the vessel accelerating
by 1000 m/s with an acceleration of 3 m/s², and later 500 m/s with an acceleration of 7 m/s².

Besides considering the **classic liquid fuel engines** as well as **solid fuel boosters**, kspalculator also
considers using the **LV-N Nerv Atomic Rocket Motor**, the **IX-6315 Dawn Electric Propulsion** and the
**O-10 Puff MonoPropellant Engine**.

Considered criterias to decide whether a design is better than another one are
 * Mass,
 * Cost,
 * Whether it is buildable with easier available technology,
 * Whether gimbal is available, or Thrust Vectoring Range,
 * Whether it uses MonoPropellant as fuel, which is also used by Reaction Control System (RCS) thrusters,
 * Whether its engine generates electric power,
 * The length of the engine, as might be meaningful when building landers,
 * Whether it meets user's radial size preference.

Even though calculating this sounds highly sophisticated, the best designs are presented to the user usually within
**less than a second**. The information shown about each design include a detailed listing of the **performance
characteristics**, i.e. the **actually reachable Delta-v** (which might be slightly more than required, because of
rounding to tank sizes), the **acceleration at full thrust** as well as the **mass** at beginning and end of each
*flight phase*.

(By the way, we are talking about Kerbal Space Program, Version 1.1.2)
