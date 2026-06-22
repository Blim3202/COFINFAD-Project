import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from groq import Groq  # Direct Groq API
import os

# Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

st.set_page_config(page_title="Dataframe Analyzer with Groq")
st.title("🤖 Ask Your Dataframe Questions")

# Initialize Groq client
client = Groq(api_key=groq_api_key)

# File uploader
uploaded_file = st.file_uploader("Upload your data (CSV file)", type=["csv"])

if uploaded_file is not None:
    # Read the uploaded CSV into a pandas DataFrame
    df = pd.read_csv(uploaded_file)
    st.write("### Data Preview", df.head())

    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Uploaded file. How can I help you with this data?"}
        ]
        st.session_state.df_info = df.head(10).to_string()
    
    # Display previous chat messages
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    # Chat input for user questions
    if prompt := st.chat_input("Ask a question about the data..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        # Build conversation history for context
        system_prompt = f"""You are a data analysis assistant. Analyze the following data and answer the user's question.

Data (first 10 rows):
{st.session_state.df_info}

Important: Use the conversation history below to maintain context and provide coherent responses.
"""

        # Build messages with full conversation history
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add all previous conversation history (excluding system prompts)
        for msg in st.session_state.messages:
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        try:
            # Get response from Groq
            response = client.chat.completions.create(
                model="qwen/qwen3-32b",
                messages=messages,
                temperature=0.5,
                max_tokens=1024,
            )
            
            assistant_response = response.choices[0].message.content
            
            # Display and store response
            st.chat_message("assistant").write(assistant_response)
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})

        except Exception as e:
            st.error(f"An error occurred: {e}")