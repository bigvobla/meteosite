#include <Wire.h>
#include <LiquidCrystal_PCF8574.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <time.h>

// ==== Настройки LCD ====
#define LCD_I2C_ADDR 0x27
LiquidCrystal_PCF8574 lcd(LCD_I2C_ADDR);

// ==== Настройки Wi-Fi и сервера ====
const char* ssid     = "Pixel 7";
const char* password = "123456789";
const char* serverUrl = "http://192.168.158.131:8000/receive/";

// ==== Диапазоны допустимых значений ====
const float T_min = 25.0, T_max = 27.0;
const float H_min = 50.0, H_max = 55.0;
const float P_min = 990.0, P_max = 1025.0;

// ==== Последние значения для плавного дрейфа ====
float lastTemp = 28.0;
float lastHum  = 52.0;
float lastPres = 1010.0;

// ==== Генерация плавного следующего значения ====
float generateNext(float& prev, float lo, float hi, float delta) {
  float change = (random(-100,101) / 100.0) * delta;
  prev += change;
  if (prev < lo) prev = lo;
  if (prev > hi) prev = hi;
  return prev;
}

void setup(){
  Serial.begin(115200);
  randomSeed(micros());

  // LCD и I2C (D14=SDA, D15=SCL)
  Wire.begin(D14, D15);
  lcd.begin(16,2);
  lcd.setBacklight(255);
  lcd.clear();
  lcd.print("Starting...");
  delay(1000);

  // Wi-Fi
  lcd.clear();
  lcd.print("WiFi...");
  WiFi.begin(ssid, password);
  while(WiFi.status()!=WL_CONNECTED){
    delay(500);
  }
  lcd.clear();
  lcd.print("WiFi OK");
  delay(500);

  // NTP (для выравнивания по секундам)
  configTime(0, 0, "pool.ntp.org", "time.google.com");
  // Можно добавить смещение для локального часового пояса, например +6*3600
  // configTime(6*3600, 0, "pool.ntp.org");

  // дожидаемся синхронизации
  time_t now = time(nullptr);
  while(now < 1000000000UL){
    delay(100);
    now = time(nullptr);
  }
}

void loop(){
  // получаем текущее время
  time_t now = time(nullptr);
  struct tm tm;
  localtime_r(&now, &tm);

  // ждём, пока не наступит начало новой минуты
  if(tm.tm_sec != 0){
    // если ещё не ноль, подождать миллисекунд до следующей проверки
    delay(1000 - (millis()%1000));
    return;
  }

  // --- Сейчас tm_sec == 0, можно генерировать и отправлять ---
  float t = generateNext(lastTemp, T_min, T_max, 0.15);
  float h = generateNext(lastHum,  H_min, H_max, 0.3);
  float p = generateNext(lastPres, P_min, P_max, 1.0);

  // Вывод на LCD
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("T:");
  lcd.print(t,1);
  lcd.print("C H:");
  lcd.print(h,1);
  lcd.print("%");
  lcd.setCursor(0,1);
  lcd.print("P:");
  lcd.print(p,0);
  lcd.print("hPa");

  // Лог
  Serial.printf("%02d:%02d:%02d → T=%.1fC H=%.1f%% P=%.0fhPa\n",
    tm.tm_hour, tm.tm_min, tm.tm_sec, t, h, p);

  // Отправка на сервер
  if(WiFi.status()==WL_CONNECTED){
    HTTPClient http;
    WiFiClient client;
    http.begin(client, serverUrl);
    http.addHeader("Content-Type", "application/json");

    String json = String("{\"temperature\":") + t +
                  ",\"humidity\":" + h +
                  ",\"pressure\":" + p + "}";

    int code = http.POST(json);
    Serial.printf("HTTP %d\n", code);
    http.end();
  } else {
    Serial.println("WiFi lost");
  }

  // Ждём секунду, чтобы не попасть ещё раз в tm_sec==0
  delay(1000);
}
