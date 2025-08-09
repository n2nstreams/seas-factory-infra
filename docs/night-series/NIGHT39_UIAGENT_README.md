# Night 39: UIDevAgent - Figma to React Scaffolding

## Overview

Night 39 implements the **UIDevAgent**, a specialized agent that scaffolds React pages from Figma JSON designs via CLI `html-to-react` integration. This agent bridges the gap between design and development by automatically converting Figma designs into production-ready React components with glassmorphism styling and olive green theming.

## Architecture

### System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Figma JSON    │    │   UIDevAgent    │    │  React Files    │
│     Design      │───▶│   (Port 8085)   │───▶│   Generated     │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              │
                       ┌─────────────────┐
                       │  html-to-react  │
                       │    CLI Tool     │
                       │                 │
                       └─────────────────┘
```

### Component Architecture

```
UIDevAgent
├── Figma JSON Parser
│   ├── Document Structure Analysis
│   ├── Frame & Node Extraction
│   └── Layout Mode Detection
├── HTML Generation Engine
│   ├── Node-to-HTML Conversion
│   ├── Layout Processing
│   └── Component Hierarchy
├── React Scaffolding Engine
│   ├── html-to-react CLI Integration
│   ├── Manual Conversion Fallback
│   └── TypeScript Generation
├── Styling & Theming
│   ├── Glassmorphism Application
│   ├── Olive Green Theme
│   └── Framework Integration
└── Code Generation
    ├── Component Extraction
    ├── Routing Configuration
    └── Setup Instructions
```

## Core Features

### 🎨 Figma Integration
- **JSON Parsing**: Comprehensive Figma document parsing
- **Frame Extraction**: Automatic page detection from frames
- **Node Processing**: Convert design nodes to HTML structure
- **Layout Detection**: Handle horizontal/vertical layouts

### ⚛️ React Scaffolding
- **TypeScript Support**: Generate TypeScript components by default
- **Functional Components**: Modern React functional components with hooks
- **Component Extraction**: Automatically extract reusable components
- **Routing Setup**: Generate React Router configuration

### 🎭 Styling & Theming
- **Glassmorphism**: Built-in glassmorphism effects
- **Olive Green Theme**: Natural olive green color palette
- **Multiple Frameworks**: Support for Tailwind, styled-components, etc.
- **Component Libraries**: Integration with MUI, Ant Design, Chakra UI

### 🛠️ CLI Integration
- **html-to-react**: Automatic CLI tool installation and usage
- **Fallback Processing**: Manual conversion when CLI unavailable
- **Error Handling**: Robust error handling and recovery

## File Structure

```
agents/ui/
├── main.py                    # UIDevAgent FastAPI server
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Multi-stage build with Node.js
└── test_ui_dev_agent.py      # Comprehensive test suite

night39_demo.py               # Demo script with examples
NIGHT39_UIAGENT_README.md     # This documentation
```

## Installation & Setup

### Prerequisites

```bash
# Python 3.11+
# Node.js 18+
# Docker (for containerized deployment)
```

### Local Development

```bash
# Install Python dependencies
cd agents/ui
pip install -r requirements.txt

# Install html-to-react CLI (optional, auto-installed)
npm install -g html-to-react

# Start the agent
python main.py
```

### Docker Deployment

```bash
# Build the container
cd agents/ui
docker build -t ui-dev-agent .

# Run the container
docker run -p 8085:8085 ui-dev-agent
```

## API Reference

### Base URL
```
http://localhost:8085
```

### Endpoints

#### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "OK",
  "agent": "ui-dev",
  "version": "1.0.0"
}
```

#### Scaffold UI
```http
POST /scaffold
```

**Request Body:**
```json
{
  "project_id": "my-project",
  "figma_data": {
    "document": {
      "id": "root",
      "name": "Root",
      "type": "DOCUMENT",
      "children": [...]
    },
    "name": "My Design"
  },
  "target_pages": ["Landing Page", "Dashboard"],
  "style_framework": "tailwind",
  "component_library": "mui",
  "typescript": true,
  "responsive": true,
  "glassmorphism": true,
  "olive_green_theme": true
}
```

**Response:**
```json
{
  "project_id": "my-project",
  "pages": [...],
  "components": [...],
  "styles": {...},
  "total_files": 12,
  "total_lines": 1500,
  "setup_instructions": [...],
  "dependencies": [...],
  "routing_config": "..."
}
```

#### Supported Frameworks
```http
GET /frameworks
```

