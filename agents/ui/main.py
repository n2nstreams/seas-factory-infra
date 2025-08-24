#!/usr/bin/env python3
"""
UIDevAgent - Night 39 Implementation
Scaffolds React pages from Figma JSON via CLI html-to-react
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import json
import os
import tempfile
import subprocess
from typing import List, Dict, Any, Optional, Literal, Union
import logging
from contextlib import asynccontextmanager
import re

# Import shared components
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from tenant_db import TenantDatabase, TenantContext, get_tenant_context_from_headers
from github_integration import (
    create_github_integration
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic Models
class FigmaNode(BaseModel):
    """Model for a Figma design node"""
    id: str
    name: str
    type: str
    visible: bool = True
    backgroundColor: Optional[str] = None
    children: List['FigmaNode'] = Field(default_factory=list)
    constraints: Optional[Dict[str, Any]] = None
    effects: List[Dict[str, Any]] = Field(default_factory=list)
    fills: List[Dict[str, Any]] = Field(default_factory=list)
    strokes: List[Dict[str, Any]] = Field(default_factory=list)
    strokeWeight: Optional[float] = None
    cornerRadius: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    x: Optional[float] = None
    y: Optional[float] = None
    rotation: Optional[float] = None
    characters: Optional[str] = None  # For text nodes
    style: Optional[Dict[str, Any]] = None  # Text styling

# Allow forward reference
FigmaNode.model_rebuild()

class FigmaFrame(BaseModel):
    """Model for a Figma frame (page/component)"""
    id: str
    name: str
    type: str = "FRAME"
    width: float
    height: float
    children: List[FigmaNode] = Field(default_factory=list)
    backgroundColor: Optional[str] = None
    layoutMode: Optional[str] = None  # NONE, HORIZONTAL, VERTICAL
    paddingLeft: Optional[float] = None
    paddingRight: Optional[float] = None
    paddingTop: Optional[float] = None
    paddingBottom: Optional[float] = None
    itemSpacing: Optional[float] = None
    counterAxisSizingMode: Optional[str] = None
    primaryAxisSizingMode: Optional[str] = None

class FigmaDocument(BaseModel):
    """Model for complete Figma document"""
    document: FigmaNode
    components: Dict[str, Any] = Field(default_factory=dict)
    styles: Dict[str, Any] = Field(default_factory=dict)
    schemaVersion: int = 0
    name: str = "Untitled"
    lastModified: Optional[str] = None
    thumbnailUrl: Optional[str] = None
    version: Optional[str] = None

class ReactComponent(BaseModel):
    """Model for generated React component"""
    name: str
    filename: str
    content: str
    imports: List[str] = Field(default_factory=list)
    props: List[Dict[str, Any]] = Field(default_factory=list)
    styles: Optional[str] = None
    component_type: Literal["functional", "class"] = "functional"
    hooks_used: List[str] = Field(default_factory=list)
    children_components: List[str] = Field(default_factory=list)

class ReactPage(BaseModel):
    """Model for generated React page"""
    name: str
    filename: str
    route: str
    content: str
    components: List[ReactComponent] = Field(default_factory=list)
    styles: Optional[str] = None
    layout: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)

class UIScaffoldRequest(BaseModel):
    """Request model for UI scaffolding"""
    project_id: str = Field(..., description="Project ID")
    figma_data: Union[FigmaDocument, Dict[str, Any]] = Field(..., description="Figma design data")
    target_pages: List[str] = Field(default_factory=list, description="Specific pages to generate")
    style_framework: Literal["tailwind", "styled-components", "css-modules", "emotion"] = Field(default="tailwind")
    component_library: Optional[str] = Field(None, description="UI library (mui, antd, chakra)")
    typescript: bool = Field(True, description="Generate TypeScript components")
    responsive: bool = Field(True, description="Generate responsive designs")
    glassmorphism: bool = Field(True, description="Apply glassmorphism styling")
    olive_green_theme: bool = Field(True, description="Use olive green color theme")

class ScaffoldResult(BaseModel):
    """Result model for UI scaffolding"""
    project_id: str
    pages: List[ReactPage]
    components: List[ReactComponent]
    styles: Dict[str, str] = Field(default_factory=dict)
    total_files: int
    total_lines: int
    setup_instructions: List[str]
    dependencies: List[str]
    routing_config: Optional[str] = None

class UIDevAgent:
    """Agent for scaffolding React UIs from Figma designs"""
    
    def __init__(self):
        self.tenant_db = TenantDatabase()
        self.github_integration = create_github_integration()
        
        # CLI tools configuration
        self.html_to_react_cmd = os.getenv("HTML_TO_REACT_CMD", "html-to-react")
        self.node_cmd = os.getenv("NODE_CMD", "node")
        self.npm_cmd = os.getenv("NPM_CMD", "npm")
        
        # Styling configuration
        self.olive_green_palette = {
            "primary": "#6B7280",      # Olive gray
            "secondary": "#84CC16",    # Lime green
            "accent": "#22C55E",       # Green
            "background": "#F9FAFB",   # Light gray
            "surface": "#FFFFFF",      # White
            "text": "#374151",         # Dark gray
            "textSecondary": "#6B7280" # Medium gray
        }
        
        # Glassmorphism styles
        self.glassmorphism_styles = {
            "backdrop": "backdrop-blur-lg",
            "background": "bg-white/10",
            "border": "border border-white/20",
            "shadow": "shadow-xl",
            "rounded": "rounded-xl"
        }
        
    def parse_figma_json(self, figma_data: Union[Dict[str, Any], FigmaDocument]) -> FigmaDocument:
        """Parse Figma JSON data into structured format"""
        try:
            if isinstance(figma_data, dict):
                return FigmaDocument(**figma_data)
            return figma_data
        except Exception as e:
            logger.error(f"Error parsing Figma JSON: {e}")
            # Create a minimal valid document
            return FigmaDocument(
                document=FigmaNode(
                    id="root",
                    name="Root",
                    type="DOCUMENT",
                    children=[]
                )
            )
    
    def extract_frames_from_figma(self, figma_doc: FigmaDocument) -> List[FigmaFrame]:
        """Extract page frames from Figma document"""
        frames = []
        
        def extract_frames_recursive(node: FigmaNode):
            if node.type == "FRAME" and node.name and not node.name.startswith("_"):
                # Convert FigmaNode to FigmaFrame
                frame = FigmaFrame(
                    id=node.id,
                    name=node.name,
                    type=node.type,
                    width=node.width or 375,  # Default mobile width
                    height=node.height or 812,  # Default mobile height
                    children=node.children,
                    backgroundColor=node.backgroundColor
                )
                frames.append(frame)
            
            # Recursively search children
            for child in node.children:
                extract_frames_recursive(child)
        
        extract_frames_recursive(figma_doc.document)
        return frames
    
    def figma_node_to_html(self, node: FigmaNode, depth: int = 0) -> str:
        """Convert Figma node to HTML structure"""
        indent = "  " * depth
        
        # Determine HTML element type based on Figma node
        if node.type == "TEXT":
            tag = "p" if not node.style or node.style.get("fontSize", 16) <= 18 else "h2"
            content = node.characters or node.name
            return f"{indent}<{tag} className=\"figma-text\">{content}</{tag}>\n"
        
        elif node.type == "RECTANGLE":
            if node.fills and any(fill.get("type") == "IMAGE" for fill in node.fills):
                return f"{indent}<img className=\"figma-image\" alt=\"{node.name}\" />\n"
            else:
                return f"{indent}<div className=\"figma-rectangle\">{node.name}</div>\n"
        
        elif node.type == "FRAME" or node.type == "GROUP":
            tag = "section" if node.type == "FRAME" else "div"
            class_name = f"figma-{node.type.lower()}"
            
            # Handle layout mode
            layout_class = ""
            if hasattr(node, 'layoutMode') and node.layoutMode:
                if node.layoutMode == "HORIZONTAL":
                    layout_class = " flex-row"
                elif node.layoutMode == "VERTICAL":
                    layout_class = " flex-col"
            
            html = f"{indent}<{tag} className=\"{class_name}{layout_class}\">\n"
            
            # Process children
            for child in node.children:
                html += self.figma_node_to_html(child, depth + 1)
            
            html += f"{indent}</{tag}>\n"
            return html
        
        elif node.type == "VECTOR" or node.type == "BOOLEAN_OPERATION":
            return f"{indent}<svg className=\"figma-vector\" aria-label=\"{node.name}\"></svg>\n"
        
        else:
            # Generic container for unknown types
            if node.children:
                html = f"{indent}<div className=\"figma-{node.type.lower()}\">\n"
                for child in node.children:
                    html += self.figma_node_to_html(child, depth + 1)
                html += f"{indent}</div>\n"
                return html
            else:
                return f"{indent}<div className=\"figma-element\">{node.name}</div>\n"
    
    def generate_css_from_figma(self, node: FigmaNode, olive_theme: bool = True) -> str:
        """Generate CSS styles from Figma node properties"""
        styles = []
        
        # Background color
        if node.backgroundColor:
            if olive_theme:
                # Map to olive green palette
                styles.append(f"background-color: {self.olive_green_palette['background']};")
            else:
                styles.append(f"background-color: {node.backgroundColor};")
        
        # Dimensions
        if node.width:
            styles.append(f"width: {node.width}px;")
        if node.height:
            styles.append(f"height: {node.height}px;")
        
        # Position
        if node.x is not None and node.y is not None:
            styles.append("position: absolute;")
            styles.append(f"left: {node.x}px;")
            styles.append(f"top: {node.y}px;")
        
        # Border radius
        if node.cornerRadius:
            styles.append(f"border-radius: {node.cornerRadius}px;")
        
        # Effects (shadows, etc.)
        for effect in node.effects:
            if effect.get("type") == "DROP_SHADOW":
                offset_x = effect.get("offset", {}).get("x", 0)
                offset_y = effect.get("offset", {}).get("y", 0)
                blur = effect.get("radius", 0)
                styles.append(f"box-shadow: {offset_x}px {offset_y}px {blur}px rgba(0,0,0,0.1);")
        
        return " ".join(styles)
    
    async def install_html_to_react_cli(self) -> bool:
        """Install html-to-react CLI tool if not available"""
        try:
            # Check if already installed
            result = subprocess.run([self.html_to_react_cmd, "--version"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("html-to-react CLI already available")
                return True
        except FileNotFoundError:
            pass
        
        try:
            # Try to install via npm
            logger.info("Installing html-to-react CLI...")
            result = subprocess.run([self.npm_cmd, "install", "-g", "html-to-react"], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("html-to-react CLI installed successfully")
                return True
            else:
                logger.warning(f"Failed to install html-to-react CLI: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error installing html-to-react CLI: {e}")
            return False
    
    async def convert_html_to_react(self, html_content: str, component_name: str) -> str:
        """Convert HTML to React component using CLI tool"""
        # Fallback to manual conversion if CLI not available
        if not await self.install_html_to_react_cli():
            return self.manual_html_to_react_conversion(html_content, component_name)
        
        try:
            # Create temporary files
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as html_file:
                html_file.write(html_content)
                html_file_path = html_file.name
            
            # Run html-to-react conversion
            result = subprocess.run([
                self.html_to_react_cmd,
                html_file_path,
                "--component-name", component_name,
                "--typescript"
            ], capture_output=True, text=True)
            
            # Cleanup
            os.unlink(html_file_path)
            
            if result.returncode == 0:
                return result.stdout
            else:
                logger.warning(f"html-to-react CLI failed: {result.stderr}")
                return self.manual_html_to_react_conversion(html_content, component_name)
                
        except Exception as e:
            logger.error(f"Error running html-to-react CLI: {e}")
            return self.manual_html_to_react_conversion(html_content, component_name)
    
    def manual_html_to_react_conversion(self, html_content: str, component_name: str) -> str:
        """Manual HTML to React conversion as fallback"""
        
        # Basic HTML to JSX conversion
        jsx_content = html_content
        
        # Replace class with className
        jsx_content = re.sub(r'\bclass=', 'className=', jsx_content)
        
        # Replace for with htmlFor
        jsx_content = re.sub(r'\bfor=', 'htmlFor=', jsx_content)
        
        # Close self-closing tags
        jsx_content = re.sub(r'<(img|input|br|hr)([^>]*?)>', r'<\1\2 />', jsx_content)
        
        # Convert inline styles
        jsx_content = re.sub(r'style="([^"]*)"', lambda m: f'style={{{{ {self.convert_css_to_js_object(m.group(1))} }}}}', jsx_content)
        
        # Generate React component template
        react_component = f"""import React from 'react';

