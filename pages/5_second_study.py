import streamlit as st
import pandas as pd 
import io
import openai
import datetime
import faiss
import json
import numpy as np
from sandbox import main_sand
from groups import groups
from rag import rag


# Optional: Protect this page
if not st.session_state.get("neutral_done"):
    st.warning("Please complete the middle activity before proceeding.")
    st.stop()


# Initialize session state
st.set_page_config(page_title="Second Session", layout="wide")
st.title("Wikipedia Editing Task")

# helper function to log data into a pandas dataframe 
def log_event(AorH, component, content):
    st.session_state.logs_second.append({
        "AorH": AorH,
        "PID": st.session_state["participant_id"], 
        "group": st.session_state["group"],
        "component": component,
        "timestamp": datetime.datetime.now().isoformat(),
        "content": content
    })


group = st.session_state.get("group")
# print(group)


GROUPS = {
    "Group A": groups.system_prompt_baseline(),
    "Group B": groups.system_prompt_baseline(),
    "Group C": groups.system_prompt_scaffolding(),
    "Group D": groups.system_prompt_scaffolding(),
}

NAMES = {
    "Group A": "WikiAnswer",
    "Group B": "WikiAnswer",
    "Group C": "WikiCoach",
    "Group D": "WikiCoach",
}

INITIALS = {
    "Group A": groups.initials_baseline(),
    "Group B": groups.initials_baseline(),
    "Group C": groups.initials_scaffolding(),
    "Group D": groups.initials_scaffolding(),
}

STAGE_PROMPTS = {
    "before edit": groups.scaffolding_before_task(),
    "during edit": groups.scaffolding_during_task(),
    "after edit": groups.scaffolding_after_task()
}

TASKS = {
    "Group A": groups.task_2(),
    "Group B": groups.task_1(),
    "Group C": groups.task_2(),
    "Group D": groups.task_1(),
}




initial = INITIALS[group]
system_prompt = GROUPS[group]
task = TASKS[group]
name = NAMES[group]

# assign Google Doc to work in 
p_id = st.session_state.get("participant_id")
MAIN_SAND = main_sand.main_sand(int(p_id)-1)

