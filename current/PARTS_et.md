# Osade nimekiri ja kust osta (lamp v5)

Hinnad on ligikaudsed (oktoober 2026), käibemaksuga. Enamik osi tuleb AliExpressist, LED-draiverid
Euroopa edasimüüjalt. Ingliskeelne versioon: [`PARTS.md`](PARTS.md).

**Kokku: umbes 75–110 €** Mean Welli draiveritega või **umbes 60–90 €** PT4115 draiveritega. Lisaks
saatmiskulu ja umbes 6 € filamenti.

| Osa | Tk | Umbes € | Kust |
|---|---|---|---|
| LED 16 mm vaskplaadil: Luminus SST-20 (või Cree XM-L2), 3 V, 4000–5000 K | 3 | 10–12 | AliExpressi taskulambipoed (Convoy, Simon's, Kaidomain). Suvalised „Cree“ pakkumised on sageli võltsid. |
| 20 mm TIR-optika 16 mm plaadile: 1 × 10°, 2 × 25° | 3 | 4–6 | samad poed. Originaal Carclo / Fusion Optix: 3–5 € tükk (Mouser, LEDSupply). |
| Ribidega alumiiniumradiaator, 25 mm lai, lõigatud 64 mm pikkuseks, kuni 20 mm sügav | 1 | 3–6 | AliExpress („aluminium heatsink 100 × 25 × 20“) |
| Mean Well **LDD-1500L** LED-draiver | 3 | 18–24 | Farnell, Mouser, TME või Itaalia poed, näiteks alimentatorishop. **Tootmisest maas, vt allpool.** |
| ESP32-C3 SuperMini | 1 | 2–4 | AliExpress; kiiremini Partco (FI) või Oomipood (EE) |
| MPU-6050 (GY-521) | 1 | 2–3 | AliExpress |
| VL53L1X moodul (13 × 18 mm) | 1 | 4–8 | AliExpress |
| MG90S metallhammasratastega servo | 1 | 3–4 | AliExpress |
| MP1584EN pingemuundur (5 tk pakk) | 1 | 2–3 | AliExpress |
| MOSFET-moodul (D4184 / AO3400) | 1 | 1–2 | AliExpress |
| 5 V valge LED-riba, 2835, 120 LEDi/m | 1 m | 2–3 | AliExpress |
| GL5528 fototakisti, 10 k NTC (B3950), takistid 10 k ×3 ja 47 k | | 2–4 | AliExpressi komplektid või koos draiverite tellimusega |
| JST-XH 2-pin pistikud, 26 AWG silikoonjuhe | | 5–7 | AliExpress |
| Soojusjuhtiv liim (LED-plaadid radiaatorile) | | 3–5 | AliExpress |
| M4 sissesulatatavad keermehülsid (5,7 × 5,6 mm), M2/M3 kruvide komplekt | | 6–8 | AliExpress |
| PETG või ASA, umbes 250 g | | 5–7 | 3DJake, Prusa pood või kohalik pood |

## LED-draiverid

Mean Well LDD-1500L ei ole enam tootmises. Farnellil ja mõnel poel on neid veel laos, umbes 6 € tükk.

- **Variant 1: osta kolm LDD-1500L, kuni neid veel saab.** Lamp on just nende jaoks tehtud: 1,5 A LEDi
  kohta, umbes 1200 lm.
- **Variant 2: kolm PT4115 LED-draiveri moodulit** (AliExpress, 1–2 € tükk, sisend 6–30 V, DIM-viiguga).
  Need annavad kuni umbes 1,2 A, nii et lamp annab umbes 1000 lm. Mahuvad samasse elektroonikakarpi ja
  püsivara ei pea muutma: ühenda nende DIM-viigud GPIO5 külge nagu Mean Welli omadel.

Ära kasuta Mean Welli soovitatud asendajat (NLDD-H). See vajab kõrgemat sisendpinget ega tööta ratta
6,5 V hämarrežiimis.

## Tellimise nõuanded

- **Miinimumtellimus:** Farnell, Mouser ja TME saadavad kiiresti Soome ja Eestisse ning sageli tasuta, kui
  tellimus ületab teatud summa. Selleni jõudmiseks lisa draiverite tellimusse takistid, NTC, fototakisti ja
  pistikud.
- **Käibemaks:** AliExpressi alla 150 € tellimustel lisatakse käibemaks juba ostul, nii et kättesaamisel
  midagi juurde maksta ei tule.
- **Tarne:** AliExpressist tuleb kaup 1–3 nädalaga. Partco (partco.fi) ja Oomipood (oomipood.ee) on
  tavaliste moodulite puhul kiiremad. Kontrolli enne laoseisu.
