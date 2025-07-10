import os
import json
import time
from datetime import datetime
from twilio.rest import Client
from dotenv import load_dotenv

# ✅ Cargar tu archivo .env con nombre personalizado
load_dotenv(dotenv_path="tokensTwilio.env")

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
FROM_WHATSAPP = os.getenv("TWILIO_WHATSAPP_NUMBER")
TO_WHATSAPP = os.getenv("MI_NUMERO_WHATSAPP")

archivo_resumen = os.path.join("Output", "resumen_urgente.json")
ultimo_timestamp = None

client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

def leer_resumen():
    try:
        with open(archivo_resumen, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[{datetime.now()}] Error al leer el resumen: {e}")
        return None

def enviar_whatsapp(resumen_data):
    resumen_texto = resumen_data.get("resumen", "Sin resumen")
    remitente = resumen_data.get("correo", "Desconocido")
    fecha = resumen_data.get("fecha", "")
    
    mensaje = f"📬 *Correo urgente detectado*\n\n👤 De: {remitente}\n📅 Fecha: {fecha}\n📝 Resumen:\n{resumen_texto}"
    
    try:
        message = client.messages.create(
            body=mensaje,
            from_=FROM_WHATSAPP,
            to=TO_WHATSAPP
        )
        print(f"[{datetime.now()}] WhatsApp enviado correctamente (SID: {message.sid})")
    except Exception as e:
        print(f"[{datetime.now()}] Error al enviar WhatsApp: {e}")

print(f"[{datetime.now()}] Iniciando bot de aviso...")
while True:
    if os.path.exists(archivo_resumen):
        datos = leer_resumen()
        if datos:
            timestamp = datos.get("fecha")
            if timestamp and timestamp != ultimo_timestamp:
                enviar_whatsapp(datos)
                ultimo_timestamp = timestamp
    time.sleep(5)