if group == "Group C" or group =="Group D":
    # Initialize session state
    if "stage_second" not in st.session_state or st.session_state.get("first_load_second", True):
        st.session_state.stage_second = "before edit"
        st.session_state.first_load_second = False

    # Floating badge (display only)
    st.markdown(
        f"""
        <div style="
            position: fixed;
            top: 90px;
            right: 40px;
            background-color: #0047ab;
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            box-shadow: 0px 4px 6px rgba(0,0,0,0.2);
            z-index: 9999;
            font-weight: bold;
        ">
            🟢 Stage: {st.session_state.stage_second}
        </div>
        """,
        unsafe_allow_html=True
    )

    # load index and chuncks once
    @st.cache_resource(show_spinner=False)
    def _load_rag():
        return rag.load_index_and_chunks()
    INDEX, CHUNKS = _load_rag()


    # initialize logs, count, messages
    if "logs_second" not in st.session_state:
        st.session_state.logs_second = []
    if "count_second" not in st.session_state:
        st.session_state.count_second = 0
    if "message_second" not in st.session_state:
        st.session_state.messages_second = [{"role": "assistant", "content": initial}]
    log_event(name, "before edit", initial)


    # Initialize OpenAI client
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    # Function to render messages
    def render_message(role, content):
        if role == "user":
            st.markdown(
                f"""
                <div style='background-color:#e6f0ff; padding:10px 15px; border-radius:10px; margin:10px 0;'>
                    <strong style='color:#0047ab;'>You:</strong><br>{content}
                </div>
                """, unsafe_allow_html=True
            )
        elif role == "assistant":
            st.markdown(
                f"""
                <div style='background-color:#eaffea; padding:10px 15px; border-radius:10px; margin:10px 0;'>
                    <strong style='color:#008000;'>{NAMES[group]}:</strong><br>{content}
                </div>
                """, unsafe_allow_html=True
            )


    # Layout with two columns
    left_col, right_col = st.columns([1.25, 1.25])


    # Left column: user editing sandbox
    with left_col:
        st.subheader("✍️ Your task: Contribute to Wikipedia as a new editor")

        st.markdown(f"""
        You will be working on a short Wikipedia article. Your job is to help improve this article by expanding it with content that aligns with *Wikipedia policies and guidelines*. 
                    
        **Your task:**  
        - Use **{NAMES[group]}**, an AI assistant on the right, to help you think and edit the task. Start <u>**the first few minutes**</u> interacting with **{NAMES[group]}**, 
                    and feel free to keep using it throughout this task. You can ask questions, explore ideas, or get feedback as you go.
        - Add ***some new information***. 
        This is not a personal writing assignment — the goal is <u>to practice making a Wikipedia-style contribution</u>.

        ⏰ You can stop when you feel comfortable with your edit.   
            
        **🚫 DON’Ts**
        - <u>**DO NOT** use other AI tools </u> like ChatGPT, Claude, Gemini. <u>**DO NOT** look at </u> AI generated summaries.
        - <u>**DO NOT open or read**</u> the same current Wikipedia article.  

        **✅ DOs**
        - Have ***at least 5 total interactions*** with the assistant **throughout the task**. (<u>*1 interaction = a question/request + the assistant’s response.*</u>)    
        - You are allowed to search for sources on your own, and include links for sources if you could. You don't need to format the sources.   
        - Submit whatever you have -- it's ok if your edit is not finished. We are interested in the process. 

        **NOTE**: The AI assistant DOES NOT have access to the Google doc (your edit space).            
        
        ---
        """, unsafe_allow_html=True)

        st.markdown("### 🧾 Current Article Content")
        st.markdown(task, unsafe_allow_html=True)


    # Right column: AI interaction
    with right_col:

        st.subheader(f"🤖 Chat with {NAMES[group]}, the AI assistant.")
        # st.write("WikiCoach is an AI helper for you to edit Wikipedia. It's designed both to help you complete edits, and learn about important Wikipedia policies and editing skills along the way. You can ask WikiCoach questions, follow up on its answers, or explore ideas together. The more you talk with it, the more helpful it can be. If the assistant didn't respond, it is likely because it didn't receive your message. Simply send your question or request again. It may take a moment for the assistant to think.")
        # st.markdown(
        # "<p style='color: red; font-weight: bold;'>Note: WikiCoach may behave differently from other AI you've used before.</p>",
        # unsafe_allow_html=True
        # )

        for message in st.session_state.messages_second:  # Skip system message
            render_message(message["role"], message["content"])
        
        st.selectbox(
            "Select your editing stage:",
            ["before edit", "during edit", "after edit"],
            index=["before edit", "during edit", "after edit"].index(st.session_state.stage_second),
            key="stage"
        )

        user_input = st.text_area("Enter your question or request:", key="user_input", height=100)
        use_rag = st.toggle("Use policy-aware RAG grounding", value=True, help="Adds relevant Wikipedia policy context to answers")

        if st.button("Send"):
            if user_input.strip() == "":
                st.warning("Please enter a prompt.")
            else:
                st.session_state.messages_second.append({"role": "user", "content": user_input})
                log_event("human", st.session_state.stage_second, user_input) 

                stage_system_prompt = STAGE_PROMPTS.get(st.session_state.stage_second)
                log_event(name, st.session_state.stage_second, stage_system_prompt)

                with st.spinner("Wiki-helper AI is thinking..."):
                    try:
                        context_block = ""
                        if use_rag:
                            qvec = rag.embed_query(user_input, client)  # embed user query
                            retrieved = rag.search(INDEX, CHUNKS, qvec, top_k=3)    # retrieve most relevant chuncks
                            context_block = rag.format_context(retrieved)     # tag with source document
                            log_event("AI", "rag", context_block)     # log event

                        history = st.session_state.messages_second

                        msgs = rag.make_rag_messages(
                            system_prompt=GROUPS[group],
                            stage_prompt=stage_system_prompt,
                            history=history,
                            user_input=user_input,
                            context_block=context_block
                        )

                        response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=msgs,
                        
                        )

                        assistant_reply = response.choices[0].message.content
                        st.session_state.messages_second.append({"role": "assistant", "content": assistant_reply})
                        log_event(name, st.session_state.stage_second, assistant_reply)
                        st.session_state.count_second = st.session_state.count_second + 1      # enforce users to have at least 6 interactions (interaction = input + response)

                    except Exception as e:
                        st.error(f"An error occurred: {e}")

                st.rerun()


    st.markdown("""
                
    ---
    """)

