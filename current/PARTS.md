# Parts list and where to buy (lamp v6.4)

Prices are rough estimates (October 2026), VAT included. Most parts come from AliExpress; the LED drivers
come from a European distributor.

**Total: about €115–170** with the Mean Well drivers, or **about €100–150** with PT4115 drivers. The USB charger and
the buttons are about €20–30 of that, the road sensor about €12–15. Add shipping;
the filament is already in the list.

| Part | Qty | Approx. € | Where |
|---|---|---|---|
| LED on a 16 mm copper star: Luminus SST-20 (or Cree XM-L2), 3 V, 4000–5000 K | 3 | 10–12 | AliExpress flashlight shops (Convoy, Simon's, Kaidomain). Random "Cree" listings are often fakes. |
| 20 mm TIR optic for a 16 mm star: 1 × 10° round, 2 × elliptical (wide) | 3 | 5–10 | the same shops. Genuine Carclo / Fusion Optix: €3–5 each (Mouser, LEDSupply). |
| Finned aluminium heat-sink bar, 25 mm wide, cut to 64 mm, no deeper than 20 mm | 1 | 3–6 | AliExpress ("aluminium heatsink 100 × 25 × 20") |
| Mean Well **LDD-1500L** LED driver | 3 | 18–24 | Farnell, Mouser, TME, or Italian shops such as alimentatorishop. **Discontinued: see below.** |
| ESP32-C3 SuperMini | 1 | 2–4 | AliExpress (Partco doesn't stock it) |
| MPU-6050 (GY-521) | 1 | 2–3 | AliExpress |
| VL53L1X laser distance sensor, **Pololu carrier #3415** (12.7 × 17.8 mm) | 1 | 12–15 | Pololu distributors (Botland, Kiwi Electronics, Robotshop). The hood is sized for this board; other VL53L1X boards differ |
| INA219 module (0.1 Ω shunt) | 1 | 1–3 | AliExpress |
| MG90S metal-gear servo | 1 | 3–4 | AliExpress |
| 6800-2RS ball bearing, 10 × 19 × 5 mm, sealed | 1 | 1–3 | AliExpress (packs of 2–10) |
| MP1584EN buck module (pack of 5; you need 2) | 1 | 2–3 | AliExpress |
| Small logic-level MOSFET module (AO3400 type), at most 18 × 11 × 4 mm | 2 | 2–4 | AliExpress ("AO3400 MOSFET module"). The D4184 boards with screw terminals are too big |
| 8 mm sealed momentary push button, IP67, flat head | 2 | 3–6 | AliExpress ("8mm waterproof momentary push button") |
| C&K KSC6 sealed tact switch, IP67, 6.2 × 6.2 mm, hard actuator (e.g. KSC621J LFS) | 2 | 2–4 | Farnell, Mouser, TME (with the driver order). The riding buttons on the handle |
| USB-C female receptacle with CC1/CC2 brought out (6-pin, solder tabs or a small board up to 13 × 8 mm), and a silicone USB-C dust plug | 1 + 1 | 1–3 | AliExpress ("USB-C female 6 pin", "USB-C silicone dust plug"). Not a "charging-in" board with 5.1 k resistors fitted, or remove them |
| 2-core 24 AWG silicone wire (about 40 cm), three 28 AWG wires (about 40 cm), 2-part epoxy, CA glue | | 4–7 | AliExpress or a hardware shop |
| 5 V white LED strip, 2835, 120 LEDs/m | 1 m | 2–3 | AliExpress |
| GL5528 LDR, 10 k NTC (B3950), resistors 10 k ×2 and 22 k ×2 | | 2–4 | AliExpress assortments, or with the driver order |
| JST-XH 2-pin plugs, 26 AWG silicone wire | | 5–7 | AliExpress |
| Thermal adhesive (stars to the heat sink) | | 3–5 | AliExpress |
| M4 heat-set inserts (5.7 × 5.6 mm), M2/M3 screw assortment, 4 × M3 × 10 countersunk | | 6–8 | AliExpress |
| PETG or ASA, about 250 g | | 5–7 | 3DJake, Prusa store, or a local shop |
| Neutral-cure clear silicone, 2 rubber grommets (6 mm hole), conformal coating spray | | 12–18 | hardware shop; coating: Partco, AliExpress |
| Clear polycarbonate sheet 1.5 mm (A5 is plenty), thin double-sided foam tape | | 5–9 | hardware or plastics shop, or AliExpress |

## The LED drivers

The Mean Well LDD-1500L is discontinued. Farnell and a few shops still have stock, at about €6 each.

- **Option 1: buy three LDD-1500L while they last.** This is what the lamp is designed for: 1.5 A per LED,
  about 1200 lm.
- **Option 2: three PT4115 LED driver modules** (AliExpress, €1–2 each, 6–30 V in, with a dim pin). They give
  up to about 1.2 A, so the lamp makes about 1000 lm. They fit in the same electronics box and need no firmware
  change: wire their DIM pins to GPIO5, as with the Mean Well drivers.
- **Option 3: three Mean Well LDD-1000L** (Partco stocks them, about €8.50 each). Same fit and wiring, 1 A per
  LED, about 850–900 lm. At 1 A the lamp is well inside the wheel's power, so 100 % brightness is fine.

Don't use Mean Well's suggested replacement (NLDD-H). It needs a higher input voltage and won't work in the
wheel's 6.5 V dim mode.

## Ordering tips

- **Minimum orders:** Farnell, Mouser and TME ship quickly to Finland and Estonia, and often ship free above a
  minimum order. To get there, add the resistors, NTC, LDR, connectors and the KSC6 switches to the driver order.
- **VAT:** AliExpress orders under €150 have VAT added at checkout, so there's nothing extra to pay on delivery.
- **Delivery:** AliExpress takes 1–3 weeks. Partco (partco.fi) and Oomipood (oomipood.ee) are quicker for the
  common modules. Check their stock first.
