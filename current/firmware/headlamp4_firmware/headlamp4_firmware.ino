// Auto-levelling headlamp v4 for the Begode Master: built into the stock lamp opening (±10° head).
// ESP32-C3 SuperMini + MPU-6050 + VL53L1X road sensor + LDR + MG90S servo
// + Mean Well LDD-1500L (main beam; runs from 6 V) + MOSFET module (daytime running lights).
//
// Power comes from the wheel's lamp plug: about 6.5 V in the wheel's dim mode, 12 V at full, and the
// wheel raises it when accelerating. The lamp reads that voltage and scales the main beam with it,
// so the wheel's dim/full setting and its "brighter when accelerating" still work.
//
// Levelling:
//  - the road sensor looks 15° down at the road ~2 m ahead and works out how the road slopes
//    relative to the wheel; the beam is kept that much above the road (AIM below "level");
//  - the gyro fills in between road readings and cancels fast pitching (braking, bumps);
//  - when the road sensor has no reading (sun, rain, a kerb in the way) it falls back to the
//    gyro/accelerometer alone, which cancels fast pitching and follows hills halfway.
// Lights: day = DRL only; night = main beam + DRL dimmed. AUTO picks from the light sensor.
//
// Settings: join the Wi-Fi "Headlamp-xxxx" (password masterlamp) within 10 minutes of switching
// on, and open http://192.168.4.1
//
// Board: "ESP32C3 Dev Module", USB CDC On Boot: Enabled.
// Library: "VL53L1X" by Pololu (Library Manager). Everything else comes with the ESP32 core.

#include <cmath>
#include <Wire.h>
#include <Preferences.h>
#include <WiFi.h>
#include <WebServer.h>
#include <VL53L1X.h>

// ---------------- pins ----------------
const int PIN_SDA   = 6;
const int PIN_SCL   = 7;
const int PIN_SERVO = 10;
const int PIN_DIM   = 5;    // LDD-1500H DIM (PWM; 3.3 V is "on")
const int PIN_DRL   = 4;    // MOSFET module gate (PWM)
const int PIN_NTC   = 3;    // 10k NTC to GND, 10k to 3V3
const int PIN_LDR   = 1;    // LDR to 3V3, 10k to GND: brighter = higher reading
const int PIN_BTN   = 9;    // BOOT button (inside the box: for the bench)
const int PIN_VIN   = 0;    // wheel plug voltage: 47k from plug +, 10k to GND
const float VIN_DIVIDER = 5.7;   // (47k + 10k) / 10k
const float VIN_DIM = 6.5, VIN_FULL = 12.0;

// ---------------- fixed tuning ----------------
const float TILT_MAX    = 10.0;   // deg; v4 head in the stock opening: the lens stays above the cover lip to ±10
const float TOF_DOWN    = 15.0;   // deg the road sensor looks below the wheel's level
const float TAU_FILTER  = 8.0;    // s, gyro/accelerometer blend; long, because braking reads as tilt
const float ACC_GATE    = 0.02;   // g; ignore the accelerometer while it isn't reading ~1 g
const float TAU_SLOW    = 4.0;    // s, what counts as a slow change (fallback mode)
const float TAU_ROAD    = 0.4;    // s, smoothing of the road readings
const float ROAD_JUMP   = 10.0;   // deg; a reading this far off is a kerb, a car or a puddle
const float DEADBAND    = 0.25;
const float SLEW        = 400.0;  // deg/s
const float PITCH_SIGN  = 1.0;    // -1 if pitch goes negative when the nose goes up
const float SERVO_DIR   = 1.0;    // -1 if "beam up" tilts the head down
const float SERVO_CENTER_US  = 1500.0;
const float SERVO_US_PER_DEG = 10.5;
const float LED_FALLEN = 0.15;
const float T_DERATE = 60.0, T_HOT = 80.0, T_CUTBACK = 90.0;
const uint32_t WIFI_MINUTES = 10;