else:

    # initialize logs, count, messages
    if "logs_second" not in st.session_state:
        st.session_state.logs_second = []
    if "count_second" not in st.session_state:
        st.session_state.count_second = 0
    if "messages_second" not in st.session_state:
        st.session_state.messages_second = []
    log_event(name, "before edit", initial)


    # Initialize OpenAI client
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


    # Function to render messages
    def render_message(role, content):
        if role == "user":
            st.markdown(
                f"""
                <div style='background-color:#e6f0ff; padding:10px 15px; border-radius:10px; margin:10px 0;'>
                    <strong style='color:#0047ab;'>You:</strong><br>{content}
                </div>
                """, unsafe_allow_html=True
            )
        elif role == "assistant":
            st.markdown(
                f"""
                <div style='background-color:#eaffea; padding:10px 15px; border-radius:10px; margin:10px 0;'>
                    <strong style='color:#008000;'>{NAMES[group]}:</strong><br>{content}
                </div>
                """, unsafe_allow_html=True
            )

    # Layout with two columns
    left_col, right_col = st.columns([1.25, 1.25])


    # Left column: user editing sandbox
    with left_col:
        st.subheader("✍️ Your task: Contribute to Wikipedia as a new editor")

        st.markdown(f"""
        You will be working on a short Wikipedia article. Your job is to help improve this article by expanding it with content that aligns with *Wikipedia policies and guidelines*. 
                    
        **Your task:**  
        - Use **{NAMES[group]}**, an AI assistant on the right, to help you think and edit the task. Start <u>**the first few minutes**</u> interacting with **{NAMES[group]}**, 
                    and feel free to keep using it throughout this task. You can ask questions, explore ideas, or get feedback as you go.
        - Add ***some new information***. 
        This is not a personal writing assignment — the goal is <u>to practice making a Wikipedia-style contribution</u>.

        ⏰ You can stop when you feel comfortable with your edit.   
            
        **🚫 DON’Ts**
        - <u>**DO NOT** use other AI tools </u> like ChatGPT, Claude, Gemini. <u>**DO NOT** look at </u> AI generated summaries.
        - <u>**DO NOT open or read**</u> the same current Wikipedia article.  

        **✅ DOs**
        - Have ***at least 5 total interactions*** with the assistant **throughout the task**. (<u>*1 interaction = a question/request + the assistant’s response.*</u>)    
        - You are allowed to search for sources on your own, and include links for sources if you could. You don't need to format the sources.   
        - Submit whatever you have -- it's ok if your edit is not finished. We are interested in the process. 

        **NOTE**: The AI assistant DOES NOT have access to the Google doc (your edit space).            
        
        ---
        """, unsafe_allow_html=True)

        st.markdown("### 🧾 Current Article Content")
        st.markdown(task, unsafe_allow_html=True)


    # Right column: AI interaction
    with right_col:

        st.subheader(f"🤖 Chat with {NAMES[group]}, the AI assistant.")
        # st.write("WikiCoach is an AI helper for you to edit Wikipedia. It's designed both to help you complete edits, and learn about important Wikipedia policies and editing skills along the way. You can ask WikiCoach questions, follow up on its answers, or explore ideas together. The more you talk with it, the more helpful it can be. If the assistant didn't respond, it is likely because it didn't receive your message. Simply send your question or request again. It may take a moment for the assistant to think.")
        # st.markdown(
        # "<p style='color: red; font-weight: bold;'>Note: WikiCoach may behave differently from other AI you've used before.</p>",
        # unsafe_allow_html=True
        # )

        for message in st.session_state.messages_second:  # Skip system message
            render_message(message["role"], message["content"])
        
        user_input = st.text_area("Enter your question or request:", key="user_input", height=100)

        if st.button("Send"):
            if user_input.strip() == "":
                st.warning("Please enter a prompt.")
            else:
                st.session_state.messages_second.append({"role": "user", "content": user_input})
                log_event("human", st.session_state.stage_second, user_input) 


                with st.spinner("Wiki-helper AI is thinking..."):
                    try:

                        response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=st.session_state.messages_second,
                        
                        )

                        assistant_reply = response.choices[0].message.content
                        st.session_state.messages_second.append({"role": "assistant", "content": assistant_reply})
                        log_event(name, st.session_state.stage_second, assistant_reply)
                        st.session_state.count_second = st.session_state.count_second + 1      # enforce users to have at least 6 interactions (interaction = input + response)

                    except Exception as e:
                        st.error(f"An error occurred: {e}")

                st.rerun()


    st.markdown("""
                
    ---
    """)


st.markdown("### 📝 Your Editing Sandbox")

# try google docs

st.markdown(
    f"""
    <iframe src="{MAIN_SAND}?embedded=true"
            width="100%" height="700" frameborder="0">
    </iframe>
    """,
    unsafe_allow_html=True
)


# Session state setup
if "submitted_second" not in st.session_state:
    st.session_state.submitted_second = False
if "can_continue_second" not in st.session_state:
    st.session_state.can_continue_second = False

# Submit button (stage 1)
if st.button("Submit Draft") and not st.session_state.submitted_second:
    if st.session_state.get("count_second") >= 5:
        st.session_state.submitted_second = True
    else:
        st.markdown(
            "<div style='text-align: center; color: #856404; background-color: #fff3cd; "
            "padding: 1em; border-radius: 5px; border: 1px solid #ffeeba;'>"
            f"Please have at least {5 - st.session_state.count_second} more interactions with AI agent."
            "</div>",
            unsafe_allow_html=True
        )

# Step 2: show download if submitted
if st.session_state.submitted_second:
    st.markdown("""
    Before proceeding, please make sure to download the logs from the following button,
    and send them to the researcher at the end of the study. Feel free to keep a copy with you as well.
    """)

    if "logs_second" in st.session_state and st.session_state.logs_second:
        df = pd.DataFrame(st.session_state.logs_second)
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)

        downloaded = st.download_button(
            label="📁 Download Interaction Log",
            data=csv_buffer.getvalue(),
            file_name=f"interaction_log{p_id}.csv",
            mime="text/csv"
        )

        # When download button is clicked, allow continuing
        if downloaded:
            st.session_state.can_continue_second = True
    else:
        st.info("No interaction logs found.")

# Step 3: Continue button
if st.session_state.can_continue_second:
    if st.button("✅ Continue to Survey"):
        st.session_state.move_on_2 = True
        st.switch_page("pages/6_second_survey.py")
