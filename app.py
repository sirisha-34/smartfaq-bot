import streamlit as st
from chatbot import FAQBot
from voice_input import recognize_speech
import pandas as pd
import json
import sqlite3
import os

faq_file = "faq_data.csv"
if not os.path.exists(faq_file):
    pd.DataFrame(columns=['Question', 'Answer']).to_csv(faq_file, index=False)

bot = FAQBot(faq_file)

conn = sqlite3.connect("chat_logs.db", check_same_thread=False)
c = conn.cursor()
c.execute("""
    CREATE TABLE IF NOT EXISTS chat (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT, question TEXT, answer TEXT, feedback TEXT
    )
""")
conn.commit()

if not os.path.exists("feedback.json"):
    with open("feedback.json", "w") as f:
        json.dump({}, f)

def update_feedback(q, helpful):
    with open("feedback.json", "r") as f:
        fb = json.load(f)
    if q not in fb:
        fb[q] = {"👍": 0, "👎": 0}
    fb[q]["👍" if helpful else "👎"] += 1
    with open("feedback.json", "w") as f:
        json.dump(fb, f)

st.title("🤖 SmartFAQ Bot")
st.write("Ask me anything about our services.")

if "user_input" not in st.session_state:
    st.session_state["user_input"] = ""

col1, col2 = st.columns([3, 1])
with col1:
    typed_input = st.text_input("Your question", value=st.session_state["user_input"], key="typed_input")
with col2:
    if st.button("🎤 Speak"):
        st.session_state["user_input"] = recognize_speech()
        st.success(f"You said: {st.session_state['user_input']}")

final_input = typed_input or st.session_state["user_input"]

if final_input:
    q, a, score = bot.find_best_match(final_input)
    st.markdown(f"**Matched FAQ:** {q}")
    st.success(a)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("👍 Was this helpful?"):
            update_feedback(q, True)
            c.execute("INSERT INTO chat (user, question, answer, feedback) VALUES (?, ?, ?, ?)",
                      ("user", final_input, a, "👍"))
            conn.commit()
    with col2:
        if st.button("👎 Not helpful"):
            update_feedback(q, False)
            c.execute("INSERT INTO chat (user, question, answer, feedback) VALUES (?, ?, ?, ?)",
                      ("user", final_input, a, "👎"))
            conn.commit()

st.markdown("---")
st.subheader("➕ Add new FAQ")
new_q = st.text_input("New Question")
new_a = st.text_area("New Answer")
if st.button("Add FAQ") and new_q and new_a:
    bot.add_faq(new_q, new_a)
    st.success("Added!")

st.markdown("---")
st.subheader("📊 Chat History")
history = pd.read_sql_query("SELECT * FROM chat ORDER BY id DESC", conn)

if not history.empty:
    history_display = history[["question", "answer", "feedback"]]
    history_display.columns = ["User Question", "Bot Answer", "Feedback"]
    st.dataframe(history_display, use_container_width=True)
else:
    st.info("No chat history found yet.")

st.markdown("---")
st.sidebar.subheader("📤 Export FAQs")
if st.sidebar.button("Download FAQ CSV"):
    df = pd.read_csv(faq_file)
    csv = df.to_csv(index=False).encode("utf-8")
    st.sidebar.download_button("📄 Download", csv, "exported_faqs.csv", "text/csv")
