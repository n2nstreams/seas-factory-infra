import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from main import app, CopyWriterAgent, CopyType, ToneOfVoice, CopyRequest, GeneratedCopy

# Test client
client = TestClient(app)

@pytest.fixture
def sample_copy_request():
    """Sample copy request for testing"""
    return {
        "copy_type": "hero_section",
        "product_name": "TaskFlow Pro",
        "product_description": "AI-powered project management for remote teams",
        "target_audience": "Remote team managers and productivity enthusiasts",
        "key_features": ["AI task prioritization", "Real-time collaboration", "Advanced analytics"],
        "tone": "professional",
        "company_values": "We believe in empowering teams to work smarter, not harder",
        "competitor_analysis": "Unlike traditional PM tools, we focus on AI-driven insights"
    }

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = """
**Transform Your Team's Productivity with AI-Powered Project Management**

Stop struggling with scattered tasks and missed deadlines. TaskFlow Pro uses advanced AI to prioritize your work, predict bottlenecks, and keep your remote team perfectly synchronized.

*Start your free trial today →*
    """.strip()
    return mock_response

@pytest.fixture
def mock_openai_alternatives_response():
    """Mock OpenAI API response for alternatives"""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = """
**Alternative 1:**
Unlock Your Team's Potential with Intelligent Project Management
Experience the future of remote team collaboration with AI that thinks ahead.

---

**Alternative 2:**
Finally, Project Management That Actually Makes Sense
Let AI handle the complexity while your team focuses on what matters most.
    """.strip()
    return mock_response

