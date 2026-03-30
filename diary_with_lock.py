import streamlit as st
import json
import os
from datetime import datetime
from cryptography.fernet import Fernet

# ---------------- SETTINGS ----------------
REAL_PASSWORD = "1234"
FAKE_PASSWORD = "0000"
MAX_ATTEMPTS = 3

# ---------------- ENCRYPTION KEY ----------------
if not os.path.exists("key.key"):
    key = Fernet.generate_key()
    with open("key.key", "wb") as f:
        f.write(key)
else:
    with open("key.key", "rb") as f:
        key = f.read()

fernet = Fernet(key)

# ---------------- FUNCTIONS (MOVE HERE ✅) ----------------
def load_data(filename):
    if os.path.exists(filename):
        with open(filename, "rb") as f:
            encrypted = f.read()
            try:
                decrypted = fernet.decrypt(encrypted).decode()
                return json.loads(decrypted)
            except:
                return []
    return []

def save_data(filename, data):
    encrypted = fernet.encrypt(json.dumps(data).encode())
    with open(filename, "wb") as f:
        f.write(encrypted)

# ---------------- SESSION STATE ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "mode" not in st.session_state:
    st.session_state.mode = "real"

if "attempts" not in st.session_state:
    st.session_state.attempts = 0

if "locked" not in st.session_state:
    st.session_state.locked = False

# ---------------- LOCK SCREEN ----------------
if st.session_state.locked:
    st.error("🚫 SYSTEM LOCKED")
    st.title("Too many wrong attempts 😳")
    st.stop()

# ---------------- LOGIN SCREEN ----------------
if not st.session_state.logged_in:
    st.title("🔐 Secure Diary Login")

    password = st.text_input("Enter Password", type="password")

    if st.button("Unlock"):
        if password == REAL_PASSWORD:
            st.session_state.logged_in = True
            st.session_state.mode = "real"
            st.success("Access Granted 🔓")

        elif password == FAKE_PASSWORD:
            st.session_state.logged_in = True
            st.session_state.mode = "fake"
            st.warning("Fake Mode Activated 🎭")

        else:
            st.session_state.attempts += 1
            st.error(f"Wrong Password ❌ Attempts: {st.session_state.attempts}")

            if st.session_state.attempts >= MAX_ATTEMPTS:
                st.session_state.locked = True
                st.rerun()

# ---------------- MAIN DIARY ----------------
else:
    st.title("💻 Secret Diary System")

    if st.session_state.mode == "real":
        file = "real_diary.dat"
        st.success("Real Diary Mode 🔓")
    else:
        file = "fake_diary.dat"
        st.info("Fake Diary Mode 🎭")

    data = load_data(file)

    st.subheader("✍️ Write New Entry")
    entry = st.text_area("Write your secret...")

    if st.button("Save Entry"):
        if entry.strip():
            new_entry = {
                "text": entry,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            data.append(new_entry)
            save_data(file, data)
            st.success("Encrypted & Saved 🔒")
        else:
            st.warning("Please write something first 😅")

    st.subheader("📖 Your Entries")
    if data:
        for i, e in enumerate(reversed(data)):
            st.markdown(f"**{i+1}. {e['time']}**")
            st.write(e["text"])
            st.write("---")
    else:
        st.write("No entries yet...")

    st.subheader("⚠️ Danger Zone")
    if st.button("Delete All Data"):
        save_data(file, [])
        st.warning("All data deleted 😳")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.attempts = 0
        st.rerun()