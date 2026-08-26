# Levi V0 Test Execution Study

## Test Command
The following command was used to test the Levi CLI execution loop:
```bash
python3 -m levi.cli "12 * (3+4)"
```

## Execution Results

**Outcome:** `success`
**Notes:** All actions completed without error.

### Plan Trace
- `[step 0]` Task looks like an arithmetic expression. -> `calculator({'expression': '12 * (3+4)'})`
- `[stop]` Single-step mock planner: done after one action.

### Actions Executed
- `calculator({'expression': '12 * (3+4)'})` -> `84` (error=`None`)## Task: find the largest file in /tmp and report its size
Outcome: success
Notes:   All actions completed without error.
Plan trace:
  [step 0] No specialized tool matched; echoing task. -> echo({'text': 'find the largest file in /tmp and report its size'})
  [stop] Single-step mock planner: done after one action.
Actions:
  echo({'text': 'find the largest file in /tmp and report its size'}) -> 'find the largest file in /tmp and report its size' error=None

---

## Task: find the largest file in /tmp and report its size
Outcome: failure
Notes:   No actions were taken.
Plan trace:
  [stop] The available tools ('calculator', 'echo', 'write_file', 'read_file') do not include directory listing or command execution capabilities needed to inspect /tmp and determine the largest file.
Actions:

---

## Task: find the largest file in /tmp and report its size
Outcome: success
Notes:   All actions completed without error.
Plan trace:
  [step 0] Find the largest file in /tmp by listing all regular files with their size in bytes, sorting numerically, and getting the last line. -> run_command({'command': "find /tmp -type f -printf '%s %p\n' 2>/dev/null | sort -n | tail -n 1"})
  [stop] The largest file in /tmp is /tmp/unleash-repo-schema-v1-codeium-language-server.json with a size of 463,641 bytes (~452.7 KiB).
Actions:
  run_command({'command': "find /tmp -type f -printf '%s %p\n' 2>/dev/null | sort -n | tail -n 1"}) -> '463641 /tmp/unleash-repo-schema-v1-codeium-language-server.json\n' error=None

---



## V0 Evaluation Benchmark (Phase A)

**OVERALL RESULTS**
- Mean Recall@5: 0.800
- Mean Precision@5: 0.160
- Mean MRR: 0.733
- Total retrieved tokens across 10 queries: 1148

**RESULTS BY CATEGORY**
- **EXACT_MATCH (4 tasks):**
  - Recall@5: 1.000
  - Precision@5: 0.200
  - MRR: 1.000
- **PARAPHRASE (2 tasks):**
  - Recall@5: 1.000
  - Precision@5: 0.200
  - MRR: 0.667
- **DISTRACTOR (2 tasks):**
  - Recall@5: 1.000
  - Precision@5: 0.200
  - MRR: 1.000
- **NO_MATCH (2 tasks):**
  - Recall@5: 0.000
  - Precision@5: 0.000
  - MRR: 0.000
Running evaluation on 10 tasks...
--------------------------------------------------
Query: Fix Qdrant connection refused
  Category: exact_match
  Retrieved: ['ep_01_qdrant_success', 'ep_02_qdrant_collection_fail', 'ep_06_write_script', 'ep_05_list_tmp_files', 'ep_04_largest_file']
  Ground Truth: ['ep_01_qdrant_success']
  Recall@5: 1.00 | Precision@5: 0.20 | MRR: 1.00
  Approx Tokens Retrieved: 122

Query: My Qdrant client can't connect
  Category: paraphrase
  Retrieved: ['ep_01_qdrant_success', 'ep_02_qdrant_collection_fail', 'ep_06_write_script', 'ep_05_list_tmp_files', 'ep_04_largest_file']
  Ground Truth: ['ep_01_qdrant_success']
  Recall@5: 1.00 | Precision@5: 0.20 | MRR: 1.00
  Approx Tokens Retrieved: 122

