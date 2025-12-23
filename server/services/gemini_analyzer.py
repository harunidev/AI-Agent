import os
import google.generativeai as genai
from typing import Dict, List, Optional
import json
from dotenv import load_dotenv

# Initialize Gemini API
def initialize_gemini() -> bool:
    """Initialize Gemini API with API key from environment."""
    try:
        # Load .env from root directory
        root_env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env')
        load_dotenv(dotenv_path=root_env_path)
        
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return False
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        print(f"Gemini initialization error: {e}")
        return False

import time
import random

def _generate_with_retry(model, prompt, **kwargs):
    """Helper to retry API calls on rate limit errors."""
    max_retries = 1 
    base_delay = 2.0
    
    for attempt in range(max_retries + 1):
        try:
            return model.generate_content(prompt, **kwargs)
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                if attempt < max_retries:
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                
                    time.sleep(delay)
                    continue
            raise e


def analyze_code_quality(source_code: str, language: str = "python") -> Dict:
    """
    Analyze code quality using Gemini AI.
    Returns insights about code structure, complexity, and potential issues.
    """
    if not initialize_gemini():
        return {"error": "Gemini API not configured"}
    
    try:
        model = genai.GenerativeModel(
            'models/gemini-2.5-flash',
            generation_config={
                'temperature': 0.2,
                'max_output_tokens': 512,
                'top_p': 0.8
            }
        )
        
        # Limit code length for faster analysis
        code_snippet = source_code[:800] if len(source_code) > 800 else source_code
        
        prompt = f"""Analyze this Python code and return ONLY a valid JSON object (no markdown, no code blocks):

{code_snippet}

Return this exact JSON structure:
{{"complexity_score": 5, "testability_score": 7, "issues": ["issue1"], "strengths": ["strength1"], "test_recommendations": ["rec1"]}}

IMPORTANT: Return ONLY the JSON object, nothing else."""

        response = _generate_with_retry(
            model,
            prompt,
            request_options={'timeout': 20}
        )
        
        # Parse JSON from response
        result_text = response.text.strip()
        
        # Remove any markdown formatting
        if '```' in result_text:
            # Extract content between code blocks
            parts = result_text.split('```')
            for part in parts:
                part = part.strip()
                if part.startswith('json'):
                    result_text = part[4:].strip()
                elif part.startswith('{'):
                    result_text = part
                    break
        
        # Find JSON object
        if '{' in result_text:
            start = result_text.index('{')
            end = result_text.rindex('}') + 1
            result_text = result_text[start:end]
        
        analysis = json.loads(result_text)
        return analysis
        
        # Parse JSON from response
        result_text = response.text.strip()
        # Remove markdown code blocks if present
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]
        
        analysis = json.loads(result_text)
        return analysis
        
    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}

def analyze_test_coverage(source_code: str, test_code: str, coverage_data: Dict) -> Dict:
    """
    Analyze test coverage using Gemini AI.
    Provides insights on missing test cases and improvement suggestions.
    """
    if not initialize_gemini():
        return {"error": "Gemini API not configured"}
    
    try:
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        
        coverage_pct = coverage_data.get("coverage_percent", 0)
        missing_lines = coverage_data.get("missing_lines", [])
        
        prompt = f"""Analyze this test coverage situation:

**Source Code:**
```python
{source_code}
```

**Current Tests:**
```python
{test_code}
```

**Coverage Stats:**
- Coverage: {coverage_pct}%
- Missing lines: {missing_lines}

Provide a JSON response with:
1. "coverage_assessment": overall quality assessment
2. "missing_scenarios": list of untested scenarios
3. "improvement_suggestions": specific suggestions to increase coverage
4. "priority_areas": which parts need testing most urgently

Return ONLY valid JSON, no markdown formatting."""

        response = _generate_with_retry(model, prompt)
        
        result_text = response.text.strip()
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]
        
        analysis = json.loads(result_text)
        return analysis
        
    except Exception as e:
        return {"error": f"Coverage analysis failed: {str(e)}"}

