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

# Load the session variables - should be loaded from the app
transactions = st.session_state.transactions
customers = st.session_state.customers 

# Add session state for chat
if "followup_question" not in st.session_state:
    st.session_state.followup_question = ""

# Function to set follow-up question
def set_followup_question(question):
    st.session_state.followup_question = question

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

# This will generate follow up messages based on the user query and chat history
def generate_followup_questions(user_query, chat_history):
    # Extract conversation history for context
    conversation = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history])
    
    # Prompt for generating follow-up questions
    prompt = f"""
    Conversation History:
    {conversation}

    The user's latest question: "{user_query}".
    Generate 3 follow-up questions about the data that are relevant to the user's query and the conversation context.
    ONLY provide the respond choice. Drop ALL preamble and beginning text. Drop any numbering.
    Example:
    What is the total amount spent on this customer
    What transaction types are there
    When was this transaction made
    """

    try:
        # Use Groq to generate follow-up questions
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant", #Super lightweight model under the same groq API
            messages=[{"role": "system", "content": prompt}],
            temperature=0.7,
            max_tokens=110,
        )
        followup_questions = response.choices[0].message.content.strip().split("\n")
        return followup_questions[:3]  # Limit to 3 questions
    except Exception as e:
        st.error(f"Failed to generate follow-up questions: {e}")
        return []

if transactions is not None and customers is not None: # Dataframes copied over cleanly

    #Preview the data
    st.write("### Transaction Data Preview", transactions.head(10))
    st.write("### Customer Data Preview", customers.head(10))

    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Uploaded file. How can I help you with this data?"}
        ]
        
        # Load only the first 10 rows
        st.session_state.transactions_info = transactions.head(10).to_string()
        st.session_state.customers_info = customers.head(10).to_string()
        
        # Store thinking separately if needed
        st.session_state.thinking = {}
    
       # Check for follow-up question before displaying messages 
    if st.session_state.followup_question:
        followup_prompt = st.session_state.followup_question
        st.session_state.followup_question = ""  # Clear it
        
        # Add the follow-up question as a user message
        st.session_state.messages.append({"role": "user", "content": followup_prompt})
        
        # Process the follow-up question (same logic as main question)
        # Build conversation history for context
        system_prompt = f"""You are a data analysis assistant. Analyze the following data and briefly answer the user's question.
        
        Transactions Data (first 10 rows):
        {st.session_state.transactions_info}

        Customer Data (first 10 rows):
        {st.session_state.customers_info}

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
                # model="qwen/qwen3-32b",
                # model="groq/compound-mini", # more free tokens per minute
                model="meta-llama/llama-4-scout-17b-16e-instruct", # Evem more free tokens per minute
                messages=messages,
                temperature=0.5,
                max_tokens=1024,
            )
            
            assistant_response = response.choices[0].message.content

            # Process the response
            thinking, final_answer = process_response(assistant_response)

            # Store and display thinking
            msg_index = len(st.session_state.messages)
            if thinking:
                st.session_state.thinking[msg_index] = thinking

            # Add assistant response to messages
            st.session_state.messages.append({"role": "assistant", "content": final_answer})

        except Exception as e:
            st.error(f"An error occurred: {e}")



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
        system_prompt = f"""You are a data analysis assistant. Analyze the following data and briefly answer the user's question.
        
        Transactions Data (first 10 rows):
        {st.session_state.transactions_info}

        Customer Data (first 10 rows):
        {st.session_state.customers_info}

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
                # model="qwen/qwen3-32b",
                # model="groq/compound-mini", # more free tokens per minute
                model="meta-llama/llama-4-scout-17b-16e-instruct" , # Evem more free tokens per minute
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

            ####: Generate and display follow-up questions ###
            followup_questions = generate_followup_questions(prompt, st.session_state.messages)
            if followup_questions:
                st.write("**Suggested Follow-Up Questions:**")
                cols = st.columns(len(followup_questions))
                for idx, question in enumerate(followup_questions):
                    if question:
                        cols[idx].button(
                            question,
                            key=f"followup_{idx}_{question[:20]}",
                            on_click=lambda q=question: set_followup_question(q)
                        )

        except Exception as e:
            st.error(f"An error occurred: {e}")