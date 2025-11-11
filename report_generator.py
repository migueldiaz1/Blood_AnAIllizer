import os
import re
import google.genai as genai
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

def _configurar_cliente_gemini():
    # Grabs the API key from our .env file
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Bro, where is the GEMINI_API_KEY? Check your .env")
    genai.configure(api_key=api_key)

def _lab_results_to_text(df):
    # Turns the boring data into a clean text block for the AI
    lines = []
    for _, row in df.iterrows():
        line = (
            f"{row['Test']}: {row['Value']} {row['Unit']} "
            f"(reference range {row['Ref Low']}–{row['Ref High']}). "
            f"Status: {row['Status']}."
        )
        lines.append(line)
    return "Here are the patient's laboratory results:\n\n" + "\n".join(lines)

def _generate_doctor_prompt(content):
    # This is the prompt for the 'smart' doctor report
    return f"""
You are a licensed medical doctor specializing in clinical laboratory interpretation.
Below are the patient's blood test results:

{content}

Please write a concise medical report that follows these guidelines:
1. Summarize all normal findings briefly.
2. Describe in more detail the parameters marked as “Low” or “High”.
3. If any abnormal or borderline values could be associated, mention them as hypotheses.
4. Use clear, professional medical language in English.
5. Organize the report into 2–4 coherent paragraphs.
6. End with this disclaimer:
   “This report is for informational purposes only and does not replace professional medical evaluation.”
"""

def _generate_patient_prompt(content):
    # This is the prompt for the easy, friendly patient report
    return f"""
You are a friendly and empathetic health advisor. Your goal is to help a person
understand their lab results in a simple, clear, and positive way.

Here are the person's lab results:
{content}

Please write a summary for the patient following these guidelines:
1.  Simple Language: Explain the results as if you were talking to a friend.
2.  Normal Results: Start by congratulating the person for the normal results.
3.  Areas for Improvement: For each value marked as "High" or "Low":
    a. Explain very simply what that parameter measures.
    b. Offer 2-3 practical and actionable lifestyle recommendations.
4.  Positive and Motivational Tone.
5.  Clear Structure: Short, easy-to-read paragraphs.
6.  Final Disclaimer: You must end with the following text:
    "Remember, this is an interpretation to help you understand your results.
    It does not replace a consultation with your doctor. Always talk to your doctor!"
"""

def generar_reporte_ia(df, tipo_prompt):
    # This is the main AI function
    _configurar_cliente_gemini()
    content = _lab_results_to_text(df)
    
    if tipo_prompt == "doctor":
        prompt = _generate_doctor_prompt(content)
    elif tipo_prompt == "paciente":
        prompt = _generate_patient_prompt(content)
    else:
        raise ValueError("Wrong prompt type. Must be 'doctor' or 'paciente'.")
    
    # Init the AI model
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    response = model.generate_content(prompt)
    return response.text

def create_medical_report_pdf(output_filename, report_text, image_path=None):
    # This func just takes the AI's text and builds a PDF
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        topMargin=inch, bottomMargin=inch,
        leftMargin=inch, rightMargin=inch
    )
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(name="Normal_Justified", parent=styles["Normal"], alignment=TA_JUSTIFY, spaceAfter=12, leading=14))
    styles.add(ParagraphStyle(name="Bold_Disclaimer", parent=styles["Normal_Justified"], fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name="Bullet_Style", parent=styles["Normal_Justified"], leftIndent=20, spaceAfter=6))

    Story = []
    
    report_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', report_text)
    blocks = report_text.strip().split('\n\n')

    for block in blocks:
        block = block.strip()
        if not block:
            continue
        
        if "Remember, this is an interpretation" in block or "This report is for informational" in block:
            Story.append(Paragraph(block, styles["Bold_Disclaimer"]))
            continue
        
        if block.startswith('* '):
            list_items = block.split('\n')
            for item in list_items:
                item_clean = item.strip().lstrip('* ').strip()
                if item_clean:
                    Story.append(Paragraph(item_clean, styles["Bullet_Style"]))
            Story.append(Spacer(1, 0.1 * inch))
        else:
            Story.append(Paragraph(block, styles["Normal_Justified"]))
            
    try:
        doc.build(Story)
    except Exception as e:
        print(f"Error building PDF: {e}")