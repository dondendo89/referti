import os
from openai import OpenAI
import google.generativeai as genai


def generate_report(system_prompt: str, user_prompt: str, model: str | None = None) -> str:
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        client = OpenAI(api_key=openai_key)
        use_model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        completion = client.chat.completions.create(
            model=use_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        return completion.choices[0].message.content.strip()

    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise RuntimeError("Nessuna API key configurata: impostare OPENAI_API_KEY o GEMINI_API_KEY")
    genai.configure(api_key=gemini_key)
    preferred = []
    if model:
        preferred.append(model)
    env_model = os.getenv("GEMINI_MODEL")
    if env_model:
        preferred.append(env_model)
    preferred.extend(["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]) 
    selected = None
    try:
        models = list(genai.list_models())
        supported = [m.name for m in models if "generateContent" in getattr(m, "supported_generation_methods", [])]
        for name in preferred:
            if name in supported:
                selected = name
                break
        if not selected and supported:
            selected = supported[0]
    except Exception:
        selected = preferred[0] if preferred else "gemini-1.5-flash"
    
    # Lista di modelli da provare in ordine
    candidates = []
    if selected:
        candidates.append(selected)
    
    # Aggiungi altri modelli di fallback se non sono già in lista
    fallbacks = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp"]
    for fb in fallbacks:
        if fb not in candidates and f"models/{fb}" not in candidates:
             candidates.append(fb)
             
    import time
    from google.api_core import exceptions

    last_error = None

    for model_name in candidates:
        try:
            # Pulisci il nome del modello se necessario
            clean_name = model_name if "/" in model_name else model_name
            model_obj = genai.GenerativeModel(clean_name, system_instruction=system_prompt)
            
            # Tentativo con retry breve per ogni modello
            max_retries = 2
            base_delay = 2
            
            for attempt in range(max_retries):
                try:
                    resp = model_obj.generate_content(user_prompt, generation_config={"temperature": 0.2})
                    return (resp.text or "").strip()
                except exceptions.ResourceExhausted as e:
                    # Se abbiamo esaurito le risorse su questo modello, passiamo al prossimo (break inner loop)
                    # a meno che non sia l'ultimo tentativo
                    last_error = e
                    if attempt < max_retries - 1:
                        time.sleep(base_delay * (2 ** attempt))
                    else:
                        # Fallito su questo modello, break per provare il prossimo candidato
                        break 
                except Exception as e:
                    # Altri errori: prova prossimo modello
                    last_error = e
                    break
        except Exception:
            continue
            
    # Se siamo qui, tutti i modelli hanno fallito
    if last_error:
        raise last_error
    return ""