"""
Sistema CAT (Controle de Alertas de Temperatura) - Tópicos Segmentados
- Escuta telemetria do ESP32: temp/dht22
- Publica média contínua:     temp/media
- Publica alerta de variação: temp/alerta/dif (diferença >= 5.0°C)
- Publica alerta de média:    temp/alerta/media (média > 35.0°C)
"""

from collections import deque
import json
import paho.mqtt.client as mqtt

# -------------------------------------------------------------
# Configurações do Broker e Tópicos MQTT
# -------------------------------------------------------------
BROKER_HOST = "localhost"
BROKER_PORT = 1883

TOPICO_TELEMETRIA = "temp/dht22"
TOPICO_MEDIA = "temp/media"
TOPICO_ALERTA_DIF = "temp/alerta/dif"
TOPICO_ALERTA_MEDIA = "temp/alerta/media"

# Limiares de Alerta
LIMITE_TEMP_ALTA = 35.0
DELTA_DIFERENCA_MAX = 5.0

# Buffers de armazenamento
buffer_leituras = deque(maxlen=2)
sensores_nomeados = {"sensor1": None, "sensor2": None}


def on_connect(client, userdata, flags, rc):
    """Executado quando a ligação ao broker é concluída."""
    if rc == 0:
        print("=" * 70)
        print("[*] Sistema CAT conectado com sucesso ao Broker MQTT.")
        print(f"[*] Telemetria:            {TOPICO_TELEMETRIA}")
        print(f"[*] Publicação da Média:   {TOPICO_MEDIA}")
        print(f"[*] Alerta de Diferença:   {TOPICO_ALERTA_DIF} (>= {DELTA_DIFERENCA_MAX}°C)")
        print(f"[*] Alerta de Média Alta:  {TOPICO_ALERTA_MEDIA} (> {LIMITE_TEMP_ALTA}°C)")
        print("=" * 70)
        client.subscribe(TOPICO_TELEMETRIA)
    else:
        print(f"[!] Falha na conexão com o broker MQTT. Código: {rc}")


def on_message(client, userdata, msg):
    """Tratamento dos pacotes recebidos do sensor/simulador."""
    try:
        conteudo = msg.payload.decode("utf-8")
        dados = json.loads(conteudo)

        t1 = None
        t2 = None

        # Cenário A: Ambos os sensores presentes no mesmo payload JSON
        if "sensor1" in dados and "sensor2" in dados:
            t1 = float(dados["sensor1"])
            t2 = float(dados["sensor2"])
            sensores_nomeados["sensor1"] = t1
            sensores_nomeados["sensor2"] = t2

        # Cenário B: Mensagens individuais identificadas por sensor_id
        elif "sensor_id" in dados and "temperatura" in dados:
            s_id = str(dados["sensor_id"])
            sensores_nomeados[s_id] = float(dados["temperatura"])
            t1 = sensores_nomeados.get("sensor1")
            t2 = sensores_nomeados.get("sensor2")

        # Cenário C: Formato padrão DHT22 emitido sequencialmente
        elif "temperatura" in dados:
            temp_atual = float(dados["temperatura"])
            buffer_leituras.append(temp_atual)
            if len(buffer_leituras) == 2:
                t1 = buffer_leituras[0]
                t2 = buffer_leituras[1]
            else:
                print(f"[CAT] Primeira leitura registrada ({temp_atual:.1f}°C). Aguardando próxima...")
                return

        # Avaliação das leituras quando ambos os valores estão disponíveis
        if t1 is not None and t2 is not None:
            media = (t1 + t2) / 2.0
            diferenca = abs(t1 - t2)

            print(f"[CAT] Leituras: [{t1:.1f}°C, {t2:.1f}°C] -> Média: {media:.2f}°C | Diferença: {diferenca:.1f}°C")

            # 1. Publica o valor numérico da média
            client.publish(TOPICO_MEDIA, f"{media:.2f}")
            print(f"  >>> Publicado em [{TOPICO_MEDIA}]: {media:.2f}")

            # 2. Critério de Discrepância / Variação Repentina (>= 5°C)
            if diferenca >= DELTA_DIFERENCA_MAX:
                msg_dif = (
                    f"ALERTA: Variação de {diferenca:.1f}°C detectada entre medições "
                    f"({t1:.1f}°C vs {t2:.1f}°C)!"
                )
                client.publish(TOPICO_ALERTA_DIF, msg_dif)
                print(f"  >>> Publicado em [{TOPICO_ALERTA_DIF}]: \"{msg_dif}\"")

            # 3. Critério de Temperatura Média Elevada (> 35°C)
            if media > LIMITE_TEMP_ALTA:
                msg_media = f"ALERTA: Média Crítica em {media:.1f}°C (Acima de {LIMITE_TEMP_ALTA}°C)!"
                client.publish(TOPICO_ALERTA_MEDIA, msg_media)
                print(f"  >>> Publicado em [{TOPICO_ALERTA_MEDIA}]: \"{msg_media}\"")

    except json.JSONDecodeError:
        print(f"[!] Mensagem não é um JSON válido: {msg.payload}")
    except Exception as erro:
        print(f"[!] Erro no processamento: {erro}")


def executar():
    try:
        cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "SistemaCAT_TopicosDiferentes")
    except AttributeError:
        cliente = mqtt.Client("SistemaCAT_TopicosDiferentes")

    cliente.on_connect = on_connect
    cliente.on_message = on_message

    cliente.connect(BROKER_HOST, BROKER_PORT, keepalive=60)

    try:
        cliente.loop_forever()
    except KeyboardInterrupt:
        print("\n[*] Sistema CAT encerrado.")
        cliente.disconnect()


if __name__ == "__main__":
    executar()
