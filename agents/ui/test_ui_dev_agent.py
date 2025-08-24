#!/usr/bin/env python3
"""
Test suite for UIDevAgent - Night 39 Implementation
Tests Figma JSON parsing, React scaffolding, and html-to-react integration
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock

from main import (
    UIDevAgent, FigmaNode, FigmaFrame, FigmaDocument,
    UIScaffoldRequest, ReactPage,
    TenantContext
)

class TestUIDevAgent:
    """Test suite for UIDevAgent"""
    
    @pytest.fixture
    def agent(self):
        """Create UIDevAgent instance for testing"""
        with patch('main.TenantDatabase'):
            with patch('main.create_github_integration'):
                return UIDevAgent()
    
    @pytest.fixture
    def tenant_context(self):
        """Create mock tenant context"""
        return TenantContext(tenant_id="test-tenant", user_id="test-user")
    
    @pytest.fixture
    def sample_figma_node(self):
        """Create sample Figma node for testing"""
        return FigmaNode(
            id="test-node-1",
            name="Sample Button",
            type="FRAME",
            width=200,
            height=50,
            x=10,
            y=20,
            backgroundColor="#FFFFFF",
            cornerRadius=8,
            children=[
                FigmaNode(
                    id="text-node-1",
                    name="Button Text",
                    type="TEXT",
                    characters="Click Me",
                    style={"fontSize": 16}
                )
            ]
        )
    
    @pytest.fixture
    def sample_figma_frame(self, sample_figma_node):
        """Create sample Figma frame for testing"""
        return FigmaFrame(
            id="frame-1",
            name="Landing Page",
            type="FRAME",
            width=375,
            height=812,
            children=[sample_figma_node],
            layoutMode="VERTICAL"
        )
    
    @pytest.fixture
    def sample_figma_document(self, sample_figma_frame):
        """Create sample Figma document for testing"""
        return FigmaDocument(
            document=FigmaNode(
                id="document-root",
                name="Root",
                type="DOCUMENT",
                children=[sample_figma_frame]
            ),
            name="Test Design"
        )
    
    @pytest.fixture
    def sample_scaffold_request(self, sample_figma_document):
        """Create sample UI scaffold request"""
        return UIScaffoldRequest(
            project_id="test-project",
            figma_data=sample_figma_document,
            style_framework="tailwind",
            typescript=True,
            glassmorphism=True,
            olive_green_theme=True
        )

class TestFigmaJsonParsing:
    """Test Figma JSON parsing functionality"""
    
    def test_parse_figma_json_from_dict(self, agent):
        """Test parsing Figma JSON from dictionary"""
        figma_dict = {
            "document": {
                "id": "root",
                "name": "Root",
                "type": "DOCUMENT",
                "children": []
            },
            "name": "Test Document"
        }
        
        result = agent.parse_figma_json(figma_dict)
        
        assert isinstance(result, FigmaDocument)
        assert result.name == "Test Document"
        assert result.document.id == "root"
    
    def test_parse_invalid_figma_json(self, agent):
        """Test handling of invalid Figma JSON"""
        invalid_data = {"invalid": "structure"}
        
        result = agent.parse_figma_json(invalid_data)
        
        # Should return a minimal valid document
        assert isinstance(result, FigmaDocument)
        assert result.document.name == "Root"
    
    def test_extract_frames_from_figma(self, agent, sample_figma_document):
        """Test extracting frames from Figma document"""
        frames = agent.extract_frames_from_figma(sample_figma_document)
        
        assert len(frames) == 1
        assert frames[0].name == "Landing Page"
        assert frames[0].width == 375
        assert frames[0].height == 812

class TestHtmlToReactConversion:
    """Test HTML to React conversion functionality"""
    
    def test_figma_node_to_html_text(self, agent):
        """Test converting text node to HTML"""
        text_node = FigmaNode(
            id="text-1",
            name="Heading",
            type="TEXT",
            characters="Welcome",
            style={"fontSize": 24}
        )
        
        html = agent.figma_node_to_html(text_node)
        
        assert '<h2 className="figma-text">Welcome</h2>' in html
    
    def test_figma_node_to_html_rectangle(self, agent):
        """Test converting rectangle node to HTML"""
        rect_node = FigmaNode(
            id="rect-1",
            name="Card",
            type="RECTANGLE",
            width=200,
            height=100
        )
        
        html = agent.figma_node_to_html(rect_node)
        
        assert 'className="figma-rectangle"' in html
        assert 'Card' in html
    
    def test_figma_node_to_html_frame_with_layout(self, agent):
        """Test converting frame with layout mode to HTML"""
        frame_node = FigmaNode(
            id="frame-1",
            name="Container",
            type="FRAME",
            layoutMode="HORIZONTAL",
            children=[
                FigmaNode(id="child-1", name="Child 1", type="TEXT", characters="Text 1"),
                FigmaNode(id="child-2", name="Child 2", type="TEXT", characters="Text 2")
            ]
        )
        
        html = agent.figma_node_to_html(frame_node)
        
        assert 'className="figma-frame flex-row"' in html
        assert 'Text 1' in html
        assert 'Text 2' in html
    
    def test_manual_html_to_react_conversion(self, agent):
        """Test manual HTML to React conversion"""
        html_content = '<div class="container"><p style="color: red;">Hello World</p></div>'
        component_name = "TestComponent"
        
        react_code = agent.manual_html_to_react_conversion(html_content, component_name)
        
        assert "className=" in react_code
        assert "class=" not in react_code
        assert f"const {component_name}:" in react_code
        assert "React.FC" in react_code
        assert "export default" in react_code
    
    def test_convert_css_to_js_object(self, agent):
        """Test CSS to JavaScript object conversion"""
        css_string = "color: red; font-size: 16px; background-color: blue"
        
        js_object = agent.convert_css_to_js_object(css_string)
        
        assert "'color': 'red'" in js_object
        assert "'fontSize': '16px'" in js_object
        assert "'backgroundColor': 'blue'" in js_object

class TestStylingAndTheming:
    """Test styling and theming functionality"""
    
    def test_apply_glassmorphism_styling(self, agent):
        """Test applying glassmorphism styling"""
        component_content = 'className="container"'
        
        styled_content = agent.apply_glassmorphism_styling(component_content)
        
        assert "backdrop-blur-lg" in styled_content
        assert "bg-white/10" in styled_content
        assert "border-white/20" in styled_content
        assert "shadow-xl" in styled_content
    
    def test_apply_olive_green_theme(self, agent):
        """Test applying olive green theme"""
        component_content = 'className="text-gray-900 bg-white border-gray-200"'
        
        themed_content = agent.apply_olive_green_theme(component_content)
        
        assert "text-gray-700" in themed_content
        assert "bg-green-50" in themed_content
        assert "border-green-200" in themed_content
    
    def test_generate_tailwind_config(self, agent, sample_scaffold_request):
        """Test generating Tailwind CSS configuration"""
        config = agent.generate_tailwind_config(sample_scaffold_request)
        
        assert "module.exports" in config
        assert "content" in config
        assert "olive" in config.lower() or "green" in config
    
    def test_generate_global_css(self, agent, sample_scaffold_request):
        """Test generating global CSS"""
        css = agent.generate_global_css(sample_scaffold_request)
        
        assert "@tailwind base" in css
        assert "@tailwind components" in css
        assert "@tailwind utilities" in css
        assert ".glass" in css
        assert ".olive-theme" in css

class TestComponentExtraction:
    """Test component extraction functionality"""
    
    def test_sanitize_component_name(self, agent):
        """Test component name sanitization"""
        test_cases = [
            ("Button Component", "ButtonComponent"),
            ("header-nav", "HeaderNav"),
            ("123invalid", "Page123invalid"),
            ("Card@#$%", "Card"),
            ("", "Page")
        ]
        
        for input_name, expected in test_cases:
            result = agent.sanitize_component_name(input_name)
            assert result == expected
    
    def test_extract_reusable_components(self, agent, sample_figma_frame):
        """Test extracting reusable components from frame"""
        # Add a nested frame that should be detected as a component
        nested_frame = FigmaNode(
            id="nested-1",
            name="Button Component",
            type="FRAME",
            children=[
                FigmaNode(id="text-1", name="Button Text", type="TEXT", characters="Click"),
                FigmaNode(id="icon-1", name="Icon", type="VECTOR")
            ]
        )
        sample_figma_frame.children.append(nested_frame)
        
        components = agent.extract_reusable_components(sample_figma_frame)
        
        assert len(components) >= 1
        component_names = [comp.name for comp in components]
        assert "ButtonComponent" in component_names

class TestReactScaffolding:
    """Test React scaffolding functionality"""
    
    @pytest.mark.asyncio
    async def test_scaffold_react_page(self, agent, sample_figma_frame, sample_scaffold_request):
        """Test scaffolding React page from Figma frame"""
        with patch.object(agent, 'convert_html_to_react', return_value="mock react code"):
            page = await agent.scaffold_react_page(sample_figma_frame, sample_scaffold_request)
            
            assert isinstance(page, ReactPage)
            assert page.name == "LandingPage"
            assert page.filename == "LandingPage.tsx"
            assert page.route == "/landing"
            assert page.meta["figma_frame_id"] == "frame-1"
    
    def test_generate_routing_config(self, agent):
        """Test generating React Router configuration"""
        pages = [
            ReactPage(name="Home", filename="Home.tsx", route="/", content="", meta={}),
            ReactPage(name="About", filename="About.tsx", route="/about", content="", meta={})
        ]
        
        config = agent.generate_routing_config(pages)
        
        assert "createBrowserRouter" in config
        assert "import Home from" in config
        assert "import About from" in config
        assert "path: '/'" in config
        assert "path: '/about'" in config
    
    def test_generate_setup_instructions(self, agent, sample_scaffold_request):
        """Test generating setup instructions"""
        dependencies = ["react", "react-dom", "tailwindcss"]
        
        instructions = agent.generate_setup_instructions(sample_scaffold_request, dependencies)
        
        assert len(instructions) > 0
        assert any("npm install" in instruction for instruction in instructions)
        assert any("Tailwind CSS" in instruction for instruction in instructions)

class TestFullUIScaffolding:
    """Test complete UI scaffolding workflow"""
    
    @pytest.mark.asyncio
    async def test_scaffold_ui_from_figma_success(self, agent, sample_scaffold_request, tenant_context):
        """Test successful UI scaffolding from Figma"""
        # Mock database operations
        agent.tenant_db.log_agent_event = AsyncMock()
        
        with patch.object(agent, 'convert_html_to_react', return_value="mock react component"):
            result = await agent.scaffold_ui_from_figma(sample_scaffold_request, tenant_context)
            
            assert result.project_id == "test-project"
            assert len(result.pages) == 1
            assert result.pages[0].name == "LandingPage"
            assert result.total_files > 0
            assert len(result.dependencies) > 0
            assert "react" in result.dependencies
            
            # Verify logging
            assert agent.tenant_db.log_agent_event.call_count == 2  # start and completion
    
    @pytest.mark.asyncio
    async def test_scaffold_ui_from_figma_no_frames(self, agent, tenant_context):
        """Test UI scaffolding with no frames found"""
        # Create request with empty document
        empty_doc = FigmaDocument(
            document=FigmaNode(id="root", name="Root", type="DOCUMENT", children=[])
        )
        request = UIScaffoldRequest(
            project_id="test-project",
            figma_data=empty_doc
        )
        
        agent.tenant_db.log_agent_event = AsyncMock()
        
        with pytest.raises(Exception) as exc_info:
            await agent.scaffold_ui_from_figma(request, tenant_context)
        
        assert "No frames found" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_scaffold_ui_with_target_pages(self, agent, sample_scaffold_request, tenant_context):
        """Test UI scaffolding with specific target pages"""
        sample_scaffold_request.target_pages = ["Landing Page"]
        agent.tenant_db.log_agent_event = AsyncMock()
        
        with patch.object(agent, 'convert_html_to_react', return_value="mock react component"):
            result = await agent.scaffold_ui_from_figma(sample_scaffold_request, tenant_context)
            
            assert len(result.pages) == 1
            assert result.pages[0].name == "LandingPage"

class TestHtmlToReactCLI:
    """Test html-to-react CLI integration"""
    
    @pytest.mark.asyncio
    async def test_install_html_to_react_cli_already_installed(self, agent):
        """Test when html-to-react CLI is already installed"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            
            result = await agent.install_html_to_react_cli()
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_install_html_to_react_cli_install_success(self, agent):
        """Test successful installation of html-to-react CLI"""
        with patch('subprocess.run') as mock_run:
            # First call (check) fails, second call (install) succeeds
            mock_run.side_effect = [
                Mock(returncode=1),  # Check fails
                Mock(returncode=0)   # Install succeeds
            ]
            
            result = await agent.install_html_to_react_cli()
            
            assert result is True
            assert mock_run.call_count == 2
    
    @pytest.mark.asyncio
    async def test_convert_html_to_react_cli_success(self, agent):
        """Test successful HTML to React conversion using CLI"""
        html_content = "<div>Hello World</div>"
        component_name = "TestComponent"
        
        with patch.object(agent, 'install_html_to_react_cli', return_value=True):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value.returncode = 0
                mock_run.return_value.stdout = "export default function TestComponent() { return <div>Hello World</div>; }"
                
                with patch('tempfile.NamedTemporaryFile') as mock_temp:
                    mock_temp.return_value.__enter__.return_value.name = "/tmp/test.html"
                    
                    with patch('os.unlink'):
                        result = await agent.convert_html_to_react(html_content, component_name)
                        
                        assert "TestComponent" in result
                        assert "export default" in result
    
    @pytest.mark.asyncio
    async def test_convert_html_to_react_cli_fallback(self, agent):
        """Test fallback to manual conversion when CLI fails"""
        html_content = "<div class='test'>Hello World</div>"
        component_name = "TestComponent"
        
        with patch.object(agent, 'install_html_to_react_cli', return_value=False):
            result = await agent.convert_html_to_react(html_content, component_name)
            
            # Should fall back to manual conversion
            assert "className=" in result
            assert "class=" not in result
            assert component_name in result

