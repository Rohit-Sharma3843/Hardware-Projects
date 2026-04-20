#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include "DHT.h"

// -------- NODE CONFIG --------
#define NODE_ID 4

// -------- PINS --------
#define DHTPIN D4
#define DHTTYPE DHT11
#define SOIL_PIN A0
#define RELAY_PIN D1

// -------- SOIL CALIBRATION --------
#define DRY_VALUE 850
#define WET_VALUE 300

// -------- WIFI --------
const char* ssid = "Flanker";
const char* password = "FlankerH";
const char* mqtt_server = "192.168.137.69";

// -------- OBJECTS --------
WiFiClient espClient;
PubSubClient client(espClient);
DHT dht(DHTPIN, DHTTYPE);

// -------- LAST VALUES --------
float lastTemp = 0.0;
float lastHum = 0.0;

// -------- WIFI --------
void setup_wifi() {
  Serial.println("\n[WIFI] Connecting...");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\n[WIFI] Connected");
  Serial.println(WiFi.localIP());
}

// -------- RECONNECT --------
void reconnect() {
  while (!client.connected()) {
    Serial.print("[MQTT] Connecting... ");
    String clientId = "ESP_NODE_" + String(NODE_ID);

    if (client.connect(clientId.c_str())) {
      Serial.println("CONNECTED");
    } else {
      Serial.println("FAILED");
      delay(2000);
    }
  }
}

// -------- SETUP --------
void setup() {
  Serial.begin(115200);

  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, HIGH);

  dht.begin();
  setup_wifi();

  client.setServer(mqtt_server, 1883);

  randomSeed(analogRead(A0)); // seed randomness
}

// -------- LOOP --------
void loop() {
  if (!client.connected()) reconnect();
  client.loop();

  float temp = dht.readTemperature();
  float hum = dht.readHumidity();
  int raw_soil = analogRead(SOIL_PIN);

  if (isnan(temp) || isnan(hum)) {
    temp = lastTemp;
    hum = lastHum;
  } else {
    lastTemp = temp;
    lastHum = hum;
  }

  int soil = map(raw_soil, DRY_VALUE, WET_VALUE, 0, 100);
  soil = constrain(soil, 0, 100);

  // 🔥 LOCAL CONTROL
  if (soil < 50) {
    digitalWrite(RELAY_PIN, HIGH);
  } else {
    digitalWrite(RELAY_PIN, LOW);
  }

  // 🔥 RANDOM NPK VALUES
  int N = random(0, 141);     // 0–140
  int P = random(5, 146);     // 5–145
  int K = random(5, 206);     // 5–205

  char payload[200];
  snprintf(payload, sizeof(payload),
    "{\"id\":%d,\"temp\":%.2f,\"hum\":%.2f,\"soil\":%d,\"N\":%d,\"P\":%d,\"K\":%d}",
    NODE_ID, temp, hum, soil, N, P, K);

  client.publish("farm/data", payload);

  Serial.println(payload);

  delay(8000);
}
