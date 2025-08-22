import streamlit as st
import pandas as pd 
import io


if not st.session_state.get("second_survey_done"): 
    st.warning("Please complete follow up task before you conclude.")
    st.stop()


st.set_page_config(page_title="Final survey & Thank you", layout="wide")
st.title("🎉 Final survey & Thank you")

st.markdown("""
        Please reflect on your experiences with **WikiCoach** and **WikiAnswer**. Think about how each assistant supported (or didn’t support) your Wikipedia editing.
        Then, complete the **final survey**, where you’ll compare the two and share your overall preference.
        """)

# Replace with your real Qualtrics survey URLs
survey_1_url = "https://umn.qualtrics.com/jfe/form/SV_0AFcRPpLCt6hUmq"

st.markdown("### 📋 Survey: Final Survey")
st.components.v1.iframe(src=survey_1_url, height=500, width=800, scrolling=True)

if st.button("Next"): 
    st.markdown("""    
    🎉 Congratulations, you are all done! Thank you so much for participating in this study. Again, we truly value your participation.   
    """)
