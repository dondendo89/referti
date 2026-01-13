#+------------------------------------------------------------------+
#|                                     main.py                      |
#|      Entry point for Radiology Report Generator                  |
#+------------------------------------------------------------------+
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import os
import uvicorn
from typing import Optional

# Import relativi
from services.openai_service import generate_report
from services.pdf_service import create_pdf
from services.word_service import create_word
from services.email_service import send_email
from services.template_builder import create_tosca_template, create_mantini_template
from protocols.shoulder import get_system_prompt_shoulder, get_user_prompt_shoulder
from protocols.achilles import get_system_prompt_achilles, get_user_prompt_achilles
from datetime import datetime

# Carica variabili d'ambiente
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")
if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)

app = FastAPI()

# Configurazione percorsi
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

os.makedirs(OUTPUT_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@app.post("/generate")
async def handle_form(
    request: Request,
    patient_name: str = Form(...),
    patient_dob: str = Form(...),
    exam_type: str = Form(...),
    indications: str = Form(...),
    findings: str = Form(...),
    side: str = Form("destra"),
    prescriber: str = Form("tosca"),
    protocol: str = Form("shoulder")
):
    # 1. Seleziona protocollo
    if protocol == "shoulder":
        system_prompt = get_system_prompt_shoulder()
        user_prompt = get_user_prompt_shoulder({
            "patient_name": patient_name,
            "patient_dob": patient_dob,
            "date": datetime.now().strftime("%d.%m.%Y"),
            "indications": indications,
            "findings": findings,
            "side": side
        })
    elif protocol == "achilles":
        system_prompt = get_system_prompt_achilles()
        user_prompt = get_user_prompt_achilles({
            "patient_name": patient_name,
            "patient_dob": patient_dob,
            "date": datetime.now().strftime("%d.%m.%Y"),
            "indications": indications,
            "findings": findings,
            "side": side
        })
    else:
        # Fallback generico
        system_prompt = "Sei un radiologo."
        user_prompt = f"Referto per {exam_type}: {findings}"

    # 2. Genera testo con AI
    try:
        report_text = generate_report(system_prompt, user_prompt)
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "ResourceExhausted" in error_msg:
             error_msg = "Quota AI esaurita. Riprova tra qualche secondo o controlla il piano API."
        
        return templates.TemplateResponse("form.html", {
            "request": request, 
            "error_message": f"Errore generazione report: {error_msg}",
            # Passiamo indietro i dati per non farli perdere all'utente
            "patient_name": patient_name,
            "patient_dob": patient_dob,
            "indications": indications,
            "findings": findings
        })
    
    # 3. Crea file Word
    filename = f"Referto_{patient_name.replace(' ', '_')}.docx"
    file_path = os.path.join(OUTPUT_DIR, filename)
    
    if prescriber == "tosca":
        create_tosca_template(file_path)
    elif prescriber == "mantini":
        create_mantini_template(file_path)
    else:
        create_word(report_text, file_path)

    # Se abbiamo usato un template, sostituiamo i placeholder
    if prescriber in ["tosca", "mantini"]:
        from docx import Document
        doc = Document(file_path)
        for p in doc.paragraphs:
            if "[PAZIENTE_NOME]" in p.text:
                p.text = p.text.replace("[PAZIENTE_NOME]", patient_name)
            if "[PAZIENTE_DATA_NASCITA]" in p.text:
                p.text = p.text.replace("[PAZIENTE_DATA_NASCITA]", patient_dob)
            if "[CONTENUTO_REFERTO]" in p.text:
                p.text = p.text.replace("[CONTENUTO_REFERTO]", report_text)
        doc.save(file_path)

    # 4. Invio Email (simulato o reale)
    # send_email_with_attachment(...)

    return FileResponse(file_path, filename=filename, media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
