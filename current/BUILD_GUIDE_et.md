# Lamp v5: kolme LEDiga isetasandav esituli originaallambi avas

Originaallamp võetakse välja ja see lamp istub tasapinnaliselt selle avasse pealmises kattes. Topsihoidjat
enam ei ole. Ingliskeelne versioon: [`BUILD_GUIDE.md`](BUILD_GUIDE.md).

- **Valgus:** kolm LEDi ja optikat reas: keskel kitsas optika kaugeks valguseks, külgedel kaks laia.
- **Tasandamine:** kõik kolm on ühel ribidega jahutusradiaatoril, mida servo kallutab ±10°. Nii püsib
  valgusvihk paigal, kui ratas pidurdamisel, kiirendamisel, löökaukudes ja mägedes kaldub. Teeandur,
  güroskoop, päevatuled, päeva/öö ümberlülitus ja telefoni seadete leht töötavad nagu varem.
- **Heledus:** umbes **1200 lm** vaikimisi 90 % juures, umbes 2,5 korda heledam kui ühe LEDiga v4.
- **Elektroonika:** see on karbis, mis ripub külgkatete vahele, ja selle kaas on all. Elektroonikale pääseb
  ligi lampi välja võtmata.
- **Kinnitus:** lampi hoiavad katte kaks originaalset M4 kruvi ja kaks tugiriba, mis ulatuvad käepideme
  kõrvadeni.

Kõik on kontrollitud ratta mudeli järgi, mis on tehtud sinu nihikuga mõõdetud mõõtude põhjal
(`../reference/MEASUREMENTS.md`).

## Ostetavad osad

Hinnad ja poed: [`PARTS_et.md`](PARTS_et.md).

| Osa | Tk | Märkus |
|---|---|---|
| Luminus SST-20 (või Cree XM-L2 / XP-L), 3 V, **16 mm** vaskplaadil | 3 | 4000–5000 K |
| 20 mm TIR-optika 16 mm plaadile | 3 | 1 × 10° (keskele, kaugele), 2 × 25° (külgedele, laiale) |
| Ribidega alumiiniumradiaator | 1 | lame pind **64 × 25 mm**, kuni 20 mm sügav, ribid eest taha. Lõika profiilist. |
| Mean Well LDD-1500L | 3 | üks iga LEDi kohta; töötab ka ratta 6,5 V hämarrežiimis |
| ESP32-C3 SuperMini | 1 | |
| MPU-6050 (GY-521) | 1 | |
| VL53L1X moodul (13 × 18 mm) | 1 | teeandur |
| MG90S metallhammasratastega servo | 1 | |
| MP1584EN pingemuundur, seatud 5,0 V peale | 1 | |
| MOSFET-moodul (D4184 / AO3400) | 1 | päevatuled |
| 5 V valge LED-riba, 2835, 120/m | umbes 14 LEDi | päevatuled |
| GL5528 fototakisti + 10 k; 10 k NTC (B3950) + 10 k; 47 k + 10 k | | valgusandur, radiaatori temperatuur, ratta pinge |
| Ratta lambipistikuga sobiv pistik (originaal: kollane JST-XH, 2-pin) | 1 | |
| 26 AWG silikoonjuhe | | 8 juhet läbi õõnsa pöördtihvti |

## Prinditavad osad (PETG või ASA, 4 seina)

| Fail | Tk | Kuidas |
|---|---|---|
| `stl/master_handle_v12.stl` | 1 | sinu käepide + kaks tugiriba taga. Külili, tugedega käepideme all |
| `stl/master_handle_top_cap_p2.stl` | 1 | sinu originaalkork |
| `stl/lamp5_housing.stl` | 1 | pealmine pind aluse vastas, nagu eksporditud |
| `stl/lamp5_head.stl` | 1 | avatud tagakülg aluse vastas, nagu eksporditud |
| `stl/lamp5_lid.stl` | 1 | välimine pind aluse vastas |
| `stl/lamp5_drl_diffuser_x2.stl` | 2 | valge või läbipaistev PETG, 100 % täide |

## Kinnitusvahendid

- **Lamp katte külge:** originaallambi 2 M4 kruvi, mis lähevad 2 **M4 sissesulatatavasse keermehülssi**
  (5,7 mm pikk, välisläbimõõt 5,6 mm). Sulata hülsid korpuse peal olevasse kahte puksi.
- **Lamp käepideme külge:** 2 × M3 × 10 isekeermestavat kruvi, altpoolt läbi käepideme tugiribade korpusesse.
- **Kaas:** 4 × M3 × 8 isekeermestavat kruvi.
- **Lambi sees:**
  - 3 × M3 × 8 isekeermestavat (radiaatori ribidesse)
  - 2 × M2 × 6 (servo hoob pea külge)
  - 2 × M2 × 8 (servo oma postide külge)

## Juhtmestik

