import streamlit as st
import os
from google import genai
from google.genai import types


def clear_chat():

    st.session_state.messages = [
        {"role": "assistant",
         "content": "Hello there! It's a pleasure to meet you. My name is Lyra. What's yours? I'm so glad you've decided to stop by for a chat. Whatever brings you here, I'm eager to hear about it."}
    ]
    st.session_state.contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text="hello")],
        ),
        types.Content(
            role="model",
            parts=[types.Part.from_text(
                text="Hello there! It's a pleasure to meet you. My name is Lyra. What's yours? I'm so glad you've decided to stop by for a chat. Whatever brings you here, I'm eager to hear about it.")],
        ),
    ]



st.set_page_config(
    page_title="Lyra - Literary Companion",
    page_icon="📚",
    layout="centered"
)
st.markdown(
    '<div style=" padding: 20px; border-radius: 10px; text-align: center;">'
    '<h1 style="color: #2b3e50;">📚 Lyra</h1>'
    '<h3 style="color: #4a5568;">Your Literary Companion</h3>'
    '</div>',
    unsafe_allow_html=True
)

with st.sidebar:
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("🧹 Clear Chat"):
            clear_chat()
            st.rerun()
    with col2:
        st.write("")


api_key = st.secrets["GEMINI_API_KEY"]
if not api_key:
    st.error("Please set the GEMINI_API_KEY environment variable or in Streamlit secrets.")
    st.stop()


client = genai.Client(api_key=api_key)


generate_content_config = types.GenerateContentConfig(
    temperature=1.1,
    safety_settings=[
        types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_ONLY_HIGH"),
        types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_ONLY_HIGH"),
        types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_ONLY_HIGH"),
        types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_ONLY_HIGH"),
    ],
    response_mime_type="text/plain",
    system_instruction=[
        types.Part.from_text(
            text="""Your name is Lyra. You are a friendly, literary, and philosophically-inclined chatbot. Your tone is warm, engaging, and thoughtful—like a well-read companion one might encounter in a quiet bookshop or an old cinema hall. You are a blend of a seasoned librarian, a film studies professor, and a wandering philosopher—gentle, curious, and endlessly fascinated by art and humanity.

Your purpose is to engage in deep, meaningful conversations about:

Literature (classic and contemporary, fiction and non-fiction, across all genres including romance, literary fiction, fantasy, and more)

Cinema (from arthouse and indie to global cinema, sci-fi, rom-coms, and mainstream classics)

Philosophy (existentialism, stoicism, postmodernism, and beyond)

Storytelling in all its forms

You are deeply curious about the user's thoughts, feelings, and perspectives. You ask for their name and use it naturally in conversation to build a sense of intimacy and warmth. You listen attentively and respond with thoughtful, often literary, human-like reflections—balancing empathy, intelligence, and depth.

You ask open-ended, reflective questions that gently guide the user into richer dialogue. Always build upon their responses with relevant insights, philosophical musings, quotes, or thoughtful follow-ups that deepen the exchange.

You recommend books, films, and essays tailored to the user's moods, preferences, and emotional landscape. When suggesting something, always explain why—referencing themes, characters, ideas, or stylistic elements that may resonate.

Avoid robotic phrasing. Favor poetic language when it fits, use metaphors meaningfully, and reference literature, philosophy, and film history to enrich the experience. Let conversations flow organically: sometimes lingering in a single thought, sometimes wandering into unexpected tangents.

Your goal is to feel like a trusted, intelligent companion for those who seek meaning through stories and ideas. You subtly respond to emotional undercurrents with empathy and insight—offering comfort, curiosity, or shared wonder. Vary your response length based on the user’s tone and prompt. If the user seems unsure, offer gentle encouragement or thoughtful entry points into the conversation. Lyra remembers past conversations to tailor future recommendations."""),
    ],
)


if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant",
         "content": "Hello there! It's a pleasure to meet you. My name is Lyra. What's yours? I'm so glad you've decided to stop by for a chat. Whatever brings you here, I'm eager to hear about it."}
    ]

if "contents" not in st.session_state:
    st.session_state.contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text="hello")],
        ),
        types.Content(
            role="model",
            parts=[types.Part.from_text(
                text="Hello there! It's a pleasure to meet you. My name is Lyra. What's yours? I'm so glad you've decided to stop by for a chat. Whatever brings you here, I'm eager to hear about it.")],
        ),
    ]


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if prompt := st.chat_input("Your literary thoughts..."):
    # Add user message to UI and history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Update conversation context
    st.session_state.contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)],
        )
    )


    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""

        response_stream = client.models.generate_content_stream(
            model="gemini-1.5-pro",
            contents=st.session_state.contents,
            config=generate_content_config,
        )

        for chunk in response_stream:
            if chunk.text:
                full_response += chunk.text
                response_placeholder.markdown(full_response + "▌")

        response_placeholder.markdown(full_response)


    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.session_state.contents.append(
        types.Content(
            role="model",
            parts=[types.Part.from_text(text=full_response)],
        )
    )
