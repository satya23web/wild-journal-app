
import streamlit as st
from PIL import Image
import google.generativeai as genai
import io
from datetime import datetime

# --- CONFIGURATION ---
# WARNING: This is not secure. Do not share this code with your key in it.
GEMINI_API_KEY = "AIzaSyCRdlCXs3v1jZbfPHjGTXEqNU-jWn7EoIQ"

try:
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    st.error("🚨 There was an issue configuring the Gemini API key. Please ensure it is correct.")
    st.stop()

# --- GEMINI HELPER FUNCTION ---
def get_gemini_response(image_bytes, prompt):
    """
    Sends the image and a prompt to the Gemini API and returns the text response.
    """
    try:
        pil_image = Image.open(io.BytesIO(image_bytes))
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content([prompt, pil_image])
        return response.text
    except Exception as e:
        st.error(f"An error occurred with the Gemini API: {e}")
        return None

# --- STREAMLIT APP LAYOUT ---
st.set_page_config(page_title="Wildlife Journal", layout="centered")
st.title("🇦🇺 Wildlife Journal ")
st.write("Upload a photo of an Australian animal or plant to have Gemini identify it and add a note to your journal.")

# CHANGED: Initialize new session state variables to cache the result
if 'journal_entries' not in st.session_state:
    st.session_state.journal_entries = []
if 'gemini_response' not in st.session_state:
    st.session_state.gemini_response = None
if 'last_uploaded_filename' not in st.session_state:
    st.session_state.last_uploaded_filename = None

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Your Uploaded Image", use_container_width=True)

    # CHANGED: Only call the API if a NEW file is uploaded
    if uploaded_file.name != st.session_state.last_uploaded_filename:
        st.session_state.last_uploaded_filename = uploaded_file.name # Remember the filename

        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format=image.format or 'JPEG')
        image_bytes = img_byte_arr.getvalue()

       prompt = """
You are an expert Australian wildlife biologist with a talent for writing engaging journal entries. Analyze the provided photograph, which was taken in Australia.

Please provide a detailed report using the following markdown structure:

### [Common Name]
*(Scientific Name)*

**Physical Characteristics:**
* **Size:** [Provide its typical height/length and weight.]
* **Appearance:** [Describe its key colors, markings, and other distinguishing features.]

**Behavior & Diet:**
* **Behavior:** [Is it nocturnal? Solitary or social? Mention any unique behaviors.]
* **Diet:** [What does it primarily eat?]

**Habitat:**
* [Describe its natural environment and where it's typically found in Australia.]

**Conservation Status:**
* [Provide its status, for example: Native to Australia, Common, Endangered, etc.]

**Journalist's Note:**
* [Write one fascinating fact or a short, engaging summary perfect for a nature journal entry.]

If the image is unclear, contains no identifiable wildlife, or features a non-native domestic animal (like a cat or dog), please state that clearly instead of providing the structured report.
"""
        with st.spinner("Let's see what it is... 🧐"):
            # Store the response in session state
            st.session_state.gemini_response = get_gemini_response(image_bytes, prompt)

    # Display the analysis and journal section if a response exists
    if st.session_state.gemini_response:
        st.subheader("Internet's Analysis:")
        st.write(st.session_state.gemini_response)

        st.subheader("Add a Journal Entry")
        note = st.text_area("Your notes, thoughts, and location:", key=f"note_{uploaded_file.name}")

        if st.button("Save to Journal", key=f"save_{uploaded_file.name}"):
            if note:
                st.session_state.journal_entries.append({
                    "image": image,
                    "identification": st.session_state.gemini_response,
                    "note": note,
                    "timestamp": datetime.now()
                })
                st.toast("📝 Note saved to your journal!")
            else:
                st.warning("Please write a note before saving.")

# --- ROADMAP & JOURNAL LOG ---
# (The rest of your code for the roadmap and journal log remains the same)
# ...
st.header("🗺️ Your Discovery Roadmap")
if not st.session_state.journal_entries:
    st.info("Your roadmap will appear here as you save journal entries.")
else:
    for i, entry in enumerate(st.session_state.journal_entries):
        title = entry['identification'].split('\n')[0]
        st.markdown(f"**📍 Stop {i+1}: {entry['timestamp'].strftime('%Y-%m-%d %H:%M')}**")
        st.markdown(f"> _{title}_")
        if i < len(st.session_state.journal_entries) - 1:
            st.markdown("<p style='text-align: center; margin: 0;'>⬇️</p>", unsafe_allow_html=True)

st.markdown("---")

st.header("📖 Your Journal Log")
if not st.session_state.journal_entries:
    st.info("Your detailed journal entries will appear here.")
else:
    for i, entry in enumerate(reversed(st.session_state.journal_entries)):
        title = entry['identification'].split('\n')[0]

        st.caption(f"Logged at: {entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        st.image(entry['image'], use_container_width=True)
        st.write(f"** from internet:** {entry['identification']}")
        st.write(f"**Your Note:** {entry['note']}")
        st.markdown("---")
