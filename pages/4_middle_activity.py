import streamlit as st

# ✅ Protect this page
if not st.session_state.get("first_survey_done"):
    st.warning("Please complete the first survey before proceeding.")
    st.stop()


st.set_page_config(page_title="Mini Activity", layout="wide")
st.title("🐶🐱 Mini Activity")

st.markdown("""
We now ask you to complete **the following survey**.
""")

# Replace with your real Qualtrics survey URLs
survey_1_url = "https://umn.qualtrics.com/jfe/form/SV_7PbLnukk3xAii7Y "

st.components.v1.iframe(src=survey_1_url, height=500, width=800, scrolling=True)


if st.button("Next"):
    st.session_state.neutral_done = True  # ✅ set the flag
    st.switch_page("pages/5_second_study.py") 