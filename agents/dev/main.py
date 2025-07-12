from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ValidationError
import openai
import json
import asyncio
from typing import List, Dict, Any, Optional, Literal
import os
import logging
from contextlib import asynccontextmanager
from datetime import datetime
import uuid
import ast
import subprocess
import tempfile
import shutil
from pathlib import Path

# Import shared components
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from tenant_db import TenantDatabase, TenantContext, get_tenant_context_from_headers

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenAI configuration
openai.api_key = os.getenv("OPENAI_API_KEY")

class ModuleSpec(BaseModel):
    """Pydantic schema for module specification"""
    name: str = Field(..., description="Name of the module")
    description: str = Field(..., description="Description of what the module does")
    module_type: Literal["api", "service", "model", "utility", "component", "page"] = Field(..., description="Type of module")
    language: Literal["python", "javascript", "typescript", "html", "css"] = Field(..., description="Programming language")
    framework: Optional[str] = Field(None, description="Framework (e.g., 'fastapi', 'react', 'vue')")
    dependencies: List[str] = Field(default_factory=list, description="List of dependencies")
    inputs: List[Dict[str, Any]] = Field(default_factory=list, description="Input parameters")
    outputs: List[Dict[str, Any]] = Field(default_factory=list, description="Output parameters")
    functions: List[Dict[str, Any]] = Field(default_factory=list, description="Functions to implement")
    database_tables: List[str] = Field(default_factory=list, description="Database tables used")
    api_endpoints: List[Dict[str, Any]] = Field(default_factory=list, description="API endpoints to create")
    requirements: List[str] = Field(default_factory=list, description="Functional requirements")
    constraints: List[str] = Field(default_factory=list, description="Technical constraints")

class CodeGenerationRequest(BaseModel):
    """Request model for code generation"""
    project_id: Optional[str] = Field(None, description="Project ID")
    module_spec: ModuleSpec = Field(..., description="Module specification")
    style_preferences: Dict[str, Any] = Field(default_factory=dict, description="Code style preferences")
    target_directory: Optional[str] = Field(None, description="Target directory for generated code")
    include_tests: bool = Field(True, description="Whether to include unit tests")
    include_documentation: bool = Field(True, description="Whether to include documentation")

class GeneratedFile(BaseModel):
    """Model for a generated file"""
    filename: str
    content: str
    file_type: str
    language: str
    size_bytes: int
    functions: List[str] = Field(default_factory=list)
    imports: List[str] = Field(default_factory=list)
    exports: List[str] = Field(default_factory=list)

class CodeGenerationResult(BaseModel):
    """Result model for code generation"""
    module_name: str
    files: List[GeneratedFile]
    total_files: int
    total_lines: int
    estimated_complexity: str
    validation_results: Dict[str, Any]
    setup_instructions: List[str]
    next_steps: List[str]
    reasoning: str

