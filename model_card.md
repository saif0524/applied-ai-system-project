# Model Card: PawPal+ AI Planning System

## 1. Model/System Name
**PawPal+ AI Planning System** (Rule-based scheduler + RAG retriever)

## 2. Intended Use
PawPal+ helps pet owners create a daily care plan by prioritizing tasks (feeding, walks, medication, grooming, enrichment) under time constraints. It is intended for **planning support**, explanation, and routine organization.

## 3. Not Intended Use
- Not for veterinary diagnosis or emergency medical triage.
- Not a replacement for professional veterinary advice.
- Not designed for autonomous execution of care actions without human review.

## 4. System Components
- **Scheduling Core (`pawpal_system.py`)**: OOP models (`User`, `Pet`, `Task`, `Schedule`) and agentic plan-generate/evaluate/repair workflow.
- **Retriever (`pawpal_rag.py`)**: Retrieves relevant care guidance from text knowledge base using lexical similarity.
- **Knowledge Base (`assets/knowledge_base/pet_care_kb.txt`)**: Domain guidance snippets used for RAG.
- **UI (`app.py`)**: Streamlit interface for user input and plan output.
- **Testing (`tests/test_game_logic.py`)**: Automated checks for scheduling and reliability behavior.

## 5. Inputs and Outputs
### Inputs
- Owner information (name, available minutes)
- Pet profile (name, species, age, health notes)
- Task list (title, duration, priority, frequency, required flag, notes)
- Optional custom health cases

### Outputs
- Daily planned task list
- Total minutes used
- Reliability score
- Planner reasoning/explanations
- RAG guidance and retrieved evidence

## 6. Data and Knowledge Sources
- Primary runtime “knowledge” source: `assets/knowledge_base/pet_care_kb.txt`
- User-provided context: health notes, task notes, custom health cases
- No external web retrieval in core runtime flow.

## 7. Performance and Reliability
Current reliability mechanisms:
- Constraint checks (time budget, required-task handling)
- Heuristic reliability scoring
- Transparent evidence display from retrieval
- Automated tests for key scheduling properties

Known limits:
- Reliability score is heuristic, not a calibrated probability.
- Lexical retrieval may miss semantically similar phrasing.

### Testing Results Summary
- Test coverage includes frequency filtering, required-task prioritization, time-budget compliance, reliability downgrade on infeasible required tasks, and RAG integration presence.
- In sandbox runs, syntax checks passed; full pytest execution depends on local dependency installation (`pytest` available in environment).
- Reliability behavior observed: plans degrade gracefully under tight constraints and emit lower reliability warnings when required tasks cannot fully fit.

## 8. Safety, Risks, and Mitigations
### Risks
- Over-trust in generated plans for medical-sensitive situations
- Incomplete or biased recommendations when knowledge base/context is sparse

### Mitigations
- Explicit warning that output is planning support, not diagnosis
- Guardrails for invalid inputs
- Logging to `app.log` for traceability
- Human-in-the-loop review via displayed evidence + explanations

## 9. Fairness and Bias Considerations
- Recommendations may reflect biases or incompleteness in the knowledge base and user-provided notes.
- The system currently does not perform demographic fairness optimization; it is a task planner, not a predictive classifier.

## 9.1 Required Reflection Prompts
### Limitations or biases in the system
- The planning engine is rule-based and can miss nuanced pet-care context not explicitly encoded in tasks/notes.
- RAG output quality depends on the quality and breadth of `assets/knowledge_base/pet_care_kb.txt` and user-entered notes.
- Reliability score is useful for risk signaling but is not a clinical confidence guarantee.

### Could the AI be misused, and prevention approach
- Misuse risk: treating planning output as veterinary diagnosis or relying on low-reliability recommendations without review.
- Mitigations: guardrails for invalid inputs, evidence display, reliability warnings, and logging (`app.log`) for traceability.
- Human override expectation: owners should validate recommendations and consult veterinarians for medical decisions.

### What was surprising while testing reliability
- Small time-budget changes can significantly alter feasible plans and reliability score.
- The system can produce plausible guidance even with weak context, which reinforced the need to show retrieval evidence alongside recommendations.

### AI collaboration reflection
- Helpful suggestion: AI-assisted scaffolding of OOP modules accelerated implementation of `User`, `Pet`, `Task`, and `Schedule` components.
- Flawed suggestion: an early AI direction underemphasized edge-case testing; adding targeted tests for infeasible required workloads improved correctness and confidence.

## 10. Human Oversight
Users are expected to review:
- Final schedule
- Reliability score
- Retrieved evidence
before acting on recommendations.

## 11. Versioning
- Project: PawPal+ extended AI engineering version
- Date: April 29, 2026
- Runtime: Python + Streamlit

## 12. Contact / Maintenance
Maintainer: Project author (repository owner). Update this card when model logic, knowledge base, or safety policies change.
