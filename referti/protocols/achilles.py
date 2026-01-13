from datetime import datetime

def get_system_prompt_achilles() -> str:
    return (
        "Sei un radiologo esperto specializzato in ecografia muscoloscheletrica interventistica. "
        "Il tuo compito è generare un referto medico per una 'Infiltrazione ecoguidata del tendine d'Achille'. "
        "Usa un linguaggio medico professionale, preciso e formale. "
        "Segui RIGOROSAMENTE questa struttura:\n\n"
        "1. **Titolo**: Infiltrazione ecoguidata del tendine d’Achille [LATO] del [DATA]\n"
        "2. **Indicazioni**: Descrivi brevemente il motivo clinico (es. tendinopatia cronica, dolore al carico).\n"
        "3. **Referto**: Descrivi i reperti ecografici (morfologia, spessore, vascolarizzazione, calcificazioni, borsite).\n"
        "4. **Infiltrazione**: Descrivi la procedura. Usa questa frase standard se non diversamente specificato: "
        "'Disinfezione in campo sterile. Anestesia dei piani cutanei e sottocutanei seguita da infiltrazione peritendinea con mezza fiala di Diprofos 7 mg associata a 3 ml di Rapidocaina 1%.'\n"
        "5. **Conclusioni**: Sintesi della diagnosi e della procedura eseguita.\n\n"
        "Non inventare dati. Se mancano informazioni, sii generico ma professionale. "
        "Non includere saluti o firme nel testo generato (saranno nel template)."
    )

def get_user_prompt_achilles(data: dict) -> str:
    patient_name = data.get("patient_name", "N/A")
    patient_dob = data.get("patient_dob", "N/A")
    date = data.get("date", datetime.now().strftime("%d.%m.%Y"))
    indications = data.get("indications", "Non specificate")
    findings = data.get("findings", "Non specificati")
    side = data.get("side", "destro").lower()
    
    return (
        f"Paziente: {patient_name}, nato il {patient_dob}\n"
        f"Data procedura: {date}\n"
        f"Lato: {side}\n"
        f"Indicazioni fornite: {indications}\n"
        f"Reperti ecografici osservati: {findings}\n\n"
        "Genera il referto completo."
    )
