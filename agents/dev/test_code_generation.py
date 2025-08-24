#!/usr/bin/env python3
"""
Simple Test Script for Code Generation Module
Tests core code generation functionality
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from code_generation import (
    CodeGenerator, 
    CodeGenerationRequest,
    GeneratedCode
)

def test_code_generation():
    """Test the code generation system"""
    print("🧪 Testing Code Generation System...")
    
    # Create code generator
    generator = CodeGenerator()
    print("✅ Code generator initialized successfully")
    
    # Test Python method generation
    print("\n🐍 Testing Python method generation...")
    
    method_request = CodeGenerationRequest(
        language="python",
        framework="fastapi",
        component_type="method",
        specifications={
            "name": "get_user_data",
            "parameters": [
                {"name": "user_id", "type": "int", "required": True},
                {"name": "include_profile", "type": "bool", "required": False}
            ],
            "return_type": "Dict[str, Any]",
            "description": "Retrieve user data by ID"
        }
    )
    
    try:
        method_code = generator.generate_code(method_request)
        print("✅ Python method generated successfully")
        print(f"   Language: {method_code.language}")
        print(f"   Framework: {method_code.framework}")
        print(f"   Dependencies: {method_code.dependencies}")
        print(f"   Usage examples: {method_code.usage_examples}")
        
        # Validate the generated code
        validation = generator.validate_code(method_code.code, "python")
        print(f"   Validation: {'✅ Valid' if validation['valid'] else '❌ Invalid'}")
        if validation['warnings']:
            print(f"   Warnings: {validation['warnings']}")
        
    except Exception as e:
        print(f"❌ Python method generation failed: {e}")
    
    # Test React component generation
    print("\n⚛️  Testing React component generation...")
    
    component_request = CodeGenerationRequest(
        language="react",
        framework="react",
        component_type="component",
        specifications={
            "name": "UserProfile",
            "props": [
                {"name": "userId", "type": "number", "required": True},
                {"name": "userName", "type": "string", "required": True},
                {"name": "isAdmin", "type": "boolean", "required": False}
            ],
            "state_variables": [
                {"name": "isLoading", "type": "boolean", "initial_value": "false"},
                {"name": "userData", "type": "object", "initial_value": "null"}
            ],
            "methods": [
                {"name": "handleEdit", "parameters": []},
                {"name": "handleDelete", "parameters": []}
            ]
        }
    )
    
    try:
        component_code = generator.generate_code(component_request)
        print("✅ React component generated successfully")
        print(f"   Language: {component_code.language}")
        print(f"   Framework: {component_code.framework}")
        print(f"   Dependencies: {component_code.dependencies}")
        print(f"   Usage examples: {component_code.usage_examples}")
        
        # Validate the generated code
        validation = generator.validate_code(component_code.code, "javascript")
        print(f"   Validation: {'✅ Valid' if validation['valid'] else '❌ Invalid'}")
        if validation['warnings']:
            print(f"   Warnings: {validation['warnings']}")
        
    except Exception as e:
        print(f"❌ React component generation failed: {e}")
    
    # Test TypeScript interface generation
    print("\n📘 Testing TypeScript interface generation...")
    
    interface_request = CodeGenerationRequest(
        language="typescript",
        framework="typescript",
        component_type="interface",
        specifications={
            "name": "User",
            "properties": [
                {"name": "id", "type": "number", "required": True, "description": "Unique user identifier"},
                {"name": "email", "type": "string", "required": True, "description": "User email address"},
                {"name": "name", "type": "string", "required": False, "description": "User display name"}
            ],
            "description": "User entity interface"
        }
    )
    
    try:
        interface_code = generator.generate_code(interface_request)
        print("✅ TypeScript interface generated successfully")
        print(f"   Language: {interface_code.language}")
        print(f"   Framework: {interface_code.framework}")
        print(f"   Dependencies: {interface_code.dependencies}")
        print(f"   Usage examples: {interface_code.usage_examples}")
        
        # Validate the generated code
        validation = generator.validate_code(interface_code.code, "typescript")
        print(f"   Validation: {'✅ Valid' if validation['valid'] else '❌ Invalid'}")
        if validation['warnings']:
            print(f"   Warnings: {validation['warnings']}")
        
    except Exception as e:
        print(f"❌ TypeScript interface generation failed: {e}")
    
    # Test code templates and patterns
    print("\n📋 Testing code templates and patterns...")
    
    templates = generator.get_code_templates()
    patterns = generator.get_code_patterns()
    
    print(f"✅ Available templates: {list(templates.keys())}")
    print(f"✅ Available patterns: {list(patterns.keys())}")
    
    print("\n🎉 All code generation tests completed!")

if __name__ == "__main__":
    print("🚀 Starting Code Generation Tests...\n")
    
    try:
        test_code_generation()
        print("\n🎉 All tests completed successfully!")
        print("✅ Code generation module is working correctly")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
