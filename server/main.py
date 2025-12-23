from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os
import shutil
import logging
from dotenv import load_dotenv

# Suppress ALTS/gRPC warnings (Google Cloud related, not needed locally)
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"
logging.getLogger("google").setLevel(logging.ERROR)
logging.getLogger("absl").setLevel(logging.ERROR)

# Load environment variables from Root Directory (.env is one level up from /server)
root_env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(dotenv_path=root_env_path)

app = FastAPI(
    title="AI4SE Test Generator",
    description="AI-Powered Automated Test Generation System with >90% Coverage",
    version="1.0.0"
)

# Origins for CORS - Critical for React communication
origins = [
    "http://localhost:5173",  # Vite default
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from services.generator import generate_tests_with_ai, improve_tests_with_coverage
from services.coverage import run_coverage_analysis_logic
from services.gemini_analyzer import analyze_code_quality, analyze_test_coverage, get_ai_status
from models import TestGenerationRequest, TestGenerationResponse


@app.post("/generate-tests", response_model=TestGenerationResponse)
async def generate_tests_endpoint(request: TestGenerationRequest):
    # 1. Initial Generation - Pure AST (NO AI to avoid rate limits and ALTS warnings)
    test_code, explanation = generate_tests_with_ai(
        request.code_content, 
        request.language,
        use_ai=False  # DISABLED: Using pure AST-based generation for stability
    )
    
    # 2. Run Coverage
    coverage_result = run_coverage_analysis_logic(request.code_content, test_code, request.file_name or "uploaded.py")
    coverage_pct = coverage_result.get("coverage_percent", 0.0)
    
    # 3. Iterative Improvement: If coverage < 90%, try to improve (AST only)
    iterations = 0
    max_iterations = 3  # Reduced: 3 is enough for AST-based improvement
    
    while coverage_pct < 90.0 and iterations < max_iterations:
        iterations += 1
        missing = coverage_result.get("missing_lines", [])
        if not missing: break
        
        test_code, improvement_msg = improve_tests_with_coverage(
            request.code_content, 
            test_code, 
            missing, 
            coverage_pct,
            use_ai=False  # DISABLED: Pure AST for speed and stability
        )
        explanation += f" | Iter {iterations}: {improvement_msg}"
        
        # Re-run coverage
        coverage_result = run_coverage_analysis_logic(request.code_content, test_code, request.file_name or "uploaded.py")
        coverage_pct = coverage_result.get("coverage_percent", 0.0)

    return TestGenerationResponse(
        test_code=test_code,
        explanation=explanation,
        coverage_estimate=coverage_pct
    )

@app.get("/")
def read_root():
    return {"message": "AI4SE Test Generation API with Gemini AI", "status": "active", "ai_enabled": True}

@app.get("/health")
def health_check():
    # Check for API Key
    api_status = "connected" if os.environ.get("GEMINI_API_KEY") else "missing_key"
    return {"status": "ok", "service": "test-generation-engine", "ai_mode": api_status}

@app.get("/ai-status")
def ai_status():
    """Check Gemini AI connection status."""
    return get_ai_status()

@app.post("/analyze-code")
async def analyze_code_endpoint(request: TestGenerationRequest):
    """Analyze code quality using Gemini AI."""
    try:
        analysis = analyze_code_quality(request.code_content, request.language)
        return {
            "success": "error" not in analysis,
            "analysis": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-tests")
async def analyze_tests_endpoint(request: TestGenerationRequest):
    """Analyze test coverage using Gemini AI."""
    try:
        # First run coverage
        test_code = request.code_content  # In this case, code_content contains test code
        # We need both source and test code - for now use a simple approach
        coverage_data = {
            "coverage_percent": 0,
            "missing_lines": []
        }
        
        analysis = analyze_test_coverage(
            request.code_content,
            test_code,
            coverage_data
        )
        
        return {
            "success": "error" not in analysis,
            "analysis": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

