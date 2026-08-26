import sys
import os
from pathlib import Path
from datetime import datetime, timezone

# Add the parent directory to the path so we can import levi
sys.path.insert(0, str(Path(__file__).parent.parent))

from levi.memory import EpisodicMemory
from levi.schema import EpisodicRecord, Outcome

def generate_mock_memory():
    # Use a specific mock memory file
    mock_path = Path(__file__).parent / "mock_memory.jsonl"
    if mock_path.exists():
        mock_path.unlink()
        
    memory = EpisodicMemory(path=str(mock_path))
    
    records = [
        EpisodicRecord(
            id="ep_01_qdrant_success",
            task="Fix Qdrant connection refused",
            plan=["Check docker container", "Restart qdrant", "Test connection"],
            actions=[{"tool_name": "run_command", "tool_input": {"command": "docker ps"}, "tool_output": "...", "error": None, "duration_ms": 100.0}],
            outcome=Outcome.SUCCESS,
            verifier_notes="Connection is established.",
            tags=["qdrant", "connection", "networking", "docker"],
            timestamp=datetime.now(timezone.utc).isoformat()
        ),
        EpisodicRecord(
            id="ep_02_qdrant_collection_fail",
            task="Create a new Qdrant collection",
            plan=["Write python script to create collection", "Run script"],
            actions=[{"tool_name": "write_file", "tool_input": {"path": "test.py"}, "tool_output": None, "error": "Fail", "duration_ms": 50.0}],
            outcome=Outcome.FAILURE,
            verifier_notes="API returned 400 Bad Request due to invalid vector size.",
            tags=["qdrant", "collection", "api", "python"],
            timestamp=datetime.now(timezone.utc).isoformat()
        ),
        EpisodicRecord(
            id="ep_03_math_success",
            task="Calculate the square root of 144",
            plan=["Use calculator tool"],
            actions=[{"tool_name": "calculator", "tool_input": {"expression": "math.sqrt(144)"}, "tool_output": "12", "error": None, "duration_ms": 10.0}],
            outcome=Outcome.SUCCESS,
            verifier_notes="Result is 12.",
            tags=["math", "calculator"],
            timestamp=datetime.now(timezone.utc).isoformat()
        ),
        EpisodicRecord(
            id="ep_04_largest_file",
            task="Find the largest file in /tmp and report its size",
            plan=["Run find and sort", "Get last line"],
            actions=[{"tool_name": "run_command", "tool_input": {"command": "find /tmp"}, "tool_output": "file.txt", "error": None, "duration_ms": 200.0}],
            outcome=Outcome.SUCCESS,
            verifier_notes="Successfully found largest file.",
            tags=["linux", "filesystem", "tmp", "bash"],
            timestamp=datetime.now(timezone.utc).isoformat()
        ),
        EpisodicRecord(
            id="ep_05_list_tmp_files",
            task="List all files in /tmp",
            plan=["Run ls command"],
            actions=[{"tool_name": "run_command", "tool_input": {"command": "ls -l /tmp"}, "tool_output": "files...", "error": None, "duration_ms": 50.0}],
            outcome=Outcome.SUCCESS,
            verifier_notes="Files listed successfully.",
            tags=["linux", "filesystem", "tmp", "ls"],
            timestamp=datetime.now(timezone.utc).isoformat()
        ),
        EpisodicRecord(
            id="ep_06_write_script",
            task="Write a python script to /tmp/test_script.py",
            plan=["Write file with python code"],
            actions=[{"tool_name": "write_file", "tool_input": {"path": "/tmp/test_script.py", "content": "print('hello')"}, "tool_output": None, "error": None, "duration_ms": 5.0}],
            outcome=Outcome.SUCCESS,
            verifier_notes="Script written.",
            tags=["python", "script", "filesystem", "tmp"],
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    ]
    
    for r in records:
        memory.write(r)
        
    print(f"Generated {len(records)} mock memory records in {mock_path}")

if __name__ == "__main__":
    generate_mock_memory()
