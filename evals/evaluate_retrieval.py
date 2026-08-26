import sys
import json
from pathlib import Path
from typing import List, Dict, Optional

# Add the parent directory to the path so we can import levi
sys.path.insert(0, str(Path(__file__).parent.parent))

from levi.memory import EpisodicMemory

def calculate_recall_at_k(retrieved_ids: List[str], ground_truth_ids: List[str]) -> Optional[float]:
    if not ground_truth_ids:
        return None
    
    hits = sum(1 for gt_id in ground_truth_ids if gt_id in retrieved_ids)
    return hits / len(ground_truth_ids)

def calculate_precision_at_k(retrieved_ids: List[str], ground_truth_ids: List[str]) -> Optional[float]:
    if not ground_truth_ids:
        return None
    if not retrieved_ids:
        return 0.0
        
    hits = sum(1 for ret_id in retrieved_ids if ret_id in ground_truth_ids)
    return hits / len(retrieved_ids)

def calculate_mrr(retrieved_ids: List[str], ground_truth_ids: List[str]) -> Optional[float]:
    if not ground_truth_ids:
        return None
        
    for i, ret_id in enumerate(retrieved_ids):
        if ret_id in ground_truth_ids:
            return 1.0 / (i + 1)
    return 0.0

def count_tokens_approx(text: str) -> int:
    # Very rough approximation (words * 1.3 or just char count / 4)
    return len(text) // 4

def evaluate_retrieval(k: int = 5):
    evals_dir = Path(__file__).parent
    benchmark_path = evals_dir / "benchmark_dataset.json"
    mock_memory_path = evals_dir / "mock_memory.jsonl"
    
    if not mock_memory_path.exists():
        print(f"Error: {mock_memory_path} does not exist. Run generate_mock_memory.py first.")
        return
        
    with open(benchmark_path, "r") as f:
        benchmark_data = json.load(f)
        
    memory = EpisodicMemory(path=str(mock_memory_path))
    
    results_by_category = {}
    total_queries = len(benchmark_data)
    
    total_recall = 0.0
    total_precision = 0.0
    total_mrr = 0.0
    valid_metric_queries = 0
    total_retrieved_tokens = 0
    
    total_no_match_queries = 0
    correctly_rejected_no_match = 0
    
    print(f"Running evaluation on {total_queries} tasks...")
    print("-" * 50)
    
    for task in benchmark_data:
        query = task["query"]
        category = task["category"]
        ground_truth = task["ground_truth_memories"]
        
        # Initialize category in results if not exists
        if category not in results_by_category:
            results_by_category[category] = {"count": 0, "recall": 0.0, "precision": 0.0, "mrr": 0.0, "valid_metrics_count": 0}
            
        # Retrieve
        retrieved_records = memory.retrieve(query, k=k)
        retrieved_ids = [r.id for r in retrieved_records]
        
        # Calculate tokens for this retrieval
        retrieved_tokens = sum(count_tokens_approx(r.task + " " + " ".join(r.plan) + " " + " ".join(r.tags)) for r in retrieved_records)
        total_retrieved_tokens += retrieved_tokens
        
        # Calculate metrics
        recall = calculate_recall_at_k(retrieved_ids, ground_truth)
        precision = calculate_precision_at_k(retrieved_ids, ground_truth)
        mrr = calculate_mrr(retrieved_ids, ground_truth)
        
        # Special handling for "no_match" category
        if not ground_truth:
            total_no_match_queries += 1
            if not retrieved_ids:
                correctly_rejected_no_match += 1
            
        recall_str = f"{recall:.2f}" if recall is not None else "N/A"
        precision_str = f"{precision:.2f}" if precision is not None else "N/A"
        mrr_str = f"{mrr:.2f}" if mrr is not None else "N/A"
            
        print(f"Query: {query}")
        print(f"  Category: {category}")
        print(f"  Retrieved: {retrieved_ids}")
        print(f"  Ground Truth: {ground_truth}")
        print(f"  Recall@{k}: {recall_str} | Precision@{k}: {precision_str} | MRR: {mrr_str}")
        print(f"  Approx Tokens Retrieved: {retrieved_tokens}")
        print()
        
        if recall is not None:
            total_recall += recall
            total_precision += precision
            total_mrr += mrr
            valid_metric_queries += 1
            
            results_by_category[category]["recall"] += recall
            results_by_category[category]["precision"] += precision
            results_by_category[category]["mrr"] += mrr
            results_by_category[category]["valid_metrics_count"] += 1
            
        results_by_category[category]["count"] += 1

    print("-" * 50)
    print("OVERALL RESULTS")
    if valid_metric_queries > 0:
        print(f"Mean Recall@{k}:    {total_recall / valid_metric_queries:.3f}")
        print(f"Mean Precision@{k}: {total_precision / valid_metric_queries:.3f}")
        print(f"Mean MRR:         {total_mrr / valid_metric_queries:.3f}")
    else:
        print(f"Mean Recall@{k}:    N/A")
        print(f"Mean Precision@{k}: N/A")
        print(f"Mean MRR:         N/A")
        
    print(f"Total retrieved tokens across {total_queries} queries: {total_retrieved_tokens}")
    if total_no_match_queries > 0:
        no_match_accuracy = correctly_rejected_no_match / total_no_match_queries
        print(f"No-Match Accuracy: {no_match_accuracy:.3f} ({correctly_rejected_no_match}/{total_no_match_queries})")
    print("-" * 50)
    print("RESULTS BY CATEGORY")
    
    for cat, metrics in results_by_category.items():
        count = metrics["count"]
        valid = metrics["valid_metrics_count"]
        print(f"{cat.upper()} ({count} tasks):")
        if valid > 0:
            cat_recall = metrics["recall"] / valid
            cat_precision = metrics["precision"] / valid
            cat_mrr = metrics["mrr"] / valid
            print(f"  Recall@{k}:    {cat_recall:.3f}")
            print(f"  Precision@{k}: {cat_precision:.3f}")
            print(f"  MRR:         {cat_mrr:.3f}")
        else:
            print(f"  Recall@{k}:    N/A")
            print(f"  Precision@{k}: N/A")
            print(f"  MRR:         N/A")

if __name__ == "__main__":
    evaluate_retrieval(k=5)
