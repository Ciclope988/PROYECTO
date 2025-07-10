import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

class GeminiAssistant:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("La variable de entorno 'GOOGLE_API_KEY' no está configurada. Crea un archivo .env con tu clave.")

        genai.configure(api_key=api_key)

        # --- NUEVO: Verificar modelos disponibles ---
        self._print_available_models() 

        # Intenta usar un modelo que sabemos que es para texto y generación
        # Si 'gemini-pro' sigue dando error, podrías intentar con 'gemini-1.5-flash-latest' 
        # o 'gemini-1.0-pro' si ves que están disponibles.
        self.model = genai.GenerativeModel('models/gemini-2.5-flash') # <-- USANDO UN MODELO ACTUALIZADO

        print(f"Modelo {self.model.model_name} configurado y listo para usar.") # Cambié el print para que muestre el nombre real del modelo usado.


    def _print_available_models(self):
        """Imprime los modelos disponibles y sus capacidades."""
        print("\n--- Modelos Gemini Disponibles y Capacidades ---")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"Nombre del modelo: {m.name}, Descripción: {m.description}")
        print("------------------------------------------\n")

    def generar_respuesta(self, asunto, remitente, cuerpo_completo, resumen_existente, temperature=0.7):
        # ... (tu código actual para generar respuesta, no cambia) ...
        prompt = f"""Eres un asistente de soporte al cliente. Tu tarea es leer un correo electrónico urgente y generar una respuesta concisa, útil y profesional para el remitente.

Datos del correo urgente:
- Remitente: {remitente}
- Asunto: {asunto}
- Resumen (ya generado): {resumen_existente}
- Cuerpo completo del correo:
{cuerpo_completo}

Instrucciones para la respuesta:
- Agradece el mensaje.
- Sé empático y profesional.
- Indica claramente el siguiente paso o si necesitas más información.
- Si el resumen sugiere una acción clara (ej. "el cliente pregunta por el estado del pedido"), formula una respuesta que aborde directamente esa acción o pregunta.
- Mantén la respuesta breve y al punto, máximo 3-4 párrafos.
- Firma como "Equipo de Soporte de [Tu Empresa/Nombre]".
- No te inventes información si no está en el correo. Si falta información crucial, pídelo educadamente.
"""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(temperature=temperature)
            )
            return response.text.strip()
        except Exception as e:
            print(f"Error al generar respuesta con Gemini API: {e}")
            return "Error: No se pudo generar una respuesta con la IA."

    def es_urgente_con_gemini(self, asunto, cuerpo_completo, temperature=0.0):
        """
        Determina si un correo electrónico es urgente utilizando Gemini.
        Devuelve True o False.
        """
        prompt = f"""Analiza el siguiente correo electrónico y determina si es URGENTE.
Responde ÚNICAMENTE con 'SÍ' si es urgente y 'NO' si no lo es. No añadas ninguna otra palabra o explicación.

Asunto del correo: {asunto}
Cuerpo del correo:
{cuerpo_completo}

¿Es este correo urgente?
"""
        try:
            # Usamos una temperatura muy baja (0.0) para respuestas más deterministas
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(temperature=temperature)
            )
            respuesta_gemini = response.text.strip().upper()
            return respuesta_gemini == 'SÍ'
        except Exception as e:
            print(f"Error al determinar urgencia con Gemini API: {e}. Asumiendo no urgente.")
            return False

# Ejemplo de uso (para probar esta clase independientemente):
if __name__ == '__main__':
    assistant = GeminiAssistant()
    
    # Prueba de generación de respuesta
    asunto_ej = "Urgente: Problema con mi pedido #XYZ"
    remitente_ej = "cliente@ejemplo.com"
    cuerpo_ej = "Estimados, mi pedido #XYZ no ha llegado y lo necesito imperiosamente. ¿Podrían verificar el estado y la fecha de entrega? Estoy muy preocupado."
    resumen_ej = "El cliente necesita una actualización urgente sobre el pedido #XYZ que no ha llegado."

    print("Generando respuesta con Gemini...")
    respuesta = assistant.generar_respuesta(
        asunto_ej,
        remitente_ej,
        cuerpo_ej,
        resumen_ej
    )
    print("\n--- Respuesta Generada ---")
    print(respuesta)

    # Prueba de detección de urgencia
    print("\n--- Probando detección de urgencia ---")
    correo_urgente_test = {
        "asunto": "ACCIÓN REQUERIDA: Aprobación de presupuesto",
        "cuerpo": "Necesitamos tu aprobación del presupuesto antes de las 17:00 de hoy para poder proceder con el proyecto. Es crítico para el lanzamiento."
    }
    correo_no_urgente_test = {
        "asunto": "Newsletter semanal",
        "cuerpo": "Hola, aquí tienes el resumen de las noticias de la semana. Esperamos que te sea útil."
    }

    print(f"Correo 1 (urgente): ¿Es urgente? {assistant.es_urgente_con_gemini(correo_urgente_test['asunto'], correo_urgente_test['cuerpo'])}")
    print(f"Correo 2 (no urgente): ¿Es urgente? {assistant.es_urgente_con_gemini(correo_no_urgente_test['asunto'], correo_no_urgente_test['cuerpo'])}")