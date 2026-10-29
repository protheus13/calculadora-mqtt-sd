// Importação das bibliotecas necessárias para o funcionamento do projeto
#include <DHT.h>          //Biblioteca para leitura do sensor de temperatura
#include <WiFi.h>         //Biblioteca para gerenciamento da conexão WiFi
#include <PubSubClient.h> //Biblioteca para comunicação com o Broker MQTT
#include <ArduinoJson.h>  //Biblioteca para criar e manipular objetos JSON

// Configurando WiFi
const char* SSID = "SpaceX";             //Nome da rede WiFi
const char* PASSWORD = "socorromagal2025";                    //Senha da rede Wifi

// Configurando conexão ao Broker MQTT
const char* MQTT_HOST = "0.tcp.sa.ngrok.io";  //Endereço do servidor MQTT
const int MQTT_PORT = 21691;                   //Porta do servidor MQTT

// Configurações do sensor
const int DHTPIN = 22;          //Pino do ESP32 onde o sensor está conectado
const int DHTTYPE = DHT11;      //Tipo do sensor

// Criar objeto (instância)
DHT dht(DHTPIN, DHTTYPE);           //Objeto para gerenciar o sensor DHTxx
WiFiClient espClient;               //Objeto para gerenciar a conexão Wifi
PubSubClient client(espClient);     //Objeto para gerenciar a comunicação MQTT

// Tópico MQTT onde os dados de temperatura e umidade serão publicados
const char* MQTT_TOPICO_DHT22 = "temp/dht22";

// Configuração do LED da placa
const int LED_PIN = 2;            //Pino do LED integrado na placa ESP32

void setup() {
  Serial.begin(115200);     // Inicializa a comunicação serial para depuração
  pinMode(LED_PIN, OUTPUT); // Configura o LED como saída
  conectarWifi();           // Conecta ao WiFi
  conectarMQTT();           // Conecta ao broker MQTT
  dht.begin();              // Inicializa o sensor DHTxx
}

void conectarWifi() {
  WiFi.begin(SSID, PASSWORD);
  Serial.print("Conectando no WiFi ");

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }

  Serial.println("");
  String ip = " " + WiFi.localIP().toString();
  Serial.print("Conectado ao WiFi: ");
  Serial.print(SSID);
  Serial.print(" | com o IP:");
  Serial.println(ip.c_str());
}

void conectarMQTT() {
  // Define o servidor do MQTT que vai receber a mensagem
  client.setServer(MQTT_HOST, MQTT_PORT);

  while (!client.connected()) {
    String clientId = "ESP32";
    clientId += String(random(0xffff), HEX);

    if (client.connect(clientId.c_str())) {
      Serial.print("Conectado ao Broker com id: ");
      Serial.println(clientId);
    }
    else {
      Serial.print("Erro ao conectar ao Broker!");
      String mqttError = "Codigo do erro: " + String(client.state());
      Serial.println(mqttError.c_str());
    }
  }
}

//Função para ler os dados do sensor e eviá-los ao broker MQTT
void enviarDados() {
  float temperatura = dht.readTemperature();
  float umidade = dht.readHumidity();

  if (isnan(temperatura) || isnan(umidade)) {
    Serial.println("Erro ao ler os dados do sensor!");
  } else {
    Serial.print("Temperatura: ");
    Serial.print(temperatura);
    Serial.println("°C");

    // Serial.print("Umidade: ");
    // Serial.print(umidade);
    // Serial.println("%");

    Serial.println("-----------------------");

    //Criando um objeto JSON para enviar os dados
    StaticJsonDocument<200> doc;
    doc["temperatura"] = temperatura;
    // doc["umidade"] = umidade;

    //Serializar o objeto JSON para uma string
    char buffer[200];
    size_t tamanho = serializeJson(doc, buffer);

    //Publicar os dados no tópico MQTT
    client.publish(MQTT_TOPICO_DHT22, buffer, tamanho);
  }
}

void loop() {
  // Verificar a conexão com WiFi ativa
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi desconectado");
    digitalWrite(LED_PIN, LOW);
    conectarWifi();
  } else {
    // LED fixo quando conectado ao broker MQTT e WiFi
    digitalWrite(LED_PIN, HIGH);
  }

  client.loop();       // Mantém a conexão MQTT ativa
  enviarDados();       // Lê os dados do sensor e envia para o broker MQTT
  delay(10000);         // Aguarda 3 segundos antes de repetir o processo
}
