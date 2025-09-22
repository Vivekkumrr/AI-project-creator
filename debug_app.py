import streamlit as st
from auth import authenticate_user, register_user, create_access_token, verify_token
from datetime import timedelta

# Simple test without any complex logic
st.title("Debug Test")

# Test authentication
st.write("Testing authentication...")
test_user = authenticate_user("test", "test")
st.write(f"Auth test: {test_user}")

# Test token creation
if test_user:
    token = create_access_token({"sub": "test"})
    st.write(f"Token created: {bool(token)}")
    verified = verify_token(token)
    st.write(f"Token verified: {verified}")

# Test response function
from llm_handler import advanced_llm_response
test_response = advanced_llm_response("hello", 1)
st.write(f"LLM Response: {test_response}")

st.write("Debug completed")