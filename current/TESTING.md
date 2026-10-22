# Testing: does it work, and does it survive?

The model checks prove that the lamp fits, that it never touches the ground first in a fall, and that the
head's stops take the hit. They can't prove that the parts survive the shock, the vibration, the rain and
months of riding. Only riding and dropping a real one does. Work through this in order, and write everything
down: what broke, after how many drops, from what height, on what surface. That log is what turns a prototype
into something you could sell.

## Before you start

- [ ] Note the print settings (material, walls, infill, temperature) for every printed part in the log below.
- [ ] Note the bought parts' sources (which shop, which listing). A bad batch of servos or LEDs is a real
  finding.
- [ ] Measure the wheel's lamp plug with the light on: volts in dim and full mode, and the power the lamp draws
  (Wi-Fi page).
- [ ] Take photos of the lamp before the first test, so later damage is easy to spot.

## 1. On the bench (lamp powered from a 12 V supply)

- [ ] **Buttons:** every action in the guide's table works, and the blinks match.
- [ ] **Stillness lock:** move the lamp by hand while pressing: nothing should happen.
- [ ] **Levelling:** tilt the lamp slowly and quickly. The beam on a wall should stay put within about 1°,
  without buzzing or hunting.
- [ ] **Stops:** with the power off, push the head gently each way. It should stop on the stops, not in the
  servo.
- [ ] **Heat:** 1 hour, beam on at full, lamp standing still. Note the heat-sink temperature on the Wi-Fi page
  and when the beam starts turning itself down.
- [ ] **USB:** charge a phone with the beam on (night mode). The power on the Wi-Fi page should stay at or under
  the limit; the beam dims first, then the charger pauses.
- [ ] **Soak:** 4 hours of levelling with the lamp on a slowly rocking surface. Listen for the servo. Check it
  still centres afterwards.

## 2. Normal rides (aim for 300 km)

- [ ] The beam stays steady over bumps, on hills, braking and accelerating.
- [ ] No flicker, no LED dimmer than the others.
- [ ] After every 100 km: check for play at the head (wiggle it with the power off), loose screws, cracks at the
  screw bosses, and the window tape.

## 3. Rough roads

- [ ] Gravel, cobbles, kerbs (up and down).
- [ ] Afterwards: plugs seated? Wires through the pin intact? Running lights all lit?

## 4. Drops (start gentle, step up)

Let the wheel tip over from standing, about 10 times each way. Do every step on grass first, then on asphalt.

| Step | How | Each way |
|---|---|---|
| 1 | tip over from standing, onto the front | 10 × |
| 2 | onto the left side, then the right side | 10 × each |
| 3 | onto the back | 10 × |
| 4 | onto a front corner (left and right) | 10 × each |
| 5 | from walking speed (let it run away a metre and fall) | 5 × |

After each set:
- [ ] Does the head still swing freely and come back to level?
- [ ] Does the beam aim where it did before?
- [ ] Any cracks: corners of the electronics box, the top plate's tongues, the screw bosses, the handle's legs
  around the USB port?
- [ ] Any loose plugs, flickering LEDs, buttons that stick?
- [ ] Is the window still sealed?

Stop when something breaks. Fix it, note what and why, and start that step again.

## 5. Water, spray and sand (the sealing)

- [ ] **Bench spray:** lamp in the wheel, lid on. Spray the front with a garden hose (no nozzle jet) for 5 minutes,
  from the front and from below, as the tyre would. Then open the lid and the top plate: the electronics box,
  both side bays and the inside of the window must be dry. Water in the trap and the duct is expected.
- [ ] **Wet road:** ride on a wet road with puddles. Check the same places afterwards.
- [ ] **Sand:** ride a sandy or gravel path when it's wet. Afterwards rinse the chin and check that the drains run
  clear. Any sand in the dry spaces is a finding: note where.
- [ ] **Levelling without a road sensor:** on hills, is following them halfway right? Adjust "Follow long hills" on the Wi-Fi page if not.
- [ ] **Light output:** measure lux at 10 m on a wall (beam at 100 %) and note it. The lens gap costs some light;
  this is the real figure.

## 6. Rain and washing

- [ ] Ride in rain. Afterwards, open the lid: any water inside?
- [ ] Wash the wheel as you normally do (no pressure washer at the lamp).
- [ ] USB dust plug in: no water in the port. Also once without it (a short ride in light rain), then dry it and check a phone still charges.

## 7. Long term (a few months)

- [ ] Play in the bearing or the servo.
- [ ] Window clouding or scratching.
- [ ] Colour of the printed parts in the sun (ASA should hold up; PETG may fade).

## Log

| Date | Test | Surface / height | What happened | Fixed how |
|---|---|---|---|---|
| | | | | |
| | | | | |
| | | | | |

## What I'd expect to give out first

1. **Servo gears:** the stops should prevent this. If a servo still strips, a "servo saver" horn (a springy one)
   is the next step.
2. **LED stars coming off the heat sink:** watch for one LED going dim. Thermal epoxy holds better than
   thermal glue pads.
3. **Wires and solder joints on the modules:** silicone wire, strain relief and a dab of hot glue on the joints
   help.
4. **Printed corners and bosses:** more walls (5–6), slightly hotter printing for layer strength.
5. **Window:** polycarbonate is close to unbreakable. Watch the tape rather than the window.
