#include <WiFi.h>
#include <HTTPClient.h>

const char *ssid = "MAN1@NET_Elektro";
const char *password = "*********";
const char *serverName = "http://192.168.61.90:5000/submit-ldr";

// GPIO pins where the LDR sensors are connected
const int ldrPins[] = {33, 32, 35, 34, 39}; 
const int numSensors = 5;
  
void setup(void) {
  Serial.begin(115200);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  Serial.println("");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.print("Connected to ");
  Serial.println(ssid);
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void loop(void) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;

    String ldrValues = "{";
    for (int i = 0; i < numSensors; i++) {
      int ldrValue = analogRead(ldrPins[i]);
      ldrValues += "\"ldr" + String(i+1) + "\":" + String(ldrValue);
      if (i < numSensors - 1) {
        ldrValues += ",";
      }
    }
    ldrValues += "}";

    http.begin(serverName);
    http.addHeader("Content-Type", "application/json");

    int httpResponseCode = http.POST(ldrValues);

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println(httpResponseCode);
      Serial.println(response);
    } else {
      Serial.print("Error on sending POST: ");
      Serial.println(httpResponseCode);
    }

    http.end();

    delay(1800000); // 30mnt=1800000, 1jam=3600000
  } else {
    Serial.println("WiFi Disconnected");
  }
}
