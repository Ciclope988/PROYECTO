from flask import Flask, request, jsonify, render_template
from gmail_client import GmailClient
from resumen_ia import ResumidorEmails
from spam_detector import SpamDetector
from respondedor_gemini import GeminiAssistant # <-- Importa la clase renombrada
from bs4 import BeautifulSoup
import email.utils
import os
import json
from datetime import datetime
# Importaciones necesarias para Gmail API
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import base64
import numpy as np


app = Flask(__name__)

# Instancia de las clases
resumidor = ResumidorEmails()
detector_spam = SpamDetector()
gemini_assistant = GeminiAssistant() # <-- ¡Usa la nueva instancia de GeminiAssistant!

# ... (tus funciones limpiar_html, guardar_resumen_urgente, dominios_excluidos, index) ...
# La función 'es_urgente' que usaba palabras clave será reemplazada.
def limpiar_html(html):
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    texto = soup.get_text(separator=' ', strip=True)
    return texto

def guardar_resumen_urgente(correo, resumen, prob_spam, cuerpo_completo):
    salida = {
        "correo": correo,
        "resumen": resumen,
        "prob_spam": prob_spam,
        "urgente": True,
        "fecha": datetime.now().isoformat(),
        "texto_original": cuerpo_completo,
    }
    ruta_output = os.path.join("Output")
    os.makedirs(ruta_output, exist_ok=True)
    archivo_salida = os.path.join(ruta_output, "resumen_urgente.json")
    with open(archivo_salida, "w", encoding="utf-8") as f:
        json.dump(salida, f, ensure_ascii=False, indent=2)

dominios_excluidos = ("@introdatabs.com", "@gmail.com")

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/procesar', methods=['POST'])
def procesar():
    data = request.form
    metodo = data.get('metodo')
    n_correos = int(data.get('n_correos', 5))

    resultados = []

    if metodo == "gmail_api":
        gmail_client = GmailClient()
        emails = gmail_client.get_latest_emails(n_correos)
        if not emails:
            return jsonify({"error": "No se encontraron correos o hubo un error con Gmail API."}), 400

        for email_data in emails:
            remitente_raw = email_data.get("from", "").lower()
            nombre, correo = email.utils.parseaddr(remitente_raw)
            correo_remitente = correo.lower()
            asunto_original = email_data.get("subject", "Sin Asunto")
            mensaje_id = email_data.get("id")

            cuerpo_html = email_data.get("body_html")
            cuerpo_texto = email_data.get("body_text")
            texto_para_procesar = limpiar_html(cuerpo_html) if cuerpo_html else cuerpo_texto or ""

            if any(correo_remitente.endswith(dom) for dom in dominios_excluidos):
                es_spam = False
                prob_spam = 0.0
            else:
                try:
                    es_spam, prob_spam = detector_spam.es_spam(texto_para_procesar, threshold=0.5)
                except Exception as e:
                    print(f"Error al detectar spam: {e}. Asumiendo no spam.")
                    es_spam = False
                    prob_spam = 0.0

            if es_spam:
                print(f"Correo de {correo_remitente} detectado como SPAM. Ignorando.")
                continue

            # --- ¡NUEVO! Detección de urgencia con Gemini ---
            print(f"Analizando urgencia del correo de {correo_remitente} con Gemini...")
            urgente = gemini_assistant.es_urgente_con_gemini(asunto_original, texto_para_procesar)
            
            resumen = resumidor.resumir_texto(texto_para_procesar) # Tu resumidor BART

            respuesta_auto = "No generada/enviada" # Inicializar la variable

            if urgente and resumen.strip():
                guardar_resumen_urgente(correo_remitente, resumen, prob_spam, texto_para_procesar)

                print(f"Detectado correo URGENTE de {correo_remitente}. Generando respuesta automática con Gemini...")
                
                respuesta_auto = gemini_assistant.generar_respuesta( # <-- Llama a Gemini para la respuesta
                    asunto_original,
                    correo_remitente,
                    texto_para_procesar,
                    resumen
                )

                if respuesta_auto and respuesta_auto.strip() and respuesta_auto != "Error: No se pudo generar una respuesta con la IA.":
                    asunto_respuesta = f"Re: {asunto_original}"
                    tu_correo_gmail = "tu_correo@gmail.com" # <--- ¡CAMBIA ESTO A TU PROPIO CORREO!

                    print(f"Enviando respuesta a {correo_remitente}:")
                    print(respuesta_auto)
                    
                    sent_email_info = gmail_client.send_email(
                        sender_email=tu_correo_gmail,
                        to_email=correo_remitente,
                        subject=asunto_respuesta,
                        message_text=respuesta_auto,
                        in_reply_to_id=mensaje_id
                    )
                    if sent_email_info:
                        print("Respuesta automática enviada con éxito.")
                    else:
                        print("Fallo al enviar la respuesta automática.")
                else:
                    print("No se pudo generar una respuesta automática válida o hubo un error con la API de Gemini.")

            resultados.append({
                "from": correo_remitente,
                "urgente": urgente,
                "resumen": resumen if resumen.strip() else "No hay resumen disponible.",
                "prob_spam": prob_spam,
                "respuesta_automatica": respuesta_auto
            })

    else:
        return jsonify({"error": "Método no soportado"}), 400

    return jsonify(resultados)

if __name__ == '__main__':
    print("Iniciando la aplicación Flask con integración Gemini para urgencia y respuesta...")
    app.run(debug=True)