// ---------------- settings (kept in flash, changed on the web page) ----------------
struct Settings {
  int   mode      = 0;      // 0 auto, 1 day (DRL only), 2 night (beam)
  float aim       = -2.0;   // deg below the road/level
  float beamMax   = 1.0;    // 0..1
  float drlDay    = 1.0;
  float drlNight  = 0.2;    // dim position light while the beam is on (0 = off)
  float levelGain = 0.5;    // fallback mode: how much of a hill to follow (0..1)
  int   nightThr  = 600;    // light sensor reading (0..4095): below = getting dark
  int   dayThr    = 1200;   // above = daylight
  float levelZero = 0.0;    // accelerometer pitch when the wheel stands level
  float roadH     = 0.65;   // m, road sensor height above flat ground (Calibrate measures it)
  float trim      = 0.0;    // deg, servo horn offset
  int   follow    = 1;      // 1 = the main beam follows the wheel's brightness (dim/full/accelerating)
  float dimFloor  = 0.35;   // beam level when the wheel is in dim mode
} cfg;
Preferences prefs;

void loadCfg() {
  cfg.mode = prefs.getInt("mode", cfg.mode);
  cfg.aim = prefs.getFloat("aim", cfg.aim);
  cfg.beamMax = prefs.getFloat("beam", cfg.beamMax);
  cfg.drlDay = prefs.getFloat("drlD", cfg.drlDay);
  cfg.drlNight = prefs.getFloat("drlN", cfg.drlNight);
  cfg.levelGain = prefs.getFloat("gain", cfg.levelGain);
  cfg.nightThr = prefs.getInt("nThr", cfg.nightThr);
  cfg.dayThr = prefs.getInt("dThr", cfg.dayThr);
  cfg.levelZero = prefs.getFloat("level", NAN);
  cfg.roadH = prefs.getFloat("roadH", cfg.roadH);
  cfg.trim = prefs.getFloat("trim", cfg.trim);
  cfg.follow = prefs.getInt("follow", cfg.follow);
  cfg.dimFloor = prefs.getFloat("dimF", cfg.dimFloor);
}

// ---------------- hardware helpers ----------------
const uint8_t MPU = 0x68;
VL53L1X tof;
bool tofOk = false;
float gyroBiasX = 0, gyroBiasY = 0;

void mpuWrite(uint8_t reg, uint8_t v) {
  Wire.beginTransmission(MPU); Wire.write(reg); Wire.write(v); Wire.endTransmission();
}

bool mpuRead(float &ax, float &ay, float &az, float &gx, float &gy) {
  Wire.beginTransmission(MPU); Wire.write(0x3B);
  if (Wire.endTransmission(false) != 0) return false;
  if (Wire.requestFrom(MPU, (uint8_t)14) != 14) return false;
  int16_t v[7];
  for (int i = 0; i < 7; i++) v[i] = (Wire.read() << 8) | Wire.read();
  ax = v[0] / 8192.0; ay = v[1] / 8192.0; az = v[2] / 8192.0;
  gx = v[4] / 65.5;   gy = v[5] / 65.5;
  return true;
}

bool tofStart() {
  tof.setTimeout(100);
  if (!tof.init()) return false;
  tof.setDistanceMode(VL53L1X::Long);
  tof.setMeasurementTimingBudget(50000);
  tof.setROISize(4, 4);           // narrow view: misses the head and the cup holder
  tof.startContinuous(50);
  return true;
}

const int SERVO_BITS = 14, PWM_BITS = 10;
#if ESP_ARDUINO_VERSION_MAJOR >= 3
void pwmSetup() {
  ledcAttach(PIN_SERVO, 50, SERVO_BITS);
  ledcAttach(PIN_DIM, 1000, PWM_BITS);
  ledcAttach(PIN_DRL, 1000, PWM_BITS);
}
void pwmWrite(int pin, uint32_t d) { ledcWrite(pin, d); }
#else
void pwmSetup() {
  ledcSetup(0, 50, SERVO_BITS);  ledcAttachPin(PIN_SERVO, 0);
  ledcSetup(1, 1000, PWM_BITS);  ledcAttachPin(PIN_DIM, 1);
  ledcSetup(2, 1000, PWM_BITS);  ledcAttachPin(PIN_DRL, 2);
}
void pwmWrite(int pin, uint32_t d) { ledcWrite(pin == PIN_SERVO ? 0 : pin == PIN_DIM ? 1 : 2, d); }
#endif

void servoDeg(float deg) {   // + = beam up
  float us = SERVO_CENTER_US + SERVO_DIR * (deg + cfg.trim) * SERVO_US_PER_DEG;
  pwmWrite(PIN_SERVO, (uint32_t)(us / 20000.0 * ((1 << SERVO_BITS) - 1)));
}
void level(int pin, float x) { pwmWrite(pin, (uint32_t)(constrain(x, 0.0f, 1.0f) * ((1 << PWM_BITS) - 1))); }