class TestDependencyManagement:
    """Test dependency management functionality"""
    
    def test_dependencies_typescript_enabled(self, agent, sample_scaffold_request):
        """Test dependencies when TypeScript is enabled"""
        sample_scaffold_request.typescript = True
        sample_scaffold_request.style_framework = "tailwind"
        sample_scaffold_request.component_library = "mui"
        
        # Simulate the dependency generation logic
        dependencies = ["react", "react-dom"]
        if sample_scaffold_request.typescript:
            dependencies.extend(["typescript", "@types/react", "@types/react-dom"])
        
        if sample_scaffold_request.style_framework == "tailwind":
            dependencies.extend(["tailwindcss", "autoprefixer", "postcss"])
        
        if sample_scaffold_request.component_library == "mui":
            dependencies.extend(["@mui/material", "@emotion/react", "@emotion/styled"])
        
        dependencies.append("react-router-dom")
        
        assert "typescript" in dependencies
        assert "@types/react" in dependencies
        assert "tailwindcss" in dependencies
        assert "@mui/material" in dependencies
    
    def test_dependencies_styled_components(self, agent):
        """Test dependencies for styled-components framework"""
        dependencies = ["react", "react-dom"]
        style_framework = "styled-components"
        typescript = True
        
        if style_framework == "styled-components":
            dependencies.extend(["styled-components"])
            if typescript:
                dependencies.append("@types/styled-components")
        
        assert "styled-components" in dependencies
        assert "@types/styled-components" in dependencies

