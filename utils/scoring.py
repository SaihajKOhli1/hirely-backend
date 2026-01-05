"""
LLM-based resume scoring utility using Ollama or Groq.
Note: Environment variables are loaded in app.py before this module is imported.
"""
import os
import json
from typing import Dict, Any
import httpx

# LLM Provider configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")

# Ollama configuration
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")

# Groq configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

PROMPT_VERSION = "1.0"


async def ollama_generate(prompt: str) -> str:
    """
    Send a request to Ollama API to generate text.
    
    Args:
        prompt: The prompt text to send to the model
        
    Returns:
        str: Raw text response from Ollama
        
    Raises:
        ValueError: If required env vars are missing or API request fails
    """
    if not OLLAMA_BASE_URL:
        raise ValueError("OLLAMA_BASE_URL environment variable is not set")
    if not OLLAMA_MODEL:
        raise ValueError("OLLAMA_MODEL environment variable is not set")
    
    # Check if using local Ollama (no API key required)
    is_local_ollama = OLLAMA_BASE_URL.startswith("http://localhost") or OLLAMA_BASE_URL.startswith("http://127.0.0.1")
    
    # API key is only required for cloud instances
    if not is_local_ollama:
        if not OLLAMA_API_KEY:
            raise ValueError("OLLAMA_API_KEY environment variable is required for cloud Ollama instances")
    
    # Ensure base URL doesn't end with trailing slash for clean endpoint construction
    base_url = OLLAMA_BASE_URL.rstrip('/')
    url = f"{base_url}/api/generate"
    
    # Build headers - only include Authorization for cloud instances
    headers = {
        "Content-Type": "application/json"
    }
    if not is_local_ollama and OLLAMA_API_KEY:
        headers["Authorization"] = f"Bearer {OLLAMA_API_KEY}"
    
    # Always build enhanced_prompt and payload (works for both local and cloud)
    enhanced_prompt = "You must return raw JSON only. Do not use markdown, backticks, or commentary.\n\n" + prompt
    
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": enhanced_prompt,
        "stream": False,
        "options": {
            "temperature": 0,
            "num_predict": 300
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(240.0)) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            
            # Ollama /api/generate returns {"response": "..."} format
            if "response" in result:
                # Sanitize the response
                cleaned = result["response"].strip()
                # Remove triple backticks if present
                if cleaned.startswith("```") and cleaned.endswith("```"):
                    cleaned = cleaned[3:-3].strip()
                # Remove single backtick if present
                elif cleaned.startswith("`") and cleaned.endswith("`"):
                    cleaned = cleaned[1:-1].strip()
                # Final strip
                cleaned = cleaned.strip()
                return cleaned
            else:
                # Fallback: if response format is different, try to get text
                raise ValueError(f"Unexpected Ollama response format: {result}")
                
    except httpx.HTTPStatusError as e:
        raise ValueError(f"Ollama API HTTP error: {e.response.status_code} - {e.response.text}")
    except httpx.TimeoutException:
        raise ValueError("Ollama API request timed out after 240 seconds")
    except Exception as e:
        raise ValueError(f"Ollama API error: {str(e)}")


async def groq_generate(prompt: str) -> str:
    """
    Send a request to Groq API to generate text.
    
    Args:
        prompt: The prompt text to send to the model
        
    Returns:
        str: Raw text response from Groq
        
    Raises:
        ValueError: If required env vars are missing or API request fails
    """
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY environment variable is not set")
    if not GROQ_MODEL:
        raise ValueError("GROQ_MODEL environment variable is not set")
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "Return raw JSON only. No markdown, no backticks, no commentary."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0,
        "max_tokens": 600
    }
    
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(240.0)) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            
            # Groq returns OpenAI-compatible format: {"choices": [{"message": {"content": "..."}}]}
            # Defensive parsing with .get()
            choices = result.get("choices", [])
            if choices and len(choices) > 0:
                message = choices[0].get("message", {})
                content = message.get("content", "")
                if not content:
                    raise ValueError(f"Groq response missing content. Full result: {result}")
                # Sanitize the response (same as ollama_generate)
                cleaned = content.strip()
                # Remove triple backticks if present
                if cleaned.startswith("```") and cleaned.endswith("```"):
                    cleaned = cleaned[3:-3].strip()
                # Remove single backtick if present
                elif cleaned.startswith("`") and cleaned.endswith("`"):
                    cleaned = cleaned[1:-1].strip()
                # Final strip
                cleaned = cleaned.strip()
                return cleaned
            else:
                raise ValueError(f"Unexpected Groq response format: {result}")
                
    except httpx.HTTPStatusError as e:
        raise ValueError(f"Groq API HTTP error: {e.response.status_code} - {e.response.text}")
    except httpx.TimeoutException:
        raise ValueError("Groq API request timed out after 240 seconds")
    except Exception as e:
        raise ValueError(f"Groq API error: {str(e)}")


