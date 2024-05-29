import os
import chainlit as cl
from chainlit.types import ThreadDict
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient
from langchain.agents import initialize_agent
from langchain_openai import OpenAIEmbeddings
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.agents import initialize_agent
from langchain_core.tools import tool
from langchain.prompts.prompt import PromptTemplate
from langchain_google_vertexai import VertexAI
from langchain.sql_database import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI


model = VertexAI(model_name="gemini-1.5-pro-preview-0409")



db_lite = SQLDatabase.from_uri("sqlite:///side_effects.db")



#from langchain_experimental import  SQLDatabaseChain
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") # Replace with your OpenAI API key
llm = ChatOpenAI(
    openai_api_key=OPENAI_API_KEY,
    model_name='gpt-4-0125-preview',
    temperature=0.0,
    max_tokens=4096
    
   # streaming=True
)

embeddings_model = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
client = QdrantClient(host="localhost", port=6333)
vector_store = Qdrant(client, collection_name="Documents", embeddings=embeddings_model)
vector_store_p = Qdrant(client, collection_name="Patients", embeddings=embeddings_model)
agent_executor_lite = create_sql_agent(llm, db=db_lite, agent_type="openai-tools", verbose=True)


def retrieve_pdf_data(query):
    # Use the vector store to perform similarity search based on the query
    profiles = vector_store.similarity_search(query)
    data = [profile.page_content for profile in profiles]
    return ' '.join(data)

def retrieve_patient_data(query):
    # Use the vector store to perform similarity search based on the query
    profiles = vector_store_p.similarity_search(query)
    data = [profile.page_content for profile in profiles]
    return ' '.join(data)

@tool
def  database_query_lite(query):
    """
Retrive Information about Drug side effects from the Table side_effects. The Columns drug_name and side_effect.

To find side effects Following is an example Query 
SELECT side_effect from side_effects where drug_name='carnitine';

To Find drugs based on Side Affects 
SELECT drug_name from side_effects where side_effect='Abdominal pain'
"""
    # Use the vector store to perform similarity search based on the query
   # question = QUERY.format(question=query)
    response = agent_executor_lite.run(query)
    print(response)
    return  response

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



tools = [pdf_query,patient_query,database_query_lite]


welcome_message = ("Welcome to the Princess Maxima Patient Care Center. We’re here to support you "
                   "and your loved ones every step of the way. If you have any questions or need "
                   "assistance with your care, please feel free to ask. Our team is committed to "
                   "providing you with the best possible support and information.")

@cl.on_chat_start
async def  start():

    print("A new chat session has started!")

    await cl.Message(content=welcome_message).send()

    conversational_memory = ConversationBufferWindowMemory(
    memory_key='chat_history',
    k=10,
    return_messages=True
)
    agent = initialize_agent(
        agent='chat-conversational-react-description',
        tools=tools,
        llm=llm,
        verbose=True,
        max_iterations=10,
        early_stopping_method='generate',
        memory=conversational_memory,
        handle_parsing_errors=True
    )
    cl.user_session.set("agent", agent)


@cl.on_message
async def main(message: cl.Message):

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


@cl.on_stop
def on_stop():
    print("The user wants to stop the task!")

@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict):
    print("The user resumed a previous chat session!")