import streamlit as st

"""
======================================================================
APISweeper Premium Web Dashboard (Streamlit)
Assigned to: Jatin
======================================================================

Jatin: Write the frontend code here using Streamlit!
Since we are using Python for the frontend now, you don't need HTML/JS.
Just use `st.title()`, `st.button()`, etc. to build the cybersecurity dashboard.

To run this dashboard locally, run:
    streamlit run ui.py
"""

st.set_page_config(page_title="APISweeper Dashboard", page_icon="🛡️", layout="wide")

st.title("🛡️ APISweeper")
st.write("Lightweight DAST Scanner for REST APIs")

st.markdown("---")
st.subheader("New Scan")
target_url = st.text_input("Target API URL", placeholder="http://localhost:5001/api/v1")
auth_token = st.text_input("Auth Token (Optional)", type="password")

if st.button("Launch Scan", type="primary"):
    if not target_url:
        st.error("Please enter a target URL.")
    else:
        with st.spinner("Scanning target..."):
            # Jatin: Here you will integrate the backend API call to the scanner engine
            # and render the results using st.success(), st.warning(), etc.
            st.info("Scanner integration goes here!")
