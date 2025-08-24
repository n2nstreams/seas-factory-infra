#!/usr/bin/env python3
"""
Demo script for DevAgent - Shows how to use the DevAgent for code generation
"""

import asyncio
from main import DevAgent, ModuleSpec, CodeGenerationRequest, TenantContext

async def demo_python_service_generation():
    """Demo: Generate a Python FastAPI service"""
    print("🚀 Demo: Generating Python FastAPI Service")
    print("=" * 50)
    
    # Create DevAgent instance
    dev_agent = DevAgent()
    
    # Define module specification
    module_spec = ModuleSpec(
        name="TaskService",
        description="A REST API service for managing tasks and todo items",
        module_type="service",
        language="python",
        framework="fastapi",
        dependencies=["fastapi", "pydantic", "sqlalchemy", "uvicorn"],
        functions=[
            {
                "name": "create_task",
                "description": "Create a new task",
                "parameters": ["title", "description", "priority"]
            },
            {
                "name": "get_task",
                "description": "Retrieve a task by ID",
                "parameters": ["task_id"]
            },
            {
                "name": "update_task",
                "description": "Update an existing task",
                "parameters": ["task_id", "updates"]
            },
            {
                "name": "delete_task",
                "description": "Delete a task",
                "parameters": ["task_id"]
            }
        ],
        api_endpoints=[
            {
                "method": "POST",
                "path": "/tasks",
                "handler_name": "create_task_endpoint",
                "description": "Create a new task"
            },
            {
                "method": "GET",
                "path": "/tasks/{task_id}",
                "handler_name": "get_task_endpoint",
                "description": "Get task by ID"
            },
            {
                "method": "PUT",
                "path": "/tasks/{task_id}",
                "handler_name": "update_task_endpoint",
                "description": "Update task"
            },
            {
                "method": "DELETE",
                "path": "/tasks/{task_id}",
                "handler_name": "delete_task_endpoint",
                "description": "Delete task"
            }
        ],
        requirements=[
            "Tasks must have unique IDs",
            "Task titles are required",
            "Priority must be high, medium, or low",
            "API should return proper HTTP status codes"
        ]
    )
    
    # Create generation request
    request = CodeGenerationRequest(
        project_id="demo-project",
        module_spec=module_spec,
        style_preferences={
            "follow_pep8": True,
            "use_type_hints": True,
            "include_docstrings": True
        },
        include_tests=True,
        include_documentation=True
    )
    
    # Create tenant context
    tenant_context = TenantContext(tenant_id="demo-tenant", user_id="demo-user")
    
    try:
        # Generate code
        print("🔧 Generating code...")
        result = await dev_agent.generate_code(request, tenant_context)
        
        print("✅ Code generation completed!")
        print(f"📁 Generated {result.total_files} files")
        print(f"📝 Total lines of code: {result.total_lines}")
        print(f"🎯 Estimated complexity: {result.estimated_complexity}")
        
        # Display generated files
        print("\n📋 Generated Files:")
        for file in result.files:
            print(f"  - {file.filename} ({file.file_type}, {file.language})")
        
        # Show validation results
        print("\n🔍 Validation Results:")
        for filename, validation in result.validation_results.items():
            status = "✅ Valid" if validation["valid"] else "❌ Invalid"
            print(f"  - {filename}: {status}")
            if validation.get("errors"):
                for error in validation["errors"]:
                    print(f"    ⚠️  {error}")
        
        # Show setup instructions
        print("\n📖 Setup Instructions:")
        for i, instruction in enumerate(result.setup_instructions, 1):
            print(f"  {i}. {instruction}")
        
        # Show first generated file content (preview)
        if result.files:
            print(f"\n📄 Preview of {result.files[0].filename}:")
            print("-" * 40)
            print(result.files[0].content[:500] + "..." if len(result.files[0].content) > 500 else result.files[0].content)
        
    except Exception as e:
        print(f"❌ Error during code generation: {e}")

