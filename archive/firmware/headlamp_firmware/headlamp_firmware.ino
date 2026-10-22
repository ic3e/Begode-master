// Self-levelling headlamp for the Begode Master front handle.
// ESP32-C3 SuperMini + MPU-6050 (GY-521) + MG90S servo + Mean Well LDD-1500H LED driver.
//
// The servo tilts the lamp head so the beam stays put while the wheel pitches:
//  - fast pitch changes (braking dips, bumps, the start of tilt-back) are cancelled fully;
//  - slow changes are followed partly (LEVEL_GAIN), so on a long hill the beam settles back
//    to the road instead of pointing at the sky or the ground.
// The MPU-6050 sits flat on the floor of the electronics block, its X arrow pointing forward.
//
// Board: "ESP32C3 Dev Module" (Arduino-ESP32 2.x or 3.x), USB CDC On Boot: Enabled.

#include <Wire.h>
#include <Preferences.h>

// ---------------- pins ----------------
const int PIN_SDA   = 6;
const int PIN_SCL   = 7;
const int PIN_SERVO = 10;
const int PIN_DIM   = 5;    // LDD-1500H DIM input (PWM, 3.3 V is "on")
const int PIN_NTC   = 3;    // 10k NTC to GND, 10k resistor to 3V3
const int PIN_BTN   = 9;    // the board's BOOT button: short press = beam up, long press = beam down

// ---------------- tuning ----------------
const float TILT_MAX    = 12.0;   // deg; the head clears the handle to 13
const float AIM_DEFAULT = -2.0;   // deg below level; keeps the bright centre out of people's eyes
const float LEVEL_GAIN  = 0.5;    // 0 = only cancel fast movements, 1 = always level to gravity
const float TAU_FILTER  = 8.0;    // s, gyro/accelerometer blend; long, because braking reads as tilt
const float TAU_SLOW    = 4.0;    // s, what counts as a "slow" change
const float ACC_GATE    = 0.02;   // g; ignore the accelerometer while it isn't reading ~1 g
                                  // (simulated: a 5 deg braking dip at 0.3 g moves the beam 7 deg
                                  //  with 2 s / 0.08 g, 2 deg with these values)
const float DEADBAND    = 0.25;   // deg; stops the servo buzzing on tiny corrections
const float SLEW        = 400.0;  // deg/s, servo speed limit
const float PITCH_SIGN  = 1.0;    // set to -1 if "pitch" goes negative when the nose goes up

// servo calibration: pulse for the head level, and microseconds per degree
const float SERVO_CENTER_US = 1500.0;
const float SERVO_US_PER_DEG = 10.5;   // MG90S is roughly 1000 us per 95 deg
const float SERVO_TRIM_DEG = 0.0;      // if the horn sat one spline tooth off
const float SERVO_DIR = 1.0;           // -1 if "beam up" tilts the head down

// LED brightness, 0..1, and when to back off for heat
const float LED_MAX    = 1.0;
const float LED_FALLEN = 0.15;   // wheel on its side or picked up
const float T_DERATE   = 60.0;   // C on the heat sink: start dimming
const float T_HOT      = 80.0;   // C: down to 30 %
const float T_CUTBACK  = 90.0;   // C: 10 %

// ---------------- MPU-6050 ----------------
const uint8_t MPU = 0x68;
float gyroBiasY = 0, gyroBiasX = 0;

void mpuWrite(uint8_t reg, uint8_t v) {
  Wire.beginTransmission(MPU); Wire.write(reg); Wire.write(v); Wire.endTransmission();
}

bool mpuRead(float &ax, float &ay, float &az, float &gx, float &gy) {
  Wire.beginTransmission(MPU); Wire.write(0x3B);
  if (Wire.endTransmission(false) != 0) return false;
  if (Wire.requestFrom(MPU, (uint8_t)14) != 14) return false;
  int16_t v[7];
  for (int i = 0; i < 7; i++) v[i] = (Wire.read() << 8) | Wire.read();
  ax = v[0] / 8192.0; ay = v[1] / 8192.0; az = v[2] / 8192.0;   // +-4 g
  gx = v[4] / 65.5;   gy = v[5] / 65.5;                         // +-500 deg/s
  return true;
}

// ---------------- PWM (works on Arduino-ESP32 2.x and 3.x) ----------------
const int SERVO_BITS = 14, DIM_BITS = 10;
#if ESP_ARDUINO_VERSION_MAJOR >= 3
void pwmSetup() {
  ledcAttach(PIN_SERVO, 50, SERVO_BITS);
  ledcAttach(PIN_DIM, 1000, DIM_BITS);
}
void servoWrite(uint32_t d) { ledcWrite(PIN_SERVO, d); }
void dimWrite(uint32_t d)   { ledcWrite(PIN_DIM, d); }
#else
void pwmSetup() {
  ledcSetup(0, 50, SERVO_BITS);  ledcAttachPin(PIN_SERVO, 0);
  ledcSetup(1, 1000, DIM_BITS);  ledcAttachPin(PIN_DIM, 1);
}
void servoWrite(uint32_t d) { ledcWrite(0, d); }
void dimWrite(uint32_t d)   { ledcWrite(1, d); }
#endif

void servoDeg(float deg) {   // + = beam up
  float us = SERVO_CENTER_US + SERVO_DIR * (deg + SERVO_TRIM_DEG) * SERVO_US_PER_DEG;
  servoWrite((uint32_t)(us / 20000.0 * ((1 << SERVO_BITS) - 1)));
}

void led(float level) {      // 0..1
  dimWrite((uint32_t)(constrain(level, 0.0f, 1.0f) * ((1 << DIM_BITS) - 1)));
}