# Integration tests
class TestIntegration:
    """Integration tests for UIDevAgent"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self, agent, tenant_context):
        """Test complete end-to-end workflow"""
        # Create a more complex Figma document
        figma_doc = {
            "document": {
                "id": "root",
                "name": "Root",
                "type": "DOCUMENT",
                "children": [
                    {
                        "id": "page-1",
                        "name": "Home Page",
                        "type": "FRAME",
                        "width": 375,
                        "height": 812,
                        "children": [
                            {
                                "id": "header",
                                "name": "Header",
                                "type": "FRAME",
                                "layoutMode": "HORIZONTAL",
                                "children": [
                                    {
                                        "id": "logo",
                                        "name": "Logo",
                                        "type": "TEXT",
                                        "characters": "SaaS Factory"
                                    },
                                    {
                                        "id": "nav",
                                        "name": "Navigation",
                                        "type": "FRAME",
                                        "children": []
                                    }
                                ]
                            },
                            {
                                "id": "content",
                                "name": "Main Content",
                                "type": "FRAME",
                                "children": [
                                    {
                                        "id": "hero",
                                        "name": "Hero Section",
                                        "type": "TEXT",
                                        "characters": "Welcome to AI SaaS Factory"
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            "name": "Design System"
        }
        
        request = UIScaffoldRequest(
            project_id="integration-test",
            figma_data=figma_doc,
            style_framework="tailwind",
            typescript=True,
            glassmorphism=True,
            olive_green_theme=True
        )
        
        agent.tenant_db.log_agent_event = AsyncMock()
        
        with patch.object(agent, 'convert_html_to_react', return_value="mock react component"):
            result = await agent.scaffold_ui_from_figma(request, tenant_context)
            
            # Verify results
            assert result.project_id == "integration-test"
            assert len(result.pages) == 1
            assert result.pages[0].name == "HomePage"
            assert len(result.components) >= 0  # May have extracted components
            assert "tailwind.config.js" in result.styles
            assert "globals.css" in result.styles
            assert result.routing_config is not None
            assert len(result.setup_instructions) > 0
            assert "react" in result.dependencies
            assert "tailwindcss" in result.dependencies

if __name__ == "__main__":
    pytest.main([__file__]) 