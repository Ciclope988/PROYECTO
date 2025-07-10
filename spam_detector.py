import numpy as np
import os
from keras.models import load_model
import joblib

class SpamDetector:
    def __init__(self):
        self.vectorizer = joblib.load("modelo/vectorizer.pkl")
        self.model = load_model("modelo/spam_model.h5")

    def es_spam(self, texto, threshold=0.5):
        if not isinstance(texto, str) or texto.strip() == "":
            raise ValueError("El texto debe ser una cadena no vacía")
        X = self.vectorizer.transform([texto]).toarray()
        proba = self.model.predict(X)
        proba_val = float(np.squeeze(proba))  # Asegura que sea un escalar
        es_spam = proba_val >= threshold
        return es_spam, proba_val