async def demo_react_component_generation():
    """Demo: Generate a React component"""
    print("\n🚀 Demo: Generating React Component")
    print("=" * 50)
    
    # Create DevAgent instance
    dev_agent = DevAgent()
    
    # Define module specification
    module_spec = ModuleSpec(
        name="TaskCard",
        description="A React component for displaying task information with glassmorphism styling",
        module_type="component",
        language="typescript",
        framework="react",
        dependencies=["react", "@types/react", "tailwindcss"],
        functions=[
            {
                "name": "onTaskClick",
                "description": "Handle task click events",
                "parameters": ["task"]
            },
            {
                "name": "onTaskComplete",
                "description": "Handle task completion",
                "parameters": ["taskId"]
            },
            {
                "name": "onTaskDelete",
                "description": "Handle task deletion",
                "parameters": ["taskId"]
            }
        ],
        requirements=[
            "Component should use glassmorphism styling",
            "Component should be responsive",
            "Component should handle loading states",
            "Component should use natural olive green color scheme"
        ]
    )
    
    # Create generation request
    request = CodeGenerationRequest(
        project_id="demo-project",
        module_spec=module_spec,
        style_preferences={
            "use_glassmorphism": True,
            "color_scheme": "natural_olive_green",
            "responsive": True
        },
        include_tests=False,  # Skip tests for component demo
        include_documentation=True
    )
    
    # Create tenant context
    tenant_context = TenantContext(tenant_id="demo-tenant", user_id="demo-user")
    
    try:
        # Generate code
        print("🔧 Generating React component...")
        result = await dev_agent.generate_code(request, tenant_context)
        
        print("✅ Component generation completed!")
        print(f"📁 Generated {result.total_files} files")
        
        # Display generated files
        print("\n📋 Generated Files:")
        for file in result.files:
            print(f"  - {file.filename} ({file.file_type}, {file.language})")
        
        # Show first generated file content (preview)
        if result.files:
            print(f"\n📄 Preview of {result.files[0].filename}:")
            print("-" * 40)
            print(result.files[0].content)
        
    except Exception as e:
        print(f"❌ Error during component generation: {e}")

async def demo_api_endpoint_generation():
    """Demo: Generate API endpoints"""
    print("\n🚀 Demo: Generating API Endpoints")
    print("=" * 50)
    
    # Create DevAgent instance
    dev_agent = DevAgent()
    
    # Define module specification
    module_spec = ModuleSpec(
        name="UserAPI",
        description="REST API endpoints for user management",
        module_type="api",
        language="python",
        framework="fastapi",
        dependencies=["fastapi", "pydantic", "bcrypt", "python-jose"],
        api_endpoints=[
            {
                "method": "POST",
                "path": "/api/users/register",
                "handler_name": "register_user",
                "description": "Register a new user"
            },
            {
                "method": "POST",
                "path": "/api/users/login",
                "handler_name": "login_user",
                "description": "Authenticate user and return JWT token"
            },
            {
                "method": "GET",
                "path": "/api/users/profile",
                "handler_name": "get_user_profile",
                "description": "Get authenticated user profile"
            },
            {
                "method": "PUT",
                "path": "/api/users/profile",
                "handler_name": "update_user_profile",
                "description": "Update user profile"
            }
        ],
        requirements=[
            "All endpoints should require authentication except registration and login",
            "Passwords should be hashed using bcrypt",
            "JWT tokens should be used for authentication",
            "Proper HTTP status codes should be returned"
        ]
    )
    
    # Create generation request
    request = CodeGenerationRequest(
        project_id="demo-project",
        module_spec=module_spec,
        style_preferences={
            "follow_pep8": True,
            "use_type_hints": True,
            "include_error_handling": True
        },
        include_tests=True,
        include_documentation=True
    )
    
    # Create tenant context
    tenant_context = TenantContext(tenant_id="demo-tenant", user_id="demo-user")
    
    try:
        # Generate code
        print("🔧 Generating API endpoints...")
        result = await dev_agent.generate_code(request, tenant_context)
        
        print("✅ API generation completed!")
        print(f"📁 Generated {result.total_files} files")
        
        # Display generated files
        print("\n📋 Generated Files:")
        for file in result.files:
            print(f"  - {file.filename} ({file.file_type}, {file.language})")
        
        # Show reasoning
        print("\n🤔 Generation Reasoning:")
        print(result.reasoning)
        
    except Exception as e:
        print(f"❌ Error during API generation: {e}")

async def main():
    """Run all demos"""
    print("🎯 DevAgent Code Generation Demo")
    print("=" * 60)
    print("This demo shows the DevAgent's capability to generate code using GPT-4o")
    print("function calling with pydantic schemas for module specifications.")
    print()
    
    # Run demos
    await demo_python_service_generation()
    await demo_react_component_generation()
    await demo_api_endpoint_generation()
    
    print("\n🎉 Demo completed!")
    print("📚 The DevAgent can generate:")
    print("  - Python FastAPI services")
    print("  - React/TypeScript components")
    print("  - API endpoints")
    print("  - Unit tests")
    print("  - Documentation")
    print("  - Setup instructions")
    print()
    print("💡 Next steps:")
    print("  1. Start the DevAgent server: python main.py")
    print("  2. Send POST requests to /generate endpoint")
    print("  3. Integrate with the orchestrator for full workflow")

if __name__ == "__main__":
    asyncio.run(main()) 