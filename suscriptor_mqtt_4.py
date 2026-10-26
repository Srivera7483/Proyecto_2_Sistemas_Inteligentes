import paho.mqtt.client as mqtt
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import telepot
import os

TELEGRAM_TOKEN = "8406420805:AAHXnLKbAJ5u5eCXu0aFaJ2hlkfn5nCo4r0"
CHAT_ID = "8483080265"
MQTT_CLIENT_ID = "suscriptor_04"

BROKER_HOST = "127.0.0.1"
BROKER_PORT = 1883

TOPICO_MP = "DATA/MP"
TOPICO_MA = "DATA/MA"

MUESTRAS_PARA_GRAFICAR = 10
NOMBRE_IMAGEN = "grafico_bot_4.png"

lista_mp01 = []
lista_mp25 = []
lista_mp10 = []
lista_tempe = []
lista_hr = []

def todas_las_listas_completas():
    return all(
        len(lst) >= MUESTRAS_PARA_GRAFICAR
        for lst in (lista_mp01, lista_mp25, lista_mp10, lista_tempe, lista_hr)
    )

def graficar_y_enviar():
    config_plots = [
        (lista_mp01[:MUESTRAS_PARA_GRAFICAR], "MP01", "ug/m3", "blue", (0, 50), [0, 10, 20, 30, 40, 50]),
        (lista_mp25[:MUESTRAS_PARA_GRAFICAR], "MP25", "ug/m3", "green", (0, 50), [0, 10, 20, 30, 40, 50]),
        (lista_mp10[:MUESTRAS_PARA_GRAFICAR], "MP10", "ug/m3", "red", (0, 50), [0, 10, 20, 30, 40, 50]),
        (lista_tempe[:MUESTRAS_PARA_GRAFICAR], "Tempe", "Tempe", "blue", (0, 50), [0, 10, 20, 30, 40, 50]),
        (lista_hr[:MUESTRAS_PARA_GRAFICAR], "HR(%)", "HR(%)", "red", (50, 90), [50, 55, 60, 65, 70, 75, 80, 85, 90]),
    ]

    fig, ejes = plt.subplots(5, 1, figsize=(10, 8), sharex=True)
    fig.suptitle("Medicion MP1, MP2.5, MP10um - Tempe, HR", fontsize=12)

    muestras_eje = list(range(1, MUESTRAS_PARA_GRAFICAR + 1))

    for ax, (valores, etiqueta, ylabel, color, ylim, yticks) in zip(ejes, config_plots):
        ax.plot(muestras_eje, valores, color=color, linewidth=1.5, label=etiqueta)
        ax.set_ylabel(ylabel, fontsize=10)
        ax.set_ylim(ylim)
        ax.set_yticks(yticks)
        ax.set_xlim(1, 13)
        ax.grid(True, linestyle=":", color="gray", alpha=0.8)
        ax.legend(loc="center right", frameon=True, edgecolor="black", facecolor="white")
        ax.tick_params(direction="in", top=True, right=True)

    ejes[-1].set_xlabel("10 Samples Datas...", fontsize=11)
    ejes[-1].set_xticks([2, 4, 6, 8, 10, 12])

    plt.subplots_adjust(hspace=0.25, top=0.92, bottom=0.08, left=0.10, right=0.95)
    plt.savefig(NOMBRE_IMAGEN, dpi=150)
    plt.close(fig)
    print(f"[INFO] Gráfico guardado como '{NOMBRE_IMAGEN}'")

    try:
        bot = telepot.Bot(TELEGRAM_TOKEN)
        with open(NOMBRE_IMAGEN, "rb") as foto:
            bot.sendPhoto(CHAT_ID, foto, caption="Dashboard ambiental - ultimas 10 muestras")
        print("[INFO] Imagen enviada exitosamente a Telegram.")
    except Exception as e:
        print(f"[ERROR] No se pudo enviar la imagen a Telegram: {e}")

    lista_mp01.clear()
    lista_mp25.clear()
    lista_mp10.clear()
    lista_tempe.clear()
    lista_hr.clear()
    print("[INFO] Listas vaciadas. Esperando nuevas muestras...\n")

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print(f"[MQTT] Conectado al broker {BROKER_HOST}:{BROKER_PORT}")
        client.subscribe([(TOPICO_MP, 0), (TOPICO_MA, 0)])
        print(f"[MQTT] Suscrito a '{TOPICO_MP}' y '{TOPICO_MA}'")
    else:
        print(f"[MQTT] Fallo de conexión - código de retorno: {reason_code}")

def on_message(client, userdata, msg):
    topico = msg.topic
    payload = msg.payload.decode("utf-8").strip()

    try:
        if topico == TOPICO_MP:
            partes = payload.split(",")
            val_mp01 = float(partes[0])
            val_mp25 = float(partes[1])
            val_mp10 = float(partes[2])

            lista_mp01.append(val_mp01)
            lista_mp25.append(val_mp25)
            lista_mp10.append(val_mp10)

            print(f"  [DATA/MP] MP01={val_mp01}  MP25={val_mp25}  MP10={val_mp10}  (muestras MP: {len(lista_mp01)})")

        elif topico == TOPICO_MA:
            partes = payload.split(",")
            val_tempe = float(partes[0])
            val_hr = float(partes[1])

            lista_tempe.append(val_tempe)
            lista_hr.append(val_hr)

            print(f"  [DATA/MA] Temp={val_tempe}  HR={val_hr}  (muestras MA: {len(lista_tempe)})")

    except (ValueError, IndexError) as e:
        print(f"[WARN] Dato malformado en '{topico}': '{payload}' -> {e}")
        return

    if todas_las_listas_completas():
        print("[INFO] Se alcanzaron 10 muestras en todas las variables. Graficando...")
        graficar_y_enviar()

def main():
    cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=MQTT_CLIENT_ID)
    cliente.on_connect = on_connect
    cliente.on_message = on_message

    print(f"[MQTT] Conectando a {BROKER_HOST}:{BROKER_PORT} como '{MQTT_CLIENT_ID}'...")
    cliente.connect(BROKER_HOST, BROKER_PORT, keepalive=60)

    try:
        cliente.loop_forever()
    except KeyboardInterrupt:
        print("\n[INFO] Desconectando del broker...")
        cliente.disconnect()
        print("[INFO] Cliente detenido.")

if __name__ == "__main__":
    main()
