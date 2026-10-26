# Proyecto #2 – INFO1157: Sistemas Inteligentes
**Sistema Distribuido de Monitoreo Ambiental con MQTT, Matplotlib y Telegram**  
*Docente: Dr. (c) Alberto Caro*

---

## 📄 Documentación Técnica Completa
Para una explicación exhaustiva con diagramas, análisis bloque por bloque y desglose línea por línea, consulte el documento PDF adjunto en este repositorio:
👉 **[Documentacion_Proyecto2_INFO1157.pdf](Documentacion_Proyecto2_INFO1157.pdf)**

---

## 🏗️ Arquitectura del Sistema
El proyecto implementa el patrón **Publicador/Suscriptor (Pub/Sub)** sobre **Mosquitto MQTT**:

1. **`publicador.py`**: Publica datos periódicos cada 5 segundos alternando aleatoriamente entre los tópicos `DATA/MP` (MP01, MP25, MP10) y `DATA/MA` (Temperatura, Humedad Relativa).
2. **Mosquitto Broker (`127.0.0.1:1883`)**: Servidor central que distribuye los mensajes a los suscriptores.
3. **4 Clientes Suscriptores en Paralelo**:
   - `suscriptor_mqtt_1.py` (Client ID: `suscriptor_01` $\rightarrow$ Bot 1 de Telegram)
   - `suscriptor_mqtt_2.py` (Client ID: `suscriptor_02` $\rightarrow$ Bot 2 de Telegram)
   - `suscriptor_mqtt_3.py` (Client ID: `suscriptor_03` $\rightarrow$ Bot 3 de Telegram)
   - `suscriptor_mqtt_4.py` (Client ID: `suscriptor_04` $\rightarrow$ Bot 4 de Telegram)
4. **Dashboard y Telegram**: Al acumular exactamente 10 datos en todas las variables, cada suscriptor genera una figura con 5 subgráficos apilados (réplica exacta de la **Figura 3** de la pauta) y la despacha al Chat ID correspondiente mediante la librería `telepot`. Las listas se vacían inmediatamente para continuar la recolección sin detener el cliente.

---

## 🚀 Requisitos e Instalación

Instalar las librerías necesarias con:

```bash
py -m pip install paho-mqtt matplotlib telepot
```

---

## 💻 Instrucciones de Ejecución

1. **Verificar que el broker Mosquitto esté corriendo** en `127.0.0.1:1883`.
2. **Abrir 4 terminales independientes** y ejecutar los 4 suscriptores:
   ```bash
   # Terminal 1
   py suscriptor_mqtt_1.py

   # Terminal 2
   py suscriptor_mqtt_2.py

   # Terminal 3
   py suscriptor_mqtt_3.py

   # Terminal 4
   py suscriptor_mqtt_4.py
   ```
3. **Abrir una 5ª terminal** y ejecutar el publicador oficial:
   ```bash
   py publicador.py
   ```
4. Cada vez que se acumulen 10 muestras completas, cada suscriptor generará su gráfico local (`grafico_bot_1.png` a `grafico_bot_4.png`) y lo transmitirá a tu chat de Telegram.