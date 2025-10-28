import streamlit as st
from openai import OpenAI
from helper import read_text_file
import time
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(	page_title="ZygfrydChat", page_icon="💬")
st.title("💬 Zygfryd ChatBot")

if "setup_complete" not in st.session_state:
		st.session_state.setup_complete = False
if "user_message_count" not in st.session_state:
		st.session_state.user_message_count = 0
if "chat_complete" not in st.session_state:
		st.session_state.chat_complete = False  
if "thank_feedback" not in st.session_state:
		st.session_state.thank_feedback = False
if "messages" not in st.session_state:
		st.session_state.messages = []

def setup_complete():
		st.session_state.setup_complete = True

def chat_complete():
		st.session_state.chat_complete = True

def show_thank_feedback():
		st.session_state.thank_feedback = True

def start_chat():
    all_filled = all([
        st.session_state.first_name.strip(),
        # st.session_state.last_name.strip(),
        st.session_state.company.strip(),
        st.session_state.position.strip(),
        st.session_state.role.strip(),
        st.session_state.level.strip()
    ])
    if not all_filled:
        st.session_state.show_warning = True
    else:
        st.session_state.show_warning = False
        with st.spinner("Initializing chat… Please wait a moment."):
            time.sleep(1)  # Simulate some setup time
            st.session_state.setup_complete = True

if not st.session_state.setup_complete:
  st.subheader("Before we start out conversation, please fill out some info about yourself:", divider ='rainbow')
  if "first_name" not in st.session_state:
    st.session_state.first_name = ""
  # if "last_name" not in st.session_state:
  #   st.session_state.last_name = ""
  if "company" not in st.session_state:
    st.session_state.company = ""
  if "position" not in st.session_state:
    st.session_state.position = ""
    
  col1_personal_details, col2_personal_details = st.columns(2)
  with col1_personal_details:
    st.session_state["first_name"] = st.text_input(label="First name", value=st.session_state.first_name, placeholder="Enter your first name or nickname", max_chars= 40)
    #st.session_state["last_name"] = st.text_input(label="Last name", value=st.session_state.last_name, placeholder="Enter your last name", max_chars= 40)
  with col2_personal_details:
    st.session_state["position"] = st.text_input(label="Job title", value=st.session_state.position, placeholder="Enter your job title", max_chars= 40 )
    st.session_state["company"] = st.text_input(label="Company", value=st.session_state.company, placeholder="Enter company you work for", max_chars= 40 )
  st.subheader("And lastly, what role are you hiring for?", 
							divider ='rainbow')
  if "role" not in st.session_state:
    st.session_state.role = "Frontend Developer"
  if "level" not in st.session_state:
    st.session_state.level = "Regular"
  col1, col2 = st.columns(2)
  with col1:
    st.session_state["role"] = st.selectbox( "Role(s) you are hiring for", ("AI Data Engineer", "Frontend Developer", "Backend Developer", "Full Stack Engineer", "Business Analyst", "Other"))
    if st.session_state["role"] == "Other":
      st.session_state["role"] = st.text_input(	label="Please specify the role you are hiring for", value=st.session_state.role, placeholder="Enter Other role", max_chars= 40,)
  with col2:
    st.session_state["level"] = st.radio("Seniority Level", options=["Junior", "Mid-level", "Regular", "Senior", "Tech Lead"])
  if "show_warning" not in st.session_state:
    st.session_state.show_warning = False
  st.button("Start Conversation", on_click=start_chat)
  if st.session_state.show_warning:
    st.warning("Please fill all fields before starting the chat.") 
# HERE SOME SPINNER?
if st.session_state.setup_complete and not st.session_state.chat_complete and not st.session_state.thank_feedback:

  st.info("""
    You can ask me anything related to Sebastian Wieczorek's professional background.
    But please note that our conversation is limited to 5 exchanges.
    """, icon="💡"
  )

  client = OpenAI(api_key=st.secrets["OPEN_API_KEY"])

  if "open_model" not in st.session_state:
      st.session_state.open_model = "gpt-4o"
  #text_temp = f'"""\nThe user first name is {first_name}, last name is {last_name}, works at {company} as {position}. The user is hiring for the role of {role} at {level} level."""'
  system_message = system_message =  st.secrets["ZYGFRYD_SYSTEM_MESSAGE"]
    #read_text_file("system_message.txt")

  if not st.session_state.messages:
      st.session_state.messages = [
        {"role": "system",
         "content": f"{system_message} User's name: {st.session_state.first_name} works at {st.session_state.company} as {st.session_state.position}. The user is hiring for the role of {st.session_state.role} at {st.session_state.level} level."
         },
        {"role": "assistant", 
        "content": f"Hello {st.session_state.first_name}! I am Zygfryd. Sebastian's Assistant. How can I help you today?"}
        ]

  for message in st.session_state.messages:
      if message["role"] != "system" and message["role"] != "developer":
          with st.chat_message(message["role"]):
              st.markdown(message["content"])
  if st.session_state.user_message_count < 5:
    if prompt := st.chat_input("Type your message here...", max_chars = 100):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        if st.session_state.user_message_count < 4:
          with st.chat_message("assistant"):
              stream = client.chat.completions.create(
                  model=st.session_state.open_model,
                  messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                  stream=True
              )
              response = st.write_stream(stream) 
          st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.user_message_count += 1
        if st.session_state.user_message_count >= 5:
          chat_complete()

if st.session_state.chat_complete and not st.session_state.thank_feedback:
    if st.button("Get Summary", on_click = show_thank_feedback):
       # with st.spinner("Loading..."):
        st.write("Generating summary and feedback... Please wait a moment.")
        time.sleep(3)

if st.session_state.thank_feedback:
   st.subheader("💡 Feedback")
   conversation_summary = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in st.session_state.messages if msg['role'] != 'system'])
   feedback_client = OpenAI(api_key=st.secrets["OPEN_API_KEY"])
   # apply replace function to convert User: Name from Form
   feedback_completion = feedback_client.chat.completions.create(
       model="gpt-4o",
       messages=[
           {
               "role": "system",
               "content": f'''
                You are an expert in generating concise summaries in a funny and concise way. 
                Your goal is to generate summary / assessment if Sebastian Wieczorek fits role 
                Based on:
                - User form input:
                  - User's name: {st.session_state.first_name} 
                  - Works at": {st.session_state.company} as {st.session_state.position}. 
                  - Hiring for the role of {st.session_state.role} at {st.session_state.level} level.
                - Chat conversation: {conversation_summary}
            
               '''
           },
       ]
    )
   st.write(feedback_completion.choices[0].message.content)

   if st.button("Restart Chat", type="primary"):
        with st.spinner("Restarting chat..."):
          time.sleep(2)
          streamlit_js_eval(js_expressions="parent.window.location.reload()")