Query: Create a new Qdrant collection
  Category: distractor
  Retrieved: ['ep_02_qdrant_collection_fail', 'ep_01_qdrant_success', 'ep_06_write_script', 'ep_05_list_tmp_files', 'ep_04_largest_file']
  Ground Truth: ['ep_02_qdrant_collection_fail']
  Recall@5: 1.00 | Precision@5: 0.20 | MRR: 1.00
  Approx Tokens Retrieved: 122

Query: Debug my Redis authentication problem
  Category: no_match
  Retrieved: ['ep_06_write_script', 'ep_05_list_tmp_files', 'ep_04_largest_file', 'ep_03_math_success', 'ep_01_qdrant_success']
  Ground Truth: []
  Recall@5: 0.00 | Precision@5: 0.00 | MRR: 0.00
  Approx Tokens Retrieved: 112

Query: Calculate the square root of 144
  Category: exact_match
  Retrieved: ['ep_03_math_success', 'ep_06_write_script', 'ep_05_list_tmp_files', 'ep_04_largest_file', 'ep_01_qdrant_success']
  Ground Truth: ['ep_03_math_success']
  Recall@5: 1.00 | Precision@5: 0.20 | MRR: 1.00
  Approx Tokens Retrieved: 112

Query: Find the largest file in /tmp
  Category: exact_match
  Retrieved: ['ep_04_largest_file', 'ep_06_write_script', 'ep_05_list_tmp_files', 'ep_03_math_success', 'ep_01_qdrant_success']
  Ground Truth: ['ep_04_largest_file']
  Recall@5: 1.00 | Precision@5: 0.20 | MRR: 1.00
  Approx Tokens Retrieved: 112

Query: Identify the biggest document inside the temporary folder
  Category: paraphrase
  Retrieved: ['ep_06_write_script', 'ep_05_list_tmp_files', 'ep_04_largest_file', 'ep_03_math_success', 'ep_01_qdrant_success']
  Ground Truth: ['ep_04_largest_file']
  Recall@5: 1.00 | Precision@5: 0.20 | MRR: 0.33
  Approx Tokens Retrieved: 112

Query: List all files in /tmp
  Category: distractor
  Retrieved: ['ep_05_list_tmp_files', 'ep_06_write_script', 'ep_04_largest_file', 'ep_03_math_success', 'ep_01_qdrant_success']
  Ground Truth: ['ep_05_list_tmp_files']
  Recall@5: 1.00 | Precision@5: 0.20 | MRR: 1.00
  Approx Tokens Retrieved: 112

Query: Write a python script to /tmp/test_script.py
  Category: exact_match
  Retrieved: ['ep_06_write_script', 'ep_05_list_tmp_files', 'ep_04_largest_file', 'ep_02_qdrant_collection_fail', 'ep_03_math_success']
  Ground Truth: ['ep_06_write_script']
  Recall@5: 1.00 | Precision@5: 0.20 | MRR: 1.00
  Approx Tokens Retrieved: 110

Query: How do I install postgresql on ubuntu?
  Category: no_match
  Retrieved: ['ep_06_write_script', 'ep_05_list_tmp_files', 'ep_04_largest_file', 'ep_03_math_success', 'ep_01_qdrant_success']
  Ground Truth: []
  Recall@5: 0.00 | Precision@5: 0.00 | MRR: 0.00
  Approx Tokens Retrieved: 112

--------------------------------------------------
OVERALL RESULTS
Mean Recall@5:    0.800
Mean Precision@5: 0.160
Mean MRR:         0.733
Total retrieved tokens across 10 queries: 1148
--------------------------------------------------
RESULTS BY CATEGORY
EXACT_MATCH (4 tasks):
  Recall@5:    1.000
  Precision@5: 0.200
  MRR:         1.000
PARAPHRASE (2 tasks):
  Recall@5:    1.000
  Precision@5: 0.200
  MRR:         0.667
DISTRACTOR (2 tasks):
  Recall@5:    1.000
  Precision@5: 0.200
  MRR:         1.000
NO_MATCH (2 tasks):
  Recall@5:    0.000
  Precision@5: 0.000
  MRR:         0.000