```
ratta lambipistik + ──┬── LDD-1500L nr 1, 2, 3  VIN+
                      ├── MP1584 IN+
                      └── 47 k ── GPIO0 ── 10 k ── GND       (ratta pinge)
ratta lambipistik − ──── ühine maa
LDD nr n  LED+ / LED− ── LED nr n        (iga LED oma draiveril; LED− juhtmeid kokku ei ühenda)
LDD DIM nr 1 + 2 + 3 ── GPIO5            (kõik kolm koos)
MP1584 OUT 5,0 V ──┬── ESP32-C3 5V, servo punane, MOSFET-mooduli DC+ (→ mõlemad päevatule ribad)
ESP32 3V3 ──┬── MPU-6050 VCC, VL53L1X VIN
            ├── 10 k ── GPIO3 ── NTC ── GND (NTC liimitud radiaatori külge)
            └── fototakisti ── GPIO1 ── 10 k ── GND
GPIO6 SDA / GPIO7 SCL ── MPU-6050 ja VL53L1X      GPIO10 ── servo      GPIO4 ── MOSFET-moodul
```

**Võimsus:** kolm LEDi vaikimisi 90 % juures võtavad umbes 13 W. Päeval lisanduvad päevatuled umbes 3 W ja
ülejäänu umbes 1 W. See jääb ratta umbes 20 W lambiväljundi piiresse. Öösel lülituvad päevatuled
ääretuleks. Ära tõsta seadete lehel „Beam“ 100 % peale, kui sa pole pistikut mõõtnud ja see ei anna rohkem.

## Kokkupanek

1. **Pea:**
   - Liimi kolm LED-plaati soojusjuhtiva liimiga radiaatorile. Kitsas optika läheb keskele, kohakuti pea
     kolme avaga.
   - Liimi NTC radiaatori külge.
   - Lükka radiaator tagant pähe ja kinnita kolme M3 kruviga ribidesse.
   - Vii 6 LED-juhet ja 2 NTC juhet välja läbi õõnsa tihvti.
2. **Korpus,** tagurpidi:
   - Sulata kaks M4 hülssi pealmistesse puksidesse.
   - Pane pea tihvt vasakule laagrisse, servohoova puks paremale.
   - Kinnita servo oma kahele postile, splain hoovas.
   - Liimi hajutid sisse, LED-riba read nende taha.
   - Lükka fototakisti oma avasse, üleval paremal.
3. **Elektroonikakarp:** pane kolm LDD-1500L, ESP32, MPU-6050 (lapiti, X-nool ette), pingemuundur ja
   MOSFET-moodul vahtteibiga pea all olevasse karpi. Lükka teeanduri plaat oma pilusse karbi esiküljel oleva
   väikese tunneli taha. Selle ette ei tohi panna klaasi ega kilet.
4. **Rattasse:** lükka lamp altpoolt avasse ja keera katte kaks M4 kruvi hülssidesse.
5. **Käepide:** kinnita nagu tavaliselt, siis keera kaks M3 kruvi läbi tugiribade lambi sisse.
6. **Kaas:** kinnita 4 × M3. Elektroonikale pääsemiseks võta see igal ajal maha.
7. **Püsivara:**
   - Laadi `firmware/headlamp5_firmware/headlamp5_firmware.ino` (Arduino IDE, plaat *ESP32C3 Dev Module*,
     Pololu „VL53L1X“ teek).
   - Ühendu WiFi-ga **Headlamp-xxxx** (parool **masterlamp**), ava **192.168.4.1** ja vajuta „Calibrate“,
     kui ratas seisab püsti tasasel maal.
   - Sea suund (vaikimisi 2° tee alla) ja heledus.

## Mida ma kontrollisin (mõõdetud ratta järgi)

- **Sobivus:** korpus ja kaas ei puutu külgkatteid, pealmist katet, kontrollerit ega mootori kaablit.
- **Vedrustus:** kui vedrustus on täiesti kokku surutud, jääb kaane ja rehvi kohal oleva ristplaadi vahele 4,5 mm.
- **Pea:** see kallub ±10° ilma korpust või servot puudutamata (üleval 4–5 mm, all 6 mm ruumi). Läätsed
  jäävad kogu aeg katte esiserva kohale: kõige madalamas asendis on veel 2,3 mm varu.
- **Käepide:** käepide v12 ei puutu ratast ja selle tugiribad on lambi kruvipukside kohal.
- **Teeandur:** selle vaateväli on vaba ja see vaatab teed umbes 2,2 m ees.
- **Osad:** iga osa on üks terviklik tükk.
- **Püsivara:** see kompileerub asendus-Arduino-päistega. Päris riistvaral pole seda veel käivitatud.

## Hea teada

- **Soojus:** pea on poolkinnises avas. Õhk tuleb pea ümbert sisse, läheb läbi ribide ja väljub
  elektroonikakarbi tagaküljel olevatest piludest. Kui seisad paigal ja tuli põleb, keerab radiaatori andur
  valgust tagasi. See on normaalne.
- **Suund:** sea telefoni lehel (vt peamine README). Kruviga reguleerimist pole, pea teeb selle ise.
- **Pealmine kate:** lamp on selle külge kruvitud nagu originaallamp. Enne katte tõstmist keera kaks
  pealmist kruvi välja.
- **Mõõda pistik üks kord üle** enne esimest kasutamist, tuli põlemas (oodata võib umbes 6,5 V hämaras ja
  12 V täisrežiimis). Kui lehel näidatud pinge ei klapi, muuda püsivaras `VIN_DIVIDER`.
