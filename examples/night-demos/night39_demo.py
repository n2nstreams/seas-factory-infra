#!/usr/bin/env python3
"""
Night 39 Demo: UIDevAgent - Figma to React Scaffolding
Demonstrates scaffolding React pages from Figma JSON via CLI html-to-react
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any

# Mock implementations for demo purposes
class MockTenantDatabase:
    def __init__(self):
        self.events = []
    
    async def log_agent_event(self, **kwargs):
        self.events.append({
            "timestamp": datetime.now().isoformat(),
            **kwargs
        })
        print(f"🔍 Event logged: {kwargs.get('event_type', 'unknown')} - {kwargs.get('status', 'unknown')}")

class MockGitHubIntegration:
    def __init__(self):
        self.files = []
    
    async def create_pull_request(self, files, **kwargs):
        self.files.extend(files)
        print(f"📁 PR would be created with {len(files)} files")
        return {"number": 42, "html_url": "https://github.com/demo/pr/42"}

class MockUIDevAgent:
    """Mock UIDevAgent for demo purposes"""
    
    def __init__(self):
        self.tenant_db = MockTenantDatabase()
        self.github_integration = MockGitHubIntegration()
        
        # Olive green color palette for theming
        self.olive_green_palette = {
            "primary": "#6B7280",      # Olive gray
            "secondary": "#84CC16",    # Lime green
            "accent": "#22C55E",       # Green
            "background": "#F9FAFB",   # Light gray
            "surface": "#FFFFFF",      # White
            "text": "#374151",         # Dark gray
            "textSecondary": "#6B7280" # Medium gray
        }
    
    def parse_figma_json(self, figma_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Figma JSON data"""
        print(f"📋 Parsing Figma document: {figma_data.get('name', 'Untitled')}")
        return figma_data
    
    def extract_frames_from_figma(self, figma_doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract page frames from Figma document"""
        frames = []
        
        def extract_recursive(node):
            if node.get("type") == "FRAME" and node.get("name") and not node.get("name", "").startswith("_"):
                frames.append(node)
            
            for child in node.get("children", []):
                extract_recursive(child)
        
        extract_recursive(figma_doc.get("document", {}))
        print(f"🔍 Found {len(frames)} frames: {[f.get('name') for f in frames]}")
        return frames
    
    def figma_node_to_html(self, node: Dict[str, Any], depth: int = 0) -> str:
        """Convert Figma node to HTML structure"""
        indent = "  " * depth
        node_type = node.get("type", "")
        node_name = node.get("name", "")
        
        if node_type == "TEXT":
            content = node.get("characters", node_name)
            font_size = node.get("style", {}).get("fontSize", 16)
            tag = "h2" if font_size > 18 else "p"
            return f"{indent}<{tag} className=\"figma-text\">{content}</{tag}>\n"
        
        elif node_type == "RECTANGLE":
            if any(fill.get("type") == "IMAGE" for fill in node.get("fills", [])):
                return f"{indent}<img className=\"figma-image\" alt=\"{node_name}\" />\n"
            else:
                return f"{indent}<div className=\"figma-rectangle\">{node_name}</div>\n"
        
        elif node_type in ["FRAME", "GROUP"]:
            tag = "section" if node_type == "FRAME" else "div"
            class_name = f"figma-{node_type.lower()}"
            
            # Handle layout mode
            layout_mode = node.get("layoutMode", "")
            layout_class = ""
            if layout_mode == "HORIZONTAL":
                layout_class = " flex-row"
            elif layout_mode == "VERTICAL":
                layout_class = " flex-col"
            
            html = f"{indent}<{tag} className=\"{class_name}{layout_class}\">\n"
            
            # Process children
            for child in node.get("children", []):
                html += self.figma_node_to_html(child, depth + 1)
            
            html += f"{indent}</{tag}>\n"
            return html
        
        elif node_type in ["VECTOR", "BOOLEAN_OPERATION"]:
            return f"{indent}<svg className=\"figma-vector\" aria-label=\"{node_name}\"></svg>\n"
        
        else:
            if node.get("children"):
                html = f"{indent}<div className=\"figma-{node_type.lower()}\">\n"
                for child in node.get("children", []):
                    html += self.figma_node_to_html(child, depth + 1)
                html += f"{indent}</div>\n"
                return html
            else:
                return f"{indent}<div className=\"figma-element\">{node_name}</div>\n"
    
    def convert_html_to_react(self, html_content: str, component_name: str) -> str:
        """Convert HTML to React component"""
        # Mock conversion with glassmorphism and olive green theme
        react_component = f"""import React from 'react';

interface {component_name}Props {{
  className?: string;
  children?: React.ReactNode;
}}

const {component_name}: React.FC<{component_name}Props> = ({{ className = '', children }}) => {{
  return (
    <div className={{`{component_name.lower()}-container backdrop-blur-lg bg-white/10 border border-white/20 shadow-xl rounded-xl ${{className}}`}}>
      {html_content.replace('class=', 'className=').replace('bg-white', 'bg-green-50').replace('text-gray-900', 'text-gray-700')}
      {{children}}
    </div>
  );
}};

export default {component_name};"""
        
        return react_component
    
    def extract_reusable_components(self, frame: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract reusable components from Figma frame"""
        components = []
        
        def extract_components_recursive(node, depth=0):
            if (node.get("type") in ["FRAME", "GROUP"] and 
                len(node.get("children", [])) > 1 and 
                depth > 0 and 
                not node.get("name", "").lower().startswith("page")):
                
                component_name = self.sanitize_component_name(node.get("name", ""))
                html_content = self.figma_node_to_html(node)
                react_content = self.convert_html_to_react(html_content, component_name)
                
                components.append({
                    "name": component_name,
                    "filename": f"{component_name}.tsx",
                    "content": react_content,
                    "type": "functional"
                })
            
            for child in node.get("children", []):
                extract_components_recursive(child, depth + 1)
        
        for child in frame.get("children", []):
            extract_components_recursive(child)
        
        return components
    
    def sanitize_component_name(self, name: str) -> str:
        """Sanitize component name"""
        import re
        sanitized = re.sub(r'[^a-zA-Z0-9\s]', '', name)
        sanitized = ''.join(word.capitalize() for word in sanitized.split())
        return sanitized if sanitized and sanitized[0].isupper() else f"Page{sanitized}"
    
    def generate_styles(self, request: Dict[str, Any]) -> Dict[str, str]:
        """Generate style files"""
        styles = {}
        
        if request.get("style_framework") == "tailwind":
            styles["tailwind.config.js"] = f"""module.exports = {{
  content: ["./src/**/*.{{js,ts,jsx,tsx}}"],
  theme: {{
    extend: {{
      colors: {json.dumps(self.olive_green_palette, indent=8)},
      backdropBlur: {{
        "xs": "2px"
      }}
    }}
  }},
  plugins: []
}};"""
            
            styles["globals.css"] = """@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    font-family: 'Inter', sans-serif;
  }
}

@layer components {
  .glass {
    @apply backdrop-blur-lg bg-white/10 border border-white/20 shadow-xl rounded-xl;
  }
  
  .olive-theme {
    @apply text-gray-700 bg-green-50;
  }
}

@layer utilities {
  .figma-text {
    @apply text-gray-700;
  }
  
  .figma-frame {
    @apply flex flex-col;
  }
  
  .figma-rectangle {
    @apply bg-gray-100 rounded;
  }
}"""
        
        return styles
    
    def generate_routing_config(self, pages: List[Dict[str, Any]]) -> str:
        """Generate React Router configuration"""
        imports = []
        routes = []
        
        for page in pages:
            component_name = page["name"]
            imports.append(f"import {component_name} from './pages/{component_name}';")
            routes.append(f"  {{ path: '{page['route']}', element: <{component_name} /> }}")
        
        return f"""import React from 'react';
import {{ createBrowserRouter, RouterProvider }} from 'react-router-dom';
{chr(10).join(imports)}

const router = createBrowserRouter([
{chr(10).join(routes)}
]);

const AppRouter: React.FC = () => {{
  return <RouterProvider router={{router}} />;
}};

export default AppRouter;"""
    
    async def scaffold_ui_from_figma(self, request: Dict[str, Any], tenant_context: Dict[str, Any]) -> Dict[str, Any]:
        """Main method to scaffold React UI from Figma design"""
        project_id = request["project_id"]
        figma_data = request["figma_data"]
        
        print(f"🚀 Starting UI scaffolding for project: {project_id}")
        
        # Log start event
        await self.tenant_db.log_agent_event(
            event_type="ui_scaffolding",
            agent_name="UIDevAgent",
            stage="ui_scaffolding",
            status="started",
            project_id=project_id
        )
        
        # Parse Figma data
        figma_doc = self.parse_figma_json(figma_data)
        
        # Extract frames (pages)
        frames = self.extract_frames_from_figma(figma_doc)
        
        if not frames:
            raise ValueError("No frames found in Figma document")
        
        # Filter frames if specific pages requested
        if request.get("target_pages"):
            frames = [f for f in frames if f.get("name") in request["target_pages"]]
        
        # Scaffold pages
        pages = []
        all_components = []
        
        for frame in frames:
            print(f"📄 Scaffolding page: {frame.get('name')}")
            
            # Generate HTML structure
            html_content = "<div className=\"page-container\">\n"
            for child in frame.get("children", []):
                html_content += self.figma_node_to_html(child, 1)
            html_content += "</div>"
            
            # Convert to React component
            page_name = self.sanitize_component_name(frame.get("name", ""))
            react_content = self.convert_html_to_react(html_content, page_name)
            
            # Generate route
            route = f"/{page_name.lower().replace('page', '').replace('screen', '')}"
            if route == "/":
                route = "/home"
            
            # Extract reusable components
            components = self.extract_reusable_components(frame)
            all_components.extend(components)
            
            page = {
                "name": page_name,
                "filename": f"{page_name}.tsx",
                "route": route,
                "content": react_content,
                "components": components,
                "meta": {
                    "title": f"{page_name} - AI SaaS Factory",
                    "description": f"Auto-generated {page_name} page from Figma design",
                    "figma_frame_id": frame.get("id"),
                    "width": frame.get("width", 375),
                    "height": frame.get("height", 812)
                }
            }
            
            pages.append(page)
            print(f"✅ Page {page_name} scaffolded with {len(components)} components")
        
        # Generate styles
        styles = self.generate_styles(request)
        
        # Generate routing configuration
        routing_config = self.generate_routing_config(pages)
        
        # Determine dependencies
        dependencies = ["react", "react-dom"]
        if request.get("typescript", True):
            dependencies.extend(["typescript", "@types/react", "@types/react-dom"])
        
        if request.get("style_framework") == "tailwind":
            dependencies.extend(["tailwindcss", "autoprefixer", "postcss"])
        
        if request.get("component_library"):
            lib = request["component_library"]
            if lib == "mui":
                dependencies.extend(["@mui/material", "@emotion/react", "@emotion/styled"])
            elif lib == "antd":
                dependencies.append("antd")
            elif lib == "chakra":
                dependencies.extend(["@chakra-ui/react", "@emotion/react", "@emotion/styled"])
        
        dependencies.append("react-router-dom")
        
        # Generate setup instructions
        setup_instructions = [
            "1. Install dependencies:",
            f"   npm install {' '.join(dependencies)}",
            "2. Set up the project structure:",
            "   - Place components in src/components/",
            "   - Place pages in src/pages/",
            "   - Update src/App.tsx with the routing configuration",
            "3. Configure Tailwind CSS:",
            "   - Replace tailwind.config.js with the generated configuration",
            "   - Update src/index.css with the generated global styles",
            "4. Start the development server:",
            "   npm start",
            "5. Open http://localhost:3000 to view the application"
        ]
        
        # Calculate metrics
        total_lines = sum(len(page["content"].splitlines()) for page in pages)
        total_lines += sum(len(comp["content"].splitlines()) for comp in all_components)
        
        result = {
            "project_id": project_id,
            "pages": pages,
            "components": all_components,
            "styles": styles,
            "total_files": len(pages) + len(all_components) + len(styles),
            "total_lines": total_lines,
            "setup_instructions": setup_instructions,
            "dependencies": dependencies,
            "routing_config": routing_config
        }
        
        print(f"📊 Scaffolding complete: {result['total_files']} files, {result['total_lines']} lines of code")
        
        # Log completion
        await self.tenant_db.log_agent_event(
            event_type="ui_scaffolding",
            agent_name="UIDevAgent",
            stage="ui_scaffolding",
            status="completed",
            project_id=project_id,
            output_data={
                "pages_count": len(pages),
                "components_count": len(all_components),
                "total_files": result["total_files"],
                "total_lines": result["total_lines"]
            }
        )
        
        return result

async def demo_figma_to_react_scaffolding():
    """Demo the complete Figma to React scaffolding workflow"""
    print("=" * 80)
    print("🎨 NIGHT 39 DEMO: UIDevAgent - Figma to React Scaffolding")
    print("=" * 80)
    
    # Create mock UIDevAgent
    ui_agent = MockUIDevAgent()
    
    # Sample Figma design document
    figma_design = {
        "document": {
            "id": "root",
            "name": "Root",
            "type": "DOCUMENT",
            "children": [
                {
                    "id": "page-1",
                    "name": "Landing Page",
                    "type": "FRAME",
                    "width": 1440,
                    "height": 1024,
                    "layoutMode": "VERTICAL",
                    "children": [
                        {
                            "id": "header",
                            "name": "Header",
                            "type": "FRAME",
                            "width": 1440,
                            "height": 80,
                            "layoutMode": "HORIZONTAL",
                            "children": [
                                {
                                    "id": "logo",
                                    "name": "Logo",
                                    "type": "TEXT",
                                    "characters": "AI SaaS Factory",
                                    "style": {"fontSize": 24, "fontWeight": "bold"}
                                },
                                {
                                    "id": "nav",
                                    "name": "Navigation",
                                    "type": "FRAME",
                                    "layoutMode": "HORIZONTAL",
                                    "children": [
                                        {
                                            "id": "nav-home",
                                            "name": "Home Link",
                                            "type": "TEXT",
                                            "characters": "Home"
                                        },
                                        {
                                            "id": "nav-about",
                                            "name": "About Link",
                                            "type": "TEXT",
                                            "characters": "About"
                                        },
                                        {
                                            "id": "nav-contact",
                                            "name": "Contact Link",
                                            "type": "TEXT",
                                            "characters": "Contact"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "id": "hero",
                            "name": "Hero Section",
                            "type": "FRAME",
                            "width": 1440,
                            "height": 500,
                            "layoutMode": "VERTICAL",
                            "children": [
                                {
                                    "id": "hero-title",
                                    "name": "Hero Title",
                                    "type": "TEXT",
                                    "characters": "Build Your SaaS with AI",
                                    "style": {"fontSize": 48, "fontWeight": "bold"}
                                },
                                {
                                    "id": "hero-subtitle",
                                    "name": "Hero Subtitle",
                                    "type": "TEXT",
                                    "characters": "Transform your ideas into production-ready SaaS applications with our AI-powered development platform.",
                                    "style": {"fontSize": 18}
                                },
                                {
                                    "id": "cta-button",
                                    "name": "CTA Button",
                                    "type": "FRAME",
                                    "width": 200,
                                    "height": 60,
                                    "cornerRadius": 8,
                                    "fills": [{"type": "SOLID", "color": "#22C55E"}],
                                    "children": [
                                        {
                                            "id": "cta-text",
                                            "name": "CTA Text",
                                            "type": "TEXT",
                                            "characters": "Get Started"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "id": "features",
                            "name": "Features Section",
                            "type": "FRAME",
                            "width": 1440,
                            "height": 400,
                            "layoutMode": "HORIZONTAL",
                            "children": [
                                {
                                    "id": "feature-1",
                                    "name": "Feature Card",
                                    "type": "FRAME",
                                    "width": 300,
                                    "height": 200,
                                    "cornerRadius": 12,
                                    "children": [
                                        {
                                            "id": "feature-icon-1",
                                            "name": "Feature Icon",
                                            "type": "VECTOR"
                                        },
                                        {
                                            "id": "feature-title-1",
                                            "name": "Feature Title",
                                            "type": "TEXT",
                                            "characters": "AI-Powered Development"
                                        },
                                        {
                                            "id": "feature-desc-1",
                                            "name": "Feature Description",
                                            "type": "TEXT",
                                            "characters": "Generate code, APIs, and UI components automatically"
                                        }
                                    ]
                                },
                                {
                                    "id": "feature-2",
                                    "name": "Feature Card",
                                    "type": "FRAME",
                                    "width": 300,
                                    "height": 200,
                                    "cornerRadius": 12,
                                    "children": [
                                        {
                                            "id": "feature-icon-2",
                                            "name": "Feature Icon",
                                            "type": "VECTOR"
                                        },
                                        {
                                            "id": "feature-title-2",
                                            "name": "Feature Title",
                                            "type": "TEXT",
                                            "characters": "Scalable Architecture"
                                        },
                                        {
                                            "id": "feature-desc-2",
                                            "name": "Feature Description",
                                            "type": "TEXT",
                                            "characters": "Built-in multi-tenancy and horizontal scaling"
                                        }
                                    ]
                                },
                                {
                                    "id": "feature-3",
                                    "name": "Feature Card",
                                    "type": "FRAME",
                                    "width": 300,
                                    "height": 200,
                                    "cornerRadius": 12,
                                    "children": [
                                        {
                                            "id": "feature-icon-3",
                                            "name": "Feature Icon",
                                            "type": "VECTOR"
                                        },
                                        {
                                            "id": "feature-title-3",
                                            "name": "Feature Title",
                                            "type": "TEXT",
                                            "characters": "Production Ready"
                                        },
                                        {
                                            "id": "feature-desc-3",
                                            "name": "Feature Description",
                                            "type": "TEXT",
                                            "characters": "Deploy with CI/CD, monitoring, and security"
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                },
                {
                    "id": "page-2",
                    "name": "About Page",
                    "type": "FRAME",
                    "width": 1440,
                    "height": 800,
                    "layoutMode": "VERTICAL",
                    "children": [
                        {
                            "id": "about-header",
                            "name": "About Header",
                            "type": "TEXT",
                            "characters": "About AI SaaS Factory",
                            "style": {"fontSize": 36, "fontWeight": "bold"}
                        },
                        {
                            "id": "about-content",
                            "name": "About Content",
                            "type": "TEXT",
                            "characters": "We are revolutionizing SaaS development through AI-powered tools and automation."
                        }
                    ]
                },
                {
                    "id": "page-3",
                    "name": "Dashboard",
                    "type": "FRAME",
                    "width": 1440,
                    "height": 900,
                    "layoutMode": "VERTICAL",
                    "children": [
                        {
                            "id": "dashboard-nav",
                            "name": "Dashboard Navigation",
                            "type": "FRAME",
                            "layoutMode": "HORIZONTAL",
                            "children": [
                                {
                                    "id": "dashboard-title",
                                    "name": "Dashboard Title",
                                    "type": "TEXT",
                                    "characters": "Dashboard"
                                }
                            ]
                        },
                        {
                            "id": "dashboard-content",
                            "name": "Dashboard Content",
                            "type": "FRAME",
                            "layoutMode": "VERTICAL",
                            "children": [
                                {
                                    "id": "metrics-card",
                                    "name": "Metrics Card",
                                    "type": "FRAME",
                                    "cornerRadius": 8,
                                    "children": [
                                        {
                                            "id": "metrics-title",
                                            "name": "Metrics Title",
                                            "type": "TEXT",
                                            "characters": "Project Metrics"
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        "name": "AI SaaS Factory Design System",
        "version": "1.0.0"
    }
    
    # Create scaffolding request
    scaffold_request = {
        "project_id": "ai-saas-factory",
        "figma_data": figma_design,
        "target_pages": [],  # All pages
        "style_framework": "tailwind",
        "component_library": "mui",
        "typescript": True,
        "responsive": True,
        "glassmorphism": True,
        "olive_green_theme": True
    }
    
    # Mock tenant context
    tenant_context = {
        "tenant_id": "demo-tenant",
        "user_id": "demo-user"
    }
    
    try:
        print("🔄 Starting Figma to React scaffolding...")
        result = await ui_agent.scaffold_ui_from_figma(scaffold_request, tenant_context)
        
        print("\n📊 SCAFFOLDING RESULTS:")
        print(f"  - Project ID: {result['project_id']}")
        print(f"  - Pages generated: {len(result['pages'])}")
        print(f"  - Components extracted: {len(result['components'])}")
        print(f"  - Total files: {result['total_files']}")
        print(f"  - Total lines of code: {result['total_lines']}")
        
        print("\n📄 GENERATED PAGES:")
        for page in result['pages']:
            print(f"  - {page['name']} ({page['filename']}) -> Route: {page['route']}")
            print(f"    Components: {len(page['components'])}")
            print(f"    Figma Frame: {page['meta']['figma_frame_id']}")
        
        print("\n🧩 EXTRACTED COMPONENTS:")
        for comp in result['components']:
            print(f"  - {comp['name']} ({comp['filename']})")
        
        print("\n🎨 GENERATED STYLES:")
        for style_file, content in result['styles'].items():
            print(f"  - {style_file} ({len(content.splitlines())} lines)")
        
        print("\n📦 DEPENDENCIES:")
        for dep in result['dependencies']:
            print(f"  - {dep}")
        
        print("\n📋 SETUP INSTRUCTIONS:")
        for i, instruction in enumerate(result['setup_instructions'], 1):
            print(f"  {i}. {instruction}")
        
        print("\n🚀 PREVIEW OF GENERATED CODE:")
        print("-" * 50)
        
        # Show first page content (truncated)
        first_page = result['pages'][0]
        page_lines = first_page['content'].splitlines()
        preview_lines = page_lines[:20]
        print(f"📄 {first_page['filename']}:")
        for line in preview_lines:
            print(f"  {line}")
        if len(page_lines) > 20:
            print(f"  ... ({len(page_lines) - 20} more lines)")
        
        print("\n" + "-" * 50)
        
        # Show Tailwind config
        if 'tailwind.config.js' in result['styles']:
            config_lines = result['styles']['tailwind.config.js'].splitlines()
            print("🎨 tailwind.config.js:")
            for line in config_lines[:15]:
                print(f"  {line}")
            if len(config_lines) > 15:
                print(f"  ... ({len(config_lines) - 15} more lines)")
        
        print("\n✅ UI scaffolding completed successfully!")
        
        # Demo: Show how components could be used
        print("\n🔧 COMPONENT USAGE EXAMPLE:")
        print("```tsx")
        print("// App.tsx")
        print("import React from 'react';")
        print("import { BrowserRouter } from 'react-router-dom';")
        print("import AppRouter from './AppRouter';")
        print("import './globals.css';")
        print("")
        print("function App() {")
        print("  return (")
        print("    <BrowserRouter>")
        print("      <div className=\"app olive-theme\">")
        print("        <AppRouter />")
        print("      </div>")
        print("    </BrowserRouter>")
        print("  );")
        print("}")
        print("")
        print("export default App;")
        print("```")
        
    except Exception as e:
        print(f"❌ Error during scaffolding: {str(e)}")
        return False
    
    return True

async def demo_specific_page_scaffolding():
    """Demo scaffolding specific pages only"""
    print("\n" + "=" * 60)
    print("🎯 DEMO: Scaffolding Specific Pages")
    print("=" * 60)
    
    ui_agent = MockUIDevAgent()
    
    # Simple Figma design with multiple pages
    figma_design = {
        "document": {
            "id": "root",
            "name": "Root",
            "type": "DOCUMENT",
            "children": [
                {
                    "id": "login-page",
                    "name": "Login Page",
                    "type": "FRAME",
                    "width": 400,
                    "height": 600,
                    "children": [
                        {
                            "id": "login-form",
                            "name": "Login Form",
                            "type": "FRAME",
                            "children": [
                                {
                                    "id": "username-input",
                                    "name": "Username Input",
                                    "type": "RECTANGLE"
                                },
                                {
                                    "id": "password-input",
                                    "name": "Password Input",
                                    "type": "RECTANGLE"
                                },
                                {
                                    "id": "login-button",
                                    "name": "Login Button",
                                    "type": "RECTANGLE"
                                }
                            ]
                        }
                    ]
                },
                {
                    "id": "profile-page",
                    "name": "Profile Page",
                    "type": "FRAME",
                    "width": 600,
                    "height": 800,
                    "children": [
                        {
                            "id": "profile-header",
                            "name": "Profile Header",
                            "type": "TEXT",
                            "characters": "User Profile"
                        }
                    ]
                },
                {
                    "id": "settings-page",
                    "name": "Settings Page",
                    "type": "FRAME",
                    "width": 600,
                    "height": 800,
                    "children": [
                        {
                            "id": "settings-header",
                            "name": "Settings Header",
                            "type": "TEXT",
                            "characters": "Settings"
                        }
                    ]
                }
            ]
        },
        "name": "Auth & Profile Pages"
    }
    
    # Request only Login and Profile pages
    scaffold_request = {
        "project_id": "auth-pages",
        "figma_data": figma_design,
        "target_pages": ["Login Page", "Profile Page"],  # Specific pages only
        "style_framework": "tailwind",
        "typescript": True,
        "glassmorphism": True,
        "olive_green_theme": True
    }
    
    tenant_context = {"tenant_id": "demo", "user_id": "demo"}
    
    result = await ui_agent.scaffold_ui_from_figma(scaffold_request, tenant_context)
    
    print(f"📄 Generated {len(result['pages'])} pages (filtered from 3 total)")
    for page in result['pages']:
        print(f"  - {page['name']} -> {page['route']}")
    
    print("✅ Specific page scaffolding completed!")

async def demo_different_style_frameworks():
    """Demo different styling frameworks"""
    print("\n" + "=" * 60)
    print("🎨 DEMO: Different Style Frameworks")
    print("=" * 60)
    
    ui_agent = MockUIDevAgent()
    
    # Simple Figma design
    figma_design = {
        "document": {
            "id": "root",
            "name": "Root",
            "type": "DOCUMENT",
            "children": [
                {
                    "id": "sample-page",
                    "name": "Sample Page",
                    "type": "FRAME",
                    "width": 400,
                    "height": 300,
                    "children": [
                        {
                            "id": "sample-text",
                            "name": "Sample Text",
                            "type": "TEXT",
                            "characters": "Hello World"
                        }
                    ]
                }
            ]
        },
        "name": "Style Framework Test"
    }
    
    frameworks = ["tailwind", "styled-components"]
    
    for framework in frameworks:
        print(f"\n🎯 Testing {framework}...")
        
        scaffold_request = {
            "project_id": f"test-{framework}",
            "figma_data": figma_design,
            "style_framework": framework,
            "typescript": True,
            "glassmorphism": True,
            "olive_green_theme": True
        }
        
        tenant_context = {"tenant_id": "demo", "user_id": "demo"}
        result = await ui_agent.scaffold_ui_from_figma(scaffold_request, tenant_context)
        
        print(f"  - Generated {len(result['styles'])} style files")
        for style_file in result['styles'].keys():
            print(f"    - {style_file}")
        
        print(f"  - Dependencies: {len(result['dependencies'])}")
        framework_deps = [dep for dep in result['dependencies'] if framework in dep]
        print(f"  - Framework-specific deps: {framework_deps}")
    
    print("✅ Style framework comparison completed!")

async def main():
    """Run all demos"""
    print("🎨 Night 39: UIDevAgent Demo Suite")
    print("Scaffolding React pages from Figma JSON via CLI html-to-react")
    print("=" * 80)
    
    # Run main demo
    success = await demo_figma_to_react_scaffolding()
    
    if success:
        # Run additional demos
        await demo_specific_page_scaffolding()
        await demo_different_style_frameworks()
        
        print("\n" + "=" * 80)
        print("🎉 ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        
        print("\n📋 SUMMARY:")
        print("✅ Figma JSON parsing and frame extraction")
        print("✅ HTML structure generation from Figma nodes")
        print("✅ HTML to React component conversion")
        print("✅ Glassmorphism styling application")
        print("✅ Olive green theme integration")
        print("✅ Reusable component extraction")
        print("✅ Multi-page scaffolding")
        print("✅ Tailwind CSS configuration generation")
        print("✅ React Router setup")
        print("✅ TypeScript support")
        print("✅ Dependency management")
        print("✅ Setup instructions generation")
        
        print("\n🚀 Ready for production integration!")
        print("The UIDevAgent can now scaffold complete React applications from Figma designs!")
        
    else:
        print("❌ Demo failed. Please check the logs for details.")

if __name__ == "__main__":
    asyncio.run(main()) 