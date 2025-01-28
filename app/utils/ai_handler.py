import os
from typing import Optional, Dict
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AIHandler:
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.model = "gpt-4"
    
    async def generate_script(
        self,
        content: str,
        template_name: Optional[str] = None,
        highlighted_concept: Optional[str] = None,
        previous_topic: Optional[str] = None
    ) -> str:
        """Generate a script from the provided content using optional template and context."""
        try:
            # Build the system message
            system_message = """You are an expert script writer for YouTube documentaries.
            Your task is to transform the provided content into an engaging, well-structured script
            that maintains accuracy while being accessible and entertaining."""
            
            # Build the user message
            user_message = f"Content to transform:\n\n{content}\n\n"
            
            if template_name:
                user_message += f"\nPlease follow the {template_name} style template structure."
            
            if highlighted_concept:
                user_message += f"\nEmphasize this key concept: {highlighted_concept}"
            
            if previous_topic:
                user_message += f"\nThis follows a previous video about: {previous_topic}"
            
            # Call the OpenAI API
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"Error generating script: {str(e)}")
    
    async def improve_script(self, script: str, validation_results: Dict) -> str:
        """Improve the script based on validation results."""
        try:
            # Build the improvement prompt
            system_message = """You are an expert script editor.
            Your task is to improve the script based on the validation results while
            maintaining its core message and style."""
            
            user_message = f"""Please improve this script based on the following validation results:

            Script:
            {script}

            Validation Results:
            {validation_results}

            Please address all issues while maintaining the script's core message and engagement level.
            Return only the improved script without any explanations."""
            
            # Call the OpenAI API
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"Error improving script: {str(e)}")
