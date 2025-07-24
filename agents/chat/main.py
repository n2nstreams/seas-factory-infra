import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Chat Agent",
    description="A serverless chatbot that uses RAG to answer questions about the SaaS Factory.",
    version="1.0.0"
)

# --- RAG Pipeline Setup ---
def get_retriever():
    """
    Creates and returns a retriever for the RAG pipeline.
    This function loads documents, splits them, creates embeddings, and builds a vector store.
    """
    try:
        # Load documents from the docs directory
        loader = DirectoryLoader(
            './docs',
            glob="**/*.md",
            loader_cls=TextLoader,
            show_progress=True,
            use_multithreading=True
        )
        documents = loader.load()

        if not documents:
            logger.warning("No documents found in the 'docs' directory.")
            return None

        # Split documents into smaller chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(documents)

        # Create embeddings and vector store
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        vectorstore = FAISS.from_documents(documents=splits, embedding=embeddings)

        return vectorstore.as_retriever(search_kwargs={"k": 3})
    except Exception as e:
        logger.error(f"Error setting up retriever: {e}")
        return None

retriever = get_retriever()

# --- Chat Endpoint ---
class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []

@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Handles chat requests by using the RAG pipeline to generate and stream a response.
    """
    if not retriever:
        raise HTTPException(status_code=500, detail="Retriever not available.")

    logger.info(f"Received chat request: {request.message}")

    # Create prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant for the AI SaaS Factory. Answer the user's questions based on the following context:\n\n{context}"),
        # The 'history' will be a list of AIMessage and HumanMessage objects
        *[(AIMessage(content=msg['content']) if msg['role'] == 'assistant' else HumanMessage(content=msg['content'])) for msg in request.history],
        ("human", "{input}"),
    ])

    # Create language model
    llm = ChatOpenAI(model="gpt-4o", temperature=0, streaming=True)

    # Create chains
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    async def stream_response():
        try:
            async for chunk in rag_chain.astream({"input": request.message}):
                if "answer" in chunk:
                    yield chunk["answer"]
        except Exception as e:
            logger.error(f"Error during streaming: {e}")
            yield "Sorry, an error occurred while generating the response."

    return StreamingResponse(stream_response(), media_type="text/event-stream")


@app.get("/health")
async def health_check():
    """Health check endpoint to verify service is running."""
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 