**Response:**
```json
{
  "style_frameworks": ["tailwind", "styled-components", "css-modules", "emotion"],
  "component_libraries": ["mui", "antd", "chakra"],
  "features": ["typescript", "responsive", "glassmorphism", "olive_green_theme"]
}
```

## Usage Examples

### Basic Usage

```python
import httpx
import json

# Sample Figma design
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
    },
    "name": "My App Design"
}

# Scaffold request
request = {
    "project_id": "my-saas-app",
    "figma_data": figma_design,
    "style_framework": "tailwind",
    "component_library": "mui",
    "typescript": True,
    "glassmorphism": True,
    "olive_green_theme": True
}

# Make API call
response = httpx.post("http://localhost:8085/scaffold", json=request)
result = response.json()

print(f"Generated {len(result['pages'])} pages")
print(f"Total files: {result['total_files']}")
```

### Orchestrator Integration

```python
# Through the orchestrator
from orchestrator.project_orchestrator import ProjectOrchestrator

orchestrator = ProjectOrchestrator()

# Delegate to UIDevAgent
result = orchestrator.invoke(
    "Create a React application from this Figma design",
    agent_name="ui_dev_agent",
    project_id="my-app",
    figma_json=json.dumps(figma_design)
)
```

### CLI Integration

```bash
# Direct CLI usage (when available)
html-to-react input.html --component-name MyComponent --typescript
```

## Generated Code Examples

### React Component
```tsx
import React from 'react';

interface LandingPageProps {
  className?: string;
  children?: React.ReactNode;
}

const LandingPage: React.FC<LandingPageProps> = ({ className = '', children }) => {
  return (
    <div className={`landingpage-container backdrop-blur-lg bg-white/10 border border-white/20 shadow-xl rounded-xl ${className}`}>
      <section className="figma-frame flex-col">
        <h2 className="figma-text">Welcome to AI SaaS Factory</h2>
      </section>
      {children}
    </div>
  );
};

export default LandingPage;
```

### Tailwind Configuration
```js
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        "primary": "#6B7280",
        "secondary": "#84CC16",
        "accent": "#22C55E",
        "background": "#F9FAFB",
        "surface": "#FFFFFF",
        "text": "#374151",
        "textSecondary": "#6B7280"
      },
      backdropBlur: {
        "xs": "2px"
      }
    }
  },
  plugins: []
};
```

### React Router Configuration
```tsx
import React from 'react';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import Dashboard from './pages/Dashboard';

const router = createBrowserRouter([
  { path: '/landing', element: <LandingPage /> },
  { path: '/dashboard', element: <Dashboard /> }
]);

const AppRouter: React.FC = () => {
  return <RouterProvider router={router} />;
};

export default AppRouter;
```

## Figma JSON Structure

### Document Structure
```json
{
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
        "children": [...]
      }
    ]
  },
  "name": "Design System",
  "components": {},
  "styles": {}
}
```

### Supported Node Types
- **FRAME**: Converted to `<section>` or `<div>`
- **TEXT**: Converted to `<p>`, `<h1>`, etc.
- **RECTANGLE**: Converted to `<div>` or `<img>`
- **VECTOR**: Converted to `<svg>`
- **GROUP**: Converted to `<div>`

### Layout Modes
- **VERTICAL**: Adds `flex-col` class
- **HORIZONTAL**: Adds `flex-row` class
- **NONE**: No layout classes

## Styling Features

### Glassmorphism Effects
```css
.glass {
  backdrop-filter: blur(16px);
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
  border-radius: 12px;
}
```

### Olive Green Theme
```css
:root {
  --color-primary: #6B7280;
  --color-secondary: #84CC16;
  --color-accent: #22C55E;
  --color-background: #F9FAFB;
  --color-surface: #FFFFFF;
  --color-text: #374151;
  --color-text-secondary: #6B7280;
}
```

## Component Libraries

### Material-UI Integration
```tsx
import { ThemeProvider, createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    primary: {
      main: '#6B7280',
    },
    secondary: {
      main: '#84CC16',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <YourApp />
    </ThemeProvider>
  );
}
```

### Ant Design Integration
```tsx
import { ConfigProvider } from 'antd';

const theme = {
  token: {
    colorPrimary: '#6B7280',
    colorInfo: '#84CC16',
  },
};

function App() {
  return (
    <ConfigProvider theme={theme}>
      <YourApp />
    </ConfigProvider>
  );
}
```

## Testing