async def llm_generate(prompt: str) -> str:
    """
    Route LLM generation request to the appropriate provider.
    
    Args:
        prompt: The prompt text to send to the model
        
    Returns:
        str: Raw text response from the LLM
        
    Raises:
        ValueError: If provider is invalid or API request fails
    """
    if LLM_PROVIDER == "groq":
        return await groq_generate(prompt)
    else:
        return await ollama_generate(prompt)


def build_scoring_prompt(resume_text: str, company: str, role: str) -> str:
    """
    Build a prompt-engineered rubric for resume scoring.
    
    Args:
        resume_text: The resume text content
        company: Company name for context
        role: Target role/job title
        
    Returns:
        str: Complete prompt for the LLM
    """
    prompt = f"""You are an expert resume reviewer and recruiter. Analyze the following resume for a {role} position at {company}.

Return compact JSON only.
Use short strings; no paragraphs.
Limit each list to max 5 items.
If unsure, return best guess but keep JSON valid.

Resume Text:
---
{resume_text}
---

Provide a comprehensive analysis and scoring. Output MUST be valid JSON matching this exact schema (no markdown, no code blocks, just raw JSON):

{{
  "overall_score": <0-100 integer>,
  "metrics": {{
    "clarity": <0-100 integer>,
    "impact": <0-100 integer>,
    "professionalism": <0-100 integer>,
    "role_fit": <0-100 integer>,
    "ats": <0-100 integer>
  }},
  "missing_keywords": [<array of strings>],
  "strengths": [<array of strings, 3-5 items>],
  "top_fixes": [<array of strings, 3-5 items>],
  "section_feedback": [
    {{
      "section": "<Experience|Projects|Skills|Education|Summary|Other>",
      "score": <0-100 integer>,
      "feedback": [<array of strings>],
      "rewrites": [
        {{
          "original": "<exact text from resume>",
          "improved": "<improved version with metrics>"
        }}
      ]
    }}
  ],
  "notes": "<brief summary string, max 200 chars>"
}}

Scoring Guidelines:
- overall_score: Weighted average considering all factors, emphasis on role_fit
- clarity: How clear and easy to understand (formatting, structure, readability)
- impact: Use of metrics, quantifiable achievements, strong action verbs
- professionalism: Appropriate tone, grammar, consistency, no errors
- role_fit: Alignment with {role} requirements and {company} culture
- ats: ATS-friendly formatting, keyword usage, parseability

Requirements:
- All scores must be integers 0-100
- missing_keywords: 5-10 relevant technical/keywords missing for this role
- strengths: 3-5 specific strengths
- top_fixes: 3-5 highest-impact improvements
- section_feedback: Analyze 3-6 major sections (Experience, Projects, Skills, Education, Summary, etc.)
- rewrites: Include 2-4 example bullet rewrites per section with quantifiable improvements
- notes: Brief executive summary

Return ONLY valid JSON, no other text."""
    
    return prompt