def generate_smart_tests(source_code: str, code_analysis: Dict, language: str = "python") -> tuple[str, str]:
    """
    Generate intelligent tests using Gemini AI based on code analysis.
    """
    if not initialize_gemini():
        return "# Gemini API not configured", "Error: API not available"
    
    try:
        model = genai.GenerativeModel(
            'models/gemini-pro',
            generation_config={
                'temperature': 0.3,  # Lower for faster, more focused responses
                'max_output_tokens': 2048,  # Limit output length
                'top_p': 0.8,
                'top_k': 20
            }
        )
        
        prompt = f"""Generate pytest tests for:

```{language}
{source_code[:1000]}  
```

Generate concise tests covering main functions, edge cases, and errors. Target >90% coverage.

Return Python code only."""

        response = _generate_with_retry(
            model,
            prompt,
            request_options={'timeout': 30}  # 30 second timeout
        )
        test_code = response.text.strip()
        
        # Remove markdown code blocks if present
        if test_code.startswith("```"):
            lines = test_code.split("\n")
            test_code = "\n".join(lines[1:-1]) if len(lines) > 2 else test_code
        
        explanation = f"Generated AI-powered tests based on code analysis (complexity: {code_analysis.get('complexity_score', 'N/A')})"
        
        return test_code, explanation
        
    except Exception as e:
        return f"# Error generating tests: {str(e)}", f"Generation failed: {str(e)}"

def improve_tests_with_ai(source_code: str, current_tests: str, coverage_analysis: Dict) -> tuple[str, str]:
    """
    Improve existing tests using Gemini AI based on coverage analysis.
    """
    if not initialize_gemini():
        return current_tests, "Error: Gemini API not configured"
    
    try:
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        
        missing_scenarios = coverage_analysis.get("missing_scenarios", [])
        suggestions = coverage_analysis.get("improvement_suggestions", [])
        
        prompt = f"""Improve these pytest tests to increase coverage:

**Source Code:**
```python
{source_code}
```

**Current Tests:**
```python
{current_tests}
```

**Missing Scenarios:**
{json.dumps(missing_scenarios, indent=2)}

**Improvement Suggestions:**
{json.dumps(suggestions, indent=2)}

Add new test cases to cover the missing scenarios. Return ONLY the complete improved test code, no explanations."""

        response = _generate_with_retry(model, prompt)
        improved_tests = response.text.strip()
        
        # Remove markdown code blocks if present
        if improved_tests.startswith("```"):
            lines = improved_tests.split("\n")
            improved_tests = "\n".join(lines[1:-1]) if len(lines) > 2 else improved_tests
        
        explanation = f"Added tests for {len(missing_scenarios)} missing scenarios"
        
        return improved_tests, explanation
        
    except Exception as e:
        return current_tests, f"Improvement failed: {str(e)}"

def get_ai_status() -> Dict:
    """Check Gemini API connection status."""
    if initialize_gemini():
        try:
            model = genai.GenerativeModel('models/gemini-2.5-flash')
            response = model.generate_content("Say 'OK' if you can read this.")
            return {
                "status": "connected",
                "model": "models/gemini-2.5-flash",
                "response": response.text[:50]
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    else:
        return {"status": "not_configured", "message": "API key missing"}

def generate_tests_directly(source_code: str, language: str = "python") -> tuple[str, str]:
    """
    Generate pytest tests directly using Gemini AI without JSON analysis step.
    This bypasses JSON parsing issues.
    """
    if not initialize_gemini():
        return "# Gemini API not configured", "Error: API not available"
    
    try:
        model = genai.GenerativeModel(
            'models/gemini-2.5-flash',
            generation_config={
                'temperature': 0.4,
                'max_output_tokens': 3000,
                'top_p': 0.9
            }
        )
        
        prompt = f"""Generate comprehensive pytest tests for this Python code to achieve 90%+ coverage.

CODE:
{source_code}

REQUIREMENTS:
- Use pytest and pytest.mark.parametrize
- Test all functions thoroughly
- Include edge cases, boundary conditions, error handling
- Test all branches and conditions
- Aim for 90%+ code coverage
- Return ONLY the Python test code, no explanations

Generate the complete test file now:"""

        response = _generate_with_retry(
            model,
            prompt,
            request_options={'timeout': 45}
        )
        
        test_code = response.text.strip()
        
        # Clean up markdown if present
        if '```python' in test_code:
            parts = test_code.split('```python')
            if len(parts) > 1:
                test_code = parts[1].split('```')[0].strip()
        elif '```' in test_code:
            parts = test_code.split('```')
            if len(parts) >= 3:
                test_code = parts[1].strip()
        
        # Ensure it starts with import
        if not test_code.startswith('import'):
            # Try to find where actual code starts
            lines = test_code.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith('import') or line.strip().startswith('def test_'):
                    test_code = '\n'.join(lines[i:])
                    break
        
        explanation = "Generated comprehensive tests using Gemini AI for 90%+ coverage"
        return test_code, explanation
        
    except Exception as e:
        return f"# Error generating tests: {str(e)}", f"Generation failed: {str(e)}"
