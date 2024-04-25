import os
import sqlite3
import sys
import chainlit as cl
from chainlit.types import ThreadDict
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient
from langchain.agents import Tool, initialize_agent, AgentType
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from typing import Dict, Optional
from langchain.chat_models import ChatOpenAI
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.chains import RetrievalQA
from langchain.agents import Tool
from langchain.agents import initialize_agent
from langchain.sql_database import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_core.tools import tool
import sqlite3
import plotly.express as px
import pandas as pd
from langchain.chains import GraphCypherQAChain
from langchain_community.graphs import Neo4jGraph
from langchain.prompts.prompt import PromptTemplate
from langchain_google_vertexai import VertexAI
import fitz  # PyMuPDF

model = VertexAI(model_name="gemini-1.5-pro-preview-0409")

# message = "What are some of the pros and cons of Python as a programming language?"
# print(model.invoke(message))



#from langchain_experimental import  SQLDatabaseChain
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") # Replace with your OpenAI API key
embeddings_model = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
client = QdrantClient(host="localhost", port=6333)
vector_store = Qdrant(client, collection_name="Documents", embeddings=embeddings_model)
vector_store_p = Qdrant(client, collection_name="Patients", embeddings=embeddings_model)


def retrieve_pdf_data(query):
    # Use the vector store to perform similarity search based on the query
    profiles = vector_store.similarity_search(query, k=5)
    data = [profile.page_content for profile in profiles]
    return ' '.join(data)

def retrieve_patient_data(query):
    # Use the vector store to perform similarity search based on the query
    profiles = vector_store_p.similarity_search(query, k=5)
    data = [profile.page_content for profile in profiles]
    return ' '.join(data)

def read_pdf(file_path):
    """
    Reads a PDF and returns its text content.

    Args:
    file_path (str): The path to the PDF file to be read.

    Returns:
    str: The text content of the PDF.
    """
    text = ''
    # Open the provided PDF file
    with fitz.open(file_path) as doc:
        # Iterate over each page
        for page in doc:
            # Extract text from each page and append it to the text variable
            text += page.get_text()

    return text




@tool
def pdf_query(query):
    """This is a tool used to answer questions based on Main.pdf. Use this tool for all the generic guide.
    """
    template = """
    Context : {context}
    Question: {question}

    """
    prompt = PromptTemplate.from_template(template)

    chain = prompt | model

    context = retrieve_pdf_data(query)
    return chain.invoke({"question": query , "context": context})

@tool
def patient_query(query):
    """This is a tool used to answer questions about a specific patient.
    """
    template = """
    Context : {context}
    Question: {question}

    """
    prompt = PromptTemplate.from_template(template)

    chain = prompt | model

    context = retrieve_patient_data(query)
    return chain.invoke({"question": query , "context": context})

@tool
def teen_pdf_query(query):
    """This is a tool used to answer questions for teens. Use this tool for all the questions related to teens.
    """

    template = """
    Context : {context}
    Question: {question}

    """
    prompt = PromptTemplate.from_template(template)

    chain = prompt | model

    context = retrieve_pdf_data(query)
    return chain.invoke({"question": query , "context": context})

tools = [pdf_query,patient_query]


# print(agent.agent.llm_chain.prompt)
# print(agent(query))
# print(agent(query2))
# #print(agent(query2_5))
# print(agent(query3))
# print(agent(query4))

welcome_message = ("Welcome to the Princess Maxima Patient Care Center. We’re here to support you "
                   "and your loved ones every step of the way. If you have any questions or need "
                   "assistance with your care, please feel free to ask. Our team is committed to "
                   "providing you with the best possible support and information.")

@cl.on_chat_start
async def  start():
    #tools = load_tools(["requests_all"])
    #app_user = cl.user_session.get("user")
    #cl.Message(f"Hello {app_user.identifier}").send()
    print("A new chat session has started!")

    await cl.Message(content=welcome_message).send()
    # agent = initialize_agent(
    #     tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True

    # )
    conversational_memory = ConversationBufferWindowMemory(
    memory_key='chat_history',
    k=10,
    return_messages=True
)
    agent = initialize_agent(
        agent='chat-conversational-react-description',
        tools=tools,
        llm=model,
        verbose=True,
        max_iterations=10,
        early_stopping_method='generate',
        memory=conversational_memory,
        handle_parsing_errors=True
    )
    cl.user_session.set("agent", agent)

# @cl.oauth_callback
# def oauth_callback(
#         provider_id: str,
#         token: str,
#         raw_user_data: Dict[str, str],
#         default_user: cl.User,
# ) -> Optional[cl.User]:
#   return default_user

@cl.on_message
async def main(message: cl.Message):
    #agent = cl.user_session.get("agent")  # type: AgentExecutor
    #print(agent)
    # agent = initialize_agent(
    #     tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True
    # )
    # res = await agent.run(
    #     message.content, callbacks=[cl.AsyncLangchainCallbackHandler()]
    # )

    #     for chunk in await cl.make_async(runnable.stream)(
    #     {"question": message.content},
    #     config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    # ):
    #     await msg.stream_token(chunk)

    # await msg.send()
    agent = cl.user_session.get("agent") 
    cl.user_session.set("figure", None)
    res = await cl.make_async(agent.run)(
        message.content, callbacks=[cl.AsyncLangchainCallbackHandler()]
    )
    elements = []
    figure = cl.user_session.get("figure")
    if figure:
        elements.append(cl.Plotly(name="chart", figure=figure, display="inline"))
    print("This is the final result !!")
    print(res)
    await cl.Message(content=res, elements=elements).send()


@cl.action_callback("action_button")
async def on_action(action: cl.Action):
    print("The user clicked on the action button!")

    return "Thank you for clicking on the action button!"

# @cl.on_chat_start
# # def on_chat_start():
# #     print("A new chat session has started!")

@cl.on_stop
def on_stop():
    print("The user wants to stop the task!")

@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict):
    print("The user resumed a previous chat session!")