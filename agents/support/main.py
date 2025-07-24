import os
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
import json

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Support Agent",
    description="Generates an FAQ from project documentation.",
    version="1.0.0"
)

# --- Pydantic Models ---
class FAQItem(BaseModel):
    question: str = Field(..., description="The frequently asked question.")
    answer: str = Field(..., description="The answer to the question.")

class FAQ(BaseModel):
    items: List[FAQItem]

# --- FAQ Generation Logic ---
generated_faq: List[FAQItem] = []

async def generate_faq_from_docs():
    """
    Loads documents, summarizes them, and uses an LLM to generate an FAQ.
    """
    global generated_faq
    try:
        logger.info("Starting FAQ generation...")
        loader = DirectoryLoader(
            './docs',
            glob="**/*.md",
            loader_cls=TextLoader,
            show_progress=True,
            use_multithreading=True
        )
        docs = loader.load()

        if not docs:
            logger.warning("No documents found in 'docs' directory. Skipping FAQ generation.")
            return

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=200)
        split_docs = text_splitter.split_documents(docs)

        llm = ChatOpenAI(model="gpt-4o", temperature=0.2)
        
        prompt = f"""
        Based on the following documentation, please generate a list of 5-10 frequently asked questions (FAQs) that a new user might have.
        For each question, provide a clear and concise answer.
        Format the output as a JSON array of objects, where each object has a "question" and "answer" key.

        Documentation:
        {" ".join([doc.page_content for doc in split_docs])}
        """
        
        response = await llm.ainvoke(prompt)
        
        # The response content should be a JSON string
        faq_data = json.loads(response.content)
        
        # Create a Pydantic model to validate the structure
        faq_model = FAQ(items=faq_data)
        generated_faq = faq_model.items

        logger.info("FAQ generation complete.")

    except Exception as e:
        logger.error(f"Error during FAQ generation: {e}")
        # Use a default FAQ as a fallback
        generated_faq = [
            FAQItem(question="What is the AI SaaS Factory?", answer="It's a platform for building and launching SaaS applications using AI."),
            FAQItem(question="How do I get started?", answer="You can start by submitting an idea through the main dashboard.")
        ]

@app.on_event("startup")
async def startup_event():
    """
    Triggers the FAQ generation on application startup.
    """
    await generate_faq_from_docs()

@app.get("/faq", response_model=List[FAQItem])
async def get_faq():
    """
    Returns the generated list of frequently asked questions.
    """
    if not generated_faq:
        raise HTTPException(status_code=404, detail="FAQ not generated yet or generation failed.")
    return generated_faq

@app.get("/health")
async def health_check():
    """Health check endpoint to verify service is running."""
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8089) 