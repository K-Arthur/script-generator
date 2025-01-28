import pytest
from unittest.mock import patch, MagicMock
from app.utils.ai_handler import AIHandler

@pytest.fixture
def ai_handler():
    return AIHandler()

@pytest.fixture
def sample_content():
    return """
    Artificial Intelligence (AI) is revolutionizing industries across the globe.
    From healthcare to transportation, AI technologies are creating new
    possibilities and solving complex problems. Machine learning, a subset of AI,
    enables systems to learn and improve from experience.
    """

@pytest.fixture
def sample_validation_results():
    return {
        'readability': {
            'flesch_score': 65.5,
            'grade_level': 10.2,
            'reading_time': 2.5
        },
        'structure': {
            'sentence_count': 15,
            'word_count': 300,
            'paragraph_count': 4
        },
        'template_compliance': {
            'Introduction': {
                'present': True,
                'length_in_range': False,
                'actual_length': 50,
                'expected_range': [60, 100]
            }
        }
    }

@pytest.mark.asyncio
async def test_generate_script_basic(ai_handler, sample_content):
    with patch('openai.ChatCompletion.acreate') as mock_create:
        mock_create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Generated script content"))]
        )
        
        script = await ai_handler.generate_script(
            content=sample_content
        )
        
        assert isinstance(script, str)
        assert len(script) > 0
        mock_create.assert_called_once()

@pytest.mark.asyncio
async def test_generate_script_with_template(ai_handler, sample_content):
    with patch('openai.ChatCompletion.acreate') as mock_create:
        mock_create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Generated script with template"))]
        )
        
        script = await ai_handler.generate_script(
            content=sample_content,
            template_name="documentary"
        )
        
        assert isinstance(script, str)
        assert len(script) > 0
        # Verify template was included in the prompt
        call_args = mock_create.call_args[1]
        assert any("documentary" in str(msg).lower() for msg in call_args['messages'])

@pytest.mark.asyncio
async def test_generate_script_with_context(ai_handler, sample_content):
    with patch('openai.ChatCompletion.acreate') as mock_create:
        mock_create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Generated script with context"))]
        )
        
        script = await ai_handler.generate_script(
            content=sample_content,
            highlighted_concept="machine learning",
            previous_topic="computer science basics"
        )
        
        assert isinstance(script, str)
        assert len(script) > 0
        # Verify context was included in the prompt
        call_args = mock_create.call_args[1]
        assert any("machine learning" in str(msg).lower() for msg in call_args['messages'])
        assert any("computer science basics" in str(msg).lower() for msg in call_args['messages'])

@pytest.mark.asyncio
async def test_improve_script(ai_handler, sample_validation_results):
    original_script = "Original script content that needs improvement"
    
    with patch('openai.ChatCompletion.acreate') as mock_create:
        mock_create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Improved script content"))]
        )
        
        improved_script = await ai_handler.improve_script(
            original_script,
            sample_validation_results
        )
        
        assert isinstance(improved_script, str)
        assert len(improved_script) > 0
        assert improved_script != original_script
        
        # Verify validation results were included in the improvement prompt
        call_args = mock_create.call_args[1]
        messages = [str(msg).lower() for msg in call_args['messages']]
        assert any("readability" in msg for msg in messages)
        assert any("structure" in msg for msg in messages)
        assert any("template" in msg for msg in messages)

@pytest.mark.asyncio
async def test_error_handling(ai_handler, sample_content):
    with patch('openai.ChatCompletion.acreate') as mock_create:
        mock_create.side_effect = Exception("API Error")
        
        with pytest.raises(Exception):
            await ai_handler.generate_script(content=sample_content)

def test_initialization():
    handler = AIHandler()
    assert handler is not None
    # Add more specific initialization tests based on your implementation