class TestCopyWriterAgent:
    """Test cases for the CopyWriterAgent class"""
    
    def test_init(self):
        """Test CopyWriterAgent initialization"""
        agent = CopyWriterAgent()
        assert agent.model == "gpt-4o"
    
    def test_get_system_prompt_hero_section(self):
        """Test system prompt generation for hero section"""
        agent = CopyWriterAgent()
        prompt = agent._get_system_prompt(CopyType.HERO_SECTION, ToneOfVoice.PROFESSIONAL)
        
        assert "world-class copywriter" in prompt
        assert "professional tone" in prompt
        assert "hero sections" in prompt
        assert "value proposition" in prompt
    
    def test_get_system_prompt_features(self):
        """Test system prompt generation for features section"""
        agent = CopyWriterAgent()
        prompt = agent._get_system_prompt(CopyType.FEATURES, ToneOfVoice.STARTUP)
        
        assert "startup tone" in prompt
        assert "features sections" in prompt
        assert "benefits over features" in prompt
    
    def test_build_copy_prompt_basic(self):
        """Test basic copy prompt building"""
        agent = CopyWriterAgent()
        request = CopyRequest(
            copy_type=CopyType.HERO_SECTION,
            product_name="TestApp",
            product_description="A test application",
            target_audience="Test users",
            key_features=["Feature 1", "Feature 2"],
            tone=ToneOfVoice.PROFESSIONAL
        )
        
        prompt = agent._build_copy_prompt(request)
        
        assert "TestApp" in prompt
        assert "A test application" in prompt
        assert "Test users" in prompt
        assert "Feature 1, Feature 2" in prompt
        assert "professional" in prompt
        assert "headline, subheadline, and primary CTA" in prompt
    
    def test_build_copy_prompt_with_optional_fields(self):
        """Test copy prompt building with optional fields"""
        agent = CopyWriterAgent()
        request = CopyRequest(
            copy_type=CopyType.PRICING,
            product_name="TestApp",
            product_description="A test application",
            target_audience="Test users",
            key_features=["Feature 1"],
            tone=ToneOfVoice.CONVERSATIONAL,
            company_values="We value innovation",
            competitor_analysis="Better than competitors",
            pricing_tiers=[{"name": "Basic", "price": "$10"}]
        )
        
        prompt = agent._build_copy_prompt(request)
        
        assert "We value innovation" in prompt
        assert "Better than competitors" in prompt
        assert '"Basic"' in prompt
        assert '"$10"' in prompt
    
    @pytest.mark.asyncio
    @patch('main.openai_client')
    async def test_generate_copy_success(self, mock_client, sample_copy_request, mock_openai_response, mock_openai_alternatives_response):
        """Test successful copy generation"""
        # Setup mocks
        mock_client.chat.completions.create = AsyncMock()
        mock_client.chat.completions.create.side_effect = [mock_openai_response, mock_openai_alternatives_response]
        
        agent = CopyWriterAgent()
        agent.client = mock_client
        
        request = CopyRequest(**sample_copy_request)
        result = await agent.generate_copy(request)
        
        assert isinstance(result, GeneratedCopy)
        assert result.copy_type == CopyType.HERO_SECTION
        assert "Transform Your Team's Productivity" in result.content
        assert len(result.alternatives) == 2
        assert "Alternative 1" in result.alternatives[0]
        assert result.metadata["product_name"] == "TaskFlow Pro"
        assert result.metadata["tone"] == "professional"
    
    @pytest.mark.asyncio
    @patch('main.openai_client')
    async def test_generate_copy_openai_error(self, mock_client, sample_copy_request):
        """Test copy generation with OpenAI API error"""
        mock_client.chat.completions.create = AsyncMock(side_effect=Exception("API Error"))
        
        agent = CopyWriterAgent()
        agent.client = mock_client
        
        request = CopyRequest(**sample_copy_request)
        
        with pytest.raises(Exception) as exc_info:
            await agent.generate_copy(request)
        
        assert "Copy generation failed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_generate_copy_no_client(self, sample_copy_request):
        """Test copy generation without OpenAI client"""
        agent = CopyWriterAgent()
        agent.client = None
        
        request = CopyRequest(**sample_copy_request)
        
        with pytest.raises(Exception) as exc_info:
            await agent.generate_copy(request)
        
        assert "OpenAI API key not configured" in str(exc_info.value)
    
    @pytest.mark.asyncio
    @patch('main.openai_client')
    async def test_generate_full_landing_page(self, mock_client, sample_copy_request, mock_openai_response, mock_openai_alternatives_response):
        """Test full landing page generation"""
        # Setup mocks - need to handle multiple calls
        mock_client.chat.completions.create = AsyncMock()
        mock_client.chat.completions.create.side_effect = [mock_openai_response, mock_openai_alternatives_response] * 7  # 7 sections
        
        agent = CopyWriterAgent()
        agent.client = mock_client
        
        request = CopyRequest(**sample_copy_request)
        result = await agent.generate_full_landing_page(request)
        
        # Check all sections are present
        assert result.hero_section.copy_type == CopyType.HERO_SECTION
        assert result.features.copy_type == CopyType.FEATURES
        assert result.pricing.copy_type == CopyType.PRICING
        assert result.testimonials.copy_type == CopyType.TESTIMONIALS
        assert result.faq.copy_type == CopyType.FAQ
        assert result.cta.copy_type == CopyType.CTA
        assert result.about.copy_type == CopyType.ABOUT
        
        # Verify API was called correct number of times (2 calls per section)
        assert mock_client.chat.completions.create.call_count == 14

