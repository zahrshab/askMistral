import streamlit as st
import requests
import json
import emoji
import regex
import re
import random
import threading
from datetime import datetime

st.set_page_config(page_title="Ask Mistral", page_icon="🧠")

if "suggestions" not in st.session_state:
    try:
        with open("suggestions.json", "r") as file:
            st.session_state["suggestions"] = json.load(file)
    except:
        st.session_state["suggestions"] = []

def save_json(filepath, data):
    with open(filepath, "r+") as file:
        file.seek(0)
        json.dump(data, file, indent=2)
        file.truncate()

def edit_history():
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

def extract_questions(text):
    return re.findall(r"\d+\.\s(.*?\?)", text)

st.title("🧠 AskMistral – Your local AI")

if "suggestion_prompt" not in st.session_state:
    st.session_state["suggestion_prompt"] = None

column1, column2 = st.columns([2, 1])
with st.sidebar:
    col1, col2 = st.columns([3, 1.2])

    with col1:
        st.markdown("### Recently asked")
        edit_history()

    with col2:
        if st.button("Reset"):
            with open("prompts.json", "w") as file:
                json.dump([], file, indent=2)
            st.rerun()

emoji_detector = ",start your answer with a related emoji"

def extract_first_emoji_and_text(text):
    graphemes = regex.findall(r'\X', text)

    for i, g in enumerate(graphemes):
        if emoji.is_emoji(g):
            return g, ''.join(graphemes[i+1:]).lstrip()

    return None, text

def write_answer(user_input, answer, emoji):
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

def generateQuestions():
    user_input = "Generate 3 questions"
    try:
        response = requests.post(
            "http://localhost:8000/ask", 
            json={"prompt": user_input}
        )
        result = response.json()
        questions = extract_questions(result["response"])
        return questions
    except Exception as e:
        st.error(f"An error occured: {e}")

def pickThreeSuggestions():
    with open("suggestions.json", "r") as file:
        data = json.load(file)
    return data[:3]

def question(user_input):
    st.session_state["suggestion_prompt"] = None
    try:
        response = requests.post(
            "http://localhost:8000/ask", 
            json={"prompt": user_input + emoji_detector}
        )
        result = response.json()
        emoji, answer = extract_first_emoji_and_text(result["response"])
        # answer_without_emoji = result["response"][index + 1:]
        write_answer(user_input, answer, emoji)
    except Exception as e:
        st.error(f"An error occured: {e}")


with column1: 
    user_input = st.text_area("What do you want to ask Mistral?", "")
    if st.button("Ask"):
        if user_input.strip() != "":
            with st.spinner("Mistral is thinking..."):
                question(user_input)

def substitute_oneQuestion(new_question, identifier):
    st.session_state["suggestion_index"] = None

    if 0 <= identifier < len(st.session_state["suggestions"]):
        st.session_state["suggestions"][identifier]["prompt"] = new_question
        save_json("suggestions.json", st.session_state["suggestions"])


def substitute_allQuestions(questions):
    data = [{"prompt": question} for question in questions]
    save_json("suggestions.json", data)

def suggestions(): 
    left, right = st.columns([2, 1])
    with left:
        st.markdown("Frequently asked questions")
    with right:
        if st.button("new", key="generate_new_questions"):
            questions = generateQuestions()
            data = [{"prompt": question} for question in questions]
            st.session_state["suggestions"] = data
            save_json("suggestions.json", st.session_state["suggestions"])

    for index, item in enumerate(st.session_state["suggestions"][:3]):
        if st.button(item["prompt"], key=f"suggest_{item['prompt']}_{index}"):
            st.session_state["suggestion_prompt"] = item["prompt"]
            st.session_state["suggestion_index"] = index
        
with column2: 
    suggestions()

if st.session_state["suggestion_prompt"]:
    with column1:
        with st.spinner("Mistral is thinking..."):
            result_container = {}

            def get_questions():
                result_container["questions"] = generateQuestions()

            thread = threading.Thread(target=get_questions)
            thread.start()
            question(st.session_state["suggestion_prompt"])
            thread.join()

            questions = result_container.get("questions", [])
            if questions:
                substitute_oneQuestion(questions[0], st.session_state["suggestion_index"])
