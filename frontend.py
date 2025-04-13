import streamlit as st
import requests
import json
import emoji
import regex
from datetime import datetime

st.set_page_config(page_title="Ask Mistral", page_icon="🧠")

st.sidebar.title("History")
# st.sidebar.button("Klik hier")

st.title("🧠 AskMistral – Your local AI")

user_input = st.text_area("What do you want to ask Mistral?", "")
emoji_detector = ",start your answer with a related emoji"

# def extract_first_emoji_and_text(text):
#     for i, char in enumerate(text[:5]):
#         if emoji.is_emoji(char):
#             return char, i, text[i+1:].lstrip()
#     return None, text  # fallback: geen emoji gevonden

def extract_first_emoji_and_text(text):
    # Split text into grapheme clusters
    graphemes = regex.findall(r'\X', text)

    for i, g in enumerate(graphemes):
        if emoji.is_emoji(g):
            return g, ''.join(graphemes[i+1:]).lstrip()

    return None, text

if st.button("Ask"):
    if user_input.strip() != "":
        with st.spinner("Mistral is thinking..."):
            try:
                response = requests.post(
                    "http://localhost:8000/ask", 
                    json={"prompt": user_input + emoji_detector}
                )
                result = response.json()
                emoji, answer = extract_first_emoji_and_text(result["response"])
                # answer_without_emoji = result["response"][index + 1:]
                st.markdown("### 💬 Answer:")
                st.write(answer)
                with open("prompts.json", "r+") as file:
                    try:
                        data = json.load(file)
                    except json.JSONDecodeError:
                        data = []

                    data.append({
                        "prompt": user_input,
                        "response": answer,
                        "saved_emoji": emoji,
                        "timestamp": datetime.now().isoformat()
                    })
                    file.seek(0)
                    json.dump(data, file, indent=2)
            except Exception as e:
                st.error(f"An error occured: {e}")

with open("prompts.json", "r") as file:
    prompts = json.load(file)
    for item in prompts:
        if len(item["prompt"]) > 17:
            extra = "..."
        else: 
            extra = ""
        sneakpeek = item["prompt"][:17]
        extracted_emoji = item["saved_emoji"]
        # emojis_only = [char for char in text if emoji.is_emoji(char)]
        with st.sidebar.expander(f"{extracted_emoji} Question: {sneakpeek + extra}"):
            st.write("Question:", item["prompt"])
            st.write("Answer:", item["response"])
            st.write("Timestamp:", item["timestamp"])