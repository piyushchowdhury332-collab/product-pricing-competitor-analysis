import streamlit as st
from portal_auth import (
    init_db, register_user, authenticate_user, start_session
)

init_db()

st.title("Pricing Intelligence Portal")
st.caption("Product Pricing & Competitor Analysis")
st.divider()

mode = st.radio("Choose an option", ["Login", "Create Account"], horizontal=True)

if mode == "Login":
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login", use_container_width=True)

    if submitted:
        user = authenticate_user(username, password)
        if user:
            st.session_state["user_id"] = user["id"]
            st.session_state["username"] = user["username"]
            st.session_state["session_id"] = start_session(user["id"])
            st.success("Login successful.")
            st.rerun()
        else:
            st.error("Incorrect username or password.")

else:
    with st.form("signup_form"):
        username = st.text_input("Choose a username")
        email = st.text_input("Email address")
        password = st.text_input("Create password", type="password")
        confirm = st.text_input("Confirm password", type="password")
        submitted = st.form_submit_button("Create Account", use_container_width=True)

    if submitted:
        if password != confirm:
            st.error("The passwords do not match.")
        else:
            success, message = register_user(username, email, password)
            if success:
                st.success(message)
            else:
                st.error(message)

st.divider()
st.caption("Your password is stored as a salted hash, not as plain text.")
