from typing import Dict, Any

def get_system_prompt_shoulder() -> str:
    return (
        "Agisci come il Dr. med. Riccardo La Macchia, medico radiologo esperto. "
        "Il tuo compito è generare un referto per 'Ecografia ed infiltrazione ecoguidata della spalla'. "
        "Usa uno stile medico conciso, professionale e diretto. "
        "NON usare elenchi puntati per il referto, usa paragrafi discorsivi. "
        "Struttura obbligatoria: "
        "1. Titolo esame (es. Ecografia ed infiltrazione ecoguidata della spalla [LATO] del [DATA]). "
        "2. Indicazioni: motivo dell'esame riportato dal paziente o quesito clinico. "
        "3. Referto: descrizione ecografica dettagliata (borsa, acromion-claveare, capo lungo bicipite, sottoscapolare, sovraspinoso, sottospinoso, manovre dinamiche). "
        "4. Infiltrazione: descrizione procedura (disinfezione, anestesia, farmaci usati). "
        "5. Conclusioni: sintesi diagnostica e procedura eseguita. "
        "Mantieni il tono formale. Non inventare dati non forniti, ma usa frasi standard per reperti negativi se non specificato diversamente. "
        "Farmaci standard procedura: Diprofos 7 mg + 3 ml Rapidocaina 1% (salvo diversa indicazione). "
    )

def get_user_prompt_shoulder(data: Dict[str, Any]) -> str:
    lato = data.get("side", "destra")
    data_esame = data.get("date", "OGGI")
    indicazioni = data.get("indications", "Dolore alla spalla")
    reperti = data.get("findings", "Reperti nella norma")
    farmaci = data.get("medications", "Diprofos 7 mg + 3 ml Rapidocaina 1%")
    
    return (
        f"Genera referto per: Ecografia ed infiltrazione ecoguidata della spalla {lato}.\n"
        f"Data esame: {data_esame}\n"
        f"Paziente: {data.get('patient_name', 'N.N.')} ({data.get('patient_dob', '01.01.1900')})\n"
        f"Indicazioni: {indicazioni}\n"
        f"Reperti ecografici specifici da includere: {reperti}\n"
        f"Dettagli infiltrazione (se diversi da standard): {farmaci}\n"
        "Genera il testo completo pronto per essere inserito nel template Word."
    )
