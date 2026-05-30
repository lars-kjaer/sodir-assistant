import sys
import os
import streamlit as st

# Make the agent importable
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from agent.text_to_sql import generate_sql, run_query, format_answer

st.set_page_config(page_title="SODIR Assistant", page_icon="🛢️")

st.title("🛢️ SODIR Assistant")
st.caption("Ask questions about Norwegian Continental Shelf petroleum data")

# Initialise chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render past messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sql"):
            with st.expander("View generated SQL"):
                st.code(message["sql"], language="sql")

# Handle new input
if prompt := st.chat_input("e.g. How many wellbores are in the Barents Sea?"):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate and show answer
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            sql = ""
            try:
                sql = generate_sql(prompt)
                columns, rows = run_query(sql)
                if not rows:
                    answer = "No results found."
                else:
                    answer = format_answer(prompt, columns, rows)
            except Exception as e:
                answer = f"Something went wrong: {e}"

        st.markdown(answer)
        if sql:
            with st.expander("View generated SQL"):
                st.code(sql, language="sql")

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sql": sql,
    })