async def score_resume_with_llm(resume_text: str, company: str, role: str) -> Dict[str, Any]:
    """
    Call LLM API to score a resume.
    
    Args:
        resume_text: The resume text content
        company: Company name
        role: Target role/job title
        
    Returns:
        Dict: Validated scoring result matching the schema
        
    Raises:
        ValueError: If JSON is invalid after retry or API key missing
        Exception: For API errors
    """
    prompt = build_scoring_prompt(resume_text, company, role)
    
    try:
        # First attempt
        content = await llm_generate(prompt)
        content = content.strip()
        
        # Remove markdown code blocks if present
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        try:
            result = json.loads(content)
            validated_result = validate_scoring_result(result)
            return validated_result
        except json.JSONDecodeError as e:
            # Retry with fix prompt
            print(f"First attempt JSON parse failed: {e}. Raw content: {content[:500]}")
            
            fix_prompt = f"""The previous JSON output was invalid. Fix it to be valid JSON matching this exact schema:

{{
  "overall_score": <0-100 integer>,
  "metrics": {{
    "clarity": <0-100 integer>,
    "impact": <0-100 integer>,
    "professionalism": <0-100 integer>,
    "role_fit": <0-100 integer>,
    "ats": <0-100 integer>
  }},
  "missing_keywords": [<array of strings>],
  "strengths": [<array of strings>],
  "top_fixes": [<array of strings>],
  "section_feedback": [
    {{
      "section": "<Experience|Projects|Skills|Education|Summary|Other>",
      "score": <0-100 integer>,
      "feedback": [<array of strings>],
      "rewrites": [
        {{
          "original": "<string>",
          "improved": "<string>"
        }}
      ]
    }}
  ],
  "notes": "<string>"
}}

Previous invalid output:
{content[:2000]}

Return ONLY valid JSON, no markdown, no code blocks, just raw JSON:"""
            
            retry_content = await llm_generate(fix_prompt)
            retry_content = retry_content.strip()
            if retry_content.startswith("```json"):
                retry_content = retry_content[7:]
            if retry_content.startswith("```"):
                retry_content = retry_content[3:]
            if retry_content.endswith("```"):
                retry_content = retry_content[:-3]
            retry_content = retry_content.strip()
            
            try:
                result = json.loads(retry_content)
                validated_result = validate_scoring_result(result)
                return validated_result
            except json.JSONDecodeError:
                # Still invalid, return raw content for debugging
                raise ValueError(f"Could not parse JSON after retry. Raw model output: {retry_content[:2000]}")
                
    except ValueError:
        # Re-raise ValueError (API key errors, JSON errors)
        raise
    except Exception as e:
        raise ValueError(f"LLM API error: {str(e)}")


def validate_scoring_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and normalize the scoring result to match the required schema.
    
    Args:
        result: Raw result from LLM
        
    Returns:
        Dict: Validated and normalized result
        
    Raises:
        ValueError: If required fields are missing or invalid
    """
    required_fields = [
        "overall_score",
        "metrics",
        "missing_keywords",
        "strengths",
        "top_fixes",
        "section_feedback",
        "notes"
    ]
    
    # Check all required top-level fields exist
    for field in required_fields:
        if field not in result:
            raise ValueError(f"Missing required field: {field}")
    
    # Validate overall_score
    overall_score = result["overall_score"]
    if not isinstance(overall_score, int) or overall_score < 0 or overall_score > 100:
        raise ValueError(f"overall_score must be integer 0-100, got: {overall_score}")
    
    # Validate metrics
    metrics = result["metrics"]
    required_metrics = ["clarity", "impact", "professionalism", "role_fit", "ats"]
    for metric in required_metrics:
        if metric not in metrics:
            raise ValueError(f"Missing metric: {metric}")
        score = metrics[metric]
        if not isinstance(score, int) or score < 0 or score > 100:
            raise ValueError(f"{metric} must be integer 0-100, got: {score}")
    
    # Validate arrays
    for field in ["missing_keywords", "strengths", "top_fixes"]:
        if not isinstance(result[field], list):
            raise ValueError(f"{field} must be an array")
        if not all(isinstance(item, str) for item in result[field]):
            raise ValueError(f"{field} must be array of strings")
    
    # Validate section_feedback
    if not isinstance(result["section_feedback"], list):
        raise ValueError("section_feedback must be an array")
    
    for section in result["section_feedback"]:
        if not isinstance(section, dict):
            raise ValueError("Each section_feedback item must be an object")
        if "section" not in section or "score" not in section or "feedback" not in section or "rewrites" not in section:
            raise ValueError("section_feedback items must have: section, score, feedback, rewrites")
        if not isinstance(section["score"], int) or section["score"] < 0 or section["score"] > 100:
            raise ValueError(f"section score must be integer 0-100, got: {section['score']}")
        if not isinstance(section["feedback"], list):
            raise ValueError("section feedback must be an array")
        if not isinstance(section["rewrites"], list):
            raise ValueError("section rewrites must be an array")
        for rewrite in section["rewrites"]:
            if not isinstance(rewrite, dict) or "original" not in rewrite or "improved" not in rewrite:
                raise ValueError("rewrites must have original and improved fields")
    
    # Validate notes
    if not isinstance(result["notes"], str):
        raise ValueError("notes must be a string")
    
    return result
