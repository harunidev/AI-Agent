import os
import subprocess
import tempfile
import sys
import json
import shutil

def run_coverage_analysis_logic(source_code: str, test_code: str, filename: str):
    """
    Runs tests against source code in a isolated environment and returns coverage.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # 1. Setup paths
        source_name = os.path.splitext(filename)[0]
        # Ensure source_name is a valid python identifier
        source_name = source_name.replace("-", "_").replace(".", "_")
        
        source_path = os.path.join(tmpdir, f"{source_name}.py")
        test_path = os.path.join(tmpdir, "test_main.py")
        
        # 2. Write files
        with open(source_path, "w", encoding="utf-8") as f:
            f.write("# -*- coding: utf-8 -*-\n")
            f.write(source_code)
            
        # AI often uses 'from main_module import *' or 'from uploaded import *'
        # We need to fix the import in test_code to point to source_name
        adjusted_test_code = test_code.replace("from main_module import", f"from {source_name} import")
        adjusted_test_code = adjusted_test_code.replace("from uploaded import", f"from {source_name} import")
        adjusted_test_code = adjusted_test_code.replace("from source import", f"from {source_name} import")
        
        # If no import found, we prepend it as a safety measure (risky but better than failing)
        if f"from {source_name}" not in adjusted_test_code and f"import {source_name}" not in adjusted_test_code:
            adjusted_test_code = f"from {source_name} import *\n" + adjusted_test_code

        with open(test_path, "w", encoding="utf-8") as f:
            f.write("# -*- coding: utf-8 -*-\n")
            f.write(adjusted_test_code)
            
        # 3. Create dummy __init__.py to make it a package (optional but helps)
        with open(os.path.join(tmpdir, "__init__.py"), "w") as f:
            f.write("")

        try:
            env = os.environ.copy()
            env["PYTHONPATH"] = tmpdir
            
            # 4. Run Coverage
            # coverage run --source=. -m pytest test_main.py
            cmd_run = [
                sys.executable, "-m", "coverage", "run",
                f"--source={source_name}",
                "-m", "pytest", "test_main.py"
            ]
            
            result = subprocess.run(cmd_run, cwd=tmpdir, env=env, capture_output=True, text=True, timeout=20)
            
            # 5. Export JSON
            cmd_json = [sys.executable, "-m", "coverage", "json", "-o", "cov.json"]
            subprocess.run(cmd_json, cwd=tmpdir, env=env, capture_output=True)
            
            json_path = os.path.join(tmpdir, "cov.json")
            if os.path.exists(json_path):
                with open(json_path, "r") as f:
                    data = json.load(f)
                    totals = data.get("totals", {})
                    percent = totals.get("percent_covered", 0.0)
                    
                    # Missing lines for the specific source file
                    missing_lines = []
                    for fpath, finfo in data.get("files", {}).items():
                        if source_name in fpath:
                            missing_lines = finfo.get("missing_lines", [])
                            break
                            
                    return {
                        "coverage_percent": percent,
                        "missing_lines": missing_lines,
                        "report": data
                    }
            
            return {"coverage_percent": 0.0, "missing_lines": [], "error": "Coverage file not generated."}

        except Exception as e:
            return {"coverage_percent": 0.0, "missing_lines": [], "error": str(e)}
