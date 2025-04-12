import streamlit as st
import requests

st.set_page_config(page_title="Ask Mistral", page_icon="🧠")

st.title("🧠 AskMistral – Your local AI")

user_input = st.text_area("What do you want to ask Mistral?", "")

if st.button("Ask"):
    if user_input.strip() != "":
        with st.spinner("Mistral is thinking..."):
            try:
                response = requests.post(
                    "http://localhost:8000/ask", 
                    json={"prompt": user_input}
                )
                result = response.json()
                st.markdown("### 💬 Answer:")
                st.write(result["response"])
            except Exception as e:
                st.error(f"An error occured: {e}")