interface {component_name}Props {{
  className?: string;
  children?: React.ReactNode;
}}

const {component_name}: React.FC<{component_name}Props> = ({{ className = '', children }}) => {{
  return (
    <div className={{`{component_name.lower()}-container ${{className}}`}}>
      {jsx_content.strip()}
    </div>
  );
}};

export default {component_name};"""
        
        return react_component
    
    def convert_css_to_js_object(self, css_string: str) -> str:
        """Convert CSS string to JavaScript object format"""
        properties = css_string.split(';')
        js_props = []
        
        for prop in properties:
            if ':' in prop:
                key, value = prop.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Convert kebab-case to camelCase
                key = re.sub(r'-([a-z])', lambda m: m.group(1).upper(), key)
                
                js_props.append(f"'{key}': '{value}'")
        
        return ', '.join(js_props)
    
    def apply_glassmorphism_styling(self, component_content: str) -> str:
        """Apply glassmorphism styling to React component"""
        
        # Add glassmorphism classes to containers
        glassmorphism_classes = " ".join([
            self.glassmorphism_styles["backdrop"],
            self.glassmorphism_styles["background"],
            self.glassmorphism_styles["border"],
            self.glassmorphism_styles["shadow"],
            self.glassmorphism_styles["rounded"]
        ])
        
        # Replace container classes
        component_content = re.sub(
            r'className="\s*([^"]*)\s*"',
            lambda m: f'className="{m.group(1)} {glassmorphism_classes}".trim()',
            component_content
        )
        
        return component_content
    
    def apply_olive_green_theme(self, component_content: str) -> str:
        """Apply olive green color theme to React component"""
        
        # Color mappings for theme
        color_mappings = {
            'text-gray-900': 'text-gray-700',
            'bg-white': 'bg-green-50',
            'bg-gray-100': 'bg-green-100',
            'border-gray-200': 'border-green-200',
            'text-blue-500': 'text-green-600',
            'bg-blue-500': 'bg-green-600',
            'hover:bg-blue-600': 'hover:bg-green-700'
        }
        
        for old_class, new_class in color_mappings.items():
            component_content = component_content.replace(old_class, new_class)
        
        return component_content
    
    async def scaffold_react_page(self, frame: FigmaFrame, request: UIScaffoldRequest) -> ReactPage:
        """Scaffold a complete React page from Figma frame"""
        
        # Generate HTML structure from Figma frame
        html_content = "<div className=\"page-container\">\n"
        for child in frame.children:
            html_content += self.figma_node_to_html(child, 1)
        html_content += "</div>"
        
        # Convert to React component
        page_name = self.sanitize_component_name(frame.name)
        react_content = await self.convert_html_to_react(html_content, page_name)
        
        # Apply styling preferences
        if request.glassmorphism:
            react_content = self.apply_glassmorphism_styling(react_content)
        
        if request.olive_green_theme:
            react_content = self.apply_olive_green_theme(react_content)
        
        # Generate route
        route = f"/{page_name.lower().replace('page', '').replace('screen', '')}"
        if route == "/":
            route = "/home"
        
        # Create page metadata
        meta = {
            "title": f"{page_name} - AI SaaS Factory",
            "description": f"Auto-generated {page_name} page from Figma design",
            "figma_frame_id": frame.id,
            "width": frame.width,
            "height": frame.height
        }
        
        return ReactPage(
            name=page_name,
            filename=f"{page_name}.tsx" if request.typescript else f"{page_name}.jsx",
            route=route,
            content=react_content,
            components=[],  # Will be populated by component extraction
            meta=meta
        )
    
    def sanitize_component_name(self, name: str) -> str:
        """Sanitize Figma frame name for React component"""
        # Remove special characters and make PascalCase
        sanitized = re.sub(r'[^a-zA-Z0-9\s]', '', name)
        sanitized = ''.join(word.capitalize() for word in sanitized.split())
        
        # Ensure it starts with uppercase letter
        if not sanitized or not sanitized[0].isupper():
            sanitized = "Page" + sanitized
        
        return sanitized
    
    def extract_reusable_components(self, frame: FigmaFrame) -> List[ReactComponent]:
        """Extract reusable components from Figma frame"""
        components = []
        
        def extract_components_recursive(node: FigmaNode, depth: int = 0):
            # Component detection heuristics
            is_component = (
                node.type in ["FRAME", "GROUP"] and
                len(node.children) > 1 and
                depth > 0 and
                not node.name.lower().startswith("page")
            )
            
            if is_component:
                component_name = self.sanitize_component_name(node.name)
                html_content = self.figma_node_to_html(node)
                
                # Convert to React component (simplified)
                component_content = f"""import React from 'react';

