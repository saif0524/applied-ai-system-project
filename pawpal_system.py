"""Core classes for the PawPal+ scheduling system.

Implements OOP models plus an agentic scheduling workflow:
1) propose an initial plan
2) evaluate constraint violations
3) repair plan until valid or no further improvements
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
import logging
from typing import Any, Dict, List, Optional, Tuple

from pawpal_rag import build_rag_guidance, retrieve_pet_knowledge

logger = logging.getLogger(__name__)


PRIORITY_WEIGHT = {"low": 1, "medium": 2, "high": 3}


@dataclass
class User:
    """Represents a pet owner's profile and planning preferences."""

    name: str
    available_minutes_per_day: int
    preferences: Dict[str, Any] = field(default_factory=dict)

    def update_preferences(self, preferences: Dict[str, Any]) -> None:
        self.preferences.update(preferences)


@dataclass
class Pet:
    """Represents pet profile data used for scheduling decisions."""

    name: str
    species: str
    age: int
    health_notes: str = ""

    def update_profile(
        self,
        name: Optional[str] = None,
        species: Optional[str] = None,
        age: Optional[int] = None,
        health_notes: Optional[str] = None,
    ) -> None:
        if name is not None:
            self.name = name
        if species is not None:
            self.species = species
        if age is not None:
            self.age = age
        if health_notes is not None:
            self.health_notes = health_notes


