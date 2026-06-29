from __future__ import annotations
from dataclasses import dataclass, field as dc_field
from enum import Enum
from typing import Any, Optional
import uuid


class Priority(str, Enum):
    LOW    = "low"
    MEDIUM = "medium"
    HIGH   = "high"


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    foodType: str
    medication: str
    energyLevel: int
    careNeeds: list[str] = dc_field(default_factory=list)
    tasks: list[Task] = dc_field(default_factory=list)

    def addCareNeed(self, need: str) -> None:
        self.careNeeds.append(need)

    def getPetSummary(self) -> str:
        meds = self.medication or "none"
        needs = ", ".join(self.careNeeds) if self.careNeeds else "none"
        return (
            f"{self.name} ({self.breed}, {self.species}) | "
            f"Age: {self.age} | Food: {self.foodType} | "
            f"Medication: {meds} | Energy: {self.energyLevel}/10 | "
            f"Care needs: {needs}"
        )


@dataclass
class Task:
    taskName: str
    taskType: str
    durationMinutes: int
    priority: Priority
    pet: Pet
    preferredTime: str      # "HH:MM" format, e.g. "09:00"
    completed: bool = False
    notes: str = ""
    taskId: str = dc_field(default_factory=lambda: str(uuid.uuid4()))

    def markComplete(self) -> None:
        self.completed = True

    def updateTask(self, field_name: str, value: Any) -> None:
        if hasattr(self, field_name):
            setattr(self, field_name, value)

    def getTaskSummary(self) -> str:
        status = "done" if self.completed else "pending"
        summary = (
            f"[{self.priority.value.upper()}] {self.taskName} ({self.taskType}) | "
            f"{self.durationMinutes} min @ {self.preferredTime} | "
            f"Pet: {self.pet.name} | Status: {status}"
        )
        if self.notes:
            summary += f" | Notes: {self.notes}"
        return summary


class Scheduler:
    _PRIORITY_ORDER = {Priority.HIGH: 3, Priority.MEDIUM: 2, Priority.LOW: 1}

    def __init__(
        self,
        tasks: Optional[list[Task]] = None,
        timeAvailable: int = 0,
        dailyPlan: Optional[list[Task]] = None,
        unscheduledTasks: Optional[list[Task]] = None,
    ) -> None:
        self.tasks: list[Task] = tasks if tasks is not None else []
        self.timeAvailable = timeAvailable
        self.dailyPlan: list[Task] = dailyPlan if dailyPlan is not None else []
        self.unscheduledTasks: list[Task] = unscheduledTasks if unscheduledTasks is not None else []

    def addTask(self, task: Task) -> None:
        self.tasks.append(task)
        if task not in task.pet.tasks:
            task.pet.tasks.append(task)

    def editTask(self, task: Task) -> None:
        """Replace the stored task that shares task.taskId with the updated version."""
        for i, t in enumerate(self.tasks):
            if t.taskId == task.taskId:
                self.tasks[i] = task
                for j, pt in enumerate(task.pet.tasks):
                    if pt.taskId == task.taskId:
                        task.pet.tasks[j] = task
                        break
                return

    def generatePlan(self) -> list[Task]:
        """Greedily fill the plan highest-priority first; remainder goes to unscheduledTasks."""
        sorted_tasks = self.sortTasksByPriority()
        self.dailyPlan = []
        self.unscheduledTasks = []
        remaining = self.timeAvailable
        for task in sorted_tasks:
            if task.durationMinutes <= remaining:
                self.dailyPlan.append(task)
                remaining -= task.durationMinutes
            else:
                self.unscheduledTasks.append(task)
        self.dailyPlan.sort(key=lambda t: t.preferredTime)
        return self.dailyPlan

    def sortTasksByPriority(self) -> list[Task]:
        return sorted(
            self.tasks,
            key=lambda t: self._PRIORITY_ORDER.get(t.priority, 0),
            reverse=True,
        )

    def detectConflicts(self) -> list[Task]:
        """Return any tasks whose time windows overlap with another task."""
        from datetime import datetime, timedelta

        def parse_time(t_str: str) -> Optional[datetime]:
            try:
                return datetime.strptime(t_str, "%H:%M")
            except ValueError:
                return None

        timed = [(task, parse_time(task.preferredTime)) for task in self.tasks]
        timed = [(task, start) for task, start in timed if start is not None]

        seen: dict[str, Task] = {}
        for i, (task_a, start_a) in enumerate(timed):
            end_a = start_a + timedelta(minutes=task_a.durationMinutes)
            for task_b, start_b in timed[i + 1:]:
                end_b = start_b + timedelta(minutes=task_b.durationMinutes)
                if start_a < end_b and start_b < end_a:
                    seen[task_a.taskId] = task_a
                    seen[task_b.taskId] = task_b

        return list(seen.values())

    def explainPlan(self) -> str:
        if not self.dailyPlan:
            return "No plan generated yet. Call generatePlan() first."

        total_min = sum(t.durationMinutes for t in self.dailyPlan)
        lines = [
            f"Daily plan — {len(self.dailyPlan)} task(s), "
            f"{total_min} of {self.timeAvailable} min used:"
        ]
        for i, task in enumerate(self.dailyPlan, 1):
            lines.append(
                f"  {i}. {task.preferredTime}  {task.taskName} "
                f"({task.durationMinutes} min) [{task.priority.value}] — {task.pet.name}"
            )

        if self.unscheduledTasks:
            lines.append(
                f"\nNot scheduled ({len(self.unscheduledTasks)} task(s) — insufficient time):"
            )
            for task in self.unscheduledTasks:
                lines.append(
                    f"  - {task.taskName} ({task.durationMinutes} min) [{task.priority.value}]"
                )

        return "\n".join(lines)


class Owner:
    def __init__(
        self,
        name: str,
        availableMinutes: int,
        preferences: dict[str, str],
        pets: Optional[list[Pet]] = None,
        scheduler: Optional[Scheduler] = None,
    ) -> None:
        self.name = name
        self.availableMinutes = availableMinutes
        self.preferences = preferences
        self.pets: list[Pet] = pets if pets is not None else []
        self.scheduler: Scheduler = (
            scheduler if scheduler is not None
            else Scheduler(timeAvailable=availableMinutes)
        )

    def addPet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def updatePreferences(self, prefs: dict[str, str]) -> None:
        self.preferences.update(prefs)

    def getAvailableTime(self) -> int:
        return self.availableMinutes
