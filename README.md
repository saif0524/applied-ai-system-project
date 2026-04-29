# PawPal+ Smart Pet Care Manager

## Original Project (Modules 1-3)
My original project from Modules 1-3 was **PawPal+**, a Streamlit pet care planning app focused on organizing daily care tasks like walks, feeding, and medications. Its initial goals were to model owner/pet/task information and generate a daily schedule under time and priority constraints. In this extended version, I evolved that foundation into a fuller AI engineering system with integrated RAG, agentic scheduling, reliability scoring, and stronger guardrails/logging.

## Title and Summary
**PawPal+** is a smart pet care management system that builds a practical daily care plan for a pet owner. It tracks tasks like feeding, walks, medications, grooming, and enrichment, then prioritizes and schedules them under real constraints such as available time and required tasks. This matters because it turns a messy to-do list into a structured, explainable care routine.

## Architecture Overview
PawPal+ uses a modular OOP backend in `pawpal_system.py` and a Streamlit frontend in `app.py`.
- `User`, `Pet`, `Task` model the core domain.
- `Schedule.generate_plan()` runs an **agentic workflow**: propose an initial plan, evaluate constraints, and repair the plan if needed.
- `Schedule.generate_plan()` also runs **RAG**: it retrieves pet-care guidance from a knowledge base using current pet/task context, then attaches evidence-grounded advice to the final plan.
- A reliability evaluator returns a score and warning messages when the plan is weak.
- Guardrails and logging protect against bad inputs and improve traceability.

System diagram: see `mermaid..js`.

## Setup Instructions
1. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   python3 -m streamlit run app.py
   ```
4. Open the local URL from Streamlit.
5. Enter owner/pet info, add tasks, and click **Build Schedule**.
6. Review the **RAG Guidance** and **Retrieved Knowledge** sections to see evidence used by the assistant.

## Demo Walkthrough
End-to-end walkthrough assets are in `assets/demo/`:
- Screenshot 1: `assets/demo/demo_image_1.png`
- Screenshot 2: `assets/demo/demo_image_2.png`
- Screenshot 3: `assets/demo/demo_image_3.png`

These walkthrough images correspond to the 3 sample interactions below and show:
- user inputs (owner/pet/task constraints),
- generated schedule output,
- AI sections (**RAG Guidance**, **Retrieved Knowledge**, and **Reliability score**).

## Sample Interactions
### Example 1: Balanced Day
Input:
- Available minutes: 90
- Tasks: Walk (30, high), Feed (10, high, required), Medication (10, high, required), Play (20, medium)

Output (representative):
- Plan includes Feed, Medication, Walk, Play (or similar high-value combination)
- Total minutes <= 90
- Reliability score near 1.0 with "Reliability check passed"

### Example 2: Tight Constraint Day
Input:
- Available minutes: 25
- Tasks: Feed (10, required), Long Walk (30), Groom (20)

Output (representative):
- Plan keeps Feed and drops longer optional tasks to fit budget
- Explanation includes removed task reason
- Reliability score medium/high depending on required coverage

### Example 3: Infeasible Required Tasks
Input:
- Available minutes: 10
- Required tasks: Medication (15), Feed (10)

Output (representative):
- Only feasible subset can be scheduled
- Reliability warning shown (score < 0.7)
- Explanation indicates constraint conflict

## Design Decisions
1. **OOP domain modeling** (`User`, `Pet`, `Task`, `Schedule`) keeps logic modular and maintainable.
2. **Agentic workflow integration** makes planning adaptive: the system plans, self-checks constraints, then repairs the schedule.
3. **Reliability scoring** is part of main behavior so users can judge plan confidence.
4. **Guardrails + logging** improve safety and debuggability.
5. **RAG integration** improves recommendation quality by retrieving relevant care references before generating guidance.

Trade-offs:
- Rule-based planning is transparent and deterministic but less personalized than ML-based optimization.
- Reliability score is heuristic, not a clinical guarantee.
- Time-only optimization is simple; future versions could model exact time windows and travel constraints.

## Testing Summary
Automated tests cover key scheduling and reliability behaviors:
- frequency filtering (`weekdays` excludes Sunday)
- required-task prioritization
- strict daily time budget compliance
- reliability score drop when required workload is infeasible

In one sandbox environment, tests could not run until `pytest` was installed; syntax checks passed. The test suite helped confirm the algorithm is deterministic and exposes edge-case failures clearly.

## Reflection
This project taught me that AI engineering is about system behavior, not just model output. Building PawPal+ required combining OOP design, algorithmic planning, safety checks, reliability metrics, and user-facing explanations into one coherent workflow. I learned that explainability and constraint handling are just as important as “smartness” when users depend on daily recommendations.

## Responsible AI Reflection
### What are the limitations or biases in your system?
- The scheduler is rule-based, so it may miss nuanced care needs that are not explicitly represented in task inputs.
- RAG quality depends on the built-in knowledge base and user-provided context; if either is incomplete, recommendations can be biased or shallow.
- Reliability score is a heuristic, not a clinical or veterinary guarantee.

### Could your AI be misused, and how would you prevent that?
- Misuse risk: over-trusting suggestions as medical advice, or asking unsafe prompt-injection style questions.
- Mitigations: input guardrails, explicit reliability warnings, transparent evidence display, and logging (`app.log`) for review.
- Product boundary: recommendations should be treated as planning support, not diagnosis; urgent health decisions should go to a veterinarian.

### What surprised you while testing your AI's reliability?
- Small changes in available minutes can cause large shifts in feasible plans.
- Answers can sound confident even when evidence is weak, which is why surfacing retrieved evidence next to guidance was important.

### Collaboration with AI during this project
- Helpful suggestion: AI-assisted scaffolding of modular OOP components (`User`, `Pet`, `Task`, `Schedule`) sped up implementation and testing.
- Flawed suggestion: an early AI suggestion focused on generic behavior without enough edge-case testing; adding tests for infeasible required tasks and time-budget limits exposed and fixed that gap.
