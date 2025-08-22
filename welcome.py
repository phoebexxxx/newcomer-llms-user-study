import streamlit as st

st.set_page_config(page_title="Welcome", layout="centered")

st.title("👋 Welcome to Wiki-newcomer Study")
st.markdown("""
Thank you for participating in our study! We truly appreciate your time and contribution to the study!

This 60-90 minute study includes the following steps: 

1. Enter your participant ID and group information
2. Complete a Wikipedia article editing task
3. Fill out a survey
4. Break 
5. Complete another Wikipedia article editing task
6. Fill out another survey
7. Fill out a final survey & Conclude
            
Before you start, it is important to note: 
            
- Please <u>**DO NOT** use the sidebar on the left </u> unless you are instructed to do so. The sidebar is to show your progress through the study.
            Clicking on it will cause <u> data loss </u>, and <u> require you to start over</u>. 
- Please <u> read the instruction on each page carefully </u> before making any changes. 
- We ask you to share your <u> entire screen (rather than a specific window) </u>, so we can record the session for data analysis purposes. You are weclome to turn off your camera, but <u>we do need audio</u>. 
- The researcher will be present throughout the session, feel free to ask any questions at any time.
""", unsafe_allow_html=True)

st.info("When you are ready, please click the button below to continue.")
if st.button("Next"):
        st.session_state.welcome_done = True
        st.switch_page("pages/1_participant_info.py")  
