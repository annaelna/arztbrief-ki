import streamlit as st
import openai
from fpdf import FPDF
import tempfile
import os

st.set_page_config(page_title="KI-Arztbrief Generator", layout="centered")
st.title("🩺 KI-Arztbrief Generator")

openai.api_key = st.secrets["OPENAI_API_KEY"]

def create_letter_from_text(text):
    prompt = f"Erstelle einen strukturierten Arztbrief auf Deutsch aus diesen Stichpunkten:
{text}"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Du bist ein medizinischer Schreibassistent."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4,
        max_tokens=800
    )
    return response.choices[0].message.content.strip()

def save_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for line in text.split("\n"):
        pdf.multi_cell(0, 10, line)
    pdf_path = tempfile.mktemp(".pdf")
    pdf.output(pdf_path)
    return pdf_path

def transcribe_audio(file):
    import whisper
    model = whisper.load_model("base")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
        tmpfile.write(file.read())
        tmpfile_path = tmpfile.name
    result = model.transcribe(tmpfile_path, language="de")
    os.remove(tmpfile_path)
    return result["text"]

text_input = st.text_area("📝 Stichpunkte eingeben:", height=200)
audio_file = st.file_uploader("🎙️ Oder MP3-Datei hochladen:", type=["mp3"])

if st.button("📄 Arztbrief erstellen"):
    if audio_file:
        with st.spinner("Transkribiere Audiodatei..."):
            text_input = transcribe_audio(audio_file)
            st.text_area("✍️ Transkribierter Text:", text_input, height=150)
    if text_input.strip() != "":
        with st.spinner("Erstelle Arztbrief..."):
            letter = create_letter_from_text(text_input)
            st.success("✅ Arztbrief erstellt")
            st.text_area("📄 Vorschau:", letter, height=300)
            pdf_path = save_pdf(letter)
            with open(pdf_path, "rb") as file:
                st.download_button("⬇️ PDF herunterladen", file, file_name="arztbrief.pdf")
    else:
        st.error("Bitte Stichpunkte eingeben oder Audiodatei hochladen.")
