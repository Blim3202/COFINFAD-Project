import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from groq import Groq  # Direct Groq API
import os
import re

# Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

st.set_page_config(page_title="Dataframe Analyzer with Groq")
st.title("🤖 Ask Your Dataframe Questions")

# Initialize Groq client
client = Groq(api_key=groq_api_key)


# Custom CSS for better thinking display
st.markdown("""
<style>
    .thinking-container {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
        font-size: 0.9em;
        color: #666;
    }
    .thinking-container details {
        cursor: pointer;
    }
    .thinking-container summary {
        font-weight: bold;
        color: #333;
    }
</style>
""", unsafe_allow_html=True)


# File uploader
uploaded_file = st.file_uploader("Upload your data (CSV file)", type=["csv"])

# Build the thinking dropdown button to hide thinking for the specific model used which in this case is "qwen/qwen3-32b"
def process_response(text):
    """Extract thinking and final answer from response"""
    # Pattern to match <think>...</think> tags
    think_pattern = r'<think>(.*?)</think>'
    
    # Find all thinking sections
    think_matches = re.findall(think_pattern, text, re.DOTALL)
    
    if think_matches:
        # Combine all thinking sections
        thinking = "\n\n".join([match.strip() for match in think_matches])
        # Remove all think tags from the main text
        final_answer = re.sub(think_pattern, '', text, flags=re.DOTALL).strip()
        return thinking, final_answer
    else:
        return None, text

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
        
        # Store thinking separately if needed
        st.session_state.thinking = {}
    
    # Display previous chat messages
    for i, msg in enumerate(st.session_state.messages):
        st.chat_message(msg["role"]).write(msg["content"])
        
        # If this was an assistant message with thinking, show it
        if msg["role"] == "assistant" and i in st.session_state.thinking:
            with st.expander("🧠 Thinking process", expanded=False):
                st.write(st.session_state.thinking[i])
            
    # Chat input for user questions
    if prompt := st.chat_input("Ask a question about the data..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        # Build conversation history for context
        system_prompt = f"""You are a data analysis assistant. Analyze the following data and answer the user's question.

        Data (first 10 rows):
        {st.session_state.df_info}

        Important: 
        1. Use the conversation history below to maintain context.
        2. If you need to reason through the problem, put your reasoning between <think> and </think> tags. This will be hidden from the final answer.
        3. Provide your final, concise answer after the thinking process.
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

            # Process the response
            thinking, final_answer = process_response(assistant_response)

            # Display thinking in expander
            msg_index = len(st.session_state.messages)
            if thinking:
                with st.expander("🧠 Thinking process", expanded=False):
                    st.write(thinking)
                st.session_state.thinking[msg_index] = thinking

           # Display final answer
            st.chat_message("assistant").write(final_answer)
            st.session_state.messages.append({"role": "assistant", "content": final_answer})

        except Exception as e:
            st.error(f"An error occurred: {e}")