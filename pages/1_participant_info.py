import streamlit as st

# protect page 
if not st.session_state.get("welcome_done"): 
    st.warning("Please read the welcome page (home) before proceeding.")
    st.stop()


st.set_page_config(page_title="Participant Info", layout="centered")
st.title("👤 Participant Information")

# Initialize session state
if "participant_id" not in st.session_state:
    st.session_state.participant_id = ""
if "group" not in st.session_state:
    st.session_state.group = ""

st.markdown("""
You should receive your participant ID and group information from the researcher. If not, please ask the researcher now.
""")


# Input fields
st.session_state.participant_id = st.text_input("Enter your Participant ID:", st.session_state.participant_id)
st.session_state.group = st.selectbox("Select your Group:", ["", "Group A", "Group B", "Group C", "Group D"])
# Group A: first [scaffolding + task 1], then [baseline + task 2]
# Group B: first [scaffolding + task 2], then [baseline + task 1]
# Group C: first [baseline + task 1], then [scaffolding + task 2]
# Group D: first [baseline + task 2], then [scaffolding + task 1]

# Navigation
if st.session_state.participant_id and st.session_state.group:
    st.success("✅ Please click the button to continue.")
    if st.button("Next"):
        st.switch_page("pages/2_first_study.py")  
else:
    st.warning("Please complete both fields to continue.")