float heatSinkC() {
  int raw = analogRead(PIN_NTC);
  if (raw <= 10 || raw >= 4085) return 25.0;            // no NTC fitted: don't derate
  float r = 10000.0 * raw / (4095.0 - raw);              // NTC to GND, 10k pull-up
  float t = 1.0 / (log(r / 10000.0) / 3950.0 + 1.0 / 298.15) - 273.15;
  return t;
}

float thermalLimit(float c) {
  if (c < T_DERATE) return 1.0;
  if (c < T_HOT) return 1.0 - 0.7 * (c - T_DERATE) / (T_HOT - T_DERATE);
  if (c < T_CUTBACK) return 0.3;
  return 0.1;
}

// ---------------- state ----------------
Preferences prefs;
float aim = AIM_DEFAULT;
float pitch = 0, roll = 0, pitchSlow = 0, levelZero = 0, cmd = 0;
float ledLevel = 0, tempC = 25;
uint32_t lastUs = 0, lastPrint = 0, btnDown = 0;

void calibrate() {
  // the wheel has just been switched on and should be standing still
  float sx = 0, sy = 0, ax, ay, az, gx, gy, sumP = 0, sumR = 0;
  int n = 0;
  for (int i = 0; i < 400; i++) {
    if (mpuRead(ax, ay, az, gx, gy)) {
      sx += gx; sy += gy;
      sumP += atan2(ax, az) * 57.2958; sumR += atan2(ay, az) * 57.2958; n++;
    }
    delay(5);
  }
  if (n == 0) return;
  gyroBiasX = sx / n; gyroBiasY = sy / n;
  pitch = PITCH_SIGN * sumP / n; roll = sumR / n;
  pitchSlow = pitch;
  levelZero = prefs.getFloat("level", pitch);   // first start: whatever "standing" is
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_BTN, INPUT_PULLUP);
  analogReadResolution(12);
  pwmSetup();
  led(0);
  servoDeg(AIM_DEFAULT);
  Wire.begin(PIN_SDA, PIN_SCL, 400000);
  mpuWrite(0x6B, 0x00);   // wake
  mpuWrite(0x1A, 0x03);   // 44 Hz low-pass
  mpuWrite(0x1B, 0x08);   // gyro +-500 deg/s
  mpuWrite(0x1C, 0x08);   // accel +-4 g
  prefs.begin("headlamp", false);
  aim = prefs.getFloat("aim", AIM_DEFAULT);
  calibrate();
  lastUs = micros();
}

void handleButton() {
  bool down = digitalRead(PIN_BTN) == LOW;
  uint32_t now = millis();
  if (down && btnDown == 0) btnDown = now;
  if (!down && btnDown != 0) {
    uint32_t held = now - btnDown;
    btnDown = 0;
    if (held > 3000) {                 // very long press: "the wheel is level right now"
      levelZero = pitchSlow; prefs.putFloat("level", levelZero);
    } else if (held > 700) {
      aim = max(aim - 0.5f, -TILT_MAX); prefs.putFloat("aim", aim);
    } else if (held > 30) {
      aim = min(aim + 0.5f, TILT_MAX); prefs.putFloat("aim", aim);
    }
  }
}

void loop() {
  uint32_t nowUs = micros();
  float dt = (nowUs - lastUs) * 1e-6;
  if (dt < 0.005) return;              // 200 Hz
  lastUs = nowUs;

  float ax, ay, az, gx, gy;
  bool ok = mpuRead(ax, ay, az, gx, gy);
  if (ok) {
    float rate = -(gy - gyroBiasY) * PITCH_SIGN;     // nose up positive (X forward, Y left)
    float accPitch = PITCH_SIGN * atan2(ax, az) * 57.2958;
    float accRoll = atan2(ay, az) * 57.2958;
    float g = sqrt(ax * ax + ay * ay + az * az);
    float a = TAU_FILTER / (TAU_FILTER + dt);
    pitch += rate * dt;
    roll += (gx - gyroBiasX) * dt;
    if (fabs(g - 1.0) < ACC_GATE) {    // only trust the accelerometer when nothing is pushing
      pitch = a * pitch + (1 - a) * accPitch;
      roll = a * roll + (1 - a) * accRoll;
    }
    pitchSlow += (pitch - pitchSlow) * dt / TAU_SLOW;
  }

  bool fallen = !ok || fabs(roll) > 45 || fabs(pitch - levelZero) > 40;
  float want;
  if (fallen) {
    want = aim;                         // park, and dim so it doesn't blind anyone or cook
  } else {
    float fast = pitch - pitchSlow;
    float slow = pitchSlow - levelZero;
    want = aim - (fast + LEVEL_GAIN * slow);
  }
  want = constrain(want, -TILT_MAX, TILT_MAX);
  if (fabs(want - cmd) > DEADBAND) {
    float step = SLEW * dt;
    cmd += constrain(want - cmd, -step, step);
  }
  servoDeg(cmd);

  // LED: soft start, heat and fallen limits
  if (millis() - lastPrint > 100) tempC = heatSinkC();
  float target = (fallen ? LED_FALLEN : LED_MAX) * thermalLimit(tempC);
  ledLevel += constrain(target - ledLevel, -dt, dt);   // 1 s ramp
  led(ledLevel);

  handleButton();

  if (millis() - lastPrint > 100) {
    lastPrint = millis();
    Serial.printf("pitch %6.2f  slow %6.2f  roll %6.1f  servo %6.2f  aim %5.1f  heat %5.1fC  led %3d%%%s\n",
                  pitch - levelZero, pitchSlow - levelZero, roll, cmd, aim, tempC,
                  (int)(ledLevel * 100), fallen ? "  FALLEN" : "");
  }
}
