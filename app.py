import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import os
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceInstructEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from htmlTemplates import css, bot_template, user_template
from langchain.llms import HuggingFaceHub


myName ='Saksham'
def get_pdf_text(pdf_docs):
    text = ""
    # for pdf in pdf_docs:
    #     pdf_reader = PdfReader(pdf)
    #     for page in pdf_reader.pages:
    #         text += page.extract_text()
  
    pdf_reader = PdfReader(pdf_docs)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text


def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks


def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    # embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-xl")
    # embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-large")
    # st.write('embeddings',embeddings)
    # st.write('client-->',embeddings.client[0].max_seq_length)
    # embeddings.client[0].max_seq_length = 5000
    
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore


def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()
    # llm = HuggingFaceHub(repo_id="google/flan-t5-xxl", model_kwargs={"temperature":0.5, "max_length":1024})
    # llm = HuggingFaceHub(repo_id="google/flan-t5-xxl")
    # st.write('llm-->',llm)

    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain


def handle_userinput(user_question):
    # response = st.session_state.conversation({'question': user_question})
    # print('in the method')
    # if(user_question!=None):
    #     response = st.session_state.conversation({'question': user_question})
    # else:

    response = st.session_state.conversation({'question': 'Tell me the list of skillset'})

    st.session_state.chat_history = response['chat_history']

 
    # st.write(response)

    # for i, message in enumerate(st.session_state.chat_history):
    #     # print('hello')
    #     # st.write('i-->',i)
    #     # st.write('message-->',message)
    #     if i % 2 == 0:
    #         st.write(user_template.replace(
    #             "{{MSG}}", message.content), unsafe_allow_html=True)
          
    #     else:
    #         st.write(bot_template.replace(
    #             "{{MSG}}", message.content), unsafe_allow_html=True)
    
    
def main():
    # load_dotenv()

    # os.environ["OPENAI_API_KEY"] = "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"
    os.environ.get("OPENAI_API_KEY")
    st.set_page_config(page_title="Resume Parser",page_icon=":books:")
    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None
    
    
    

    st.header("Find answers from your Resume :books:")
    user_question = st.text_input("Ask a question about your resume:")
    # st.write(os.environ.get('Environment'))

    # user_question=''
    # st.write('userinput-->',user_question)
    
    # user_question ='What is your name'
    if user_question:
        handle_userinput(user_question)

    with st.sidebar:
        st.subheader("Your document")
        pdf_docs = st.file_uploader(
            "Upload your PDF here and click on 'Process'", accept_multiple_files=False)
        # pdf_docs = st.file_uploader(
        #     "Upload your PDFs here and click on 'Process'", accept_multiple_files=True)
        if st.button("Process"):
            with st.spinner("Processing"):
                # get pdf text
                raw_text = get_pdf_text(pdf_docs)
                # st.write(raw_text) 

                # get the text chunks
                text_chunks = get_text_chunks(raw_text)

                # create vector store
                vectorstore = get_vectorstore(text_chunks)

                # create conversation chain
                st.session_state.conversation = get_conversation_chain(
                    vectorstore)
                
                
            handle_userinput(user_question)
    # st.write('hello user')
    # st.write(myName)
    # st.write(user_template.replace(
    #             "{{MSG}}", myName), unsafe_allow_html=True)
    # st.write('sesssion state-->',st.session_state)
    # st.write('sesssion state-->',st.session_state.chat_history)
    if(st.session_state.chat_history!=None):
         for i, message in enumerate(st.session_state.chat_history):
            # print('hello')
            # st.write('i-->',i)
            # st.write('message-->',message)
            if i % 2 == 0:
                # st.write('message.content-->',message.content)
                print('test')
                # st.write(user_template.replace(
                #     "{{MSG}}", message.content), unsafe_allow_html=True)
            
            else:
                st.write(bot_template.replace(
                    "{{MSG}}", message.content), unsafe_allow_html=True)



    
    
        

if __name__ == '__main__':
    main()
