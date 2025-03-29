# -*- coding: utf-8 -*-
"""Agentic AI app.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1K99X_VjCw8gjyL6gHS_HjrEjFeyGdnqw
"""

# pip install streamlit

import streamlit as st
import io
# import deepnote_toolkit
# from matplotlib.pyplot as plt
import os

# pip install langchain

# pip install -U langchain-community langgraph langchain-tavily-python langgraph-checkpoint-sqlite

!pip install -r requirements.txt

!pip install langgraph-checkpoint-sqlite

from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.checkpoint.memory import MemorySaver
from langchain.agents import Tool,AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain_experimental.utilities import PythonREPL

"""Python REPL"""

import os
os.environ['TAVILY_API_KEY'] = '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'
os.environ['GROQ_API_KEY'] = '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'  # Replace 'YOUR_API_KEY' with your actual key  # Replace 'YOUR_API_KEY' with your actual key

search_tool = TavilySearchResults(max_results = 1, api_key = os.getenv("TAVILY_API_KEY"))
python_repl = PythonREPL()

repl_tool = Tool(
    name = 'python_repl',
    description = 'Executes Python code and returns the result',
    func = python_repl.run,
)

"""LLM initialization"""

llm = ChatGroq(
    model = 'llama-3.3-70b-versatile',
    temperature = 0.7,
    max_tokens = 1024,
    max_retries = 3,
    verbose = True,
    api_key = os.getenv('GROQ_API_KEY'),
)

"""Chat prompt Template and the memory of chats"""

prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a very creative and helpul assisstant that can use tools."),
        MessagesPlaceholder(variable_name = 'chat_history'),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ]

)

"""Tools"""

tools=[search_tool,repl_tool]

if "session_id" not in st.session_state:
  st.session_state.session_id = f"session_{id(st.session_state)}"

"""Agent creation"""

agent = create_tool_calling_agent(llm, tools, prompt_template)

"""Memory initialization"""

if 'memory' not in st.session_state:
  st.session_state.memory = MemorySaver()

if 'agent_executor' not in st.session_state:
  st.session_state.agent_executor = AgentExecutor(agent=agent , tools = tools, checkpoint = st.session_state.memory)

"""initialize chat history"""

if 'messages' not in st.session_state:
  st.session_state.messages = []

if 'chat_history' not in st.session_state:
  st.session_state.chat_history = []

"""Reset Function"""

def reset():
  st.session_state.messages = []
  st.session_state.chat_history = []
  st.session_state.seesion_id = f"session_{id(st.session_state)}"
  st.session_state.memory = MemorySaver()
  st.session_state.agent_executor = AgentExecutor(agent=agent , tools = tools, checkpoint = st.session_state.memory)

"""STREAMLIT APP SETUP"""

col1, col2 = st.columns([8,2])

with col1:
  st.title(" ⛧ — 🩻 🌀  My Web ˖°. 🌀 🩻  — ⛧ ")
  st.markdown("Ask Me!!!")

with col2:
  if st.button("🌱" , help = "Clear chat history"):
    reset =()
    st.success("The chat history has been earthed!")


for i, message in enumerate(st.session_state.messages):
  with st.chat_message(message["role"]):
    st.markdown(message["content"])

"""#Accepts user input"""

user_input = st.chat_input("What do u wanna know about?")

if user_input:
  st.session_state.messages.append({"role": "user", "content": user_input})
  st.session_state.chat_history.append(("human", user_input))

  with st.chat_message("user"):
    st.markdown(user_input)

  # process the query with proper error handling
  with st.chat_message("assisstant"):
    #create a message container for streaming
    message_placeholder = st.empty()

    max_attempts = 2
    attempts = 0
    success = False
    full_response =""
    while attempts < max_attempts and not success:
      try:
        for step in st.session_state.agent_executor.stream(
            {
                "input":user_input,
                "chat_history":st.session_state.chat_history,
            },
            {"configurable": {"thread_id":st.session_state.session_id}},):
          if "output" in step:
            full_response += step["output"]
            message_placeholder.markdown(full_response)

          success = True
      except Exception as e:
          if "Failed to call a function" in str(error):
            attempts+=1
            full_response = " "
            continue
          else:
            st.error(f"An error occurred: {str(e)}")
            break

    if not success:
        st.error("Failed to process the query after multiple attempts.")


    st.sesseion_state.messages.append({"role": "assisstant", "content": full_response})
    st.session_state.chat_history.append(("ai", full_response))

