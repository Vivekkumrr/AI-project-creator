import streamlit as st
from datetime import timedelta

from auth import (
    authenticate_user, 
    register_user, 
    create_access_token, 
    verify_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from database import get_db_connection
from llm_handler import advanced_llm_response
from project_manager import get_user_projects

def save_chat_history(user_id, message, response):
    """Save chat history to database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chat_history (user_id, message, response) VALUES (?, ?, ?)",
        (user_id, message, response)
    )
    conn.commit()
    conn.close()

def get_chat_history(user_id):
    """Retrieve chat history for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT message, response, timestamp FROM chat_history WHERE user_id = ? ORDER BY timestamp DESC LIMIT 10",
        (user_id,)
    )
    history = cursor.fetchall()
    conn.close()
    return history

def main():
    st.set_page_config(page_title="LLM Project Creator", page_icon="🤖", layout="wide")
    
    # Initialize session state
    if 'token' not in st.session_state:
        st.session_state.token = None
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    # Check if user is logged in
    if st.session_state.token:
        try:
            payload = verify_token(st.session_state.token)
            if payload:
                st.session_state.user = payload
            else:
                st.session_state.token = None
                st.session_state.user = None
        except:
            st.session_state.token = None
            st.session_state.user = None
    
    # Show appropriate page based on auth status
    if st.session_state.user:
        show_chat_interface()
    else:
        show_auth_interface()

def show_auth_interface():
    """Show authentication interface"""
    st.title("🤖 LLM Project Creator")
    st.write("Please log in or register to start creating projects with AI")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            st.subheader("Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_btn = st.form_submit_button("Login")
            
            if login_btn:
                user = authenticate_user(username, password)
                if user:
                    access_token = create_access_token(
                        data={"sub": user["username"], "user_id": user["user_id"]},
                        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                    )
                    st.session_state.token = access_token
                    st.session_state.user = user
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
    
    with tab2:
        with st.form("register_form"):
            st.subheader("Register")
            new_username = st.text_input("New Username")
            new_email = st.text_input("Email")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            register_btn = st.form_submit_button("Register")
            
            if register_btn:
                if new_password != confirm_password:
                    st.error("Passwords don't match!")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters long")
                else:
                    success = register_user(new_username, new_email, new_password)
                    if success:
                        st.success("Registration successful! Please log in.")
                    else:
                        st.error("Username or email already exists")

def show_chat_interface():
    """Show chat interface for authenticated users"""
    st.title(f"🤖 AI Project Creator - Welcome {st.session_state.user['sub']}!")
    
    # Sidebar for user projects
    with st.sidebar:
        st.header("Your Projects")
        projects = get_user_projects(st.session_state.user["user_id"])
        
        if projects:
            for project in projects:
                st.write(f"**{project[1]}** ({project[2].replace('_', ' ')})")
                st.caption(f"Created: {project[4]}")
                st.divider()
        else:
            st.info("You haven't created any projects yet. Try asking me to create one!")
    
    # Logout button
    if st.button("Logout"):
        st.session_state.token = None
        st.session_state.user = None
        st.rerun()
    
    # Project creation tips
    with st.expander("💡 How to create projects"):
        st.write("""
        You can ask me to create projects or agents using natural language. For example:
        - "Create a web application for task management"
        - "Build a data analysis agent for sales data"
        - "I need a chatbot for customer support"
        - "Develop an automation agent for social media posting"
        """)
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Load previous chat history
    if not st.session_state.messages:
        history = get_chat_history(st.session_state.user["user_id"])
        for message, response, _ in reversed(history):
            st.session_state.messages.append({"role": "user", "content": message})
            st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("What would you like to create or ask?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = advanced_llm_response(prompt, st.session_state.user["user_id"])
                st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Save to database
        save_chat_history(st.session_state.user["user_id"], prompt, response)

if __name__ == "__main__":
    main()