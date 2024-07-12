import os
from dotenv import load_dotenv
from langchain_community.llms.ollama import Ollama
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain.prompts.prompt import PromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter

load_dotenv('.env')

OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'https://9e1f-34-83-91-213.ngrok-free.app')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3')
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-mpnet-base-v2')

llm = Ollama(base_url=OLLAMA_HOST, model=OLLAMA_MODEL)
embedding = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

md_directory = "data/"
md_files = [f for f in os.listdir(md_directory) if f.endswith('.md')]

print(f"Markdown files: {md_files}")

text_splitter = CharacterTextSplitter(
    separator="\n",
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
Ты - помощник с искусственным интеллектом.
Отвечай, исходя из предоставленного контекста.
Ответы должны быть только на русском языке.

### Контекст:
{context}

### Вопрос:
{input}

### Ответ:
"""

prompt = PromptTemplate.from_template(template)
combine_docs_chain = create_stuff_documents_chain(llm, prompt)
retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)

def get_response(query: str) -> str:
    response = retrieval_chain.invoke({"input": query})
    return response["answer"]