float heatSinkC() {
  int raw = analogRead(PIN_NTC);
  if (raw <= 10 || raw >= 4085) return 25.0;            // no NTC fitted
  float r = 10000.0 * raw / (4095.0 - raw);
  return 1.0 / (log(r / 10000.0) / 3950.0 + 1.0 / 298.15) - 273.15;
}
float thermalLimit(float c) {
  if (c < T_DERATE) return 1.0;
  if (c < T_HOT) return 1.0 - 0.7 * (c - T_DERATE) / (T_HOT - T_DERATE);
  return c < T_CUTBACK ? 0.3 : 0.1;
}

// ---------------- state ----------------
float pitch = 0, roll = 0, pitchSlow = 0, cmd = 0;
float roadSlope = 0, roadW = 0, roadDist = 0;    // road slope vs the wheel (deg), trust 0..1, last reading (m)
uint32_t lastRoadMs = 0, tofRetryMs = 0;
float ledBeam = 0, ledDrl = 0, tempC = 25, light = 2000, vin = 12.0;
bool night = false; uint32_t darkSince = 0, brightSince = 0;
bool fallen = false;
uint32_t lastUs = 0, lastSlowMs = 0, btnDown = 0;

void calibrateGyro() {
  float sx = 0, sy = 0, ax, ay, az, gx, gy, sp = 0, sr = 0; int n = 0;
  for (int i = 0; i < 400; i++) {
    if (mpuRead(ax, ay, az, gx, gy)) {
      sx += gx; sy += gy; sp += atan2(ax, az) * 57.2958; sr += atan2(ay, az) * 57.2958; n++;
    }
    delay(5);
  }
  if (n == 0) return;
  gyroBiasX = sx / n; gyroBiasY = sy / n;
  pitch = pitchSlow = PITCH_SIGN * sp / n; roll = sr / n;
  if (std::isnan(cfg.levelZero)) cfg.levelZero = pitch;   // first start: take "standing" as level
}

// "the wheel is standing upright on flat ground right now"
void calibrateHere() {
  cfg.levelZero = pitchSlow; prefs.putFloat("level", cfg.levelZero);
  if (roadW > 0.5 && roadDist > 0.3) {
    cfg.roadH = roadDist * sin(TOF_DOWN / 57.2958); prefs.putFloat("roadH", cfg.roadH);
  }
}

// the wheel's own brightness: 6.5 V dim .. 12 V full (it rises further while accelerating)
float wheelFactor() {
  if (!cfg.follow) return 1.0;
  float k = constrain((vin - VIN_DIM) / (VIN_FULL - VIN_DIM), 0.0f, 1.0f);
  return cfg.dimFloor + (1.0f - cfg.dimFloor) * k;
}

// ---------------- web page ----------------
WebServer web(80);
bool wifiOn = false;

