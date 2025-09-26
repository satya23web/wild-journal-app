
import streamlit as st
from PIL import Image
import google.generativeai as genai
import io
from datetime import datetime

# --- CONFIGURATION ---
# WARNING: This method is not secure. Your key is visible.
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
st.title("🇦🇺 Wildlife Journal")
st.write("Upload a photo of an Australian animal or plant to identify it and add a note to your journal.")

# Initialize session state variables
if 'journal_entries' not in st.session_state:
    st.session_state.journal_entries = []
if 'gemini_response' not in st.session_state:
    st.session_state.gemini_response = None
if 'last_uploaded_filename' not in st.session_state:
    st.session_state.last_uploaded_filename = None

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Your Uploaded Image", width='stretch')
    
    if uploaded_file.name != st.session_state.last_uploaded_filename:
        st.session_state.last_uploaded_filename = uploaded_file.name
        
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format=image.format or 'JPEG')
        image_bytes = img_byte_arr.getvalue()

        prompt = """
Alright, imagine you're an on-the-ground Australian conservation biologist, out in the field, passionate about what you do, and you've just snapped this photo. Your goal is to write a compelling, informative journal entry that sounds genuinely human, highlights the species, and clearly articulates its conservation story to someone who cares.

Please structure your observations and insights using the following markdown format:

### [Common Name]
*(Scientific Name)*

**About This Amazing Creature:**
* **Size & Looks:** [Give a vivid description of its typical size, key colors, markings, and what makes it visually unique. Make it sound like you're describing it to a friend.]
* **Lifestyle & Diet:** [Describe its typical behavior – is it shy, bold, active at night? What's its routine? And what does it love to munch on? Keep it engaging.]

**Where They Call Home:**
* [Describe its natural habitat. Where would you typically stumble upon this creature in Australia?]

**Their Story - A Call for Action:**
* **Conservation Status:** [What's its official status (e.g., Endangered, Vulnerable, etc.) and, in your own words, why is it in this situation? What are the main challenges it's facing?]
* **What We're Doing & How You Can Help:** [Explain some active conservation efforts. More importantly, what can an everyday person do to make a difference? Think practical, impactful steps.]

If the image is too blurry, doesn't clearly show wildlife, or if it's just a domestic animal (like a pet dog or cat), please politely say you couldn't identify a native species for the journal this time.
"""


        with st.spinner("Let's see what it is... 🧐"):
            st.session_state.gemini_response = get_gemini_response(image_bytes, prompt)

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
st.header("🗺️ Your Discovery Roadmap")
if not st.session_state.journal_entries:
    st.info("Your roadmap will appear here as you save journal entries.")
else:
    for i, entry in enumerate(st.session_state.journal_entries):
        title = entry['identification'].split('\n')[0]
        st.markdown(f"**📍 Stop {i+1}: {entry['timestamp'].strftime('%Y-m-%d %H:%M')}**")
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
        st.subheader(f"Entry #{len(st.session_state.journal_entries) - i}: {title}")
        st.caption(f"Logged at: {entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        st.image(entry['image'], width='stretch')
        st.write(f"**Gemini's Description:** {entry['identification']}")
        st.write(f"**Your Note:** {entry['note']}")
        st.markdown("---")
