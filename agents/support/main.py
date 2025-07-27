import os
import logging
import re
import ast
from pathlib import Path
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Set
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
import json
import fnmatch

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Support Agent - FAQ Generator",
    description="Generates comprehensive FAQs from project documentation and code comments.",
    version="2.0.0"
)

# --- Pydantic Models ---
class FAQItem(BaseModel):
    question: str = Field(..., description="The frequently asked question.")
    answer: str = Field(..., description="The answer to the question.")
    category: str = Field(default="General", description="Category of the FAQ item.")
    source: str = Field(default="docs", description="Source of the FAQ (docs, code, etc.)")

class FAQ(BaseModel):
    items: List[FAQItem]

class CodeComment(BaseModel):
    content: str = Field(..., description="The comment content")
    file_path: str = Field(..., description="Path to the file containing the comment")
    line_number: int = Field(..., description="Line number of the comment")
    comment_type: str = Field(..., description="Type of comment (TODO, FIXME, NOTE, etc.)")
    context: str = Field(default="", description="Surrounding code context")

# --- Code Comment Extraction Logic ---
class CodeCommentExtractor:
    """Extracts meaningful comments from code files for FAQ generation"""
    
    COMMENT_PATTERNS = {
        'TODO': r'(?:TODO|@todo)\s*:?\s*(.+)',
        'FIXME': r'(?:FIXME|@fixme)\s*:?\s*(.+)',
        'NOTE': r'(?:NOTE|@note)\s*:?\s*(.+)',
        'HACK': r'(?:HACK|@hack)\s*:?\s*(.+)',
        'BUG': r'(?:BUG|@bug)\s*:?\s*(.+)',
        'WARNING': r'(?:WARNING|@warning)\s*:?\s*(.+)',
        'IMPORTANT': r'(?:IMPORTANT|@important)\s*:?\s*(.+)',
        'DEPRECATED': r'(?:DEPRECATED|@deprecated)\s*:?\s*(.+)',
    }
    
    # File patterns to exclude
    EXCLUDE_PATTERNS = [
        '*.pyc', '*.pyo', '*.pyd', '__pycache__/*',
        '*.so', '*.dylib', '*.dll',
        '.git/*', '.gitignore', 
        'node_modules/*', '*.lock', 'package-lock.json',
        '*.log', '*.tmp', '*.temp',
        '.env', '.env.*',
        '*.pdf', '*.png', '*.jpg', '*.jpeg', '*.gif', '*.svg',
        'venv/*', 'env/*', '.venv/*'
    ]
    
    # File extensions to process
    INCLUDE_EXTENSIONS = {
        '.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.cpp', '.c', '.h',
        '.go', '.rs', '.rb', '.php', '.cs', '.swift', '.kt', '.scala',
        '.yaml', '.yml', '.json', '.md', '.txt', '.sh', '.bat',
        '.tf', '.hcl', '.sql', '.html', '.css', '.scss', '.less'
    }
    
    def __init__(self, root_path: str = "../../"):
        self.root_path = Path(root_path).resolve()
        
    def should_process_file(self, file_path: Path) -> bool:
        """Check if file should be processed based on patterns and extensions"""
        relative_path = str(file_path.relative_to(self.root_path))
        
        # Check exclude patterns
        for pattern in self.EXCLUDE_PATTERNS:
            if fnmatch.fnmatch(relative_path, pattern):
                return False
                
        # Check file extension
        return file_path.suffix.lower() in self.INCLUDE_EXTENSIONS
    
    def extract_python_docstrings(self, file_path: Path) -> List[CodeComment]:
        """Extract docstrings from Python files"""
        comments = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                    docstring = ast.get_docstring(node)
                    if docstring and len(docstring.strip()) > 10:  # Filter out trivial docstrings
                        comments.append(CodeComment(
                            content=docstring.strip(),
                            file_path=str(file_path.relative_to(self.root_path)),
                            line_number=node.lineno,
                            comment_type="DOCSTRING",
                            context=f"{node.__class__.__name__}: {node.name}"
                        ))
        except Exception as e:
            logger.debug(f"Could not parse Python AST for {file_path}: {e}")
        
        return comments
    
    def extract_line_comments(self, file_path: Path) -> List[CodeComment]:
        """Extract line comments from any file type"""
        comments = []
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                line_stripped = line.strip()
                
                # Skip empty lines
                if not line_stripped:
                    continue
                
                # Check for different comment patterns based on file type
                comment_content = None
                if file_path.suffix in ['.py']:
                    if line_stripped.startswith('#'):
                        comment_content = line_stripped[1:].strip()
                elif file_path.suffix in ['.js', '.ts', '.tsx', '.jsx', '.java', '.cpp', '.c', '.h', '.go', '.rs', '.cs', '.swift', '.kt', '.scala']:
                    if line_stripped.startswith('//'):
                        comment_content = line_stripped[2:].strip()
                    elif '/*' in line_stripped and '*/' in line_stripped:
                        start = line_stripped.find('/*') + 2
                        end = line_stripped.find('*/')
                        comment_content = line_stripped[start:end].strip()
                elif file_path.suffix in ['.html', '.xml']:
                    if '<!--' in line_stripped and '-->' in line_stripped:
                        start = line_stripped.find('<!--') + 4
                        end = line_stripped.find('-->')
                        comment_content = line_stripped[start:end].strip()
                elif file_path.suffix in ['.yaml', '.yml']:
                    if line_stripped.startswith('#'):
                        comment_content = line_stripped[1:].strip()
                
                # Check if comment matches our patterns
                if comment_content:
                    for comment_type, pattern in self.COMMENT_PATTERNS.items():
                        match = re.search(pattern, comment_content, re.IGNORECASE)
                        if match:
                            # Get surrounding context
                            context_lines = []
                            for i in range(max(0, line_num-3), min(len(lines), line_num+2)):
                                if i != line_num-1:  # Skip the comment line itself
                                    context_lines.append(lines[i].strip())
                            context = " | ".join(filter(None, context_lines))
                            
                            comments.append(CodeComment(
                                content=match.group(1).strip(),
                                file_path=str(file_path.relative_to(self.root_path)),
                                line_number=line_num,
                                comment_type=comment_type,
                                context=context[:200]  # Limit context length
                            ))
                            break
                            
        except Exception as e:
            logger.debug(f"Could not read file {file_path}: {e}")
        
        return comments
    
    def extract_all_comments(self) -> List[CodeComment]:
        """Extract all relevant comments from the codebase"""
        all_comments = []
        
        for file_path in self.root_path.rglob('*'):
            if file_path.is_file() and self.should_process_file(file_path):
                try:
                    # Extract line comments
                    line_comments = self.extract_line_comments(file_path)
                    all_comments.extend(line_comments)
                    
                    # Extract Python docstrings
                    if file_path.suffix == '.py':
                        docstring_comments = self.extract_python_docstrings(file_path)
                        all_comments.extend(docstring_comments)
                        
                except Exception as e:
                    logger.debug(f"Error processing file {file_path}: {e}")
        
        logger.info(f"Extracted {len(all_comments)} code comments from codebase")
        return all_comments

