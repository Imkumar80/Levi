import sys
import json
import time
from pathlib import Path
from dataclasses import asdict

# Add the parent directory to the path so we can import levi
sys.path.insert(0, str(Path(__file__).parent.parent))

from levi.cli import build_agent
from levi.schema import Outcome

def evaluate_agent():
    evals_dir = Path(__file__).parent
    benchmark_path = evals_dir / "agent_benchmark.json"
    mock_memory_path = evals_dir / "mock_memory.jsonl"
    
    if not mock_memory_path.exists():
        print(f"Error: {mock_memory_path} does not exist. Run generate_mock_memory.py first.")
        return
        
    with open(benchmark_path, "r") as f:
        benchmark_data = json.load(f)
        
    # Build agent using the frozen mock_memory
    agent = build_agent(memory_path=str(mock_memory_path))
    
    results = []
    
    print(f"Running Agent Evaluation on {len(benchmark_data)} tasks...")
    print("=" * 80)
    
    total_baseline_success = 0
    total_baseline_tokens = 0
    total_levi_success = 0
    total_levi_tokens = 0
    
    for task_data in benchmark_data:
        task = task_data["task"]
        expected_answer = task_data["expected_answer"]
        category = task_data["category"]
        
        print(f"Task: {task}")
        print(f"Category: {category}")
        
        # --- Baseline Run (Memory OFF) ---
        print("  Running Baseline (Memory OFF)...")
        start_time = time.time()
        # Ensure we don't write to the frozen memory file
        baseline_result = agent.run(task, use_memory=False, read_only_memory=True)
        baseline_latency = time.time() - start_time
        
        baseline_success = (baseline_result.record.outcome == Outcome.SUCCESS and 
                            expected_answer in "\n".join([a.tool_output for a in baseline_result.record.actions if a.tool_output] + baseline_result.record.plan))
                            
        if baseline_success:
            total_baseline_success += 1
            total_baseline_tokens += baseline_result.total_tokens
            
        print(f"    Success: {baseline_success}")
        print(f"    Total Tokens: {baseline_result.total_tokens} (Prompt: {baseline_result.prompt_tokens}, Output: {baseline_result.output_tokens})")
        print(f"    Latency: {baseline_latency:.2f}s")
        
        # --- LEVI Run (Memory ON) ---
        print("  Running LEVI V0 (Memory ON)...")
        start_time = time.time()
        levi_result = agent.run(task, use_memory=True, read_only_memory=True)
        levi_latency = time.time() - start_time
        
        levi_success = (levi_result.record.outcome == Outcome.SUCCESS and 
                        expected_answer in "\n".join([a.tool_output for a in levi_result.record.actions if a.tool_output] + levi_result.record.plan))
                        
        if levi_success:
            total_levi_success += 1
            total_levi_tokens += levi_result.total_tokens
            
        print(f"    Success: {levi_success}")
        print(f"    Total Tokens: {levi_result.total_tokens} (Prompt: {levi_result.prompt_tokens}, Output: {levi_result.output_tokens})")
        print(f"    Latency: {levi_latency:.2f}s")
        print("-" * 80)
        
    print("\n" + "=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)
    print(f"{'Metric':<30} | {'Baseline (No Memory)':<20} | {'LEVI V0 (Memory)':<20}")
    print("-" * 80)
    print(f"{'Tasks Successful':<30} | {total_baseline_success}/{len(benchmark_data):<20} | {total_levi_success}/{len(benchmark_data):<20}")
    
    baseline_avg_tokens = (total_baseline_tokens / total_baseline_success) if total_baseline_success > 0 else 0
    levi_avg_tokens = (total_levi_tokens / total_levi_success) if total_levi_success > 0 else 0
    
    print(f"{'Avg Tokens per Success':<30} | {baseline_avg_tokens:<20.1f} | {levi_avg_tokens:<20.1f}")
    print("=" * 80)

if __name__ == "__main__":
    evaluate_agent()
