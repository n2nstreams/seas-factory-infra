#!/usr/bin/env python3
"""
Code Generation Module - Development Agent Implementation
Implements comprehensive code generation including:
- Python method and function generation
- React component generation
- API endpoint generation
- Test code generation
- AI-powered code suggestions
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class CodeGenerationRequest:
    """Request for code generation"""
    language: str
    framework: str
    component_type: str
    specifications: Dict[str, Any]
    context: Optional[str] = None
    requirements: Optional[List[str]] = None

@dataclass
class GeneratedCode:
    """Generated code result"""
    code: str
    language: str
    framework: str
    component_type: str
    metadata: Dict[str, Any]
    dependencies: List[str]
    usage_examples: List[str]

class CodeGenerator:
    """Advanced code generation engine"""
    
    def __init__(self):
        self.templates = self._load_code_templates()
        self.patterns = self._load_code_patterns()
        self.logger = logging.getLogger(__name__)
        
    def _load_code_templates(self) -> Dict[str, Any]:
        """Load code generation templates"""
        return {
            "python": {
                "method": "Python method template",
                "function": "Python function template",
                "class": "Python class template",
                "api_endpoint": "Python API endpoint template"
            },
            "react": {
                "component": "React component template",
                "hook": "React hook template",
                "context": "React context template"
            },
            "typescript": {
                "interface": "TypeScript interface template",
                "type": "TypeScript type template",
                "utility": "TypeScript utility template"
            }
        }
    
    def _load_code_patterns(self) -> Dict[str, Any]:
        """Load common code patterns"""
        return {
            "error_handling": {
                "python": "try:\n    {code}\nexcept Exception as e:\n    logger.error(f\"Error: {e}\")\n    raise",
                "javascript": "try {\n    {code}\n} catch (error) {\n    console.error('Error:', error);\n    throw error;\n}"
            },
            "logging": {
                "python": "logger.info(f\"{message}\")",
                "javascript": "console.log('{message}')"
            },
            "validation": {
                "python": "if not {variable}:\n    raise ValueError(f\"{variable} is required\")",
                "javascript": "if (!{variable}) {\n    throw new Error('{variable} is required');\n}"
            }
        }
    
    def generate_code(self, request: CodeGenerationRequest) -> GeneratedCode:
        """Generate code based on request"""
        try:
            self.logger.info(f"Generating {request.language} code for {request.component_type}")
            
            if request.language == "python":
                return self._generate_python_code(request)
            elif request.language == "react":
                return self._generate_react_code(request)
            elif request.language == "typescript":
                return self._generate_typescript_code(request)
            else:
                raise ValueError(f"Unsupported language: {request.language}")
                
        except Exception as e:
            self.logger.error(f"Error generating code: {e}")
            raise
    
    def _generate_python_code(self, request: CodeGenerationRequest) -> GeneratedCode:
        """Generate Python code"""
        try:
            if request.component_type == "method":
                code = self._generate_python_method(request.specifications)
            elif request.component_type == "function":
                code = self._generate_python_function(request.specifications)
            elif request.component_type == "class":
                code = self._generate_python_class(request.specifications)
            elif request.component_type == "api_endpoint":
                code = self._generate_python_api_endpoint(request.specifications)
            else:
                raise ValueError(f"Unsupported Python component type: {request.component_type}")
            
            return GeneratedCode(
                code=code,
                language="python",
                framework=request.framework,
                component_type=request.component_type,
                metadata={"generated_at": datetime.now().isoformat()},
                dependencies=self._extract_python_dependencies(code),
                usage_examples=self._generate_python_usage_examples(request.specifications)
            )
            
        except Exception as e:
            self.logger.error(f"Error generating Python code: {e}")
            raise
    
    def _generate_python_method(self, specs: Dict[str, Any]) -> str:
        """Generate Python method implementation"""
        method_name = specs.get("name", "method")
        parameters = specs.get("parameters", [])
        return_type = specs.get("return_type", "Any")
        description = specs.get("description", "")
        implementation = specs.get("implementation", "pass")
        
        # Build method signature
        param_str = ", ".join([f"{p['name']}: {p.get('type', 'Any')}" for p in parameters])
        if param_str:
            param_str = f"self, {param_str}"
        else:
            param_str = "self"
        
        # Generate method code
        code_lines = []
        if description:
            code_lines.append(f'    """{description}"""')
        
        # Add parameter validation
        for param in parameters:
            if param.get("required", True):
                param_name = param["name"]
                code_lines.append(f"        if {param_name} is None:")
                code_lines.append(f"            raise ValueError(\"{param_name} is required\")")
        
        if parameters and any(p.get("required", True) for p in parameters):
            code_lines.append("")
        
        # Add implementation
        if implementation == "pass":
            # Generate smart implementation based on method name
            implementation = self._generate_smart_python_implementation(method_name, parameters)
        
        code_lines.append(f"        {implementation}")
        
        # Add return statement if needed
        if return_type != "None":
            code_lines.append("        return result")
        
        # Build complete method
        method_code = f"    def {method_name}({param_str}) -> {return_type}:"
        method_code += "\n" + "\n".join(code_lines)
        
        return method_code
    
    def _generate_python_function(self, specs: Dict[str, Any]) -> str:
        """Generate Python function implementation"""
        func_name = specs.get("name", "function")
        parameters = specs.get("parameters", [])
        return_type = specs.get("return_type", "Any")
        description = specs.get("description", "")
        implementation = specs.get("implementation", "pass")
        
        # Build function signature
        param_str = ", ".join([f"{p['name']}: {p.get('type', 'Any')}" for p in parameters])
        
        # Generate function code
        code_lines = []
        if description:
            code_lines.append(f'    """{description}"""')
        
        # Add parameter validation
        for param in parameters:
            if param.get("required", True):
                param_name = param["name"]
                code_lines.append(f"    if {param_name} is None:")
                code_lines.append(f"        raise ValueError(\"{param_name} is required\")")
        
        if parameters and any(p.get("required", True) for p in parameters):
            code_lines.append("")
        
        # Add implementation
        if implementation == "pass":
            # Generate smart implementation based on function name
            implementation = self._generate_smart_python_implementation(func_name, parameters)
        
        code_lines.append(f"    {implementation}")
        
        # Add return statement if needed
        if return_type != "None":
            code_lines.append("    return result")
        
        # Build complete function
        func_code = f"def {func_name}({param_str}) -> {return_type}:"
        func_code += "\n" + "\n".join(code_lines)
        
        return func_code
    
    def _generate_smart_python_implementation(self, name: str, parameters: List[Dict[str, Any]]) -> str:
        """Generate smart Python implementation based on method/function name"""
        name_lower = name.lower()
        
        # Common patterns
        if "get" in name_lower or "fetch" in name_lower:
            return "result = self._retrieve_data()"
        elif "set" in name_lower or "update" in name_lower:
            return "result = self._update_data()"
        elif "create" in name_lower or "add" in name_lower:
            return "result = self._create_new_item()"
        elif "delete" in name_lower or "remove" in name_lower:
            return "result = self._remove_item()"
        elif "validate" in name_lower or "check" in name_lower:
            return "result = self._perform_validation()"
        elif "process" in name_lower or "handle" in name_lower:
            return "result = self._process_data()"
        elif "calculate" in name_lower or "compute" in name_lower:
            return "result = self._perform_calculation()"
        else:
            # Generic implementation
            return "result = self._execute_business_logic()"
    
    def _generate_python_class(self, specs: Dict[str, Any]) -> str:
        """Generate Python class implementation"""
        class_name = specs.get("name", "MyClass")
        methods = specs.get("methods", [])
        attributes = specs.get("attributes", [])
        description = specs.get("description", "")
        parent_class = specs.get("parent_class", "")
        
        code_lines = []
        
        # Add class docstring
        if description:
            code_lines.append(f'    """{description}"""')
        
        # Add __init__ method
        if attributes:
            init_params = ", ".join([f"{attr['name']}: {attr.get('type', 'Any')}" for attr in attributes])
            code_lines.append(f"    def __init__(self, {init_params}):")
            for attr in attributes:
                code_lines.append(f"        self.{attr['name']} = {attr['name']}")
        else:
            code_lines.append("    def __init__(self):")
            code_lines.append("        pass")
        
        code_lines.append("")
        
        # Add methods
        for method in methods:
            method_code = self._generate_python_method(method)
            code_lines.append(method_code)
            code_lines.append("")
        
        # Build complete class
        if parent_class:
            class_def = f"class {class_name}({parent_class}):"
        else:
            class_def = f"class {class_name}:"
        
        class_code = class_def + "\n" + "\n".join(code_lines)
        return class_code
    
    def _generate_python_api_endpoint(self, specs: Dict[str, Any]) -> str:
        """Generate Python API endpoint"""
        endpoint_path = specs.get("path", "/endpoint")
        method = specs.get("method", "GET")
        parameters = specs.get("parameters", [])
        response_model = specs.get("response_model", "Dict[str, Any]")
        description = specs.get("description", "")
        
        # Build endpoint code
        code_lines = []
        
        # Add decorator
        code_lines.append(f'@app.{method.lower()}("{endpoint_path}")')
        
        # Add function signature
        param_str = ", ".join([f"{p['name']}: {p.get('type', 'Any')}" for p in parameters])
        code_lines.append(f"async def {endpoint_path.replace('/', '_').replace('-', '_').strip('_')}({param_str}) -> {response_model}:")
        
        # Add docstring
        if description:
            code_lines.append(f'    """{description}"""')
        
        # Add implementation
        code_lines.append("    try:")
        code_lines.append("        # TODO: Implement endpoint logic")
        code_lines.append("        result = {}")
        code_lines.append("        return result")
        code_lines.append("    except Exception as e:")
        code_lines.append("        logger.error(f\"Error in endpoint: {e}\")")
        code_lines.append("        raise HTTPException(status_code=500, detail=str(e))")
        
        return "\n".join(code_lines)
    
    def _generate_react_code(self, request: CodeGenerationRequest) -> GeneratedCode:
        """Generate React code"""
        try:
            if request.component_type == "component":
                code = self._generate_react_component(request.specifications)
            elif request.component_type == "hook":
                code = self._generate_react_hook(request.specifications)
            elif request.component_type == "context":
                code = self._generate_react_context(request.specifications)
            else:
                raise ValueError(f"Unsupported React component type: {request.component_type}")
            
            return GeneratedCode(
                code=code,
                language="react",
                framework="react",
                component_type=request.component_type,
                metadata={"generated_at": datetime.now().isoformat()},
                dependencies=self._extract_react_dependencies(code),
                usage_examples=self._generate_react_usage_examples(request.specifications)
            )
            
        except Exception as e:
            self.logger.error(f"Error generating React code: {e}")
            raise
    
    def _generate_react_component(self, specs: Dict[str, Any]) -> str:
        """Generate React component"""
        component_name = specs.get("name", "MyComponent")
        props = specs.get("props", [])
        state_vars = specs.get("state_variables", [])
        methods = specs.get("methods", [])
        imports = specs.get("imports", ["React", "useState", "useEffect"])
        
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
            initial_value = state_var.get("initial_value", "undefined")
            if initial_value == "undefined":
                initial_value = "undefined"
            elif isinstance(initial_value, str) and initial_value.startswith("'"):
                initial_value = initial_value
            else:
                initial_value = f"'{initial_value}'"
            
            code_lines.append(f"  const [{state_var['name']}, set{state_var['name'].capitalize()}] = useState<{state_var['type']}>({initial_value});")
        
        if state_vars:
            code_lines.append("")
        
        # Add methods
        for method in methods:
            method_params = method.get("parameters", [])
            param_str = ", ".join(method_params)
            code_lines.append(f"  const {method['name']} = ({param_str}) => {{")
            
            # Generate method implementation
            implementation = self._generate_react_method_implementation(method)
            code_lines.append(f"    {implementation}")
            code_lines.append("  };")
            code_lines.append("")
        
        # Add return JSX
        code_lines.append("  return (")
        code_lines.append(f"    <div className=\"{component_name.lower()}-container\">")
        code_lines.append(f"      <h2>{component_name}</h2>")
        
        # Add dynamic content based on props and state
        if props:
            code_lines.append("      <div className=\"props-display\">")
            for prop in props:
                code_lines.append(f"        <p><strong>{prop['name']}:</strong> {{String({prop['name']})}}</p>")
            code_lines.append("      </div>")
        
        if state_vars:
            code_lines.append("      <div className=\"state-display\">")
            for state_var in state_vars:
                code_lines.append(f"        <p><strong>{state_var['name']}:</strong> {{String({state_var['name']})}}</p>")
            code_lines.append("      </div>")
        
        code_lines.append("    </div>")
        code_lines.append("  );")
        code_lines.append("};")
        code_lines.append("")
        code_lines.append(f"export default {component_name};")
        
        return "\n".join(code_lines)
    
    def _generate_react_method_implementation(self, method: Dict[str, Any]) -> str:
        """Generate React method implementation"""
        method_name = method.get("name", "method")
        method_name_lower = method_name.lower()
        
        # Common patterns
        if "handle" in method_name_lower or "on" in method_name_lower:
            return f"// Handle {method_name} event"
        elif "update" in method_name_lower or "set" in method_name_lower:
            return f"// Update state or data for {method_name}"
        elif "fetch" in method_name_lower or "get" in method_name_lower:
            return f"// Fetch data for {method_name}"
        elif "validate" in method_name_lower or "check" in method_name_lower:
            return f"// Validate data for {method_name}"
        else:
            return f"// Implement {method_name} functionality"
    
    def _generate_react_hook(self, specs: Dict[str, Any]) -> str:
        """Generate React custom hook"""
        hook_name = specs.get("name", "useMyHook")
        parameters = specs.get("parameters", [])
        return_values = specs.get("return_values", [])
        description = specs.get("description", "")
        
        code_lines = []
        
        # Add hook function
        param_str = ", ".join([f"{p['name']}: {p.get('type', 'any')}" for p in parameters])
        code_lines.append(f"export const {hook_name} = ({param_str}) => {{")
        
        # Add description
        if description:
            code_lines.append(f"  // {description}")
        
        # Add state variables
        for return_val in return_values:
            if return_val.get("type") == "state":
                code_lines.append(f"  const [{return_val['name']}, set{return_val['name'].capitalize()}] = useState<{return_val.get('type', 'any')}>({return_val.get('initial_value', 'undefined')});")
        
        code_lines.append("")
        
        # Add effect
        code_lines.append("  useEffect(() => {")
        code_lines.append("    // Hook initialization logic")
        code_lines.append("  }, []);")
        code_lines.append("")
        
        # Add return statement
        return_str = ", ".join([val["name"] for val in return_values])
        code_lines.append(f"  return {{ {return_str} }};")
        code_lines.append("};")
        
        return "\n".join(code_lines)
    
    def _generate_react_context(self, specs: Dict[str, Any]) -> str:
        """Generate React context"""
        context_name = specs.get("name", "MyContext")
        provider_name = f"{context_name}Provider"
        value_type = specs.get("value_type", "any")
        description = specs.get("description", "")
        
        code_lines = []
        
        # Add context creation
        code_lines.append("import React, { createContext, useContext, ReactNode } from 'react';")
        code_lines.append("")
        
        # Add type definition
        code_lines.append(f"interface {context_name}Value {{")
        code_lines.append("  // Define context value properties")
        code_lines.append("}")
        code_lines.append("")
        
        # Add context
        code_lines.append(f"const {context_name} = createContext<{context_name}Value | undefined>(undefined);")
        code_lines.append("")
        
        # Add provider
        code_lines.append(f"interface {provider_name}Props {{")
        code_lines.append("  children: ReactNode;")
        code_lines.append("}")
        code_lines.append("")
        
        code_lines.append(f"export const {provider_name}: React.FC<{provider_name}Props> = ({{ children }}) => {{")
        code_lines.append("  // Initialize context value")
        code_lines.append("  const value: MyContextValue = {")
        code_lines.append("    // Set context values")
        code_lines.append("  };")
        code_lines.append("")
        code_lines.append(f"  return <{context_name}.Provider value={{value}}>{{children}}</{context_name}.Provider>;")
        code_lines.append("};")
        code_lines.append("")
        
        # Add hook
        code_lines.append(f"export const use{context_name} = (): {context_name}Value => {{")
        code_lines.append(f"  const context = useContext({context_name});")
        code_lines.append("  if (context === undefined) {")
        code_lines.append(f"    throw new Error(`use{context_name} must be used within a {provider_name}`);")
        code_lines.append("  }")
        code_lines.append("  return context;")
        code_lines.append("};")
        
        return "\n".join(code_lines)
    
    def _generate_typescript_code(self, request: CodeGenerationRequest) -> GeneratedCode:
        """Generate TypeScript code"""
        try:
            if request.component_type == "interface":
                code = self._generate_typescript_interface(request.specifications)
            elif request.component_type == "type":
                code = self._generate_typescript_type(request.specifications)
            elif request.component_type == "utility":
                code = self._generate_typescript_utility(request.specifications)
            else:
                raise ValueError(f"Unsupported TypeScript component type: {request.component_type}")
            
            return GeneratedCode(
                code=code,
                language="typescript",
                framework="typescript",
                component_type=request.component_type,
                metadata={"generated_at": datetime.now().isoformat()},
                dependencies=self._extract_typescript_dependencies(code),
                usage_examples=self._generate_typescript_usage_examples(request.specifications)
            )
            
        except Exception as e:
            self.logger.error(f"Error generating TypeScript code: {e}")
            raise
    
    def _generate_typescript_interface(self, specs: Dict[str, Any]) -> str:
        """Generate TypeScript interface"""
        interface_name = specs.get("name", "MyInterface")
        properties = specs.get("properties", [])
        extends_from = specs.get("extends", [])
        description = specs.get("description", "")
        
        code_lines = []
        
        # Add description
        if description:
            code_lines.append(f"/** {description} */")
        
        # Add interface definition
        if extends_from:
            extends_str = f" extends {', '.join(extends_from)}"
            code_lines.append(f"export interface {interface_name}{extends_str} {{")
        else:
            code_lines.append(f"export interface {interface_name} {{")
        
        # Add properties
        for prop in properties:
            prop_line = f"  {prop['name']}: {prop['type']}"
            if not prop.get("required", True):
                prop_line += "?"
            if prop.get("description"):
                prop_line += f"; // {prop['description']}"
            else:
                prop_line += ";"
            code_lines.append(prop_line)
        
        code_lines.append("}")
        
        return "\n".join(code_lines)
    
    def _generate_typescript_type(self, specs: Dict[str, Any]) -> str:
        """Generate TypeScript type"""
        type_name = specs.get("name", "MyType")
        type_definition = specs.get("definition", "string")
        description = specs.get("description", "")
        
        code_lines = []
        
        # Add description
        if description:
            code_lines.append(f"/** {description} */")
        
        # Add type definition
        code_lines.append(f"export type {type_name} = {type_definition};")
        
        return "\n".join(code_lines)
    
    def _generate_typescript_utility(self, specs: Dict[str, Any]) -> str:
        """Generate TypeScript utility function"""
        function_name = specs.get("name", "utilityFunction")
        parameters = specs.get("parameters", [])
        return_type = specs.get("return_type", "any")
        description = specs.get("description", "")
        implementation = specs.get("implementation", "")
        
        code_lines = []
        
        # Add description
        if description:
            code_lines.append(f"/** {description} */")
        
        # Add function signature
        param_str = ", ".join([f"{p['name']}: {p.get('type', 'any')}" for p in parameters])
        code_lines.append(f"export function {function_name}({param_str}): {return_type} {{")
        
        # Add implementation
        if implementation:
            code_lines.append(f"  {implementation}")
        else:
            code_lines.append("  // TODO: Implement utility function")
        
        code_lines.append("}")
        
        return "\n".join(code_lines)
    
    def _extract_python_dependencies(self, code: str) -> List[str]:
        """Extract Python dependencies from generated code"""
        dependencies = []
        
        # Common Python imports
        if "import logging" in code:
            dependencies.append("logging")
        if "import json" in code:
            dependencies.append("json")
        if "import asyncio" in code:
            dependencies.append("asyncio")
        if "from fastapi import" in code:
            dependencies.append("fastapi")
        if "from pydantic import" in code:
            dependencies.append("pydantic")
        
        return dependencies
    
    def _extract_react_dependencies(self, code: str) -> List[str]:
        """Extract React dependencies from generated code"""
        dependencies = ["react"]
        
        # Check for React hooks
        if "useState" in code:
            dependencies.append("react")
        if "useEffect" in code:
            dependencies.append("react")
        if "useContext" in code:
            dependencies.append("react")
        
        return dependencies
    
    def _extract_typescript_dependencies(self, code: str) -> List[str]:
        """Extract TypeScript dependencies from generated code"""
        dependencies = ["typescript"]
        
        # Check for common TypeScript patterns
        if "interface" in code:
            dependencies.append("typescript")
        if "type" in code:
            dependencies.append("typescript")
        
        return dependencies
    
    def _generate_python_usage_examples(self, specs: Dict[str, Any]) -> List[str]:
        """Generate Python usage examples"""
        examples = []
        
        if specs.get("component_type") == "method":
            method_name = specs.get("name", "method")
            examples.append(f"# Usage: instance.{method_name}()")
        elif specs.get("component_type") == "function":
            func_name = specs.get("name", "function")
            examples.append(f"# Usage: {func_name}()")
        
        return examples
    
    def _generate_react_usage_examples(self, specs: Dict[str, Any]) -> List[str]:
        """Generate React usage examples"""
        examples = []
        
        if specs.get("component_type") == "component":
            component_name = specs.get("name", "MyComponent")
            examples.append(f"// Usage: <{component_name} />")
        elif specs.get("component_type") == "hook":
            hook_name = specs.get("name", "useMyHook")
            examples.append(f"// Usage: const value = {hook_name}()")
        
        return examples
    
    def _generate_typescript_usage_examples(self, specs: Dict[str, Any]) -> List[str]:
        """Generate TypeScript usage examples"""
        examples = []
        
        if specs.get("component_type") == "interface":
            interface_name = specs.get("name", "MyInterface")
            examples.append(f"// Usage: const obj: {interface_name} = {{}}")
        elif specs.get("component_type") == "type":
            type_name = specs.get("name", "MyType")
            examples.append(f"// Usage: const value: {type_name} = 'example'")
        
        return examples
    
    def get_code_templates(self) -> Dict[str, Any]:
        """Get available code templates"""
        return self.templates
    
    def get_code_patterns(self) -> Dict[str, Any]:
        """Get available code patterns"""
        return self.patterns
    
    def validate_code(self, code: str, language: str) -> Dict[str, Any]:
        """Validate generated code"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        try:
            # Basic syntax validation
            if language == "python":
                compile(code, '<string>', 'exec')
            elif language == "javascript" or language == "typescript":
                # Basic JS/TS validation (simplified)
                if "function" in code and "{" in code and "}" in code:
                    pass  # Basic structure check
                else:
                    validation_result["warnings"].append("Code structure may be incomplete")
            
            # Check for common issues
            if "TODO" in code:
                validation_result["warnings"].append("Code contains TODO items")
            if "pass" in code and language == "python":
                validation_result["suggestions"].append("Consider implementing the pass statement")
            
        except SyntaxError as e:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Syntax error: {e}")
        except Exception as e:
            validation_result["warnings"].append(f"Validation warning: {e}")
        
        return validation_result

# Initialize code generator
code_generator = CodeGenerator()
