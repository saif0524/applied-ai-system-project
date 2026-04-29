```mermaid
flowchart TD
    U[Pet Owner Inputs<br/>owner profile, pet profile, tasks] --> A[Streamlit UI<br/>app.py]
    A --> G[Guardrails<br/>input checks + task validation]
    G --> S[Agentic Scheduler<br/>generate -> evaluate -> repair]
    S --> R[Retriever (RAG)<br/>pet-care knowledge lookup]
    R --> E[Evaluator<br/>reliability score + explanations]
    E --> O[Output<br/>daily plan + RAG guidance + evidence]
    O --> H[Human Review<br/>owner confirms plan quality]
    S --> L[Logging<br/>app.log]
    T[Pytest Tests<br/>tests/test_game_logic.py] --> V[Verification<br/>frequency, priority, budget, reliability, RAG]
```
