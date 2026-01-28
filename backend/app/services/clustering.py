"""
Clustering service - Topic detection and organization using OpenRouter LLM.
"""
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

# OpenRouter configuration
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
CLUSTERING_MODEL = "tngtech/deepseek-r1t2-chimera:free"

# Load prompt from markdown file
_prompt_path = Path(__file__).parent.parent / "prompt" / "clustering.md"
CLUSTERING_PROMPT = _prompt_path.read_text(encoding="utf-8")


class ClusteringService:
    """Handles topic clustering using OpenRouter LLM."""
    
    async def analyze_and_cluster(
        self, 
        texts: List[Dict[str, str]], 
        api_key: str
    ) -> Dict[str, Any]:
        """
        Analyze extracted texts and create topic clusters.
        
        Args:
            texts: List of dicts with 'filename' and 'content' keys
            api_key: OpenRouter API key
            
        Returns:
            Clustering result with identified topics
        """
        # Configure OpenRouter client
        client = AsyncOpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=api_key,
        )
        
        # Combine texts with source markers
        combined_text = self._prepare_text(texts)
        
        # Generate clustering - append input to prompt template
        prompt = f"{CLUSTERING_PROMPT}\n\n## Input Materials\n\n{combined_text[:50000]}"
        
        try:
            response = await client.chat.completions.create(
                model=CLUSTERING_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=4096,
            )
            
            # Parse JSON response
            result = self._parse_response(response.choices[0].message.content)
            return result
            
        except Exception as e:
            logger.error(f"Clustering failed: {e}")
            raise
    
    def _prepare_text(self, texts: List[Dict[str, str]]) -> str:
        """Prepare combined text with source markers."""
        parts = []
        for item in texts:
            parts.append(f"\n=== SOURCE: {item['filename']} ===\n")
            parts.append(item['content'])
        return "\n".join(parts)
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse and validate Gemini response."""
        # Clean up response - extract JSON
        text = response_text.strip()
        
        # Find JSON block
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            text = text[start:end]
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            text = text[start:end]
        
        try:
            result = json.loads(text)
            
            # Validate structure
            if "clusters" not in result:
                raise ValueError("Missing 'clusters' in response")
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse clustering response: {e}")
            # Return fallback structure
            return {
                "clusters": [{
                    "id": "cluster_1",
                    "title": "All Content",
                    "keywords": [],
                    "source_mapping": [],
                    "estimated_word_count": 0,
                    "summary": "Could not automatically cluster content"
                }],
                "total_clusters": 1,
                "processing_notes": "Fallback due to parsing error"
            }


# Singleton instance
clustering_service = ClusteringService()