interface {component_name}Props {{
  className?: string;
}}

const {component_name}: React.FC<{component_name}Props> = ({{ className = '' }}) => {{
  return (
    <div className={{`{component_name.lower()}-component ${{className}}`}}>
      {html_content.strip()}
    </div>
  );
}};

export default {component_name};"""
                
                components.append(ReactComponent(
                    name=component_name,
                    filename=f"{component_name}.tsx",
                    content=component_content,
                    imports=["React"],
                    component_type="functional"
                ))
            
            # Recursively process children
            for child in node.children:
                extract_components_recursive(child, depth + 1)
        
        for child in frame.children:
            extract_components_recursive(child)
        
        return components
    
    def generate_styles(self, request: UIScaffoldRequest) -> Dict[str, str]:
        """Generate global styles and theme configuration"""
        styles = {}
        
        if request.style_framework == "tailwind":
            styles["tailwind.config.js"] = self.generate_tailwind_config(request)
            styles["globals.css"] = self.generate_global_css(request)
        elif request.style_framework == "styled-components":
            styles["theme.ts"] = self.generate_styled_components_theme(request)
        
        return styles
    
    def generate_tailwind_config(self, request: UIScaffoldRequest) -> str:
        """Generate Tailwind CSS configuration"""
        config = {
            "content": ["./src/**/*.{js,ts,jsx,tsx}"],
            "theme": {
                "extend": {
                    "colors": self.olive_green_palette if request.olive_green_theme else {},
                    "backdropBlur": {
                        "xs": "2px"
                    } if request.glassmorphism else {}
                }
            },
            "plugins": []
        }
        
        return f"""module.exports = {json.dumps(config, indent=2)};"""
    
    def generate_global_css(self, request: UIScaffoldRequest) -> str:
        """Generate global CSS styles"""
        css = """@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    font-family: 'Inter', sans-serif;
  }
}