Running evaluation on 10 tasks...
--------------------------------------------------
Query: Fix Qdrant connection refused
  Category: exact_match
  Retrieved: ['ep_01_qdrant_success', 'ep_02_qdrant_collection_fail']
  Ground Truth: ['ep_01_qdrant_success']
  Recall@5: 1.00 | Precision@5: 0.50 | MRR: 1.00
  Approx Tokens Retrieved: 56

Query: My Qdrant client can't connect
  Category: paraphrase
  Retrieved: ['ep_01_qdrant_success', 'ep_02_qdrant_collection_fail']
  Ground Truth: ['ep_01_qdrant_success']
  Recall@5: 1.00 | Precision@5: 0.50 | MRR: 1.00
  Approx Tokens Retrieved: 56

Query: Create a new Qdrant collection
  Category: distractor
  Retrieved: ['ep_02_qdrant_collection_fail', 'ep_01_qdrant_success']
  Ground Truth: ['ep_02_qdrant_collection_fail']
  Recall@5: 1.00 | Precision@5: 0.50 | MRR: 1.00
  Approx Tokens Retrieved: 56

Query: Debug my Redis authentication problem
  Category: no_match
  Retrieved: []
  Ground Truth: []
  Recall@5: 1.00 | Precision@5: 1.00 | MRR: 1.00
  Approx Tokens Retrieved: 0

Query: Calculate the square root of 144
  Category: exact_match
  Retrieved: ['ep_03_math_success']
  Ground Truth: ['ep_03_math_success']
  Recall@5: 1.00 | Precision@5: 1.00 | MRR: 1.00
  Approx Tokens Retrieved: 17

Query: Find the largest file in /tmp
  Category: exact_match
  Retrieved: ['ep_04_largest_file', 'ep_06_write_script', 'ep_05_list_tmp_files']
  Ground Truth: ['ep_04_largest_file']
  Recall@5: 1.00 | Precision@5: 0.33 | MRR: 1.00
  Approx Tokens Retrieved: 66

Query: Identify the biggest document inside the temporary folder
  Category: paraphrase
  Retrieved: []
  Ground Truth: ['ep_04_largest_file']
  Recall@5: 0.00 | Precision@5: 0.00 | MRR: 0.00
  Approx Tokens Retrieved: 0

Query: List all files in /tmp
  Category: distractor
  Retrieved: ['ep_05_list_tmp_files', 'ep_06_write_script', 'ep_04_largest_file']
  Ground Truth: ['ep_05_list_tmp_files']
  Recall@5: 1.00 | Precision@5: 0.33 | MRR: 1.00
  Approx Tokens Retrieved: 66

Query: Write a python script to /tmp/test_script.py
  Category: exact_match
  Retrieved: ['ep_06_write_script', 'ep_05_list_tmp_files', 'ep_04_largest_file', 'ep_02_qdrant_collection_fail']
  Ground Truth: ['ep_06_write_script']
  Recall@5: 1.00 | Precision@5: 0.25 | MRR: 1.00
  Approx Tokens Retrieved: 93

Query: How do I install postgresql on ubuntu?
  Category: no_match
  Retrieved: []
  Ground Truth: []
  Recall@5: 1.00 | Precision@5: 1.00 | MRR: 1.00
  Approx Tokens Retrieved: 0

--------------------------------------------------
OVERALL RESULTS
Mean Recall@5:    0.900
Mean Precision@5: 0.542
Mean MRR:         0.900
Total retrieved tokens across 10 queries: 410
No-Match Accuracy: 1.000 (2/2)
--------------------------------------------------
RESULTS BY CATEGORY
EXACT_MATCH (4 tasks):
  Recall@5:    1.000
  Precision@5: 0.521
  MRR:         1.000
PARAPHRASE (2 tasks):
  Recall@5:    0.500
  Precision@5: 0.250
  MRR:         0.500
DISTRACTOR (2 tasks):
  Recall@5:    1.000
  Precision@5: 0.417
  MRR:         1.000
NO_MATCH (2 tasks):
  Recall@5:    1.000
  Precision@5: 1.000
  MRR:         1.000
