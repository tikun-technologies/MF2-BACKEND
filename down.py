from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.llms import Ollama

from langchain.embeddings import OllamaEmbeddings

  # Initialize Ollama's embedding model
ollama_embeddings = OllamaEmbeddings(model="llama3.1")


from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("s.pdf")
pages = loader.load_and_split()



from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.llms import Ollama

# Initialize vector store
embedding = ollama_embeddings
db = Chroma.from_documents(pages, embedding)

# Set up LLaMA 3.1 model
llm = Ollama(model="llama3.1")

# Set up RetrievalQA chain
qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=db.as_retriever())

question = "give me one line summary  what you understood from this document and if i ask you t ogive a title to it then what titlew would you give to it " 
answer = qa_chain.run(question)
print(answer)
