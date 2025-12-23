from pydantic import BaseModel
from typing import Optional, List

class TestGenerationRequest(BaseModel):
    code_content: str
    file_name: str
    language: str = "python"
    existing_tests: Optional[str] = None

class TestGenerationResponse(BaseModel):
    test_code: str
    explanation: str
    coverage_estimate: Optional[float] = None

class CoverageRequest(BaseModel):
    source_code: str
    test_code: str
    file_name: str

class CoverageResponse(BaseModel):
    coverage_percent: float
    missing_lines: List[int]
    report_content: str
