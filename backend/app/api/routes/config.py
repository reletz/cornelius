"""
Configuration routes - API key validation.
"""
from fastapi import APIRouter
from openai import AsyncOpenAI

from app.schemas.schemas import ValidateKeyRequest, ValidateKeyResponse

router = APIRouter()

# OpenRouter configuration
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
VALIDATION_MODEL = "google/gemma-3n-e2b-it:free"


@router.post("/validate-key", response_model=ValidateKeyResponse)
async def validate_api_key(request: ValidateKeyRequest):
    """
    Validate the user-provided OpenRouter API Key.
    Pings OpenRouter API to verify the key works.
    """
    try:
        client = AsyncOpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=request.api_key,
        )
        
        # Quick validation with free model
        response = await client.chat.completions.create(
            model=VALIDATION_MODEL,
            messages=[{"role": "user", "content": "Say 'OK' if you can read this."}],
            max_tokens=10,
        )
        
        return ValidateKeyResponse(
            valid=True,
            message="API key is valid and working"
        )
        
    except Exception as e:
        return ValidateKeyResponse(
            valid=False,
            message=f"Invalid API key: {str(e)}"
        )
