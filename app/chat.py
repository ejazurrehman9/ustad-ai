# ─────────────────────────────────────────────
# Model Definitions
# ─────────────────────────────────────────────
GEMINI_MODEL = "gemini-1.5-flash"
# Groq par llama-3.1-8b-instant Sab se Stable Model Hai
GROQ_MODELS = ["llama-3.1-8b-instant", "mixtral-8x7b-32768", "llama3-8b-8192"]

def _stream_ai(messages: list, max_tokens: int = 1500):
    """Generator: Safely streams from Gemini, falls back to Groq models, prevents ASGI crashes."""
    
    # 1. Try Gemini First
    if GEMINI_KEY:
        try:
            genai.configure(api_key=GEMINI_KEY)
            model = genai.GenerativeModel(
                model_name=GEMINI_MODEL,
                system_instruction=next((m["content"] for m in messages if m["role"] == "system"), None)
            )
            history = []
            for m in messages:
                if m["role"] == "system":
                    continue
                role = "user" if m["role"] == "user" else "model"
                history.append({"role": role, "parts": [m["content"]]})
                
            if history:
                last = history.pop()
                chat = model.start_chat(history=history)
                for chunk in chat.send_message(last["parts"][0], stream=True,
                                               generation_config={"max_output_tokens": max_tokens}):
                    if chunk.text:
                        yield chunk.text
                return
        except Exception as e:
            print(f"[Gemini Stream Failed, Fallback to Groq]: {e}")

    # 2. Try Groq Models sequentially with localized try-except
    if GROQ_KEYS:
        for model in GROQ_MODELS:
            try:
                client = _get_groq_client()
                s = client.chat.completions.create(
                    model=model, max_tokens=max_tokens, messages=messages, stream=True
                )
                for chunk in s:
                    text = chunk.choices[0].delta.content or ""
                    if text:
                        yield text
                return  # Stream completed successfully
            except Exception as e:
                # Catch 404, Rate limits or network errors gracefully
                print(f"[Groq Model Error - Skipping '{model}']: {e}")
                continue

    # 3. Final Fallback Message if All Models Fail
    yield "⚠️ Server busy hai. Please thodi der baad dobara try karein."