"""
Note generation service - Cornell notes using OpenRouter LLM.
"""
import logging
from pathlib import Path
from typing import Optional
from openai import AsyncOpenAI

from app.services.note_formatter import note_formatter_service

logger = logging.getLogger(__name__)

# OpenRouter configuration
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
NOTE_GENERATION_MODEL = "tngtech/deepseek-r1t2-chimera:free"

# Load prompt from markdown file
_prompt_path = Path(__file__).parent.parent / "prompt" / "note-gen.md"
CORNELL_MASTER_PROMPT = _prompt_path.read_text(encoding="utf-8")


class NoteGenerationService:
    """Handles Cornell note generation using OpenRouter LLM."""
    
    async def generate_note(
        self,
        topic_title: str,
        source_content: str,
        api_key: str,
        model_name: str = NOTE_GENERATION_MODEL
    ) -> str:
        """
        Generate Cornell notes for a topic.
        
        Args:
            topic_title: Title of the topic/cluster
            source_content: Extracted text content
            api_key: OpenRouter API key
            model_name: Which model to use
            
        Returns:
            Generated markdown content
        """
        # Configure OpenRouter client
        client = AsyncOpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=api_key,
        )
        
        # Prepare prompt - append topic and source to prompt template
        prompt = f"""{CORNELL_MASTER_PROMPT}

---

## Generate Notes for This Topic

**Topic Title:** {topic_title}

**Source Materials:**

{source_content[:30000]}
"""
        
        try:
            response = await client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=8192,
            )
            
            raw_content = response.choices[0].message.content
            cleaned = self._clean_response(raw_content)
            
            # Post-process to fix formatting issues
            formatted = note_formatter_service.format_note(cleaned)
            
            # Log validation results
            is_valid, issues = note_formatter_service.validate_format(formatted)
            if not is_valid:
                logger.warning(f"Format issues in '{topic_title}': {issues}")
            
            return formatted
            
        except Exception as e:
            logger.error(f"Note generation failed for '{topic_title}': {e}")
            raise
    
    def _clean_response(self, text: str) -> str:
        """Clean up generated markdown."""
        # Remove any wrapping code blocks if present
        text = text.strip()
        if text.startswith("```markdown"):
            text = text[11:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()


# Singleton instance
note_generation_service = NoteGenerationService()
