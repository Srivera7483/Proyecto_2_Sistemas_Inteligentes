# By Alberto Caro
# Ingeniero Civil Informatico
# Dr. (c) Cs. de la Ingenieria - PUC
# --------------------------------------
import paho.mqtt.publish as MyPub, time as ti, random as Ra

sURL = '127.0.0.1'  # URL Mosquitto Server - Cambiar segun sea el caso
aTOP = ['DATA/MP', 'DATA/MA']  # TOPICOS : Material Particulado - Medio Ambiente

def Get_MP():
    nMP01 = Ra.randint(4, 10)   # MP 01um
    nMP25 = Ra.randint(10, 50)  # MP 25um
    nMP10 = Ra.randint(10, 50)  # MP 10um
    return str(nMP01) + ',' + str(nMP25) + ',' + str(nMP10) + '\n'

def Get_MA():
    nTe = Ra.randint(10, 22)    # Temperatura
    nHr = Ra.randint(60, 85)    # Humedad Relativa Aire
    return str(nTe) + ',' + str(nHr) + '\n'

if __name__ == '__main__':
    print(f"[PUBLICADOR] Iniciando envio hacia broker {sURL}...")
    while 1:
        aMsg = [[Get_MP()], [Get_MA()]]
        nTop = Ra.randint(0, 1)
        sMsg = Ra.choice(aMsg[nTop])
        MyPub.single(aTOP[nTop], sMsg, hostname=sURL)
        print(f"[PUBLICADOR] Enviado a {aTOP[nTop]}: {sMsg.strip()}")
        ti.sleep(5)  # Publica cada 5 Segundos
