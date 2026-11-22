"""
Simulasi ESP32 untuk tugas IoT Pertemuan 9.
Program ini dijalankan di komputer/laptop menggunakan Python,
lalu mengirim data sensor simulasi ke broker MQTT.

Install library:
    py -m pip install paho-mqtt

Jalankan:
    py esp32.py

Pastikan broker MQTT aktif dan alamatnya sesuai konfigurasi di bawah.
"""

import json
import random
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

# Sesuaikan dengan alamat broker MQTT yang dipakai Node-RED.
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
TOPIC_SENSOR = "kelas/iot/suhu"
TOPIC_KONTROL = "kelas/iot/lampu/control"

status_lampu = "OFF"


def saat_terhubung(client, userdata, flags, reason_code, properties=None):
    print("Terhubung ke MQTT. Kode:", reason_code)
    client.subscribe(TOPIC_KONTROL)
    print("Menunggu perintah lampu pada:", TOPIC_KONTROL)


def saat_pesan_masuk(client, userdata, message):
    global status_lampu

    perintah = message.payload.decode("utf-8").strip().upper()

    if perintah in ("ON", "OFF"):
        status_lampu = perintah
        print("Perintah diterima. Status lampu:", status_lampu)
    else:
        print("Perintah tidak dikenal:", perintah)


def buat_client():
    # Callback API versi terbaru Paho MQTT.
    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id="simulasi-esp32"
    )
    client.on_connect = saat_terhubung
    client.on_message = saat_pesan_masuk
    return client


def main():
    client = buat_client()

    print("Menghubungkan ke broker MQTT:", MQTT_BROKER)
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

    try:
        while True:
            # Nilai sensor simulasi, bukan hasil pembacaan sensor fisik.
            suhu = round(random.uniform(25.0, 34.0), 1)
            kelembaban = random.randint(45, 85)

            data_sensor = {
                "suhu": suhu,
                "kelembaban": kelembaban,
                "status_lampu": status_lampu,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            payload = json.dumps(data_sensor)
            hasil = client.publish(TOPIC_SENSOR, payload)

            if hasil.rc == mqtt.MQTT_ERR_SUCCESS:
                print("Data terkirim:", payload)
            else:
                print("Gagal mengirim data MQTT.")

            time.sleep(2)

    except KeyboardInterrupt:
        print("\nSimulasi ESP32 dihentikan.")

    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
