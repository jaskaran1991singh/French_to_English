
import streamlit as st
import os
from pathlib import Path
from openai import OpenAI
import dotenv
from PIL import Image
import pytesseract


dotenv.load_dotenv()

# Load API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2")
LANGCHAIN_ENDPOINT = os.getenv("LANGCHAIN_ENDPOINT")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT")

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["LANGCHAIN_ENDPOINT"] = LANGCHAIN_ENDPOINT
os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY
os.environ["LANGCHAIN_PROJECT"] = LANGCHAIN_PROJECT
os.environ["LANGCHAIN_TRACING_V2"] = str(LANGCHAIN_TRACING_V2)

# Create the 'output_images' directory if it doesn't exist
os.makedirs('output', exist_ok=True)

# generate session id
def generate_session_id():
    # return str(uuid.uuid4())
    from datetime import datetime
    # Get the current datetime
    current_datetime = datetime.now()

    # Convert to string representation in seconds since epoch
    current_datetime_in_seconds = str(int(current_datetime.timestamp()))
    return current_datetime_in_seconds

# creating session id
if "session_id" not in st.session_state:
    st.session_state["session_id"] = generate_session_id()
session_id = st.session_state["session_id"]


# wide page width
st.set_page_config(layout="wide")

st.title("French: Image-to-Speech")

col1, col2 = st.columns([2, 1])
with col1:
  # Predefined image options
  image_options = {"Sample 1": "sample_images/french_text1.jpg", "Sample 2": "sample_images/french_text2.jpg"}
  selected_option = st.selectbox("Choose an image or upload your own:", list(image_options.keys()) + ["Upload your own"])

  uploaded_file = None
  image_path = None
  if selected_option == "Upload your own":
      uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
      if uploaded_file is not None:
          image_path = Path(f"output/{session_id}_uploaded_image.png")
          with open(image_path, "wb") as f:
              f.write(uploaded_file.getbuffer())
  else:
      image_path = Path(image_options[selected_option])


  # with col1:
  if image_path and st.button("Create Voice",type='primary'):
      out_image = f"output/{session_id}_out.jpg"
      with st.spinner("Converting Image to text..."):
          # results = arabicocr.arabic_ocr(str(image_path), out_image)
          # Perform OCR
          # Open the image
          image = Image.open(str(image_path))
          extracted_text = pytesseract.image_to_string(image, lang="fra", config="--tessdata-dir /usr/share/tesseract-ocr/4.00/tessdata/")
      # words = [result[1] for result in results]
      # extracted_text = " ".join(words)

      with open(f"output/{session_id}_extracted_text.txt", "w", encoding="utf-8") as text_file:
          text_file.write(extracted_text)

      st.subheader("Extracted Text:")
      st.write(extracted_text)

      # Convert text to speech
      client = OpenAI()
      audio_path = f"output/{session_id}_speech.mp3"
      with st.spinner("Converting text to speech..."):
          with client.audio.speech.with_streaming_response.create(
              model="tts-1", voice="onyx", input=extracted_text
          ) as response:
              response.stream_to_file(audio_path)

      st.audio(audio_path, format="audio/mp3")

with col2:
  if image_path:
      st.image(str(image_path), use_container_width=True)

