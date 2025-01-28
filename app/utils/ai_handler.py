import os
from typing import List, Dict, Optional
import yaml
import openai
from pathlib import Path

class AIHandler:
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.openai_client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    def _load_config(self, config_path: Optional[str] = None) -> dict:
        """Load AI configuration from YAML file."""
        if not config_path:
            config_path = Path(__file__).parent.parent / "config" / "llm.yaml"
        
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    async def generate_script(self, 
                            content: str, 
                            highlighted_concept: Optional[str] = None,
                            previous_topic: Optional[str] = None) -> str:
        """Generate a script from the given content."""
        system_prompt = self.config["system_prompts"]["scriptwriter"]
        
        user_prompt = f"""{content}

Transform this into a {self.config['validation']['min_word_count']}+ word narrator script.
"""
        
        if highlighted_concept:
            user_prompt += f"\nParticularly develop the {highlighted_concept} section using the 'False Simplicity' technique - explain complex mechanics through everyday analogies."
            
        if previous_topic:
            user_prompt += f"\nInclude one subtle callback to {previous_topic} in the conclusion."
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=self.config["models"]["default"],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.config["parameters"]["temperature"],
                max_tokens=self.config["parameters"]["max_tokens"],
                top_p=self.config["parameters"]["top_p"]
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error generating script: {str(e)}")
            # Fallback to simpler model if available
            if "fallback" in self.config["models"]:
                try:
                    response = await self.openai_client.chat.completions.create(
                        model=self.config["models"]["fallback"],
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=self.config["parameters"]["temperature"],
                        max_tokens=self.config["parameters"]["max_tokens"],
                        top_p=self.config["parameters"]["top_p"]
                    )
                    return response.choices[0].message.content
                except:
                    raise
            raise
    
    async def improve_script(self, script: str, validation_results: Dict) -> str:
        """Improve script based on validation results."""
        improvement_prompt = f"""
        Original script:
        {script}
        
        The script needs improvement in the following areas:
        """
        
        for metric, result in validation_results.items():
            if not result["pass"]:
                improvement_prompt += f"\n- {metric}: Current {result['value']}, Target {result['threshold']}"
        
        improvement_prompt += "\n\nPlease improve the script while maintaining its core message and style."
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=self.config["models"]["default"],
                messages=[
                    {"role": "system", "content": self.config["system_prompts"]["scriptwriter"]},
                    {"role": "user", "content": improvement_prompt}
                ],
                temperature=0.7,
                max_tokens=self.config["parameters"]["max_tokens"]
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error improving script: {str(e)}")
            raise
    
    async def generate_chunk_summary(self, chunk_content: str) -> str:
        """Generate a concise summary of a chunk."""
        prompt = f"""Create a 3-sentence summary of the following text, focusing on key concepts and narrative flow:

{chunk_content}"""
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=self.config["models"]["default"],
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=200
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error generating chunk summary: {str(e)}")
            raise