# --- Enhanced FAQ Generation Logic ---
generated_faq: List[FAQItem] = []
last_generation_time: Optional[str] = None

class EnhancedFAQGenerator:
    """Enhanced FAQ generator that processes both docs and code comments"""
    
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.2)
        self.comment_extractor = CodeCommentExtractor()
    
    async def generate_faq_from_docs(self) -> List[FAQItem]:
        """Generate FAQ from documentation files"""
        faq_items = []
        try:
            logger.info("Generating FAQ from documentation...")
            loader = DirectoryLoader(
                '../../docs',
                glob="**/*.md",
                loader_cls=TextLoader,
                show_progress=True,
                use_multithreading=True
            )
            docs = loader.load()

            if docs:
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=200)
                split_docs = text_splitter.split_documents(docs)
                
                prompt = f"""
                Based on the following documentation, please generate 8-12 frequently asked questions (FAQs) that users might have.
                For each question, provide a clear and helpful answer.
                
                Focus on:
                - Getting started and onboarding
                - Common use cases and features
                - Technical requirements and setup
                - Troubleshooting common issues
                - Best practices and recommendations

                Format the output as a JSON array of objects, where each object has:
                - "question": The FAQ question
                - "answer": A comprehensive answer
                - "category": One of "Getting Started", "Features", "Technical", "Troubleshooting", "Best Practices"
                - "source": "docs"

                Documentation:
                {" ".join([doc.page_content[:1000] for doc in split_docs[:10]])}
                """
                
                response = await self.llm.ainvoke(prompt)
                faq_data = json.loads(response.content)
                faq_items = [FAQItem(**item) for item in faq_data]
                
        except Exception as e:
            logger.error(f"Error generating FAQ from docs: {e}")
            
        return faq_items
    
    async def generate_faq_from_code_comments(self) -> List[FAQItem]:
        """Generate FAQ from code comments and TODOs"""
        faq_items = []
        try:
            logger.info("Extracting and processing code comments...")
            comments = self.comment_extractor.extract_all_comments()
            
            if not comments:
                return faq_items
            
            # Group comments by type and file
            grouped_comments = {}
            for comment in comments:
                key = f"{comment.comment_type}_{Path(comment.file_path).parts[0] if Path(comment.file_path).parts else 'root'}"
                if key not in grouped_comments:
                    grouped_comments[key] = []
                grouped_comments[key].append(comment)
            
            # Generate FAQ for each group
            for group_key, group_comments in grouped_comments.items():
                if len(group_comments) < 2:  # Skip groups with too few comments
                    continue
                
                comment_type, component = group_key.split('_', 1)
                
                # Prepare comments summary
                comments_summary = []
                for comment in group_comments[:10]:  # Limit to prevent token overflow
                    comments_summary.append(f"- {comment.content} (in {comment.file_path})")
                
                prompt = f"""
                Based on the following {comment_type} comments from the {component} component, generate 2-4 FAQ items 
                that address what users might wonder about these development notes.
                
                Transform technical TODOs and notes into user-friendly questions and answers.
                Focus on:
                - What functionality is planned or in development
                - Known limitations or considerations
                - How users should expect the system to behave
                - Workarounds for current limitations
                
                Comments:
                {chr(10).join(comments_summary)}
                
                Format as JSON array with objects containing:
                - "question": User-friendly question
                - "answer": Helpful answer that explains the current state and expectations
                - "category": "Development Status" or "Known Issues" or "Planned Features"
                - "source": "code"
                """
                
                try:
                    response = await self.llm.ainvoke(prompt)
                    group_faq_data = json.loads(response.content)
                    group_faq_items = [FAQItem(**item) for item in group_faq_data]
                    faq_items.extend(group_faq_items)
                except Exception as e:
                    logger.debug(f"Could not generate FAQ for group {group_key}: {e}")
                    
        except Exception as e:
            logger.error(f"Error generating FAQ from code comments: {e}")
            
        return faq_items
    
    async def generate_comprehensive_faq(self) -> List[FAQItem]:
        """Generate comprehensive FAQ from both docs and code"""
        all_faq_items = []
        
        # Generate from docs
        docs_faq = await self.generate_faq_from_docs()
        all_faq_items.extend(docs_faq)
        
        # Generate from code comments
        code_faq = await self.generate_faq_from_code_comments()
        all_faq_items.extend(code_faq)
        
        # If we have items, deduplicate and optimize
        if all_faq_items:
            all_faq_items = await self.deduplicate_and_optimize_faq(all_faq_items)
        else:
            # Fallback FAQ
            all_faq_items = self.get_fallback_faq()
        
        return all_faq_items
    
    async def deduplicate_and_optimize_faq(self, faq_items: List[FAQItem]) -> List[FAQItem]:
        """Remove duplicates and optimize FAQ items"""
        if len(faq_items) <= 15:
            return faq_items
        
        # Use LLM to consolidate and prioritize
        faq_summary = []
        for item in faq_items:
            faq_summary.append(f"Q: {item.question}\nA: {item.answer[:200]}...\nCategory: {item.category}")
        
        prompt = f"""
        The following FAQ items were generated from documentation and code analysis. 
        Please consolidate them into a final set of 12-15 most important and unique FAQ items.
        
        Remove duplicates, combine similar questions, and prioritize the most valuable content for users.
        
        Current FAQ items:
        {chr(10).join(faq_summary)}
        
        Output as JSON array with the final consolidated FAQ items, each having:
        - "question": Clear, user-friendly question
        - "answer": Comprehensive but concise answer
        - "category": Appropriate category
        - "source": "consolidated"
        """
        
        try:
            response = await self.llm.ainvoke(prompt)
            final_faq_data = json.loads(response.content)
            return [FAQItem(**item) for item in final_faq_data]
        except Exception as e:
            logger.error(f"Error consolidating FAQ: {e}")
            return faq_items[:15]  # Return first 15 if consolidation fails
    
    def get_fallback_faq(self) -> List[FAQItem]:
        """Return fallback FAQ if generation fails"""
        return [
            FAQItem(
                question="What is the AI SaaS Factory?",
                answer="The AI SaaS Factory is an automated platform that transforms your ideas into production-ready SaaS applications using AI agents.",
                category="Getting Started",
                source="fallback"
            ),
            FAQItem(
                question="How does the development process work?",
                answer="Our AI agents handle the entire development pipeline: idea validation, design, coding, testing, and deployment. Each agent specializes in different aspects of software development.",
                category="Features",
                source="fallback"
            ),
            FAQItem(
                question="What if I encounter issues with my generated application?",
                answer="Our system includes monitoring and support agents that can help diagnose issues. You can also contact our support team through the dashboard.",
                category="Troubleshooting",
                source="fallback"
            )
        ]

