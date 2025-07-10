from transformers import pipeline
from bs4 import BeautifulSoup
import nltk
import re

nltk.download("punkt")

class ResumidorEmails:
    def __init__(self, modelo="facebook/bart-large-cnn", max_chars=1000, max_summary_length=130, min_summary_length=30):
        self.resumidor = pipeline("summarization", model=modelo, device=-1)
        self.max_chars = max_chars
        self.max_summary_length = max_summary_length
        self.min_summary_length = min_summary_length

    def limpiar_html(self, html):
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text(separator=' ', strip=True)

    def resumir_email(self, texto):
        texto = texto.strip()
        if len(texto) < 30:
            return "Texto demasiado corto para resumir."
        if len(texto) > 4000:
            texto = texto[:4000]
        try:
            resumen = self.resumidor(
                texto,
                max_length=self.max_summary_length,
                min_length=self.min_summary_length,
                do_sample=False
            )
            return resumen[0]['summary_text']
        except Exception as e:
            return f"[Error al resumir texto: {e}]"

    def dividir_en_fragmentos(self, texto, max_chars=900):
        oraciones = re.split(r'(?<=[.?!])\s+', texto)
        fragmentos = []
        actual = ""
        for oracion in oraciones:
            if len(actual) + len(oracion) < max_chars:
                actual += " " + oracion
            else:
                fragmentos.append(actual.strip())
                actual = oracion
        if actual:
            fragmentos.append(actual.strip())
        return fragmentos

    def resumir_largo(self, texto):
        fragmentos = self.dividir_en_fragmentos(texto)
        res_parciales = []
        for frag in fragmentos:
            if len(frag) > 30:
                res_parciales.append(self.resumir_email(frag))
        resumen_final = " ".join(res_parciales)
        if len(resumen_final) > self.max_chars:
            resumen_final = self.resumir_email(resumen_final)
        return resumen_final

    def resumir_texto(self, texto):
        texto = texto.strip()
        if not texto:
            return "No hay contenido para resumir."
        elif len(texto) <= 30:
            return "Texto demasiado corto para resumir."
        elif len(texto) > self.max_chars:
            return self.resumir_largo(texto)
        else:
            return self.resumir_email(texto)