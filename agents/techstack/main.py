from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from typing import List, Dict, Any, Optional
import os
import logging
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TechStackRequest(BaseModel):
    """Request model for tech stack recommendation"""
    project_type: str  # web, mobile, api, ml, etc.
    requirements: List[str] = []
    preferences: Dict[str, Any] = {}
    team_size: Optional[int] = None
    timeline: Optional[str] = None

class LibraryScore(BaseModel):
    """Model for library scoring data"""
    name: str
    description: str
    stars: int
    forks: int
    issues: int
    last_update: str
    language: str
    url: str
    score: float
    pros: List[str] = []
    cons: List[str] = []

class TechStackRecommendation(BaseModel):
    """Model for complete tech stack recommendation"""
    project_type: str
    frontend: List[LibraryScore]
    backend: List[LibraryScore] 
    database: List[LibraryScore]
    deployment: List[LibraryScore]
    testing: List[LibraryScore]
    overall_score: float
    reasoning: str
    alternative_stacks: List[Dict[str, Any]] = []

class TechStackAgent:
    """Agent for analyzing and recommending technology stacks"""
    
    def __init__(self):
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.awesome_lists_cache = {}
        
    async def fetch_awesome_list(self, list_name: str) -> Dict[str, Any]:
        """Fetch data from awesome lists on GitHub"""
        try:
            headers = {}
            if self.github_token:
                headers["Authorization"] = f"token {self.github_token}"
                
            async with httpx.AsyncClient() as client:
                # Fetch the awesome list README
                url = f"https://api.github.com/repos/sindresorhus/awesome-{list_name}/readme"
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    readme_data = response.json()
                    return readme_data
                    
        except Exception as e:
            logger.error(f"Error fetching awesome list {list_name}: {e}")
            
        return {}
    
    async def get_github_repo_stats(self, repo_full_name: str) -> Dict[str, Any]:
        """Get GitHub repository statistics"""
        try:
            headers = {}
            if self.github_token:
                headers["Authorization"] = f"token {self.github_token}"
                
            async with httpx.AsyncClient() as client:
                url = f"https://api.github.com/repos/{repo_full_name}"
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    repo_data = response.json()
                    return {
                        "stars": repo_data.get("stargazers_count", 0),
                        "forks": repo_data.get("forks_count", 0),
                        "issues": repo_data.get("open_issues_count", 0),
                        "last_update": repo_data.get("updated_at", ""),
                        "language": repo_data.get("language", ""),
                        "description": repo_data.get("description", ""),
                        "url": repo_data.get("html_url", "")
                    }
                    
        except Exception as e:
            logger.error(f"Error fetching repo stats for {repo_full_name}: {e}")
            
        return {}
    
    def calculate_library_score(self, repo_stats: Dict[str, Any]) -> float:
        """Calculate a score for a library based on GitHub metrics"""
        stars = repo_stats.get("stars", 0)
        forks = repo_stats.get("forks", 0)
        issues = repo_stats.get("issues", 0)
        
        # Weighted scoring algorithm
        star_score = min(stars / 1000, 10) * 0.4  # Cap at 10k stars
        fork_score = min(forks / 200, 10) * 0.3   # Cap at 2k forks
        issue_penalty = min(issues / 100, 5) * -0.1  # Penalty for too many open issues
        
        # Bonus for recent activity (simplified)
        activity_bonus = 0.3 if repo_stats.get("last_update") else 0
        
        total_score = star_score + fork_score + issue_penalty + activity_bonus
        return max(0, min(10, total_score))  # Scale 0-10
    
    def get_library_pros_cons(self, lib_name: str, repo_stats: Dict[str, Any]) -> tuple[List[str], List[str]]:
        """Generate pros and cons for a library based on stats and common knowledge"""
        pros = []
        cons = []
        
        # General pros based on metrics
        if repo_stats.get("stars", 0) > 5000:
            pros.append("Large community and ecosystem")
        if repo_stats.get("forks", 0) > 500:
            pros.append("Active contribution community")
        if repo_stats.get("issues", 0) < 100:
            pros.append("Well-maintained with few open issues")
            
        # General cons based on metrics
        if repo_stats.get("issues", 0) > 500:
            cons.append("High number of open issues")
        if repo_stats.get("forks", 0) < 50:
            cons.append("Limited community contributions")
            
        # Technology-specific pros/cons (simplified knowledge base)
        tech_knowledge = {
            "react": {
                "pros": ["Component-based architecture", "Large ecosystem", "Virtual DOM"],
                "cons": ["Learning curve", "Rapid changes", "Build complexity"]
            },
            "vue": {
                "pros": ["Gentle learning curve", "Flexible", "Good documentation"],
                "cons": ["Smaller ecosystem than React", "Less enterprise adoption"]
            },
            "fastapi": {
                "pros": ["Automatic API docs", "Type hints", "High performance"],
                "cons": ["Newer framework", "Smaller community than Flask"]
            },
            "django": {
                "pros": ["Batteries included", "ORM", "Admin interface"],
                "cons": ["Can be overkill", "Monolithic", "Learning curve"]
            }
        }
        
        lib_lower = lib_name.lower()
        for tech, knowledge in tech_knowledge.items():
            if tech in lib_lower:
                pros.extend(knowledge["pros"])
                cons.extend(knowledge["cons"])
                break
                
        return pros[:3], cons[:3]  # Limit to top 3 each
    
    async def get_recommended_libraries(self, category: str, project_type: str) -> List[LibraryScore]:
        """Get recommended libraries for a specific category"""
        # Predefined popular libraries by category and project type
        library_sets = {
            "web": {
                "frontend": ["facebook/react", "vuejs/vue", "angular/angular", "sveltejs/svelte"],
                "backend": ["tiangolo/fastapi", "django/django", "pallets/flask", "expressjs/express"],
                "database": ["postgres/postgres", "mongodb/mongo", "redis/redis"],
                "deployment": ["docker/docker", "kubernetes/kubernetes", "vercel/vercel"],
                "testing": ["facebook/jest", "pytest-dev/pytest", "cypress-io/cypress"]
            },
            "api": {
                "backend": ["tiangolo/fastapi", "django/django-rest-framework", "pallets/flask"],
                "database": ["postgres/postgres", "mongodb/mongo", "redis/redis"],
                "deployment": ["docker/docker", "kubernetes/kubernetes"],
                "testing": ["pytest-dev/pytest", "postmanlabs/newman"]
            },
            "mobile": {
                "frontend": ["facebook/react-native", "flutter/flutter", "ionic-team/ionic"],
                "backend": ["firebase/firebase-js-sdk", "supabase/supabase"],
                "testing": ["detox/detox", "wix/maestro"]
            }
        }
        
        repo_names = library_sets.get(project_type, library_sets["web"]).get(category, [])
        
        libraries = []
        for repo_name in repo_names[:5]:  # Limit to top 5
            try:
                repo_stats = await self.get_github_repo_stats(repo_name)
                if repo_stats:
                    score = self.calculate_library_score(repo_stats)
                    pros, cons = self.get_library_pros_cons(repo_name.split("/")[-1], repo_stats)
                    
                    library = LibraryScore(
                        name=repo_name.split("/")[-1],
                        description=repo_stats.get("description", ""),
                        stars=repo_stats.get("stars", 0),
                        forks=repo_stats.get("forks", 0),
                        issues=repo_stats.get("issues", 0),
                        last_update=repo_stats.get("last_update", ""),
                        language=repo_stats.get("language", ""),
                        url=repo_stats.get("url", ""),
                        score=score,
                        pros=pros,
                        cons=cons
                    )
                    libraries.append(library)
                    
            except Exception as e:
                logger.error(f"Error processing library {repo_name}: {e}")
                
        # Sort by score descending
        return sorted(libraries, key=lambda x: x.score, reverse=True)
    
    async def generate_recommendation(self, request: TechStackRequest) -> TechStackRecommendation:
        """Generate complete tech stack recommendation"""
        logger.info(f"Generating recommendation for project type: {request.project_type}")
        
        # Get recommendations for each category
        frontend_libs = await self.get_recommended_libraries("frontend", request.project_type)
        backend_libs = await self.get_recommended_libraries("backend", request.project_type)
        database_libs = await self.get_recommended_libraries("database", request.project_type)
        deployment_libs = await self.get_recommended_libraries("deployment", request.project_type)
        testing_libs = await self.get_recommended_libraries("testing", request.project_type)
        
        # Calculate overall score
        all_libs = frontend_libs + backend_libs + database_libs + deployment_libs + testing_libs
        overall_score = sum(lib.score for lib in all_libs) / len(all_libs) if all_libs else 0
        
        # Generate reasoning
        reasoning = f"Based on analysis of {len(all_libs)} libraries for {request.project_type} project. "
        reasoning += "Top recommendations prioritize community support, maintenance activity, and ecosystem maturity. "
        reasoning += f"Overall stack score: {overall_score:.1f}/10"
        
        return TechStackRecommendation(
            project_type=request.project_type,
            frontend=frontend_libs,
            backend=backend_libs,
            database=database_libs,
            deployment=deployment_libs,
            testing=testing_libs,
            overall_score=round(overall_score, 1),
            reasoning=reasoning
        )

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting TechStack Agent")
    yield
    # Shutdown
    logger.info("Shutting down TechStack Agent")

app = FastAPI(
    title="TechStack Agent",
    description="Intelligent technology stack recommendation agent",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent
tech_agent = TechStackAgent()

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "TechStack Agent v1.0", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "OK", "agent": "techstack", "version": "1.0.0"}

@app.post("/recommend", response_model=TechStackRecommendation)
async def recommend_tech_stack(request: TechStackRequest):
    """Generate technology stack recommendations"""
    try:
        recommendation = await tech_agent.generate_recommendation(request)
        return recommendation
    except Exception as e:
        logger.error(f"Error generating recommendation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/categories")
async def get_categories():
    """Get available project categories"""
    return {
        "categories": ["web", "api", "mobile", "ml", "desktop"],
        "stack_components": ["frontend", "backend", "database", "deployment", "testing"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081) 