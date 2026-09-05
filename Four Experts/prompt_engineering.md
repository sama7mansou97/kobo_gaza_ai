# Prompt Engineering Concepts

### 1. Role Prompting
By assigning explicit personas (`Database Read Expert`, `Database Write Expert`, `Database Semantic Search Expert`, `Orchestrator`), we constrain the model's domain focus, reducing hallucinations and producing structured outputs tailored to database tasks.

### 2. Few-Shot In-Context Learning
Providing structural examples within the `system_prompt` guides the LLM to format SQL queries and Python execution scripts accurately without altering schema definitions unexpectedly.

### 3. Dynamic Orchestrator Decomposition & CoT
The Orchestrator utilizes Chain-of-Thought (CoT) reasoning to break down compound queries into sequential sub-tasks, routing each sub-task to the correct expert while enforcing safety stops for deletion actions.