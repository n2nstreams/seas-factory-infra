from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import openai
import json
import asyncio
from typing import List, Dict, Any, Optional, Literal
import os
import logging
from contextlib import asynccontextmanager
from datetime import datetime
import uuid

# Import shared components
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from tenant_db import TenantDatabase, TenantContext, get_tenant_context_from_headers
from access_control import require_subscription, AccessLevel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentSpec(BaseModel):
    """Specification for document generation"""
    document_type: Literal["contributing", "readme", "api_docs", "user_guide", "architecture", "deployment", "mermaid_diagram"] = Field(..., description="Type of documentation to generate")
    title: str = Field(..., description="Document title")
    sections: List[str] = Field(default_factory=list, description="Specific sections to include")
    target_audience: Literal["developers", "users", "admins", "contributors"] = Field(..., description="Primary audience for the documentation")
    detail_level: Literal["basic", "intermediate", "comprehensive"] = Field(default="comprehensive", description="Level of detail")
    include_examples: bool = Field(default=True, description="Whether to include code examples")
    include_mermaid_diagram: bool = Field(default=False, description="Whether to include Mermaid architecture diagram")
    diagram_type: Optional[Literal["architecture", "workflow", "deployment", "data_flow"]] = Field(None, description="Type of Mermaid diagram to generate")
    project_context: Dict[str, Any] = Field(default_factory=dict, description="Project-specific context")

class GeneratedDocument(BaseModel):
    """Generated documentation response"""
    title: str
    content: str
    sections: List[str]
    metadata: Dict[str, Any]
    generated_at: datetime
    word_count: int