class DevAgent:
    """Agent for intelligent code generation using GPT-4o"""
    
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.tenant_db = TenantDatabase()
        self.code_templates = self._load_code_templates()
        
    def _load_code_templates(self) -> Dict[str, str]:
        """Load code templates for different module types"""
        return {
            "python_fastapi_service": """
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class {service_name}:
    \"\"\"
    {service_description}
    \"\"\"
    
    def __init__(self):
        pass
    
    {service_methods}

# Initialize service
{service_name_lower} = {service_name}()
""",
            
            "python_model": """
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

class {model_name}(BaseModel):
    \"\"\"
    {model_description}
    \"\"\"
    
    {model_fields}
    
    class Config:
        json_encoders = {{
            datetime: lambda v: v.isoformat(),
            uuid.UUID: lambda v: str(v)
        }}
""",
            
            "react_component": """
import React, {{ useState, useEffect }} from 'react';
import {{ {component_props_type} }} from './types';

interface {component_name}Props {{
  {component_props}
}}

const {component_name}: React.FC<{component_name}Props> = ({{
  {component_props_destructured}
}}) => {{
  {component_state}
  
  {component_effects}
  
  return (
    <div className="{{component_classes}}">
      {component_jsx}
    </div>
  );
}};

export default {component_name};
""",
            
            "typescript_utility": """
{utility_imports}

/**
 * {utility_description}
 */
export class {utility_name} {{
  {utility_properties}
  
  constructor({constructor_params}) {{
    {constructor_body}
  }}
  
  {utility_methods}
}}

export default {utility_name};
"""
        }
    
    async def _call_gpt4o_function(self, prompt: str, functions: List[Dict[str, Any]], model: str = "gpt-4o") -> Dict[str, Any]:
        """Call GPT-4o with function calling"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert software developer. Generate clean, efficient, and well-documented code following best practices."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ]
            
            response = await self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                functions=functions,
                function_call="auto",
                temperature=0.1,
                max_tokens=4000
            )
            
            choice = response.choices[0]
            
            if choice.message.function_call:
                return {
                    "status": "success",
                    "function_call": choice.message.function_call,
                    "content": choice.message.content
                }
            else:
                return {
                    "status": "success",
                    "content": choice.message.content
                }
                
        except Exception as e:
            logger.error(f"Error calling GPT-4o: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _get_code_generation_functions(self) -> List[Dict[str, Any]]:
        """Get function definitions for GPT-4o function calling"""
        return [
            {
                "name": "generate_python_module",
                "description": "Generate a Python module with specified functions and classes",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "module_name": {"type": "string"},
                        "classes": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "description": {"type": "string"},
                                    "methods": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "name": {"type": "string"},
                                                "parameters": {"type": "array"},
                                                "return_type": {"type": "string"},
                                                "description": {"type": "string"}
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "functions": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "parameters": {"type": "array"},
                                    "return_type": {"type": "string"},
                                    "description": {"type": "string"}
                                }
                            }
                        },
                        "imports": {"type": "array", "items": {"type": "string"}},
                        "dependencies": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["module_name"]
                }
            },
            {
                "name": "generate_react_component",
                "description": "Generate a React component with specified props and functionality",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "component_name": {"type": "string"},
                        "props": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "type": {"type": "string"},
                                    "required": {"type": "boolean"},
                                    "default": {"type": "string"}
                                }
                            }
                        },
                        "state_variables": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "type": {"type": "string"},
                                    "initial_value": {"type": "string"}
                                }
                            }
                        },
                        "methods": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "parameters": {"type": "array"},
                                    "description": {"type": "string"}
                                }
                            }
                        },
                        "styling": {"type": "string"},
                        "imports": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["component_name"]
                }
            },
            {
                "name": "generate_api_endpoint",
                "description": "Generate API endpoints with specified routes and handlers",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "endpoints": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "path": {"type": "string"},
                                    "method": {"type": "string"},
                                    "handler_name": {"type": "string"},
                                    "parameters": {"type": "array"},
                                    "request_body": {"type": "object"},
                                    "response_model": {"type": "object"},
                                    "description": {"type": "string"}
                                }
                            }
                        },
                        "authentication": {"type": "boolean"},
                        "cors": {"type": "boolean"},
                        "rate_limiting": {"type": "boolean"}
                    },
                    "required": ["endpoints"]
                }
            }
        ]
    
    async def generate_code_with_gpt4o(self, module_spec: ModuleSpec, style_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code using GPT-4o function calling"""
        
        # Create detailed prompt based on module spec
        prompt = f"""
        Generate a {module_spec.language} {module_spec.module_type} module with the following specifications:
        
        Module Name: {module_spec.name}
        Description: {module_spec.description}
        Framework: {module_spec.framework or 'None'}
        
        Requirements:
        {chr(10).join(f"- {req}" for req in module_spec.requirements)}
        
        Functions to implement:
        {chr(10).join(f"- {func.get('name', 'Unknown')}: {func.get('description', 'No description')}" for func in module_spec.functions)}
        
        API Endpoints:
        {chr(10).join(f"- {endpoint.get('method', 'GET')} {endpoint.get('path', '/')}: {endpoint.get('description', 'No description')}" for endpoint in module_spec.api_endpoints)}
        
        Dependencies: {', '.join(module_spec.dependencies)}
        
        Style Preferences: {json.dumps(style_preferences, indent=2)}
        
        Please generate clean, well-documented, production-ready code that follows best practices.
        Include proper error handling, type hints, and docstrings.
        """
        
        # Get appropriate functions for the module type
        functions = self._get_code_generation_functions()
        
        # Call GPT-4o
        response = await self._call_gpt4o_function(prompt, functions)
        
        return response
    
    def _parse_generated_code(self, gpt_response: Dict[str, Any], module_spec: ModuleSpec) -> List[GeneratedFile]:
        """Parse GPT-4o response and create GeneratedFile objects"""
        files = []
        
        if gpt_response.get("status") == "success":
            if gpt_response.get("function_call"):
                # Handle function call response
                function_call = gpt_response["function_call"]
                function_name = function_call["name"]
                
                try:
                    arguments = json.loads(function_call["arguments"])
                    
                    if function_name == "generate_python_module":
                        code = self._generate_python_from_spec(arguments, module_spec)
                        files.append(GeneratedFile(
                            filename=f"{module_spec.name.lower()}.py",
                            content=code,
                            file_type="source",
                            language="python",
                            size_bytes=len(code.encode('utf-8')),
                            functions=[cls.get("name", "") for cls in arguments.get("classes", [])],
                            imports=arguments.get("imports", [])
                        ))
                    
                    elif function_name == "generate_react_component":
                        code = self._generate_react_from_spec(arguments, module_spec)
                        files.append(GeneratedFile(
                            filename=f"{module_spec.name}.tsx",
                            content=code,
                            file_type="source",
                            language="typescript",
                            size_bytes=len(code.encode('utf-8')),
                            functions=[method.get("name", "") for method in arguments.get("methods", [])],
                            imports=arguments.get("imports", [])
                        ))
                    
                    elif function_name == "generate_api_endpoint":
                        code = self._generate_api_from_spec(arguments, module_spec)
                        files.append(GeneratedFile(
                            filename=f"{module_spec.name.lower()}_api.py",
                            content=code,
                            file_type="source",
                            language="python",
                            size_bytes=len(code.encode('utf-8')),
                            functions=[endpoint.get("handler_name", "") for endpoint in arguments.get("endpoints", [])],
                            imports=["fastapi", "pydantic"]
                        ))
                        
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing function arguments: {e}")
                    # Fallback to direct code generation
                    code = gpt_response.get("content", "")
                    if code:
                        files.append(GeneratedFile(
                            filename=f"{module_spec.name.lower()}.{self._get_file_extension(module_spec.language)}",
                            content=code,
                            file_type="source",
                            language=module_spec.language,
                            size_bytes=len(code.encode('utf-8')),
                            functions=[],
                            imports=[]
                        ))
            
            elif gpt_response.get("content"):
                # Handle direct content response
                code = gpt_response["content"]
                files.append(GeneratedFile(
                    filename=f"{module_spec.name.lower()}.{self._get_file_extension(module_spec.language)}",
                    content=code,
                    file_type="source",
                    language=module_spec.language,
                    size_bytes=len(code.encode('utf-8')),
                    functions=[],
                    imports=[]
                ))
        
        return files
    
    def _generate_python_from_spec(self, spec: Dict[str, Any], module_spec: ModuleSpec) -> str:
        """Generate Python code from function call specification"""
        imports = spec.get("imports", [])
        classes = spec.get("classes", [])
        functions = spec.get("functions", [])
        
        code_lines = []
        
        # Add imports
        if imports:
            code_lines.extend(imports)
            code_lines.append("")
        
        # Add classes
        for cls in classes:
            class_code = f"class {cls['name']}:"
            if cls.get("description"):
                class_code += f'\n    """{cls["description"]}"""'
            code_lines.append(class_code)
            code_lines.append("")
            
            # Add methods
            for method in cls.get("methods", []):
                method_code = f"    def {method['name']}(self"
                if method.get("parameters"):
                    method_code += f", {', '.join(method['parameters'])}"
                method_code += "):"
                
                if method.get("description"):
                    method_code += f'\n        """{method["description"]}"""'
                method_code += f"\n        pass  # TODO: Implement {method['name']}"
                
                code_lines.append(method_code)
                code_lines.append("")
        
        # Add standalone functions
        for func in functions:
            func_code = f"def {func['name']}("
            if func.get("parameters"):
                func_code += f"{', '.join(func['parameters'])}"
            func_code += "):"
            
            if func.get("description"):
                func_code += f'\n    """{func["description"]}"""'
            func_code += f"\n    pass  # TODO: Implement {func['name']}"
            
            code_lines.append(func_code)
            code_lines.append("")
        
        return "\n".join(code_lines)
    
    def _generate_react_from_spec(self, spec: Dict[str, Any], module_spec: ModuleSpec) -> str:
        """Generate React component code from function call specification"""
        component_name = spec.get("component_name", module_spec.name)
        props = spec.get("props", [])
        state_vars = spec.get("state_variables", [])
        methods = spec.get("methods", [])
        imports = spec.get("imports", ["React", "useState", "useEffect"])
        
        code_lines = []
        
        # Add imports
        code_lines.append(f"import React, {{ {', '.join(imports)} }} from 'react';")
        code_lines.append("")
        
        # Add prop interface
        if props:
            code_lines.append(f"interface {component_name}Props {{")
            for prop in props:
                prop_line = f"  {prop['name']}: {prop['type']}"
                if not prop.get("required", True):
                    prop_line += "?"
                code_lines.append(prop_line + ";")
            code_lines.append("}")
            code_lines.append("")
        
        # Add component
        code_lines.append(f"const {component_name}: React.FC<{component_name}Props> = ({{")
        if props:
            code_lines.append(f"  {', '.join(prop['name'] for prop in props)}")
        code_lines.append("}) => {")
        
        # Add state variables
        for state_var in state_vars:
            code_lines.append(f"  const [{state_var['name']}, set{state_var['name'].capitalize()}] = useState<{state_var['type']}>({state_var.get('initial_value', 'undefined')});")
        
        if state_vars:
            code_lines.append("")
        
        # Add methods
        for method in methods:
            code_lines.append(f"  const {method['name']} = ({', '.join(method.get('parameters', []))}) => {{")
            code_lines.append(f"    // TODO: Implement {method['name']}")
            code_lines.append("  };")
            code_lines.append("")
        
        # Add return JSX
        code_lines.append("  return (")
        code_lines.append(f"    <div className=\"{component_name.lower()}-container\">")
        code_lines.append(f"      <h2>{component_name}</h2>")
        code_lines.append("      {/* TODO: Add component content */}")
        code_lines.append("    </div>")
        code_lines.append("  );")
        code_lines.append("};")
        code_lines.append("")
        code_lines.append(f"export default {component_name};")
        
        return "\n".join(code_lines)
    
    def _generate_api_from_spec(self, spec: Dict[str, Any], module_spec: ModuleSpec) -> str:
        """Generate API endpoints from function call specification"""
        endpoints = spec.get("endpoints", [])
        
        code_lines = []
        
        # Add imports
        code_lines.extend([
            "from fastapi import FastAPI, HTTPException, Depends",
            "from pydantic import BaseModel",
            "from typing import List, Dict, Any, Optional",
            "import logging",
            "",
            "logger = logging.getLogger(__name__)",
            "",
            "app = FastAPI()",
            ""
        ])
        
        # Add endpoints
        for endpoint in endpoints:
            method = endpoint.get("method", "GET").lower()
            path = endpoint.get("path", "/")
            handler_name = endpoint.get("handler_name", f"handle_{method}")
            
            code_lines.append(f"@app.{method}('{path}')")
            code_lines.append(f"async def {handler_name}({', '.join(endpoint.get('parameters', []))}):")
            if endpoint.get("description"):
                code_lines.append(f'    """{endpoint["description"]}"""')
            code_lines.append(f"    # TODO: Implement {handler_name}")
            code_lines.append("    return {'status': 'success'}")
            code_lines.append("")
        
        return "\n".join(code_lines)
    
    def _get_file_extension(self, language: str) -> str:
        """Get file extension for language"""
        extensions = {
            "python": "py",
            "javascript": "js",
            "typescript": "ts",
            "html": "html",
            "css": "css"
        }
        return extensions.get(language, "txt")
    
    def _validate_generated_code(self, files: List[GeneratedFile]) -> Dict[str, Any]:
        """Validate generated code for syntax errors"""
        results = {}
        
        for file in files:
            if file.language == "python":
                try:
                    ast.parse(file.content)
                    results[file.filename] = {"valid": True, "errors": []}
                except SyntaxError as e:
                    results[file.filename] = {
                        "valid": False,
                        "errors": [f"Syntax error: {str(e)}"]
                    }
            else:
                # For other languages, basic validation
                results[file.filename] = {
                    "valid": True,
                    "errors": [],
                    "warnings": ["Syntax validation not implemented for this language"]
                }
        
        return results
    
    async def generate_code(self, request: CodeGenerationRequest, tenant_context: TenantContext) -> CodeGenerationResult:
        """Generate code based on module specification"""
        logger.info(f"Generating code for module: {request.module_spec.name}")
        
        # Log the generation request
        await self.tenant_db.log_agent_event(
            tenant_context=tenant_context,
            event_type="code_generation",
            agent_name="DevAgent",
            stage="code_generation",
            status="started",
            project_id=request.project_id,
            input_data=request.model_dump()
        )
        
        try:
            # Generate code using GPT-4o
            gpt_response = await self.generate_code_with_gpt4o(
                request.module_spec,
                request.style_preferences
            )
            
            # Parse generated code into files
            files = self._parse_generated_code(gpt_response, request.module_spec)
            
            # Add unit tests if requested
            if request.include_tests:
                test_file = self._generate_test_file(request.module_spec, files)
                if test_file:
                    files.append(test_file)
            
            # Add documentation if requested
            if request.include_documentation:
                doc_file = self._generate_documentation(request.module_spec, files)
                if doc_file:
                    files.append(doc_file)
            
            # Validate generated code
            validation_results = self._validate_generated_code(files)
            
            # Calculate metrics
            total_lines = sum(len(f.content.splitlines()) for f in files)
            
            # Generate setup instructions
            setup_instructions = self._generate_setup_instructions(request.module_spec, files)
            
            # Generate next steps
            next_steps = self._generate_next_steps(request.module_spec, files)
            
            # Create result
            result = CodeGenerationResult(
                module_name=request.module_spec.name,
                files=files,
                total_files=len(files),
                total_lines=total_lines,
                estimated_complexity="Medium" if total_lines > 100 else "Low",
                validation_results=validation_results,
                setup_instructions=setup_instructions,
                next_steps=next_steps,
                reasoning=f"Generated {len(files)} files for {request.module_spec.module_type} module '{request.module_spec.name}' using GPT-4o function calling with {request.module_spec.language} language."
            )
            
            # Log successful completion
            await self.tenant_db.log_agent_event(
                tenant_context=tenant_context,
                event_type="code_generation",
                agent_name="DevAgent",
                stage="code_generation",
                status="completed",
                project_id=request.project_id,
                output_data=result.model_dump(exclude={"files"})  # Exclude large file content
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating code: {e}")
            
            # Log failure
            await self.tenant_db.log_agent_event(
                tenant_context=tenant_context,
                event_type="code_generation",
                agent_name="DevAgent",
                stage="code_generation",
                status="failed",
                project_id=request.project_id,
                error_message=str(e)
            )
            
            raise HTTPException(status_code=500, detail=str(e))
    
    def _generate_test_file(self, module_spec: ModuleSpec, files: List[GeneratedFile]) -> Optional[GeneratedFile]:
        """Generate unit test file"""
        if module_spec.language != "python":
            return None
        
        test_content = f"""
import pytest
from {module_spec.name.lower()} import *

class Test{module_spec.name.replace('_', '').title()}:
    \"\"\"Test suite for {module_spec.name} module\"\"\"
    
    def test_{module_spec.name.lower()}_creation(self):
        \"\"\"Test basic creation functionality\"\"\"
        # TODO: Add test implementation
        pass
    
    def test_{module_spec.name.lower()}_functionality(self):
        \"\"\"Test main functionality\"\"\"
        # TODO: Add test implementation
        pass
"""
        
        return GeneratedFile(
            filename=f"test_{module_spec.name.lower()}.py",
            content=test_content.strip(),
            file_type="test",
            language="python",
            size_bytes=len(test_content.encode('utf-8')),
            functions=[f"test_{module_spec.name.lower()}_creation", f"test_{module_spec.name.lower()}_functionality"],
            imports=["pytest"]
        )
    
    def _generate_documentation(self, module_spec: ModuleSpec, files: List[GeneratedFile]) -> Optional[GeneratedFile]:
        """Generate documentation file"""
        doc_content = f"""
# {module_spec.name.title()} Module

## Description
{module_spec.description}

## Module Type
{module_spec.module_type}

## Language
{module_spec.language}

## Files Generated
{chr(10).join(f"- {file.filename}" for file in files)}

## Requirements
{chr(10).join(f"- {req}" for req in module_spec.requirements)}

## Dependencies
{chr(10).join(f"- {dep}" for dep in module_spec.dependencies)}

## Usage
TODO: Add usage examples

## API Documentation
TODO: Add API documentation if applicable
"""
        
        return GeneratedFile(
            filename=f"{module_spec.name.lower()}_README.md",
            content=doc_content.strip(),
            file_type="documentation",
            language="markdown",
            size_bytes=len(doc_content.encode('utf-8')),
            functions=[],
            imports=[]
        )
    
    def _generate_setup_instructions(self, module_spec: ModuleSpec, files: List[GeneratedFile]) -> List[str]:
        """Generate setup instructions"""
        instructions = []
        
        if module_spec.language == "python":
            instructions.extend([
                "1. Install Python dependencies:",
                f"   pip install {' '.join(module_spec.dependencies)}",
                "2. Place generated files in your project directory",
                "3. Run tests: pytest test_*.py"
            ])
        elif module_spec.language in ["javascript", "typescript"]:
            instructions.extend([
                "1. Install Node.js dependencies:",
                f"   npm install {' '.join(module_spec.dependencies)}",
                "2. Place generated files in your project directory", 
                "3. Build project: npm run build"
            ])
        
        return instructions
    
    def _generate_next_steps(self, module_spec: ModuleSpec, files: List[GeneratedFile]) -> List[str]:
        """Generate next steps"""
        return [
            "1. Review generated code for accuracy",
            "2. Implement TODO items in the code",
            "3. Add proper error handling",
            "4. Write comprehensive unit tests",
            "5. Test integration with other components",
            "6. Deploy to development environment"
        ]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Dev Agent")
    yield
    # Shutdown
    logger.info("Shutting down Dev Agent")

app = FastAPI(
    title="Dev Agent",
    description="Intelligent code generation agent using GPT-4o",
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
dev_agent = DevAgent()

async def get_tenant_context(request) -> TenantContext:
    """Get tenant context from request headers"""
    headers = dict(request.headers)
    tenant_context = get_tenant_context_from_headers(headers)
    if not tenant_context:
        # For development, use default tenant
        tenant_context = TenantContext(tenant_id="default", user_id="dev-user")
    return tenant_context

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Dev Agent v1.0", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "OK", "agent": "dev", "version": "1.0.0"}

@app.post("/generate", response_model=CodeGenerationResult)
async def generate_code_endpoint(
    request: CodeGenerationRequest,
    tenant_context: TenantContext = Depends(get_tenant_context)
):
    """Generate code based on module specification"""
    return await dev_agent.generate_code(request, tenant_context)

@app.get("/templates")
async def get_code_templates():
    """Get available code templates"""
    return {
        "python": ["fastapi_service", "pydantic_model", "utility_class"],
        "javascript": ["react_component", "express_router", "utility_function"],
        "typescript": ["react_component", "type_definitions", "service_class"]
    }

@app.get("/languages")
async def get_supported_languages():
    """Get supported programming languages"""
    return {
        "languages": ["python", "javascript", "typescript", "html", "css"],
        "frameworks": ["fastapi", "react", "vue", "express", "flask"]
    }

@app.post("/feedback")
async def receive_review_feedback(
    feedback_data: Dict[str, Any],
    tenant_context: TenantContext = Depends(get_tenant_context)
):
    """Receive feedback from ReviewAgent and potentially regenerate code"""
    try:
        request_id = feedback_data.get("request_id")
        review_passed = feedback_data.get("review_passed", False)
        issues = feedback_data.get("issues", [])
        suggestions = feedback_data.get("suggestions", [])
        code_quality_score = feedback_data.get("code_quality_score", 0.0)
        retry_recommended = feedback_data.get("retry_recommended", False)
        
        logger.info(f"Received review feedback for request {request_id}: passed={review_passed}")
        
        # Log feedback event
        await dev_agent.tenant_db.log_agent_event(
            tenant_context=tenant_context,
            event_type="review_feedback",
            agent_name="DevAgent",
            stage="feedback_received",
            status="completed",
            input_data={
                "request_id": request_id,
                "review_passed": review_passed,
                "issues_count": len(issues),
                "code_quality_score": code_quality_score,
                "retry_recommended": retry_recommended
            }
        )
        
        feedback_response = {
            "message": "Feedback received successfully",
            "request_id": request_id,
            "will_retry": False
        }
        
        # If review failed and retry is recommended, we could implement auto-retry logic here
        if not review_passed and retry_recommended:
            # Store feedback for potential retry
            # In a full implementation, this would:
            # 1. Store the original request
            # 2. Analyze the feedback
            # 3. Modify the prompt/generation strategy
            # 4. Regenerate the code
            # 5. Send back to ReviewAgent
            
            logger.info(f"Review failed for {request_id}. Issues: {len(issues)}, Score: {code_quality_score}")
            
            # For now, just log what we would do
            if issues:
                logger.info("Issues to address:")
                for issue in issues[:5]:  # Log first 5 issues
                    logger.info(f"  - {issue}")
            
            if suggestions:
                logger.info("Suggestions received:")
                for suggestion in suggestions[:3]:  # Log first 3 suggestions
                    logger.info(f"  - {suggestion}")
            
            feedback_response["will_retry"] = False  # Set to True when auto-retry is implemented
            feedback_response["feedback_stored"] = True
        
        return feedback_response
        
    except Exception as e:
        logger.error(f"Error processing review feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/regenerate")
async def regenerate_code_with_feedback(
    regenerate_request: Dict[str, Any],
    tenant_context: TenantContext = Depends(get_tenant_context)
):
    """Regenerate code based on review feedback"""
    try:
        original_request_id = regenerate_request.get("original_request_id")
        feedback = regenerate_request.get("feedback", {})
        issues = feedback.get("issues", [])
        suggestions = feedback.get("suggestions", [])
        original_spec = regenerate_request.get("original_module_spec")
        
        if not original_spec:
            raise HTTPException(status_code=400, detail="Original module spec required for regeneration")
        
        logger.info(f"Regenerating code for request {original_request_id} based on feedback")
        
        # Create enhanced module spec incorporating feedback
        enhanced_spec = ModuleSpec(**original_spec)
        
        # Add feedback-based requirements
        feedback_requirements = []
        for issue in issues:
            if "assertion" in issue.lower():
                feedback_requirements.append("Ensure all test assertions use correct expected values")
            elif "import" in issue.lower():
                feedback_requirements.append("Verify all import statements and dependencies")
            elif "type" in issue.lower():
                feedback_requirements.append("Add comprehensive type hints and validate function signatures")
            elif "syntax" in issue.lower():
                feedback_requirements.append("Review code syntax and Python grammar")
        
        enhanced_spec.requirements.extend(feedback_requirements)
        
        # Add suggestion-based constraints
        enhanced_spec.constraints.extend(suggestions)
        
        # Create new generation request
        enhanced_request = CodeGenerationRequest(
            project_id=regenerate_request.get("project_id"),
            module_spec=enhanced_spec,
            style_preferences={
                "follow_pep8": True,
                "use_type_hints": True,
                "include_docstrings": True,
                "address_review_feedback": True
            },
            include_tests=True,
            include_documentation=True
        )
        
        # Generate improved code
        result = await dev_agent.generate_code(enhanced_request, tenant_context)
        
        # Mark as regeneration
        result_dict = result.model_dump()
        result_dict["is_regeneration"] = True
        result_dict["original_request_id"] = original_request_id
        result_dict["feedback_addressed"] = len(issues) + len(suggestions)
        
        return result_dict
        
    except Exception as e:
        logger.error(f"Error regenerating code: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/generation-history/{project_id}")
async def get_generation_history(
    project_id: str,
    limit: int = 10,
    tenant_context: TenantContext = Depends(get_tenant_context)
):
    """Get code generation history for a project"""
    try:
        events = await dev_agent.tenant_db.get_tenant_events(
            tenant_context=tenant_context,
            event_type="code_generation"
        )
        
        # Filter by project and limit
        project_events = [e for e in events if e.get('project_id') == project_id][:limit]
        
        return {"project_id": project_id, "generations": project_events}
        
    except Exception as e:
        logger.error(f"Error getting generation history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8083) 