import os
from typing import List, Dict, Tuple, Optional
import yaml
import textstat
from semantic_text_splitter import TextSplitter

class TextProcessor:
    def __init__(self, templates_path: Optional[str] = None):
        """Initialize the text processor with optional templates path."""
        if templates_path is None:
            templates_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                        "config", "templates.yaml")
        self.templates = self._load_templates(templates_path)
        self.splitter = TextSplitter()

    def _load_templates(self, templates_path: str) -> dict:
        """Load script templates from YAML file."""
        if os.path.exists(templates_path):
            with open(templates_path, 'r') as f:
                return yaml.safe_load(f)
        return {}

    def chunk_text(self, text: str) -> List[str]:
        """Split text into semantic chunks."""
        return self.splitter.split_text(text)

    async def process_chunks(self, chunks: List[str]) -> List[str]:
        """Process text chunks asynchronously."""
        # In a real implementation, this might involve parallel processing
        # For now, we'll just return the chunks as is
        return chunks

    def validate_script(self, script: str, template_name: Optional[str] = None) -> Dict:
        """Validate script against readability metrics and template if provided."""
        validation = {
            'readability': self._check_readability(script),
            'structure': self._check_structure(script),
            'engagement': self._check_engagement(script)
        }

        if template_name and template_name in self.templates:
            validation['template_compliance'] = self._check_template_compliance(
                script, self.templates[template_name]
            )

        return validation

    def _check_readability(self, text: str) -> Dict:
        """Check text readability metrics."""
        return {
            'flesch_score': textstat.flesch_reading_ease(text),
            'grade_level': textstat.coleman_liau_index(text),
            'reading_time': len(text.split()) / 200  # Assuming 200 words per minute
        }

    def _check_structure(self, text: str) -> Dict:
        """Check text structure metrics."""
        paragraphs = [p for p in text.split('\n\n') if p.strip()]
        sentences = textstat.sentence_count(text)
        words = len(text.split())

        return {
            'paragraph_count': len(paragraphs),
            'sentence_count': sentences,
            'word_count': words,
            'avg_paragraph_length': words / len(paragraphs) if paragraphs else 0,
            'avg_sentence_length': words / sentences if sentences else 0
        }

    def _check_engagement(self, text: str) -> Dict:
        """Check text engagement metrics."""
        questions = text.count('?')
        quotes = text.count('"') // 2  # Divide by 2 as quotes come in pairs
        
        # Simple list of transition words
        transition_words = ['however', 'therefore', 'furthermore', 'moreover', 'meanwhile']
        transition_count = sum(text.lower().count(word) for word in transition_words)

        return {
            'question_count': questions,
            'quote_count': quotes,
            'transition_words': transition_count
        }

    def _check_template_compliance(self, text: str, template: Dict) -> Dict:
        """Check if text follows template structure."""
        compliance = {}
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        current_section = None
        section_content = []

        for section in template['sections']:
            section_name = section['name']
            expected_range = section['length_range']
            
            # Simple heuristic: Look for section headers
            section_found = False
            for i, para in enumerate(paragraphs):
                if section_name.lower() in para.lower():
                    section_found = True
                    current_section = section_name
                    section_content = []
                elif current_section == section_name:
                    section_content.append(para)
                
            if section_found:
                section_text = ' '.join(section_content)
                word_count = len(section_text.split())
                compliance[section_name] = {
                    'present': True,
                    'length_in_range': expected_range[0] <= word_count <= expected_range[1],
                    'actual_length': word_count,
                    'expected_range': expected_range
                }
            else:
                compliance[section_name] = {
                    'present': False,
                    'length_in_range': False,
                    'actual_length': 0,
                    'expected_range': expected_range
                }

        return compliance

    def format_script_for_export(self, script: str, format_type: str) -> Tuple[str, str]:
        """Format script for export in various formats."""
        if format_type == 'txt':
            return script, 'text/plain'
        
        elif format_type == 'html':
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Script</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1, h2 {{ color: #333; }}
        p {{ margin-bottom: 1em; }}
    </style>
</head>
<body>
    {script.replace('\n\n', '</p><p>').replace('\n', '<br>')}
</body>
</html>"""
            return html_content, 'text/html'
        
        elif format_type == 'md':
            # Convert paragraphs to markdown format
            md_content = script.replace('\n\n', '\n\n## ')
            if not md_content.startswith('# '):
                md_content = '# ' + md_content
            return md_content, 'text/markdown'
        
        else:
            raise ValueError(f"Unsupported format type: {format_type}")
