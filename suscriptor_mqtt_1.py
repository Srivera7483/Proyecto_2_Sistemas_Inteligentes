"""
Cliente Suscriptor MQTT – Monitoreo Ambiental con Dashboard y Bot de Telegram
==============================================================================
Instancia 1 de 4
"""

import paho.mqtt.client as mqtt
import matplotlib
matplotlib.use("Agg")  # Backend sin GUI para evitar conflictos en ejecución paralela
import matplotlib.pyplot as plt
import telepot
import os

# ──────────────────────────────────────────────────────────────────────────────
# VARIABLES DE CONFIGURACIÓN  (ajustar antes de ejecutar)
# ──────────────────────────────────────────────────────────────────────────────
TELEGRAM_TOKEN = "8990440636:AAHGEfFqc85LbeMlc_M9N_nTlAwoqu1FAR0"
CHAT_ID        = "8483080265"
MQTT_CLIENT_ID = "suscriptor_01"

BROKER_HOST = "127.0.0.1"
BROKER_PORT = 1883

TOPICO_MP = "DATA/MP"   # Formato esperado: "MP01,MP25,MP10"
TOPICO_MA = "DATA/MA"   # Formato esperado: "Tempe,HR"

MUESTRAS_PARA_GRAFICAR = 10
NOMBRE_IMAGEN = "grafico_bot_1.png"

# ──────────────────────────────────────────────────────────────────────────────
# LISTAS DE ALMACENAMIENTO DE DATOS
# ──────────────────────────────────────────────────────────────────────────────
lista_mp01  = []
lista_mp25  = []
lista_mp10  = []
lista_tempe = []
lista_hr    = []


# ──────────────────────────────────────────────────────────────────────────────
# FUNCIONES AUXILIARES
# ──────────────────────────────────────────────────────────────────────────────
def todas_las_listas_completas():
    """Retorna True cuando las 5 listas tienen al menos MUESTRAS_PARA_GRAFICAR datos."""
    return all(
        len(lst) >= MUESTRAS_PARA_GRAFICAR
        for lst in (lista_mp01, lista_mp25, lista_mp10, lista_tempe, lista_hr)
    )


def graficar_y_enviar():
    """Genera el dashboard de 5 subgráficos y lo envía a Telegram."""

    datos = [
        (lista_mp01[:MUESTRAS_PARA_GRAFICAR],  "MP 0.1 µm",     "#E74C3C"),   # Rojo
        (lista_mp25[:MUESTRAS_PARA_GRAFICAR],  "MP 2.5 µm",     "#3498DB"),   # Azul
        (lista_mp10[:MUESTRAS_PARA_GRAFICAR],  "MP 10 µm",      "#2ECC71"),   # Verde
        (lista_tempe[:MUESTRAS_PARA_GRAFICAR], "Temperatura °C", "#F39C12"),   # Naranja
        (lista_hr[:MUESTRAS_PARA_GRAFICAR],    "Humedad Rel. %", "#9B59B6"),   # Púrpura
    ]

    fig, ejes = plt.subplots(5, 1, figsize=(10, 12), sharex=True)
    fig.suptitle("Dashboard de Monitoreo Ambiental", fontsize=14, fontweight="bold")

    muestras_eje = list(range(1, MUESTRAS_PARA_GRAFICAR + 1))

    for ax, (valores, etiqueta, color) in zip(ejes, datos):
        ax.plot(muestras_eje, valores, marker="o", color=color, linewidth=2, label=etiqueta)
        ax.set_ylabel(etiqueta)
        ax.legend(loc="upper right")
        ax.grid(True)

    ejes[-1].set_xlabel("Nº de muestra")
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(NOMBRE_IMAGEN, dpi=150)
    plt.close(fig)
    print(f"[INFO] Gráfico guardado como '{NOMBRE_IMAGEN}'")

    # Enviar la imagen por Telegram
    try:
        bot = telepot.Bot(TELEGRAM_TOKEN)
        with open(NOMBRE_IMAGEN, "rb") as foto:
            bot.sendPhoto(CHAT_ID, foto, caption="📊 Dashboard ambiental – últimas 10 muestras")
        print("[INFO] Imagen enviada exitosamente a Telegram.")
    except Exception as e:
        print(f"[ERROR] No se pudo enviar la imagen a Telegram: {e}")

    # Vaciar las listas para el siguiente bloque de muestras
    lista_mp01.clear()
    lista_mp25.clear()
    lista_mp10.clear()
    lista_tempe.clear()
    lista_hr.clear()
    print("[INFO] Listas vaciadas. Esperando nuevas muestras…\n")


# ──────────────────────────────────────────────────────────────────────────────
# CALLBACKS MQTT
# ──────────────────────────────────────────────────────────────────────────────
def on_connect(client, userdata, flags, reason_code, properties):
    """Se ejecuta al conectarse al broker (firma compatible con paho-mqtt v2)."""
    if reason_code == 0:
        print(f"[MQTT] Conectado al broker {BROKER_HOST}:{BROKER_PORT}")
        client.subscribe([(TOPICO_MP, 0), (TOPICO_MA, 0)])
        print(f"[MQTT] Suscrito a '{TOPICO_MP}' y '{TOPICO_MA}'")
    else:
        print(f"[MQTT] Fallo de conexión – código de retorno: {reason_code}")


def on_message(client, userdata, msg):
    """Procesa cada mensaje entrante y almacena los valores en las listas."""
    topico  = msg.topic
    payload = msg.payload.decode("utf-8").strip()

    try:
        if topico == TOPICO_MP:
            # Formato esperado: "MP01,MP25,MP10"
            partes = payload.split(",")
            val_mp01 = float(partes[0])
            val_mp25 = float(partes[1])
            val_mp10 = float(partes[2])

            lista_mp01.append(val_mp01)
            lista_mp25.append(val_mp25)
            lista_mp10.append(val_mp10)

            print(f"  [DATA/MP] MP01={val_mp01}  MP25={val_mp25}  MP10={val_mp10}  "
                  f"(muestras MP: {len(lista_mp01)})")

        elif topico == TOPICO_MA:
            # Formato esperado: "Tempe,HR"
            partes = payload.split(",")
            val_tempe = float(partes[0])
            val_hr    = float(partes[1])

            lista_tempe.append(val_tempe)
            lista_hr.append(val_hr)

            print(f"  [DATA/MA] Temp={val_tempe}  HR={val_hr}  "
                  f"(muestras MA: {len(lista_tempe)})")

    except (ValueError, IndexError) as e:
        print(f"[WARN] Dato malformado en '{topico}': '{payload}' → {e}")
        return

    # Verificar si ya se acumularon 10 muestras en las 5 listas
    if todas_las_listas_completas():
        print("[INFO] Se alcanzaron 10 muestras en todas las variables. Graficando…")
        graficar_y_enviar()


# ──────────────────────────────────────────────────────────────────────────────
# PUNTO DE ENTRADA
# ──────────────────────────────────────────────────────────────────────────────
def main():
    cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=MQTT_CLIENT_ID)
    cliente.on_connect = on_connect
    cliente.on_message = on_message

    print(f"[MQTT] Conectando a {BROKER_HOST}:{BROKER_PORT} como '{MQTT_CLIENT_ID}'…")
    cliente.connect(BROKER_HOST, BROKER_PORT, keepalive=60)

    # loop_forever bloquea y mantiene la conexión activa
    try:
        cliente.loop_forever()
    except KeyboardInterrupt:
        print("\n[INFO] Desconectando del broker…")
        cliente.disconnect()
        print("[INFO] Cliente detenido.")


if __name__ == "__main__":
    main()