### Running Tests
```bash
# Run all tests
cd agents/ui
python -m pytest test_ui_dev_agent.py -v

# Run specific test categories
python -m pytest test_ui_dev_agent.py::TestFigmaJsonParsing -v
python -m pytest test_ui_dev_agent.py::TestHtmlToReactConversion -v
python -m pytest test_ui_dev_agent.py::TestStylingAndTheming -v
```

### Test Coverage
- **Figma JSON Parsing**: Document parsing, frame extraction, node processing
- **HTML Generation**: Node-to-HTML conversion, layout handling
- **React Scaffolding**: Component generation, TypeScript support
- **Styling**: Glassmorphism, theming, framework integration
- **CLI Integration**: html-to-react tool installation and usage
- **Error Handling**: Invalid input handling, fallback processing

## Deployment

### Production Configuration

```yaml
# docker-compose.yml
version: '3.8'
services:
  ui-dev-agent:
    build: ./agents/ui
    ports:
      - "8085:8085"
    environment:
      - NODE_ENV=production
      - HTML_TO_REACT_CMD=html-to-react
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8085/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Environment Variables
```bash
# Optional CLI tool configuration
HTML_TO_REACT_CMD=html-to-react
NODE_CMD=node
NPM_CMD=npm

# Agent configuration
ENABLE_GLASSMORPHISM=true
ENABLE_OLIVE_THEME=true
DEFAULT_STYLE_FRAMEWORK=tailwind
```

## Performance Optimization

### Caching Strategy
- **Figma Parsing**: Cache parsed documents
- **Component Generation**: Cache generated components
- **CLI Tools**: Cache CLI tool installation

### Scaling Considerations
- **Horizontal Scaling**: Multiple agent instances
- **Load Balancing**: Distribute requests across instances
- **Resource Limits**: CPU and memory limits for large designs

## Troubleshooting

### Common Issues

#### html-to-react CLI Not Found
```bash
# Manual installation
npm install -g html-to-react

# Verify installation
html-to-react --version
```

#### Invalid Figma JSON
```json
{
  "error": "Invalid Figma JSON format",
  "details": "Document structure missing required fields"
}
```

#### Memory Issues with Large Designs
```bash
# Increase Node.js memory limit
export NODE_OPTIONS="--max-old-space-size=4096"
```

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python main.py
```

## Integration Examples

### With Design Agent
```python
# Complete design-to-code workflow
# 1. Generate wireframes with Design Agent
design_result = design_agent.generate_wireframes(
    project_type="web",
    pages=["landing", "dashboard"]
)

# 2. Convert to React with UI Dev Agent
ui_result = ui_dev_agent.scaffold_ui_from_figma(
    project_id="my-app",
    figma_data=design_result['figma_data']
)
```

### With GitHub Integration
```python
# Auto-commit generated code
files = []
for page in result['pages']:
    files.append({
        'path': f"src/pages/{page['filename']}",
        'content': page['content']
    })

github_integration.create_pull_request(
    files=files,
    branch_name="ui-scaffolding",
    commit_message="Add scaffolded React UI components"
)
```

## Future Enhancements

### Planned Features
- **Interactive Preview**: Live preview of generated components
- **Design Tokens**: Export/import design tokens
- **Animation Support**: Convert Figma animations to React animations
- **Responsive Breakpoints**: Generate responsive designs
- **Accessibility**: Auto-generate accessibility attributes

### Extension Points
- **Custom Converters**: Plugin system for custom node converters
- **Template System**: Custom component templates
- **Style Processors**: Custom styling processors
- **Integration Hooks**: Webhook support for external integrations

## Contributing

### Development Setup
```bash
# Clone repository
git clone https://github.com/your-org/seas-factory-infra.git
cd seas-factory-infra/agents/ui

# Install dependencies
pip install -r requirements.txt
npm install -g html-to-react

# Run tests
python -m pytest test_ui_dev_agent.py -v

# Start development server
python main.py
```

### Code Style
- **Python**: Follow PEP 8
- **TypeScript**: Use generated TypeScript style
- **Documentation**: Comprehensive docstrings
- **Testing**: 100% test coverage goal

## License

This project is part of the AI SaaS Factory and is licensed under the MIT License.

## Support

For issues and questions:
- **GitHub Issues**: [Create an issue](https://github.com/your-org/seas-factory-infra/issues)
- **Documentation**: This README and inline documentation
- **Examples**: See `night39_demo.py` for comprehensive examples

---

**Night 39 UIDevAgent** - Transforming Figma designs into production-ready React applications with AI-powered scaffolding and beautiful glassmorphism styling. 