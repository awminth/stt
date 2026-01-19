import io
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydub import AudioSegment
import speech_recognition as sr

app = FastAPI()

# CORS Setting (React ကနေ ခေါ်လို့ရအောင်)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

recognizer = sr.Recognizer()

@app.post("/stt")
async def speech_to_text(file: UploadFile = File(...)):
    try:
        # ၁။ အသံဖိုင်ကို Memory (BytesIO) ထဲသို့ တိုက်ရိုက်ဖတ်ယူခြင်း
        audio_bytes = await file.read()
        audio_buffer = io.BytesIO(audio_bytes)

        # ၂။ Pydub သုံးပြီး Buffer ထဲက data ကို AudioSegment အဖြစ်ပြောင်းခြင်း
        # (ဒါကြောင့် format က webm ဖြစ်ဖြစ် mp3 ဖြစ်ဖြစ် အကုန်အလုပ်လုပ်ပါတယ်)
        audio = AudioSegment.from_file(audio_buffer)

        # ၃။ SpeechRecognition က WAV format ပဲ သိတာကြောင့် 
        # Memory ပေါ်မှာတင် WAV အဖြစ် ပြန်ထုတ်ယူ (Export) ခြင်း
        wav_buffer = io.BytesIO()
        audio.export(wav_buffer, format="wav")
        wav_buffer.seek(0) # Buffer ရဲ့ အစမှတ်ကို ပြန်သွားရန်

        # ၄။ Recognition ပြုလုပ်ခြင်း
        with sr.AudioFile(wav_buffer) as source:
            audio_data = recognizer.record(source)
            # မြန်မာဘာသာစကား (my-MM) ဖြင့် ပြောင်းလဲခြင်း
            text = recognizer.recognize_google(audio_data, language="my-MM")

        return {"status": "success", "text": text}

    except sr.UnknownValueError:
        raise HTTPException(status_code=400, detail="အသံကို စာသားအဖြစ် ပြောင်းမရပါ")
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
if __name__ == "__main__":
    # Render အတွက် Port ကို environment variable မှ ဖတ်ယူခြင်း
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)