import pytest
import os
from pathlib import Path
from app.utils.text_processor import TextProcessor

@pytest.fixture
def text_processor():
    return TextProcessor()

@pytest.fixture
def sample_text():
    return """
    This is a sample text for testing. It contains multiple sentences and paragraphs.
    We need to ensure that our text processor can handle various cases properly.

    This is a second paragraph. It adds more content for testing purposes.
    We want to make sure that paragraph detection works correctly.
    
    Finally, this is the last paragraph. It helps us verify that our metrics
    are calculated accurately across multiple paragraphs of text.
    """

@pytest.fixture
def sample_script():
    return """
    The Rise of Artificial Intelligence

    In recent years, artificial intelligence has transformed from science fiction
    into everyday reality. From virtual assistants to autonomous vehicles,
    AI technologies are reshaping how we live and work.

    One of the most significant developments is machine learning, which enables
    computers to learn from experience without explicit programming. This
    breakthrough has led to remarkable advances in image recognition, natural
    language processing, and decision-making systems.

    However, these advancements raise important questions about ethics and
    responsibility. How do we ensure AI systems make fair decisions? What
    safeguards should we put in place?

    As we look to the future, one thing is clear: AI will continue to evolve
    and influence our world in profound ways. The challenge lies in harnessing
    its potential while addressing the concerns it raises.
    """

def test_chunk_text(text_processor, sample_text):
    chunks = text_processor.chunk_text(sample_text)
    assert len(chunks) > 0
    assert isinstance(chunks[0], str)
    assert sum(len(chunk.split()) for chunk in chunks) >= len(sample_text.split())

def test_validate_script_basic(text_processor, sample_script):
    validation = text_processor.validate_script(sample_script)
    
    # Check if all expected metrics are present
    assert 'readability' in validation
    assert 'structure' in validation
    assert 'engagement' in validation
    
    # Check readability metrics
    assert 'flesch_score' in validation['readability']
    assert 'grade_level' in validation['readability']
    assert 'reading_time' in validation['readability']
    
    # Check structure metrics
    assert validation['structure']['word_count'] > 0
    assert validation['structure']['sentence_count'] > 0
    assert validation['structure']['paragraph_count'] > 0
    
    # Check engagement metrics
    assert 'question_count' in validation['engagement']
    assert 'quote_count' in validation['engagement']
    assert 'transition_words' in validation['engagement']

def test_validate_script_with_template(text_processor, sample_script):
    validation = text_processor.validate_script(sample_script, template_name='documentary')
    
    # Check template compliance
    assert 'template_compliance' in validation
    template_results = validation['template_compliance']
    
    # Verify template sections
    assert any('Introduction' in section for section in template_results.keys())
    assert any('Main Content' in section for section in template_results.keys())
    assert any('Conclusion' in section for section in template_results.keys())

def test_format_script_export(text_processor, sample_script):
    # Test TXT export
    txt_content, txt_type = text_processor.format_script_for_export(sample_script, 'txt')
    assert txt_type == 'text/plain'
    assert isinstance(txt_content, str)
    assert len(txt_content) > 0
    
    # Test HTML export
    html_content, html_type = text_processor.format_script_for_export(sample_script, 'html')
    assert html_type == 'text/html'
    assert '<!DOCTYPE html>' in html_content
    assert '<body>' in html_content
    assert '</body>' in html_content
    
    # Test Markdown export
    md_content, md_type = text_processor.format_script_for_export(sample_script, 'md')
    assert md_type == 'text/markdown'
    assert '#' in md_content  # Should have at least one heading

def test_invalid_export_format(text_processor, sample_script):
    with pytest.raises(ValueError):
        text_processor.format_script_for_export(sample_script, 'invalid_format')

@pytest.mark.asyncio
async def test_process_chunks(text_processor, sample_text):
    chunks = text_processor.chunk_text(sample_text)
    processed_chunks = await text_processor.process_chunks(chunks)
    
    assert len(processed_chunks) == len(chunks)
    assert all(isinstance(chunk, str) for chunk in processed_chunks)
    assert all(len(chunk) > 0 for chunk in processed_chunks)
