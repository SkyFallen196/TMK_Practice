import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.prompts.prompt import PromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_community.vectorstores import Chroma
import google.generativeai as genai
from langchain.text_splitter import CharacterTextSplitter

load_dotenv('.env')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

llm = ChatGoogleGenerativeAI(model="models/gemini-pro")

embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

pdf_directory = "data/"
pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith('.pdf')]

text_splitter = CharacterTextSplitter(
    separator=".",
    chunk_size=2500,
    chunk_overlap=150,
    length_function=len,
    is_separator_regex=False,
)

all_pages = []

for pdf_file in pdf_files:
    pdf_path = os.path.join(pdf_directory, pdf_file)
    loader = PyPDFLoader(pdf_path)
    pages = loader.load_and_split(text_splitter)
    all_pages.extend(pages)

db = Chroma.from_documents(pages, embedding)
db

retriever = db.as_retriever(search_kwargs={"k": 7})

template = """
Вы - помощник с искусственным интеллектом.
Отвечайте, исходя из предоставленного контекста.

context: {context}
input: {input}
answer:
"""

prompt = PromptTemplate.from_template(template)
combine_docs_chain = create_stuff_documents_chain(llm, prompt)
retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)

def get_response(query: str) -> str:
    response = retrieval_chain.invoke({"input": query})
    return response["answer"]