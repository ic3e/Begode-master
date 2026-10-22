# Measurements taken on the wheel

Owner's caliper measurements. They are the basis of `source/master_model2.py` and everything from v10 on.
Positions are in the handle STL frame: −X forward, +Y up, Z across, centre Z = −70.5. The handle's bolt
holes on the black controller block are at X 0 / Y 12 and X 0 / Y 0 (M4), and X −2 / Y −13.2 (Ø4.9, the
lowest hole).

## Front of the wheel

| What | Measured | → STL frame |
|---|---|---|
| Hole spacings on the block | 11.5 and 13.5 (edge to edge) | matches the STL (12.0 and 13.2 centre to centre) |
| Lowest hole → front face of the black block | 7.3 | block face X −9.3 |
| Block face → stock lamp face | 50.3 | X −59.6 |
| Block face → front tip of the top cover | 52.8 | X −62.1 |
| Block face → front edge of the shells | 58.7 | X −68.0 |
| Stock lamp underside below the lowest hole | 7.5 | Y −20.7 |
| Shell top at its front corner | 3 above the lamp underside (the top slopes) | Y −17.7 |
| Lowest hole → shell top straight below it | 24.9 | Y −38.1 |
| Shells move with the suspension? | no | |

## The bay between the shells (under the lamp)

| What | Measured |
|---|---|
| Width between the shells | 95 |
| Depth from the front edge to the motor cable | 50 (the cable can't be moved) |
| Lamp underside → cross plate over the tyre | 77 (71 at another spot) |
| Same, suspension bottomed out | 37 left |

## Stock lamp opening (stock lamp removed)

| What | Measured |
|---|---|
| Width, inside | 134 |
| Height at the front and at the back | 36.8 |
| Depth, cover front edge → back wall | 49.3 |
| Lowest hole → top of the opening | 39.1 |
| Fixing | 2 × M4 down through the top of the cover; the stock lamp's end brackets went to the two M4 holes on the block |
| The two top screw holes | 60.8 apart, 32.8 behind the cover's front edge, 37.2 from the cover's side edge |
| Stock lamp width over its brackets | 141.5 |

## Electrical (as reported, not measured)

The wheel's lamp plug gives about 6.5 V in dim mode and 12 V at full, about 20 W, and gets brighter
when accelerating. Measure it once before trusting the voltage divider in the firmware.

The sheets `measurements_needed.png` and `measurements_lamp_space.png` show where each one was taken.
