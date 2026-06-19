"""
utils/auth.py
bcrypt password hashing + Streamlit session management.
"""
import bcrypt
import streamlit as st
from database.db import create_user, get_user_by_username


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return False


def register(username, email, password):
    if get_user_by_username(username):
        return False, "Username already exists."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    create_user(username, email, hash_password(password))
    return True, "Account created! Please log in."


def login(username, password):
    user = get_user_by_username(username)
    if not user or not verify_password(password, user["password_hash"]):
        return False, "Invalid credentials."
    st.session_state.user = {"id": user["id"], "username": user["username"]}
    st.session_state.authenticated = True
    return True, "Welcome back!"


def logout():
    for k in ["user", "authenticated"]:
        st.session_state.pop(k, None)


def require_auth():
    """Guard for protected pages."""
    if not st.session_state.get("authenticated"):
        st.warning("🔒 Please log in from the Home page to access this module.")
        st.stop()
    return st.session_state.user