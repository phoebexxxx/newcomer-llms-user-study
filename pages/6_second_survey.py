import streamlit as st

# ✅ Protect this page
if not st.session_state.get("move_on_2"):
    st.warning("Please complete the main study before proceeding.")
    st.stop()


st.set_page_config(page_title="In-Task Surveys", layout="wide")
st.title("🧠 In-Task Surveys")

st.markdown("""
We now ask you to complete **the following survey** about your experience during the second task.
""")

# Replace with your real Qualtrics survey URLs
survey_1_url = "https://umn.qualtrics.com/jfe/form/SV_cInILnxV2n9YNgi"

st.markdown("### 📋 Survey: User Experience Survey")
st.components.v1.iframe(src=survey_1_url, height=500, width=800, scrolling=True)


if st.button("Next"):
    st.session_state.second_survey_done = True  # ✅ set the flag
    st.switch_page("pages/7_conclusion.py")  