@dataclass
class Task:
    """Represents a care task that may be included in a daily schedule."""

    title: str
    duration_min: int
    priority: str
    frequency: str
    is_required: bool = False
    earliest_time: Optional[str] = None
    latest_time: Optional[str] = None
    notes: str = ""

    def edit_task(
        self,
        title: Optional[str] = None,
        duration_min: Optional[int] = None,
        priority: Optional[str] = None,
        frequency: Optional[str] = None,
        is_required: Optional[bool] = None,
        earliest_time: Optional[str] = None,
        latest_time: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> None:
        if title is not None:
            self.title = title
        if duration_min is not None:
            self.duration_min = duration_min
        if priority is not None:
            self.priority = priority
        if frequency is not None:
            self.frequency = frequency
        if is_required is not None:
            self.is_required = is_required
        if earliest_time is not None:
            self.earliest_time = earliest_time
        if latest_time is not None:
            self.latest_time = latest_time
        if notes is not None:
            self.notes = notes

    def is_valid_for_day(self, target_day: date) -> bool:
        """Return whether this task should be considered on a given day."""
        weekday = target_day.weekday()
        f = self.frequency.lower()

        if f == "daily":
            return True
        if f == "weekdays":
            return weekday < 5
        if f == "weekends":
            return weekday >= 5
        if f == "monday":
            return weekday == 0
        if f == "tuesday":
            return weekday == 1
        if f == "wednesday":
            return weekday == 2
        if f == "thursday":
            return weekday == 3
        if f == "friday":
            return weekday == 4
        if f == "saturday":
            return weekday == 5
        if f == "sunday":
            return weekday == 6

        return True

    def priority_score(self) -> int:
        return PRIORITY_WEIGHT.get(self.priority.lower(), 1)


@dataclass
class Schedule:
    """Represents a generated daily plan and explanation trail."""

    target_day: date
    planned_tasks: List[Task] = field(default_factory=list)
    total_minutes_used: int = 0
    explanations: List[str] = field(default_factory=list)
    reliability_score: float = 0.0
    rag_guidance: str = ""
    rag_evidence: List[str] = field(default_factory=list)

    def _guardrail_tasks(self, tasks: List[Task]) -> List[Task]:
        clean: List[Task] = []
        for task in tasks:
            if task.duration_min <= 0:
                logger.warning("Skipping invalid task %s because duration <= 0", task.title)
                self.explanations.append(f"Skipped '{task.title}' due to invalid duration.")
                continue
            clean.append(task)
        return clean

    def _evaluate_plan(self, tasks: List[Task], user: User) -> Tuple[int, int, int]:
        """Returns (required_missing_count, minutes_over_budget, low_priority_count)."""
        planned_titles = {t.title for t in tasks}
        required_missing = sum(1 for t in self._candidate_tasks if t.is_required and t.title not in planned_titles)
        minutes_used = sum(t.duration_min for t in tasks)
        minutes_over = max(0, minutes_used - user.available_minutes_per_day)
        low_priority = sum(1 for t in tasks if t.priority_score() == 1)
        return required_missing, minutes_over, low_priority

    def _initial_plan(self, candidates: List[Task], user: User) -> List[Task]:
        # Sort by required first, then priority, then shorter duration for better fit.
        ranked = sorted(
            candidates,
            key=lambda t: (not t.is_required, -t.priority_score(), t.duration_min),
        )
        plan: List[Task] = []
        minutes = 0
        for task in ranked:
            if minutes + task.duration_min <= user.available_minutes_per_day:
                plan.append(task)
                minutes += task.duration_min
        return plan

    def _repair_plan(self, plan: List[Task], user: User) -> List[Task]:
        """Agentic repair: enforce required tasks and budget by replacing weaker tasks."""
        working = list(plan)
        changed = True

        while changed:
            changed = False
            required_missing, minutes_over, _ = self._evaluate_plan(working, user)

            if required_missing == 0 and minutes_over == 0:
                break

            # Add required tasks if missing by removing weakest existing tasks.
            planned_titles = {t.title for t in working}
            missing_required = [t for t in self._candidate_tasks if t.is_required and t.title not in planned_titles]

            for req in missing_required:
                weakest = sorted(working, key=lambda t: (t.is_required, t.priority_score(), -t.duration_min))
                inserted = False
                for victim in weakest:
                    if victim.is_required:
                        continue
                    candidate_minutes = sum(t.duration_min for t in working) - victim.duration_min + req.duration_min
                    if candidate_minutes <= user.available_minutes_per_day:
                        working.remove(victim)
                        working.append(req)
                        self.explanations.append(
                            f"Replaced '{victim.title}' with required task '{req.title}'."
                        )
                        changed = True
                        inserted = True
                        break
                if not inserted and sum(t.duration_min for t in working) + req.duration_min <= user.available_minutes_per_day:
                    working.append(req)
                    self.explanations.append(f"Added required task '{req.title}'.")
                    changed = True

            # If still over budget, remove lowest value optional tasks.
            while sum(t.duration_min for t in working) > user.available_minutes_per_day:
                optional = [t for t in working if not t.is_required]
                if not optional:
                    break
                victim = sorted(optional, key=lambda t: (t.priority_score(), -t.duration_min))[0]
                working.remove(victim)
                self.explanations.append(
                    f"Removed optional task '{victim.title}' to fit daily time budget."
                )
                changed = True

        return sorted(working, key=lambda t: (not t.is_required, -t.priority_score(), t.duration_min))

    def _compute_reliability(self, plan: List[Task], user: User) -> float:
        required_missing, minutes_over, _ = self._evaluate_plan(plan, user)
        penalty = required_missing * 0.35
        penalty += 0.25 if minutes_over > 0 else 0.0
        if not plan:
            penalty += 0.4
        score = max(0.0, min(1.0, 1.0 - penalty))
        return score

    def generate_plan(
        self,
        tasks: List[Task],
        user: User,
        pet: Pet,
        custom_health_cases: str = "",
    ) -> List[Task]:
        logger.info("Generating plan for %s with %d tasks", pet.name, len(tasks))
        self.explanations = []
        self.rag_guidance = ""
        self.rag_evidence = []

        guarded = self._guardrail_tasks(tasks)
        filtered = [t for t in guarded if t.is_valid_for_day(self.target_day)]
        self._candidate_tasks = filtered  # internal temporary cache for evaluator/repair

        self.explanations.append(f"Considered {len(filtered)} tasks valid for {self.target_day.isoformat()}.")

        initial = self._initial_plan(filtered, user)
        self.explanations.append(f"Initial planner selected {len(initial)} tasks by required/priority fit.")

        repaired = self._repair_plan(initial, user)

        self.planned_tasks = repaired
        self.total_minutes_used = sum(t.duration_min for t in repaired)
        self.reliability_score = self._compute_reliability(repaired, user)

        if self.reliability_score < 0.7:
            self.explanations.append(
                "Reliability warning: plan may be incomplete due to tight time constraints or missing context."
            )
        else:
            self.explanations.append("Reliability check passed for schedule constraints.")

        # RAG is integrated into the core planning output: we retrieve pet-care knowledge
        # using current pet profile and selected tasks, then attach evidence-grounded guidance.
        task_notes_blob = " ".join(t.notes for t in self.planned_tasks if t.notes)
        rag_query = " ".join(
            [
                pet.species,
                pet.health_notes,
                custom_health_cases,
                " ".join(t.title for t in self.planned_tasks),
                task_notes_blob,
                "required tasks priority routine",
            ]
        ).strip()
        retrieved = retrieve_pet_knowledge(rag_query, top_k=2)
        self.rag_evidence = [f"{r.source} (score={r.score:.2f}): {r.text}" for r in retrieved]
        self.rag_guidance = build_rag_guidance(rag_query, retrieved)
        self.explanations.append("RAG guidance attached using retrieved pet-care knowledge.")

        logger.info(
            "Plan generated: tasks=%d minutes=%d reliability=%.2f",
            len(self.planned_tasks),
            self.total_minutes_used,
            self.reliability_score,
        )
        return self.planned_tasks

    def add_task(self, task: Task, user: Optional[User] = None) -> bool:
        if task.duration_min <= 0:
            return False
        if user is not None and self.total_minutes_used + task.duration_min > user.available_minutes_per_day:
            return False
        self.planned_tasks.append(task)
        self.total_minutes_used += task.duration_min
        return True

    def explain_plan(self) -> str:
        if not self.explanations:
            return "No explanation available."
        return "\n".join(self.explanations)
