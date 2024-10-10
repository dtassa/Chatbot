import streamlit as st
import requests
import json
# Streamlit app title
st.title('Residential Mortgage Virtual Assistant - Demo')

# Initialize conversation history and user name
if 'history' not in st.session_state:
    st.session_state.history = []
if 'user_name' not in st.session_state:
    st.session_state.user_name = None
if 'last_answer' not in st.session_state:
    st.session_state.last_answer = ""

# Introduce the bot
if st.session_state.user_name is None:
    st.write("Hi, I am Talia, your property virtual assistant.")
    user_name = st.text_input("Please can I have your name?:", key="name_input")
    
    if user_name:
        st.session_state.user_name = user_name
        st.session_state.history.append({"question": "", "answer": f"Hello {user_name}! How can I assist you today?"})
else:
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_question = st.text_input("Ask a question:", key="user_input", on_change=lambda: st.session_state.update({"submit": True}))
    
    with col2:
        submit_button = st.button("Submit", key="submit_button")
    
    # Function to get response from the chatbot API
    def get_chatbot_response(user_input):
        API_URL = "https://c0jtsdy5ch.execute-api.us-east-1.amazonaws.com/prod/docs"
        headers = {'Content-Type': 'application/json'}
        data = {
            "question": user_input,
            "modelId": "anthropic.claude-3-sonnet-20240229-v1:0"
        }
        
        try:
            response = requests.post(API_URL, headers=headers, data=json.dumps(data), timeout=10)
            if response.status_code == 200:
                return response.json().get("response", "Sorry, I don't understand.")
            else:
                return f"Error: {response.status_code}, could not get a response from the chatbot."
        except requests.exceptions.Timeout:
            return "Error: Request timed out. Please try again."
        except Exception as e:
            return f"Error: {e}"

    # If the user submits a question
    if st.session_state.get('submit') or submit_button:
        st.session_state.submit = False
        if user_question:
            answer = get_chatbot_response(user_question)
            
            # Store the question and answer in history
            st.session_state.history.append({"question": user_question, "answer": answer})

            # Display the answer
            st.write(answer)
            
            # Update last answer in session state
            st.session_state.last_answer = answer

    # Add feedback buttons
    if st.session_state.last_answer:
        feedback_col1, feedback_col2 = st.columns(2)
        with feedback_col1:
            thumbs_up = st.button("👍", key="thumbs_up")
        with feedback_col2:
            thumbs_down = st.button("👎", key="thumbs_down")
        
        # Handle feedback
        if thumbs_up or thumbs_down:
            feedback = "Correct" if thumbs_up else "Wrong"
            st.write(f"Thank you for your feedback! You marked the answer as: {feedback}")

# CSS for chat bubbles
st.markdown("""
<style>
.chat-container {
    display: flex;
    flex-direction: column;
    margin-bottom: 20px;
}
.user-bubble {
    background-color: #008000;
    border-radius: 15px;
    padding: 10px;
    margin: 5px;
    align-self: flex-end; /* User messages on the right */
    max-width: 80%;
}
.assistant-bubble {
    background-color: #808000;
    border-radius: 15px;
    padding: 10px;
    margin: 5px;
    align-self: flex-start; /* Assistant messages on the left */
    max-width: 80%;
}
</style>
""", unsafe_allow_html=True)

# Display conversation history in bubbles
if st.session_state.history:
    for chat in st.session_state.history:
        user_bubble = f"<div class='user-bubble'>**{st.session_state.user_name}:** {chat['question']}</div>" if chat['question'] else ""
        assistant_bubble = f"<div class='assistant-bubble'>**Talia:** {chat['answer']}</div>" if chat['answer'] else ""
        st.markdown(f"<div class='chat-container'>{user_bubble}{assistant_bubble}</div>", unsafe_allow_html=True)
