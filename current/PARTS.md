# Parts list and where to buy (lamp v5.2)

Prices are rough estimates (October 2026), VAT included. Most parts come from AliExpress; the LED drivers
come from a European distributor. Estonian version: [`PARTS_et.md`](PARTS_et.md).

**Total: about €80–120** with the Mean Well drivers, or **about €65–100** with PT4115 drivers. Add shipping;
the filament is already in the list.

| Part | Qty | Approx. € | Where |
|---|---|---|---|
| LED on a 16 mm copper star: Luminus SST-20 (or Cree XM-L2), 3 V, 4000–5000 K | 3 | 10–12 | AliExpress flashlight shops (Convoy, Simon's, Kaidomain). Random "Cree" listings are often fakes. |
| 20 mm TIR optic for a 16 mm star: 1 × 10° round, 2 × elliptical (wide) | 3 | 5–10 | the same shops. Genuine Carclo / Fusion Optix: €3–5 each (Mouser, LEDSupply). |
| Finned aluminium heat-sink bar, 25 mm wide, cut to 64 mm, no deeper than 20 mm | 1 | 3–6 | AliExpress ("aluminium heatsink 100 × 25 × 20") |
| Mean Well **LDD-1500L** LED driver | 3 | 18–24 | Farnell, Mouser, TME, or Italian shops such as alimentatorishop. **Discontinued: see below.** |
| ESP32-C3 SuperMini | 1 | 2–4 | AliExpress; Partco (FI) or Oomipood (EE) for faster delivery |
| MPU-6050 (GY-521) | 1 | 2–3 | AliExpress |
| VL53L1X module (13 × 18 mm) | 1 | 4–8 | AliExpress |
| MG90S metal-gear servo | 1 | 3–4 | AliExpress |
| MP1584EN buck module (pack of 5) | 1 | 2–3 | AliExpress |
| Logic-level MOSFET module (D4184 / AO3400) | 1 | 1–2 | AliExpress |
| 5 V white LED strip, 2835, 120 LEDs/m | 1 m | 2–3 | AliExpress |
| GL5528 LDR, 10 k NTC (B3950), resistors 10 k ×3 and 47 k | | 2–4 | AliExpress assortments, or with the driver order |
| JST-XH 2-pin plugs, 26 AWG silicone wire | | 5–7 | AliExpress |
| Thermal adhesive (stars to the heat sink) | | 3–5 | AliExpress |
| M4 heat-set inserts (5.7 × 5.6 mm), M2/M3 screw assortment | | 6–8 | AliExpress |
| PETG or ASA, about 250 g | | 5–7 | 3DJake, Prusa store, or a local shop |
| Clear polycarbonate sheet 1.5 mm (A5 is plenty), thin double-sided foam tape | | 5–9 | hardware or plastics shop, or AliExpress |

## The LED drivers

The Mean Well LDD-1500L is discontinued. Farnell and a few shops still have stock, at about €6 each.

- **Option 1: buy three LDD-1500L while they last.** This is what the lamp is designed for: 1.5 A per LED,
  about 1200 lm.
- **Option 2: three PT4115 LED driver modules** (AliExpress, €1–2 each, 6–30 V in, with a dim pin). They give
  up to about 1.2 A, so the lamp makes about 1000 lm. They fit in the same electronics box and need no firmware
  change: wire their DIM pins to GPIO5, as with the Mean Well drivers.

Don't use Mean Well's suggested replacement (NLDD-H). It needs a higher input voltage and won't work in the
wheel's 6.5 V dim mode.

## Ordering tips

- **Minimum orders:** Farnell, Mouser and TME ship quickly to Finland and Estonia, and often ship free above a
  minimum order. To get there, add the resistors, NTC, LDR and connectors to the driver order.
- **VAT:** AliExpress orders under €150 have VAT added at checkout, so there's nothing extra to pay on delivery.
- **Delivery:** AliExpress takes 1–3 weeks. Partco (partco.fi) and Oomipood (oomipood.ee) are quicker for the
  common modules. Check their stock first.