const char PAGE[] = R"HTML(<!doctype html><html><head><meta name=viewport content="width=device-width,initial-scale=1">
<title>Headlamp</title><style>
body{font-family:system-ui,sans-serif;margin:16px;max-width:520px;background:#111;color:#eee}
h1{font-size:20px}label{display:block;margin:14px 0 4px}input[type=range]{width:100%}
.row{display:flex;gap:8px}button,select{font-size:16px;padding:10px;border-radius:8px;border:0;background:#333;color:#eee}
button.big{width:100%;background:#c8202a;margin-top:18px}#s{font-family:monospace;font-size:13px;white-space:pre;background:#222;padding:10px;border-radius:8px}
</style></head><body><h1>Headlamp</h1><div id=s>...</div>
<label>Mode</label><select id=mode onchange="set('mode',this.value)"><option value=0>Auto (light sensor)</option><option value=1>Day: running lights only</option><option value=2>Night: main beam</option></select>
<label>Beam aim below the road: <b id=aimv></b>&deg;</label><div class=row><button onclick="nudge('aim',-0.5)">Lower</button><button onclick="nudge('aim',0.5)">Higher</button></div>
<label>Main beam brightness <b id=beamv></b>%</label><input type=range id=beam min=10 max=100 onchange="set('beam',this.value/100)">
<label><input type=checkbox id=follow onchange="set('follow',this.checked?1:0)"> Beam follows the wheel (dim / full / brighter when accelerating)</label>
<label>Beam in the wheel's dim mode <b id=dimFv></b>%</label><input type=range id=dimF min=5 max=100 onchange="set('dimF',this.value/100)">
<label>Running lights, day <b id=drlDv></b>%</label><input type=range id=drlD min=0 max=100 onchange="set('drlD',this.value/100)">
<label>Running lights, at night <b id=drlNv></b>%</label><input type=range id=drlN min=0 max=100 onchange="set('drlN',this.value/100)">
<label>Without road sensor: follow hills <b id=gainv></b>%</label><input type=range id=gain min=0 max=100 onchange="set('gain',this.value/100)">
<label>Night starts below light <b id=nThrv></b></label><input type=range id=nThr min=0 max=4095 onchange="set('nThr',this.value)">
<label>Day starts above light <b id=dThrv></b></label><input type=range id=dThr min=0 max=4095 onchange="set('dThr',this.value)">
<label>Servo trim <b id=trimv></b>&deg;</label><div class=row><button onclick="nudge('trim',-0.5)">-</button><button onclick="nudge('trim',0.5)">+</button></div>
<button class=big onclick="if(confirm('Wheel upright on flat ground, standing still?'))fetch('/cal')">Calibrate: wheel upright on flat ground</button>
<script>
let c={};function set(k,v){fetch('/set?k='+k+'&v='+v)}
function nudge(k,d){set(k,(c[k]+d).toFixed(1))}
async function tick(){try{let r=await fetch('/s');c=await r.json();
s.textContent=`${c.night?'NIGHT':'DAY'}  light ${c.light}  heat ${c.temp}C${c.fallen?'  FALLEN':''}
wheel lamp ${c.vin} V  (beam x${c.wheel})
pitch ${c.pitch}  servo ${c.servo}
road ${c.roadOk?c.dist+' m  slope '+c.slope+' deg':'no reading (gyro only)'}`;
if(document.activeElement!==follow)follow.checked=!!c.follow;
for(const k of ['beam','drlD','drlN','gain','dimF']){let e=document.getElementById(k);if(document.activeElement!==e)e.value=Math.round(c[k]*100);document.getElementById(k+'v').textContent=Math.round(c[k]*100)}
for(const k of ['nThr','dThr']){let e=document.getElementById(k);if(document.activeElement!==e)e.value=c[k];document.getElementById(k+'v').textContent=c[k]}
aimv.textContent=(-c.aim).toFixed(1);trimv.textContent=c.trim.toFixed(1);if(document.activeElement!==mode)mode.value=c.mode}catch(e){}
setTimeout(tick,500)}tick()</script></body></html>)HTML";

void webStatus() {
  char b[512];
  snprintf(b, sizeof b,
    "{\"night\":%d,\"light\":%d,\"temp\":%.0f,\"fallen\":%d,\"pitch\":%.1f,\"servo\":%.1f,"
    "\"roadOk\":%d,\"dist\":%.2f,\"slope\":%.1f,\"mode\":%d,\"aim\":%.1f,\"beam\":%.2f,"
    "\"drlD\":%.2f,\"drlN\":%.2f,\"gain\":%.2f,\"nThr\":%d,\"dThr\":%d,\"trim\":%.1f,"
    "\"vin\":%.1f,\"wheel\":%.2f,\"follow\":%d,\"dimF\":%.2f}",
    night, (int)light, tempC, fallen, pitch - cfg.levelZero, cmd, roadW > 0.5, roadDist, roadSlope,
    cfg.mode, cfg.aim, cfg.beamMax, cfg.drlDay, cfg.drlNight, cfg.levelGain, cfg.nightThr, cfg.dayThr, cfg.trim,
    vin, wheelFactor(), cfg.follow, cfg.dimFloor);
  web.send(200, "application/json", b);
}

void webSet() {
  String k = web.arg("k"); float v = web.arg("v").toFloat();
  if (k == "mode")      { cfg.mode = constrain((int)v, 0, 2); prefs.putInt("mode", cfg.mode); }
  else if (k == "aim")  { cfg.aim = constrain(v, -TILT_MAX, TILT_MAX); prefs.putFloat("aim", cfg.aim); }
  else if (k == "beam") { cfg.beamMax = constrain(v, 0.1f, 1.0f); prefs.putFloat("beam", cfg.beamMax); }
  else if (k == "drlD") { cfg.drlDay = constrain(v, 0.0f, 1.0f); prefs.putFloat("drlD", cfg.drlDay); }
  else if (k == "drlN") { cfg.drlNight = constrain(v, 0.0f, 1.0f); prefs.putFloat("drlN", cfg.drlNight); }
  else if (k == "gain") { cfg.levelGain = constrain(v, 0.0f, 1.0f); prefs.putFloat("gain", cfg.levelGain); }
  else if (k == "nThr") { cfg.nightThr = constrain((int)v, 0, 4095); prefs.putInt("nThr", cfg.nightThr); }
  else if (k == "dThr") { cfg.dayThr = constrain((int)v, 0, 4095); prefs.putInt("dThr", cfg.dayThr); }
  else if (k == "trim") { cfg.trim = constrain(v, -10.0f, 10.0f); prefs.putFloat("trim", cfg.trim); }
  else if (k == "follow") { cfg.follow = v > 0.5; prefs.putInt("follow", cfg.follow); }
  else if (k == "dimF") { cfg.dimFloor = constrain(v, 0.05f, 1.0f); prefs.putFloat("dimF", cfg.dimFloor); }
  web.send(200, "text/plain", "ok");
}

void wifiStart() {
  char ssid[24];
  snprintf(ssid, sizeof ssid, "Headlamp-%04X", (uint16_t)(ESP.getEfuseMac() >> 32));
  WiFi.mode(WIFI_AP);
  WiFi.softAP(ssid, "masterlamp");
  web.on("/", [] { web.send(200, "text/html", PAGE); });
  web.on("/s", webStatus);
  web.on("/set", webSet);
  web.on("/cal", [] { calibrateHere(); web.send(200, "text/plain", "ok"); });
  web.begin();
  wifiOn = true;
}

void wifiCheck() {
  if (!wifiOn) return;
  web.handleClient();
  // switch the radio off once nobody is using it: saves power, nobody fiddles with it on the road
  if (millis() > WIFI_MINUTES * 60000UL && WiFi.softAPgetStationNum() == 0) {
    web.stop(); WiFi.softAPdisconnect(true); WiFi.mode(WIFI_OFF); wifiOn = false;
  }
}

// ---------------- setup / loop ----------------
void setup() {
  Serial.begin(115200);
  pinMode(PIN_BTN, INPUT_PULLUP);
  analogReadResolution(12);
  analogSetPinAttenuation(PIN_VIN, ADC_11db);
  pwmSetup();
  level(PIN_DIM, 0); level(PIN_DRL, 0);
  prefs.begin("headlamp", false);
  loadCfg();
  servoDeg(cfg.aim);
  Wire.begin(PIN_SDA, PIN_SCL, 400000);
  mpuWrite(0x6B, 0x00); mpuWrite(0x1A, 0x03); mpuWrite(0x1B, 0x08); mpuWrite(0x1C, 0x08);
  tofOk = tofStart();
  calibrateGyro();
  light = analogRead(PIN_LDR);
  night = light < cfg.nightThr;
  wifiStart();
  lastUs = micros();
}

void readRoad(float gravCorr, float dt) {
  if (!tofOk) {
    if (millis() - tofRetryMs > 5000) { tofRetryMs = millis(); tofOk = tofStart(); }
  } else if (tof.dataReady()) {
    tof.read(false);
    float d = tof.ranging_data.range_mm / 1000.0;
    if (tof.ranging_data.range_status == VL53L1X::RangeValid && d > 0.3 && d < 4.0) {
      float a = TOF_DOWN / 57.2958;
      // where the reading lands, relative to flat ground under the wheel: the road's slope vs the wheel
      float s = atan2(cfg.roadH - d * sin(a), d * cos(a)) * 57.2958;
      if (roadW < 0.1 || fabs(s - roadSlope) < ROAD_JUMP) {
        roadSlope += (s - roadSlope) * (0.05 / (TAU_ROAD + 0.05));
        roadDist = d; lastRoadMs = millis();
      }
    }
  }
  bool fresh = millis() - lastRoadMs < 300;
  roadW = constrain(roadW + (fresh ? 2.0f : -2.0f) * dt, 0.0f, 1.0f);
  if (!fresh) roadSlope += (gravCorr - roadSlope) * dt / 2.0;   // stay close for a smooth hand-back
}

void readSupply(float dt) {
  float v = analogReadMilliVolts(PIN_VIN) / 1000.0 * VIN_DIVIDER;
  vin += (v - vin) * constrain(dt / 0.2f, 0.0f, 1.0f);      // 0.2 s: follows the wheel's acceleration boost
}

void readLight(float dt) {
  light += (analogRead(PIN_LDR) - light) * dt / 1.0;
  uint32_t now = millis();
  if (light < cfg.nightThr) { brightSince = 0; if (!darkSince) darkSince = now; }
  else if (light > cfg.dayThr) { darkSince = 0; if (!brightSince) brightSince = now; }
  else { darkSince = brightSince = 0; }
  // on quickly when it gets dark (tunnels), off slowly when it gets light (a lamp post isn't day)
  if (!night && darkSince && now - darkSince > 2000) night = true;
  if (night && brightSince && now - brightSince > 15000) night = false;
}

void handleButton() {   // bench use: short = aim up, long = aim down, >3 s = calibrate here
  bool down = digitalRead(PIN_BTN) == LOW; uint32_t now = millis();
  if (down && !btnDown) btnDown = now;
  if (!down && btnDown) {
    uint32_t held = now - btnDown; btnDown = 0;
    if (held > 3000) calibrateHere();
    else if (held > 700) { cfg.aim = max(cfg.aim - 0.5f, -TILT_MAX); prefs.putFloat("aim", cfg.aim); }
    else if (held > 30)  { cfg.aim = min(cfg.aim + 0.5f, TILT_MAX);  prefs.putFloat("aim", cfg.aim); }
  }
}

void loop() {
  uint32_t nowUs = micros();
  float dt = (nowUs - lastUs) * 1e-6;
  if (dt < 0.005) { wifiCheck(); return; }   // 200 Hz control loop
  lastUs = nowUs;

  float ax, ay, az, gx, gy, rate = 0;
  bool ok = mpuRead(ax, ay, az, gx, gy);
  if (ok) {
    rate = -(gy - gyroBiasY) * PITCH_SIGN;                 // nose up positive
    float accPitch = PITCH_SIGN * atan2(ax, az) * 57.2958;
    float accRoll = atan2(ay, az) * 57.2958;
    float g = sqrt(ax * ax + ay * ay + az * az);
    float a = TAU_FILTER / (TAU_FILTER + dt);
    pitch += rate * dt; roll += (gx - gyroBiasX) * dt;
    if (fabs(g - 1.0) < ACC_GATE) { pitch = a * pitch + (1 - a) * accPitch; roll = a * roll + (1 - a) * accRoll; }
    pitchSlow += (pitch - pitchSlow) * dt / TAU_SLOW;
  }
  fallen = !ok || fabs(roll) > 45 || fabs(pitch - cfg.levelZero) > 40;

  // fallback correction from the gyro/accelerometer alone
  float gravCorr = -((pitch - pitchSlow) + cfg.levelGain * (pitchSlow - cfg.levelZero));
  // road correction: the gyro moves it instantly, the road readings pull it to the truth
  roadSlope += -rate * dt;
  readRoad(gravCorr, dt);
  float want = fallen ? cfg.aim : cfg.aim + roadW * roadSlope + (1 - roadW) * gravCorr;
  want = constrain(want, -TILT_MAX, TILT_MAX);
  if (fabs(want - cmd) > DEADBAND) { float st = SLEW * dt; cmd += constrain(want - cmd, -st, st); }
  servoDeg(cmd);

  // lights
  readLight(dt);
  readSupply(dt);
  if (millis() - lastSlowMs > 100) {
    lastSlowMs = millis(); tempC = heatSinkC();
    Serial.printf("%s light %4d  wheel %4.1fV  pitch %6.2f  road %s %5.2fm %5.1fdeg  servo %6.2f  heat %4.0fC\n",
                  night ? "NIGHT" : "DAY  ", (int)light, vin, pitch - cfg.levelZero, roadW > 0.5 ? "ok " : "-- ",
                  roadDist, roadSlope, cmd, tempC);
  }
  bool beamOn = cfg.mode == 2 || (cfg.mode == 0 && night);
  float beamT = fallen ? LED_FALLEN : (beamOn ? cfg.beamMax * wheelFactor() : 0.0f);
  float drlT = beamOn || fallen ? cfg.drlNight : cfg.drlDay;
  beamT *= thermalLimit(tempC);
  ledBeam += constrain(beamT - ledBeam, -dt, dt);           // 1 s fade
  ledDrl += constrain(drlT - ledDrl, -2 * dt, 2 * dt);
  level(PIN_DIM, ledBeam);
  level(PIN_DRL, ledDrl);

  handleButton();
  wifiCheck();
}
