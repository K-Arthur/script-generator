import asyncio
from typing import List, Dict, Optional
from semantic_text_splitter import TextSplitter
import textstat
import yaml
import os
from pathlib import Path

class TextProcessor:
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.text_splitter = TextSplitter(
            chunk_size=6000,
            chunk_overlap=200
        )
        
    def _load_config(self, config_path: Optional[str] = None) -> dict:
        """Load configuration from YAML file."""
        if not config_path:
            config_path = Path(__file__).parent.parent / "config" / "quality_control.yaml"
        
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def chunk_text(self, text: str) -> List[Dict]:
        """Split text into manageable chunks while preserving context."""
        chunks = self.text_splitter.chunks(text)
        return [
            {
                "id": i,
                "content": chunk,
                "summary": "",
                "metrics": self._analyze_chunk(chunk)
            }
            for i, chunk in enumerate(chunks)
        ]
    
    def _analyze_chunk(self, text: str) -> Dict:
        """Analyze text metrics for a chunk."""
        return {
            "flesch_score": textstat.flesch_reading_ease(text),
            "word_count": len(text.split()),
            "sentence_count": textstat.sentence_count(text),
            "avg_sentence_length": len(text.split()) / max(1, textstat.sentence_count(text))
        }
    
    def validate_script(self, script: str) -> Dict:
        """Validate the generated script against quality criteria."""
        metrics = self._analyze_chunk(script)
        validation = self.config["validation"]
        
        return {
            "length": {
                "pass": metrics["word_count"] >= validation["structure"]["min_word_count"],
                "value": metrics["word_count"],
                "threshold": validation["structure"]["min_word_count"]
            },
            "readability": {
                "pass": metrics["flesch_score"] >= validation["readability"]["min_flesch_score"],
                "value": metrics["flesch_score"],
                "threshold": validation["readability"]["min_flesch_score"]
            },
            "sentence_length": {
                "pass": metrics["avg_sentence_length"] <= validation["readability"]["max_sentence_length"],
                "value": metrics["avg_sentence_length"],
                "threshold": validation["readability"]["max_sentence_length"]
            }
        }
    
    def generate_transition(self, prev_chunk: Dict, next_chunk: Dict) -> str:
        """Generate a natural transition between chunks."""
        # Template for transition generation
        transition_template = f"""
        Previous context: {prev_chunk['summary']}
        Next context: {next_chunk['summary']}
        
        Create a natural 2-sentence transition that:
        1. Recalls a key point from the previous section
        2. Introduces the next topic through analogy or contrast
        3. Avoids cliché transitions
        """
        
        # In a real implementation, this would call the AI model
        # For now, return a placeholder
        return "Transition placeholder..."
    
    async def process_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """Process chunks in parallel with proper context management."""
        async def process_single_chunk(chunk: Dict) -> Dict:
            # This would normally call the AI model
            chunk["summary"] = f"Summary of chunk {chunk['id']}"
            return chunk
        
        tasks = [process_single_chunk(chunk) for chunk in chunks]
        processed_chunks = await asyncio.gather(*tasks)
        
        # Add transitions between chunks
        for i in range(len(processed_chunks) - 1):
            transition = self.generate_transition(
                processed_chunks[i],
                processed_chunks[i + 1]
            )
            processed_chunks[i]["transition"] = transition
        
        return processed_chunks
