import pdfplumber
import unicodedata
import re

# Adaptación de la celda 53 del notebook
def extraer_texto_de_pdf(ruta_pdf):
    all_text = ""
    with pdfplumber.open(ruta_pdf) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                all_text += text + "\n"
    
    # La salida debe ser una lista de líneas para data_extractor.py
    return all_text.split("\n")