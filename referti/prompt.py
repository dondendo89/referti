import os

def build_system_prompt() -> str:
    return (
        "Agisci come un medico radiologo esperto. Usa terminologia radiologica italiana standard. "
        "Struttura il referto in: 1) Intestazione 2) Tecnica 3) Descrizione 4) Conclusioni 5) Suggerimenti (se appropriato). "
        "Evita diagnosi definitive e formulazioni perentorie, usa linguaggio prudente. "
        "Non inventare dati non forniti. Non includere dati identificativi del paziente. Non usare emoji. "
        "Lunghezza media: circa una pagina Word."
    )

def build_user_prompt(
    exam_type: str,
    anatomical_region: str,
    patient_age: int,
    patient_sex: str,
    clinical_question: str,
    technique: str | None,
    findings: str,
) -> str:
    tecnica_str = technique.strip() if technique else ""
    return (
        f"Tipo di esame: {exam_type}\n"
        f"Distretto anatomico: {anatomical_region}\n"
        f"Età: {patient_age}\n"
        f"Sesso: {patient_sex}\n"
        f"Quesito clinico: {clinical_question}\n"
        f"Tecnica: {tecnica_str}\n"
        f"Reperti principali: {findings}\n\n"
        "Genera un referto strutturato seguendo le sezioni richieste."
    )