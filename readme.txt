Descripción:
------------
Este bot monitorea un archivo JSON llamado "resumen_urgente.json" en la carpeta "Output" y envía una notificación por WhatsApp cuando detecta un correo urgente nuevo.

Requisitos:
-----------
- Python 3.x instalado
- Paquetes Python:
    pip install twilio python-dotenv
- Cuenta en Twilio con número de WhatsApp habilitado

Archivos:
---------
- bot.py         : Código principal del bot
- .env           : Archivo con las variables de entorno (credenciales)
- Output/        : Carpeta donde se guarda el archivo resumen_urgente.json generado por la app

Configuración:
--------------
1. Crear archivo `.env` en la misma carpeta que bot.py con el siguiente contenido (sin espacios ni comillas):

   TWILIO_SID=TuSIDdeTwilio
   TWILIO_AUTH_TOKEN=TuTokendeTwilio
   TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886      # Número oficial de Twilio para WhatsApp
   MI_NUMERO_WHATSAPP=whatsapp:+34XXXXXXXXX          # Tu número de WhatsApp con código país

2. Asegurarse de que la carpeta "Output" exista y contenga el archivo "resumen_urgente.json" con la estructura esperada.

Uso:
----
1. Ejecutar el bot desde la terminal:

   python bot.py

2. El bot revisará el archivo cada 5 segundos y enviará un mensaje WhatsApp si detecta un correo urgente nuevo.

Notas:
------
- No compartas tu archivo `.env` ni tus credenciales públicas.
- Para obtener las credenciales Twilio, crea una cuenta en https://twilio.com, ve a tu consola y copia el Account SID y Auth Token.
- El número de WhatsApp oficial de Twilio normalmente es "whatsapp:+14155238886".

Contacto:
---------
Para dudas o soporte, contacta a [Agustin Trebucq] - [agustnintrebucq@gmail.com]

---