class DocAgent:
    """
    AI-powered documentation generation agent for the SaaS Factory
    Implements Night 71: Generate comprehensive documentation using AI
    """
    
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.tenant_db = TenantDatabase()
        
        # Documentation templates and patterns
        self.doc_patterns = self._load_doc_patterns()
        self.project_context = self._gather_project_context()
        
    def _load_doc_patterns(self) -> Dict[str, str]:
        """Load documentation patterns and templates"""
        return {
            "contributing": """
# Contributing Guidelines Template
## Overview
## Development Setup
## Coding Standards
## Testing Requirements
## Pull Request Process
## Code Review Guidelines
## Documentation Standards
## Getting Help
""",
            "readme": """
# Project README Template
## Description
## Architecture
## Features
## Quick Start
## Installation
## Usage
## Configuration
## API Reference
## Contributing
## License
""",
            "api_docs": """
# API Documentation Template
## Overview
## Authentication
## Endpoints
## Request/Response Examples
## Error Handling
## Rate Limiting
## SDK/Client Libraries
""",
            "architecture": """
# Architecture Documentation Template
## Overview
## System Components
## Data Flow
## Security Model
## Deployment Architecture
## Scalability Considerations
""",
            "mermaid_diagram": """
# Mermaid Diagram Template
## Architecture Overview
## Component Relationships
## Data Flow
## Agent Interactions
"""
        }
    
    def _gather_project_context(self) -> Dict[str, Any]:
        """Gather context about the current project"""
        return {
            "project_name": "AI SaaS Factory",
            "tech_stack": {
                "backend": "Python 3.12, FastAPI, PostgreSQL",
                "frontend": "React 18, TypeScript, Tailwind CSS",
                "cloud": "Google Cloud Platform",
                "ai": "OpenAI GPT-4o, Google Gemini 2.5 Pro",
                "deployment": "Cloud Run, Cloud Build, Terraform"
            },
            "architecture": "Multi-agent system with orchestrator pattern",
            "agents": [
                "DevAgent", "ReviewAgent", "DesignAgent", "QAAgent", 
                "AIOpsAgent", "DevOpsAgent", "UIAgent", "PersonalizationAgent",
                "BillingAgent", "MarketingAgent", "SupportAgent"
            ],
            "key_features": [
                "Automated code generation",
                "Multi-tenant architecture", 
                "AI-powered design generation",
                "Automated testing and QA",
                "DevOps automation",
                "Stripe payment integration",
                "Real-time monitoring"
            ]
        }

    async def generate_documentation(self, spec: DocumentSpec, tenant_context: TenantContext) -> GeneratedDocument:
        """Generate documentation based on specification"""
        try:
            logger.info(f"Generating {spec.document_type} documentation for tenant {tenant_context.tenant_id}")
            
            # Handle Mermaid diagram generation separately
            if spec.document_type == "mermaid_diagram":
                content = await self._generate_mermaid_diagram(spec)
            else:
                # Build context-aware prompt
                prompt = self._build_generation_prompt(spec)
                
                # Generate content using GPT-4o
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": self._get_system_prompt(spec.document_type, spec.target_audience)
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    temperature=0.3,
                    max_tokens=4000
                )
                
                content = response.choices[0].message.content
                
                # Add Mermaid diagram if requested
                if spec.include_mermaid_diagram and spec.diagram_type:
                    diagram_spec = DocumentSpec(
                        document_type="mermaid_diagram",
                        title=f"{spec.diagram_type.title()} Diagram",
                        diagram_type=spec.diagram_type,
                        target_audience=spec.target_audience
                    )
                    mermaid_content = await self._generate_mermaid_diagram(diagram_spec)
                    content = self._embed_mermaid_in_content(content, mermaid_content, spec.diagram_type)
            
            # Post-process content
            processed_content = self._post_process_content(content, spec)
            
            # Extract sections
            sections = self._extract_sections(processed_content)
            
            # Create response
            generated_doc = GeneratedDocument(
                title=spec.title,
                content=processed_content,
                sections=sections,
                metadata={
                    "document_type": spec.document_type,
                    "target_audience": spec.target_audience,
                    "detail_level": spec.detail_level,
                    "tenant_id": tenant_context.tenant_id,
                    "includes_mermaid": spec.include_mermaid_diagram or spec.document_type == "mermaid_diagram"
                },
                generated_at=datetime.utcnow(),
                word_count=len(processed_content.split())
            )
            
            # Store in database
            await self._store_generated_doc(generated_doc, tenant_context)
            
            return generated_doc
            
        except Exception as e:
            logger.error(f"Error generating documentation: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Documentation generation failed: {str(e)}")

    def _build_generation_prompt(self, spec: DocumentSpec) -> str:
        """Build context-aware prompt for documentation generation"""
        project_info = f"""
Project Context:
- Name: {self.project_context['project_name']}
- Architecture: {self.project_context['architecture']}
- Tech Stack: {self.project_context['tech_stack']}
- Key Features: {', '.join(self.project_context['key_features'])}
- Available Agents: {', '.join(self.project_context['agents'])}
"""
        
        prompt = f"""
{project_info}

Generate a comprehensive {spec.document_type} document with the following requirements:
- Title: {spec.title}
- Target Audience: {spec.target_audience}
- Detail Level: {spec.detail_level}
- Include Examples: {spec.include_examples}

{"Specific sections to include: " + ", ".join(spec.sections) if spec.sections else ""}

The documentation should follow markdown format and include:
1. Clear structure with proper headings
2. Actionable guidance and examples
3. Links to relevant resources
4. Proper formatting for code snippets
5. Professional tone appropriate for {spec.target_audience}

Please ensure the content is accurate, comprehensive, and follows best practices for technical documentation.
"""
        return prompt

    def _get_system_prompt(self, doc_type: str, audience: str) -> str:
        """Get system prompt based on document type and audience"""
        base_prompt = f"""You are an expert technical writer specializing in software documentation. 
You are creating {doc_type} documentation for {audience}."""
        
        if doc_type == "contributing":
            return f"""{base_prompt}
            
Focus on creating clear guidelines that help developers contribute effectively:
- Development environment setup
- Coding standards and conventions  
- Testing requirements and procedures
- Pull request and code review process
- Documentation standards
- Communication guidelines
- Getting help and support resources

Use a friendly but professional tone. Include specific examples and actionable steps.
Structure the content logically with clear headings and sub-sections."""

        elif doc_type == "readme":
            return f"""{base_prompt}
            
Create a comprehensive README that serves as the primary entry point:
- Clear project description and value proposition
- Architecture overview with diagrams
- Feature overview with highlights
- Quick start guide for immediate setup
- Installation and configuration steps
- Usage examples and tutorials
- API documentation links
- Contribution guidelines
- License and legal information

Make it scannable with good use of headers, lists, and formatting. Include visual elements like diagrams where helpful."""

        elif doc_type == "mermaid_diagram":
            return f"""{base_prompt}
            
Create accurate Mermaid diagrams that clearly illustrate:
- System architecture and component relationships
- Data flow between services
- Agent interactions and orchestration
- Deployment topology
- User journey flows

Use proper Mermaid syntax and clear, descriptive labels. Focus on readability and accuracy."""
            
        else:
            return f"""{base_prompt}
            
Create professional, comprehensive documentation that is:
- Well-structured and easy to navigate
- Includes relevant examples and code snippets
- Provides actionable guidance
- Uses consistent formatting and style
- Appropriate for the target audience level"""

    def _post_process_content(self, content: str, spec: DocumentSpec) -> str:
        """Post-process generated content for quality and consistency"""
        # Add standard project footer if applicable
        if spec.document_type in ["contributing", "readme"]:
            footer = f"""

---

**Generated by DocAgent** | AI SaaS Factory v1.0  
*Last updated: {datetime.utcnow().strftime('%Y-%m-%d')}*
"""
            content += footer
            
        return content

    def _extract_sections(self, content: str) -> List[str]:
        """Extract section headings from markdown content"""
        sections = []
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# ') or line.startswith('## '):
                sections.append(line.strip('# ').strip())
        return sections

    async def _generate_mermaid_diagram(self, spec: DocumentSpec) -> str:
        """Generate Mermaid diagram based on specification"""
        diagram_type = spec.diagram_type or "architecture"
        
        if diagram_type == "architecture":
            return self._generate_architecture_diagram()
        elif diagram_type == "workflow":
            return self._generate_workflow_diagram()
        elif diagram_type == "deployment":
            return self._generate_deployment_diagram()
        elif diagram_type == "data_flow":
            return self._generate_data_flow_diagram()
        else:
            return self._generate_architecture_diagram()
    
    def _generate_architecture_diagram(self) -> str:
        """Generate the main architecture diagram for the SaaS Factory"""
        return """```mermaid
flowchart TD
    subgraph "🎯 User Interface Layer"
        UI[React Dashboard]
        MP[Marketplace UI]
        API_GW[API Gateway<br/>FastAPI]
    end

    subgraph "🤖 Agent Orchestration Layer"
        PO[Project Orchestrator<br/>Vertex AI ADK]
        
        subgraph "Core Agents"
            DEV[DevAgent<br/>Code Generation]
            QA[ReviewAgent<br/>Testing & QA]
            DESIGN[DesignAgent<br/>UI/UX Generation]
            IDEA[IdeaAgent<br/>Validation]
        end
        
        subgraph "Operations Agents"
            DEVOPS[DevOpsAgent<br/>Infrastructure]
            AIOPS[AIOpsAgent<br/>Monitoring]
            SEC[SecurityAgent<br/>Compliance]
        end
        
        subgraph "Business Agents"
            BILL[BillingAgent<br/>Payments]
            MARKET[MarketingAgent<br/>Growth]
            SUPPORT[SupportAgent<br/>Help]
            DOCS[DocAgent<br/>Documentation]
        end
    end

    subgraph "🏗️ Infrastructure Layer"
        subgraph "Google Cloud Platform"
            CR[Cloud Run<br/>Services]
            SQL[Cloud SQL<br/>PostgreSQL + pgvector]
            VAI[Vertex AI<br/>Agent Engine]
            SM[Secret Manager]
            CB[Cloud Build<br/>CI/CD]
        end
        
        subgraph "External Services"
            STRIPE[Stripe<br/>Payments]
            GH[GitHub<br/>Code Repository]
            OPENAI[OpenAI<br/>GPT-4o]
            FIGMA[Figma<br/>Design]
        end
    end

    %% User Flow
    UI --> API_GW
    MP --> API_GW
    API_GW --> PO

    %% Orchestration Flow  
    PO --> IDEA
    PO --> DESIGN
    PO --> DEV
    PO --> QA
    PO --> DEVOPS

    %% Agent Interactions
    IDEA --> DESIGN
    DESIGN --> DEV
    DEV --> QA
    QA --> DEVOPS
    
    %% Business Operations
    BILL --> STRIPE
    SUPPORT --> DOCS
    MARKET --> DOCS
    
    %% Infrastructure Connections
    DEV --> GH
    DEV --> OPENAI
    DESIGN --> FIGMA
    DESIGN --> OPENAI
    QA --> CB
    DEVOPS --> CR
    AIOPS --> SQL
    
    %% Data Storage
    PO --> SQL
    DEV --> SQL
    QA --> SQL
    BILL --> SQL
    DOCS --> SQL

    %% Secrets Management
    CR --> SM
    API_GW --> SM

    %% Styling
    classDef uiLayer fill:#e8f5e8,stroke:#2d5a2d,stroke-width:2px
    classDef agentLayer fill:#f0f8ff,stroke:#1e90ff,stroke-width:2px  
    classDef infraLayer fill:#fff5ee,stroke:#ff4500,stroke-width:2px
    classDef external fill:#f5f5f5,stroke:#666,stroke-width:2px

    class UI,MP,API_GW uiLayer
    class PO,DEV,QA,DESIGN,IDEA,DEVOPS,AIOPS,SEC,BILL,MARKET,SUPPORT,DOCS agentLayer
    class CR,SQL,VAI,SM,CB infraLayer
    class STRIPE,GH,OPENAI,FIGMA external
```"""

    def _generate_workflow_diagram(self) -> str:
        """Generate workflow diagram for the SaaS Factory pipeline"""
        return """```mermaid
flowchart LR
    START([User Submits Idea]) --> VALIDATE{IdeaAgent<br/>Validation}
    VALIDATE -->|✅ Valid| MARKET[MarketResearchAgent<br/>Analysis]
    VALIDATE -->|❌ Invalid| REJECT[Reject with<br/>Feedback]
    
    MARKET --> TECH[TechStackAgent<br/>Recommendation]
    TECH --> DESIGN[DesignAgent<br/>UI/UX Creation]
    DESIGN --> DEV[DevAgent<br/>Code Generation]
    
    DEV --> QA{ReviewAgent<br/>Testing}
    QA -->|✅ Pass| DEPLOY[DevOpsAgent<br/>Deployment]
    QA -->|❌ Fail| DEV
    
    DEPLOY --> MONITOR[AIOpsAgent<br/>Monitoring]
    MONITOR --> LIVE[🚀 Live SaaS App]
    
    %% Parallel processes
    DEV -.-> DOCS[DocAgent<br/>Documentation]
    DEV -.-> SEC[SecurityAgent<br/>Scan]
    
    %% Business processes
    LIVE --> BILL[BillingAgent<br/>Setup]
    LIVE --> SUPPORT[SupportAgent<br/>Ready]
    
    %% Styling
    classDef start fill:#90EE90,stroke:#006400,stroke-width:2px
    classDef process fill:#87CEEB,stroke:#4682B4,stroke-width:2px
    classDef decision fill:#FFE4B5,stroke:#FF8C00,stroke-width:2px
    classDef end fill:#98FB98,stroke:#006400,stroke-width:2px
    classDef parallel fill:#E6E6FA,stroke:#8A2BE2,stroke-width:2px
    
    class START start
    class MARKET,TECH,DESIGN,DEV,DEPLOY,MONITOR,BILL,SUPPORT process
    class VALIDATE,QA decision
    class LIVE end
    class DOCS,SEC parallel
```"""

    def _generate_deployment_diagram(self) -> str:
        """Generate deployment architecture diagram"""
        return """```mermaid
flowchart TB
    subgraph "🌐 Internet"
        USER[👤 Users]
        DEV[👩‍💻 Developers]
    end

    subgraph "🔗 CDN & Load Balancing"
        CDN[Cloud CDN]
        LB[Cloud Load Balancer]
    end

    subgraph "🏗️ Google Cloud Platform - us-central1"
        subgraph "Frontend Tier"
            UI_CR[UI Cloud Run<br/>React App]
            GW_CR[Gateway Cloud Run<br/>FastAPI]
        end
        
        subgraph "Agent Services Tier"
            DEV_CR[DevAgent<br/>Cloud Run]
            QA_CR[ReviewAgent<br/>Cloud Run]
            DESIGN_CR[DesignAgent<br/>Cloud Run]
            OPS_CR[OpsAgents<br/>Cloud Run]
        end
        
        subgraph "Orchestration Tier"
            VAI[Vertex AI<br/>Agent Engine]
            ORCH[Orchestrator<br/>Container]
        end
        
        subgraph "Data Tier"
            SQL_PRIMARY[Cloud SQL<br/>PostgreSQL Primary]
            REDIS[Redis<br/>Caching]
            BUCKET[Cloud Storage<br/>Artifacts]
        end
        
        subgraph "Operations"
            SM[Secret Manager]
            LOG[Cloud Logging]
            MON[Cloud Monitoring]
            CB[Cloud Build]
        end
    end

    subgraph "🔄 Multi-Region (us-east1)"
        SQL_REPLICA[Cloud SQL<br/>Read Replica]
        UI_CR_BACKUP[UI Cloud Run<br/>Backup]
    end

    subgraph "🔌 External Integrations"
        GITHUB[GitHub<br/>Repositories]
        STRIPE[Stripe<br/>Payments]
        OPENAI[OpenAI<br/>API]
        FIGMA[Figma<br/>Design API]
    end

    %% User connections
    USER --> CDN
    DEV --> GITHUB
    CDN --> LB
    LB --> UI_CR
    LB --> GW_CR

    %% Internal service mesh
    GW_CR --> VAI
    VAI --> ORCH
    ORCH --> DEV_CR
    ORCH --> QA_CR
    ORCH --> DESIGN_CR
    ORCH --> OPS_CR

    %% Data connections
    DEV_CR --> SQL_PRIMARY
    QA_CR --> SQL_PRIMARY
    DESIGN_CR --> SQL_PRIMARY
    OPS_CR --> SQL_PRIMARY
    ORCH --> SQL_PRIMARY
    
    %% Caching
    GW_CR --> REDIS
    DEV_CR --> REDIS

    %% External integrations
    DEV_CR --> GITHUB
    DEV_CR --> OPENAI
    DESIGN_CR --> FIGMA
    DESIGN_CR --> OPENAI
    GW_CR --> STRIPE

    %% Operations
    ALL_SERVICES --> LOG
    ALL_SERVICES --> MON
    CB --> DEV_CR
    CB --> QA_CR
    SM --> ALL_SERVICES

    %% Disaster recovery
    SQL_PRIMARY -.->|Replication| SQL_REPLICA
    UI_CR -.->|Backup| UI_CR_BACKUP

    %% Styling
    classDef external fill:#ffeb3b,stroke:#f57f17,stroke-width:2px
    classDef frontend fill:#4caf50,stroke:#2e7d32,stroke-width:2px
    classDef agent fill:#2196f3,stroke:#1565c0,stroke-width:2px
    classDef data fill:#ff9800,stroke:#ef6c00,stroke-width:2px
    classDef ops fill:#9c27b0,stroke:#6a1b9a,stroke-width:2px
    
    class GITHUB,STRIPE,OPENAI,FIGMA external
    class UI_CR,GW_CR frontend
    class DEV_CR,QA_CR,DESIGN_CR,OPS_CR,VAI,ORCH agent
    class SQL_PRIMARY,SQL_REPLICA,REDIS,BUCKET data
    class SM,LOG,MON,CB ops
```"""

    def _generate_data_flow_diagram(self) -> str:
        """Generate data flow diagram"""
        return """```mermaid
flowchart TD
    subgraph "📝 Input Sources"
        USER_INPUT[User Idea Submission]
        CODE_REPO[GitHub Repository]
        MARKET_DATA[Market Research APIs]
        DESIGN_ASSETS[Figma Designs]
    end

    subgraph "🔄 Processing Pipeline"
        VALIDATE[Idea Validation<br/>& Enrichment]
        GENERATE[Code Generation<br/>& Review]
        BUILD[Build & Test<br/>Pipeline]
        DEPLOY[Deployment<br/>& Monitoring]
    end

    subgraph "💾 Data Storage"
        TENANT_DB[(Multi-Tenant<br/>PostgreSQL)]
        VECTOR_DB[(pgvector<br/>Embeddings)]
        ARTIFACT_STORE[(Cloud Storage<br/>Artifacts)]
        CACHE[(Redis<br/>Cache)]
    end

    subgraph "📊 Output Channels"
        LIVE_APP[🚀 Live SaaS App]
        DASHBOARD[📱 Admin Dashboard]
        DOCS[📚 Documentation]
        REPORTS[📈 Analytics Reports]
    end

    %% Input flow
    USER_INPUT --> VALIDATE
    MARKET_DATA --> VALIDATE
    CODE_REPO --> GENERATE
    DESIGN_ASSETS --> GENERATE

    %% Processing flow
    VALIDATE --> GENERATE
    GENERATE --> BUILD
    BUILD --> DEPLOY

    %% Data storage interactions
    VALIDATE <--> TENANT_DB
    VALIDATE <--> VECTOR_DB
    GENERATE <--> TENANT_DB
    GENERATE <--> ARTIFACT_STORE
    BUILD <--> ARTIFACT_STORE
    DEPLOY <--> TENANT_DB

    %% Caching layer
    VALIDATE <--> CACHE
    GENERATE <--> CACHE
    BUILD <--> CACHE

    %% Output generation
    DEPLOY --> LIVE_APP
    TENANT_DB --> DASHBOARD
    ARTIFACT_STORE --> DOCS
    TENANT_DB --> REPORTS

    %% Real-time updates
    DEPLOY -.->|WebSocket| DASHBOARD
    BUILD -.->|Events| DASHBOARD
    GENERATE -.->|Progress| DASHBOARD

    %% Styling
    classDef input fill:#e8f5e8,stroke:#2d5a2d,stroke-width:2px
    classDef process fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef storage fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef output fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    
    class USER_INPUT,CODE_REPO,MARKET_DATA,DESIGN_ASSETS input
    class VALIDATE,GENERATE,BUILD,DEPLOY process
    class TENANT_DB,VECTOR_DB,ARTIFACT_STORE,CACHE storage
    class LIVE_APP,DASHBOARD,DOCS,REPORTS output
```"""

    def _embed_mermaid_in_content(self, content: str, mermaid_content: str, diagram_type: str) -> str:
        """Embed Mermaid diagram in documentation content"""
        # Find the architecture section or add it after the description
        if "## Architecture" in content:
            content = content.replace(
                "## Architecture",
                f"## Architecture\n\n{mermaid_content}\n\n### Architecture Overview"
            )
        elif "# " in content:
            # Add after the first heading
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('# ') and i < len(lines) - 1:
                    lines.insert(i + 2, f"\n## Architecture\n\n{mermaid_content}\n")
                    break
            content = '\n'.join(lines)
        else:
            content = f"{content}\n\n## Architecture\n\n{mermaid_content}\n"
            
        return content

    async def _store_generated_doc(self, doc: GeneratedDocument, tenant_context: TenantContext):
        """Store generated documentation in database"""
        try:
            query = """
            INSERT INTO generated_documents (
                tenant_id, title, document_type, content, 
                sections, metadata, generated_at, word_count
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """
            
            await self.tenant_db.execute_query(
                query, 
                tenant_context.tenant_id, doc.title, doc.metadata["document_type"],
                doc.content, json.dumps(doc.sections), json.dumps(doc.metadata),
                doc.generated_at, doc.word_count,
                tenant_context=tenant_context
            )
            
        except Exception as e:
            logger.warning(f"Failed to store generated document: {str(e)}")

# FastAPI app setup
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("DocAgent starting up...")
    yield
    logger.info("DocAgent shutting down...")

app = FastAPI(
    title="DocAgent API",
    description="AI-powered documentation generation service",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent
doc_agent = DocAgent()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "docagent", "timestamp": datetime.utcnow()}

@app.post("/generate", response_model=GeneratedDocument)
@require_subscription(AccessLevel.STARTER)
async def generate_documentation(
    spec: DocumentSpec,
    tenant_context: TenantContext = Depends(get_tenant_context_from_headers)
):
    """Generate documentation based on specification"""
    return await doc_agent.generate_documentation(spec, tenant_context)

@app.get("/templates")
async def get_doc_templates():
    """Get available documentation templates"""
    return {
        "templates": list(doc_agent.doc_patterns.keys()),
        "project_context": doc_agent.project_context
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8089) 