# Initialize FAQ generator
faq_generator = EnhancedFAQGenerator()

async def regenerate_faq():
    """Regenerate FAQ from all sources"""
    global generated_faq, last_generation_time
    try:
        logger.info("Starting comprehensive FAQ generation...")
        generated_faq = await faq_generator.generate_comprehensive_faq()
        last_generation_time = str(datetime.now())
        logger.info(f"FAQ generation complete. Generated {len(generated_faq)} FAQ items.")
    except Exception as e:
        logger.error(f"Error during FAQ generation: {e}")
        generated_faq = faq_generator.get_fallback_faq()

@app.on_event("startup")
async def startup_event():
    """Triggers the FAQ generation on application startup"""
    await regenerate_faq()

@app.get("/faq", response_model=List[FAQItem])
async def get_faq():
    """Returns the generated list of frequently asked questions"""
    if not generated_faq:
        raise HTTPException(status_code=404, detail="FAQ not generated yet or generation failed.")
    return generated_faq

@app.post("/faq/regenerate")
async def regenerate_faq_endpoint(background_tasks: BackgroundTasks):
    """Trigger FAQ regeneration (useful for webhooks)"""
    background_tasks.add_task(regenerate_faq)
    return {"message": "FAQ regeneration started", "last_generation": last_generation_time}

@app.get("/faq/stats")
async def get_faq_stats():
    """Get statistics about the generated FAQ"""
    if not generated_faq:
        return {"error": "No FAQ generated"}
    
    categories = {}
    sources = {}
    
    for item in generated_faq:
        categories[item.category] = categories.get(item.category, 0) + 1
        sources[item.source] = sources.get(item.source, 0) + 1
    
    return {
        "total_items": len(generated_faq),
        "categories": categories,
        "sources": sources,
        "last_generation": last_generation_time
    }

@app.get("/health")
async def health_check():
    """Health check endpoint to verify service is running"""
    return {"status": "ok", "faq_items": len(generated_faq), "last_generation": last_generation_time}

if __name__ == "__main__":
    import uvicorn
    from datetime import datetime
    uvicorn.run(app, host="0.0.0.0", port=8089) 