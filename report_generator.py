import os
import re
import google.genai as genai # <-- CORRECCIÓN: Importación revertida a la original
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

def _configurar_cliente_gemini():
    API_KEY = os.getenv("GEMINI_API_KEY")
    if not API_KEY:
        raise ValueError("No se encontró la GEMINI_API_KEY.")
    
    # CORRECCIÓN: Usamos la sintaxis del 'prueba.py' que sí funciona
    os.environ["GEMINI_API_KEY"] = API_KEY 
    return genai.Client()

def _lab_results_to_text(df):
    lines = []
    for _, row in df.iterrows():
        # Usamos las claves en minúscula/camelCase que app.py define
        row_dict = row.to_dict()
        line = (
            f"{row_dict['test']}: {row_dict['value']} {row_dict['unit']} "
            f"(reference range {row_dict['refLow']}–{row_dict['refHigh']}). "
            f"Status: {row_dict['status']}."
        )
        lines.append(line)
    return "Here are the patient's laboratory results:\n\n" + "\n".join(lines)

def _generate_prompt(content, tipo_prompt):
    if tipo_prompt == "doctor":
        return f"""
You are a licensed medical doctor specializing in clinical laboratory interpretation.
Below are the patient's blood test results:

{content}

Please write a concise medical report that follows these guidelines:

1. Summarize all normal findings briefly.
2. Describe in more detail the parameters marked as “Near” or “High”.
3. If any abnormal or borderline values could be associated with physiological changes
   or potential medical conditions, mention them as possible interpretations —
   but make it clear that these are hypotheses, not diagnoses.
4. If all values are within normal ranges, state that explicitly.
5. Use clear, professional medical language in English.
6. Organize the report into 2–4 coherent paragraphs.
7. End with this disclaimer:
   “This report is for informational purposes only and does not replace professional medical evaluation.”
"""
    
    if tipo_prompt == "paciente":
        return f"""
You are a friendly and empathetic health advisor. Your goal is to help a person
understand their lab results in a simple, clear, and positive way.
Use everyday language and a relatable tone.

Here are the person's lab results:

{content}

Please write a summary for the patient following these guidelines:

1.  Simple Language: Explain the results as if you were talking to a friend.
    Avoid medical jargon completely.
2.  Normal Results: Start by congratulating the person for the results
    that are within the normal range. Briefly and simply explain
    what it means to have those values at a healthy level.
3.  Areas for Improvement: For each value marked as "High",
    "Low", or "Near", do the following:
    a. Explain very simply what that parameter measures (e.g., "LDL cholesterol
       is like the 'sticky fat transporter' in your blood").
    b. Without being alarming, mention why it's a good idea to pay attention to that value.
    c. Offer 2-3 practical and actionable lifestyle recommendations to help
       improve that value. They should be easy tips to incorporate into daily life.
4.  Positive and Motivational Tone: The goal is to empower the person to
    take small actions to improve their health, not to scare them. Use phrases like
    "A small improvement here could be...", "Your body will thank you if...".
5.  Clear Structure: Organize the report into short, easy-to-read paragraphs of about 4 lines each. The formatting must be simple, containing only explanatory text without bolding, symbols, or lists.
6.  Final Disclaimer: You must end with the following text:
    "Remember, this is an interpretation to help you understand your results.
    It does not replace a consultation with your doctor, who knows your history
    and will give you the best recommendations. Always talk to your doctor!"
 """
    return ""

def generar_reporte_ia(df, tipo_prompt):
    # CORRECCIÓN: Usamos la sintaxis del 'prueba.py'
    client = _configurar_cliente_gemini()
    content = _lab_results_to_text(df)
    prompt = _generate_prompt(content, tipo_prompt)

    response = client.models.generate_content(
        model="gemini-2.5-flash", # Asumiendo que esta es la versión correcta
        contents=prompt
    )
    return response.text

def create_medical_report_pdf(output_filename, report_text):
    doc = SimpleDocTemplate(output_filename, pagesize=letter, topMargin=inch, bottomMargin=inch, leftMargin=inch, rightMargin=inch)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Normal_Justified", parent=styles["Normal"], alignment=TA_JUSTIFY, spaceAfter=12, leading=14))
    
    Story = []
    blocks = report_text.strip().split('\n\n')

    for block in blocks:
        if block.strip():
            Story.append(Paragraph(block.strip(), styles["Normal_Justified"]))
            
    doc.build(Story)