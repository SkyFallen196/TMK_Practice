import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain.prompts.prompt import PromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter

load_dotenv('.env')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

llm = ChatGoogleGenerativeAI(model="models/gemini-pro", api_key=GOOGLE_API_KEY)
embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001", api_key=GOOGLE_API_KEY)

md_directory = "data/"
md_files = [f for f in os.listdir(md_directory) if f.endswith('.md')]

print(f"Markdown files: {md_files}")

text_splitter = CharacterTextSplitter(
    separator=".",
    chunk_size=2500,
    chunk_overlap=150,
    length_function=len,
    is_separator_regex=False,
)

all_pages = []
for md_file in md_files:
    md_path = os.path.join(md_directory, md_file)
    loader = UnstructuredMarkdownLoader(md_path)
    pages = loader.load_and_split(text_splitter)
    all_pages.extend(pages)
    
    print(f"Content of {md_file}:")
    for page in pages:
        print(page)

    all_pages.extend(pages)
    print(f"Loaded {len(pages)} pages from {md_file}")

print(f"Total number of pages loaded: {len(all_pages)}")

db = Chroma.from_documents(all_pages, embedding)
retriever = db.as_retriever(search_kwargs={"k": 14})

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

# test 

print(get_response("Какой предел прочности для стали 15ХМ ?"))