@layer components {"""
        
        if request.glassmorphism:
            css += """
  .glass {
    @apply backdrop-blur-lg bg-white/10 border border-white/20 shadow-xl rounded-xl;
  }"""
        
        if request.olive_green_theme:
            css += """
  .olive-theme {
    @apply text-gray-700 bg-green-50;
  }"""
        
        css += """
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
        
        return css
    
    def generate_styled_components_theme(self, request: UIScaffoldRequest) -> str:
        """Generate styled-components theme"""
        theme = {
            "colors": self.olive_green_palette if request.olive_green_theme else {
                "primary": "#3B82F6",
                "secondary": "#10B981", 
                "background": "#F9FAFB",
                "text": "#111827"
            },
            "spacing": {
                "xs": "0.25rem",
                "sm": "0.5rem",
                "md": "1rem",
                "lg": "1.5rem",
                "xl": "3rem"
            },
            "borderRadius": {
                "sm": "0.125rem",
                "md": "0.375rem",
                "lg": "0.5rem",
                "xl": "0.75rem"
            }
        }
        
        return f"""export const theme = {json.dumps(theme, indent=2)};

export type Theme = typeof theme;"""
    
    def generate_routing_config(self, pages: List[ReactPage]) -> str:
        """Generate React Router configuration"""
        imports = []
        routes = []
        
        for page in pages:
            component_name = page.name
            imports.append(f"import {component_name} from './pages/{component_name}';")
            routes.append(f"  {{ path: '{page.route}', element: <{component_name} /> }}")
        
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
    
    def generate_setup_instructions(self, request: UIScaffoldRequest, dependencies: List[str]) -> List[str]:
        """Generate setup instructions for the scaffolded project"""
        instructions = [
            "1. Install dependencies:",
            f"   npm install {' '.join(dependencies)}",
            "2. Set up the project structure:",
            "   - Place components in src/components/",
            "   - Place pages in src/pages/",
            "   - Update src/App.tsx with the routing configuration"
        ]
        
        if request.style_framework == "tailwind":
            instructions.extend([
                "3. Configure Tailwind CSS:",
                "   - Replace tailwind.config.js with the generated configuration",
                "   - Update src/index.css with the generated global styles"
            ])
        
        if request.component_library:
            instructions.extend([
                f"4. Configure {request.component_library}:",
                f"   - Follow {request.component_library} setup documentation",
                "   - Wrap your app with the theme provider"
            ])
        
        instructions.extend([
            "5. Start the development server:",
            "   npm start",
            "6. Open http://localhost:3000 to view the application"
        ])
        
        return instructions
    
    async def scaffold_ui_from_figma(self, request: UIScaffoldRequest, tenant_context: TenantContext) -> ScaffoldResult:
        """Main method to scaffold React UI from Figma design"""
        logger.info(f"Scaffolding UI for project: {request.project_id}")
        
        # Log the scaffolding request
        await self.tenant_db.log_agent_event(
            tenant_context=tenant_context,
            event_type="ui_scaffolding",
            agent_name="UIDevAgent",
            stage="ui_scaffolding",
            status="started",
            project_id=request.project_id,
            input_data=request.model_dump(exclude={"figma_data"})
        )
        
        try:
            # Parse Figma data
            figma_doc = self.parse_figma_json(request.figma_data)
            
            # Extract frames (pages) from Figma
            frames = self.extract_frames_from_figma(figma_doc)
            
            if not frames:
                raise ValueError("No frames found in Figma document")
            
            # Filter frames if specific pages requested
            if request.target_pages:
                frames = [f for f in frames if f.name in request.target_pages]
            
            # Scaffold pages
            pages = []
            all_components = []
            
            for frame in frames:
                page = await self.scaffold_react_page(frame, request)
                
                # Extract reusable components
                components = self.extract_reusable_components(frame)
                page.components = components
                all_components.extend(components)
                
                pages.append(page)
            
            # Generate styles
            styles = self.generate_styles(request)
            
            # Generate routing configuration
            routing_config = self.generate_routing_config(pages)
            
            # Determine dependencies
            dependencies = ["react", "react-dom"]
            if request.typescript:
                dependencies.extend(["typescript", "@types/react", "@types/react-dom"])
            
            if request.style_framework == "tailwind":
                dependencies.extend(["tailwindcss", "autoprefixer", "postcss"])
            elif request.style_framework == "styled-components":
                dependencies.extend(["styled-components"])
                if request.typescript:
                    dependencies.append("@types/styled-components")
            
            if request.component_library:
                if request.component_library == "mui":
                    dependencies.extend(["@mui/material", "@emotion/react", "@emotion/styled"])
                elif request.component_library == "antd":
                    dependencies.append("antd")
                elif request.component_library == "chakra":
                    dependencies.extend(["@chakra-ui/react", "@emotion/react", "@emotion/styled"])
            
            dependencies.append("react-router-dom")
            
            # Generate setup instructions
            setup_instructions = self.generate_setup_instructions(request, dependencies)
            
            # Calculate metrics
            total_lines = sum(len(page.content.splitlines()) for page in pages)
            total_lines += sum(len(comp.content.splitlines()) for comp in all_components)
            
            result = ScaffoldResult(
                project_id=request.project_id,
                pages=pages,
                components=all_components,
                styles=styles,
                total_files=len(pages) + len(all_components) + len(styles),
                total_lines=total_lines,
                setup_instructions=setup_instructions,
                dependencies=dependencies,
                routing_config=routing_config
            )
            
            # Log successful completion
            await self.tenant_db.log_agent_event(
                tenant_context=tenant_context,
                event_type="ui_scaffolding",
                agent_name="UIDevAgent",
                stage="ui_scaffolding",
                status="completed",
                project_id=request.project_id,
                output_data={
                    "pages_count": len(pages),
                    "components_count": len(all_components),
                    "total_files": result.total_files,
                    "total_lines": result.total_lines
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error scaffolding UI: {e}")
            
            # Log failure
            await self.tenant_db.log_agent_event(
                tenant_context=tenant_context,
                event_type="ui_scaffolding",
                agent_name="UIDevAgent",
                stage="ui_scaffolding",
                status="failed",
                project_id=request.project_id,
                error_message=str(e)
            )
            
            raise HTTPException(status_code=500, detail=str(e))

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting UIDevAgent")
    yield
    # Shutdown
    logger.info("Shutting down UIDevAgent")

app = FastAPI(
    title="UIDevAgent",
    description="React UI scaffolding agent from Figma designs",
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
ui_dev_agent = UIDevAgent()

async def get_tenant_context(request) -> TenantContext:
    """Get tenant context from request headers"""
    headers = dict(request.headers)
    tenant_context = get_tenant_context_from_headers(headers)
    if not tenant_context:
        # For development, use default tenant
        tenant_context = TenantContext(tenant_id="default", user_id="ui-dev-user")
    return tenant_context

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "UIDevAgent v1.0", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "OK", "agent": "ui-dev", "version": "1.0.0"}

@app.post("/scaffold", response_model=ScaffoldResult)
async def scaffold_ui(
    request: UIScaffoldRequest,
    tenant_context: TenantContext = Depends(get_tenant_context)
):
    """Scaffold React UI from Figma design"""
    return await ui_dev_agent.scaffold_ui_from_figma(request, tenant_context)

@app.get("/frameworks")
async def get_supported_frameworks():
    """Get supported styling frameworks and component libraries"""
    return {
        "style_frameworks": ["tailwind", "styled-components", "css-modules", "emotion"],
        "component_libraries": ["mui", "antd", "chakra"],
        "features": ["typescript", "responsive", "glassmorphism", "olive_green_theme"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8085) 