class TestCopyWriterAPI:
    """Test cases for the CopyWriter API endpoints"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "copywriter_enabled" in data
    
    def test_copy_templates_endpoint(self):
        """Test copy templates endpoint"""
        response = client.get("/copy-templates")
        assert response.status_code == 200
        data = response.json()
        
        assert "copy_types" in data
        assert "tones" in data
        assert "example_request" in data
        
        # Verify all copy types are included
        assert "hero_section" in data["copy_types"]
        assert "features" in data["copy_types"]
        assert "pricing" in data["copy_types"]
        
        # Verify all tones are included
        assert "professional" in data["tones"]
        assert "conversational" in data["tones"]
        assert "startup" in data["tones"]
    
    @patch('main.copywriter.generate_copy')
    def test_generate_copy_endpoint(self, mock_generate, sample_copy_request):
        """Test generate copy endpoint"""
        # Mock the response
        mock_result = GeneratedCopy(
            copy_type=CopyType.HERO_SECTION,
            content="Sample generated copy",
            alternatives=["Alt 1", "Alt 2"],
            metadata={"test": "data"}
        )
        mock_generate.return_value = mock_result
        
        response = client.post("/generate-copy", json=sample_copy_request)
        assert response.status_code == 200
        
        data = response.json()
        assert data["copy_type"] == "hero_section"
        assert data["content"] == "Sample generated copy"
        assert len(data["alternatives"]) == 2
    
    def test_generate_copy_endpoint_invalid_data(self):
        """Test generate copy endpoint with invalid data"""
        invalid_request = {
            "copy_type": "invalid_type",
            "product_name": "Test",
            "product_description": "Test desc",
            "target_audience": "Test audience"
        }
        
        response = client.post("/generate-copy", json=invalid_request)
        assert response.status_code == 422  # Validation error
    
    @patch('main.copywriter.generate_full_landing_page')
    def test_generate_landing_page_endpoint(self, mock_generate, sample_copy_request):
        """Test generate landing page endpoint"""
        # Create mock sections
        mock_section = GeneratedCopy(
            copy_type=CopyType.HERO_SECTION,
            content="Sample content",
            alternatives=["Alt 1"],
            metadata={}
        )
        
        mock_result = MagicMock()
        mock_result.hero_section = mock_section
        mock_result.features = mock_section
        mock_result.pricing = mock_section
        mock_result.testimonials = mock_section
        mock_result.faq = mock_section
        mock_result.cta = mock_section
        mock_result.about = mock_section
        
        # Configure dict access for JSON serialization
        mock_result.__dict__ = {
            "hero_section": mock_section.__dict__,
            "features": mock_section.__dict__,
            "pricing": mock_section.__dict__,
            "testimonials": mock_section.__dict__,
            "faq": mock_section.__dict__,
            "cta": mock_section.__dict__,
            "about": mock_section.__dict__
        }
        
        mock_generate.return_value = mock_result
        
        response = client.post("/generate-landing-page", json=sample_copy_request)
        assert response.status_code == 200
        
        # The endpoint should return the full landing page structure
        data = response.json()
        assert "hero_section" in data
        assert "features" in data
        assert "pricing" in data

class TestEmailDripIntegration:
    """Test cases for existing email drip functionality"""
    
    def test_trigger_drip_endpoint_no_sendgrid_key(self):
        """Test email drip endpoint without SendGrid key"""
        with patch.dict('os.environ', {}, clear=True):
            response = client.post("/trigger-drip")
            assert response.status_code == 500
            assert "SENDGRID_API_KEY not configured" in response.json()["detail"]
    
    @patch('main.SendGridAPIClient')
    def test_trigger_drip_endpoint_success(self, mock_sendgrid):
        """Test successful email drip trigger"""
        # Mock SendGrid client
        mock_sg_instance = MagicMock()
        mock_sg_instance.send.return_value = MagicMock(status_code=202)
        mock_sendgrid.return_value = mock_sg_instance
        
        with patch.dict('os.environ', {'SENDGRID_API_KEY': 'test_key'}):
            response = client.post("/trigger-drip")
            assert response.status_code == 200
            assert "success" in response.json()["status"]

class TestDataModels:
    """Test cases for Pydantic data models"""
    
    def test_copy_request_model_valid(self):
        """Test CopyRequest model with valid data"""
        data = {
            "copy_type": "hero_section",
            "product_name": "TestApp",
            "product_description": "A test app",
            "target_audience": "Test users",
            "key_features": ["Feature 1", "Feature 2"],
            "tone": "professional"
        }
        
        request = CopyRequest(**data)
        assert request.copy_type == CopyType.HERO_SECTION
        assert request.product_name == "TestApp"
        assert request.tone == ToneOfVoice.PROFESSIONAL
        assert len(request.key_features) == 2
    
    def test_copy_request_model_defaults(self):
        """Test CopyRequest model with default values"""
        data = {
            "copy_type": "features",
            "product_name": "TestApp",
            "product_description": "A test app",
            "target_audience": "Test users"
        }
        
        request = CopyRequest(**data)
        assert request.key_features == []
        assert request.tone == ToneOfVoice.PROFESSIONAL
        assert request.pricing_tiers is None
        assert request.company_values == ""
    
    def test_generated_copy_model(self):
        """Test GeneratedCopy model"""
        data = {
            "copy_type": "hero_section",
            "content": "Test content",
            "alternatives": ["Alt 1", "Alt 2"],
            "metadata": {"key": "value"}
        }
        
        copy = GeneratedCopy(**data)
        assert copy.copy_type == CopyType.HERO_SECTION
        assert copy.content == "Test content"
        assert len(copy.alternatives) == 2
        assert copy.metadata["key"] == "value"

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 