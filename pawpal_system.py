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
        """Append a care need string to this pet's careNeeds list."""
        self.careNeeds.append(need)

    def getPetSummary(self) -> str:
        """Return a single-line summary of the pet's key attributes."""
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
    preferredTime: str # in "HH:MM" 24-hour format
    completed: bool = False
    notes: str = ""
    taskId: str = dc_field(default_factory=lambda: str(uuid.uuid4()))

    def markComplete(self) -> None:
        """Mark this task as completed by setting completed to True."""
        self.completed = True

    def updateTask(self, field_name: str, value: Any) -> None:
        """Update a single task field by name if it exists on the task."""
        if hasattr(self, field_name):
            setattr(self, field_name, value)

    def getTaskSummary(self) -> str:
        """Return a single-line summary of the task including priority, timing, and status."""
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
    _PRIORITY_ORDER = {
        Priority.HIGH: 3,
        Priority.MEDIUM: 2,
        Priority.LOW: 1
    }

    def __init__(
        self,
        tasks: Optional[list[Task]] = None,
        timeAvailable: int = 0,
        dailyPlan: Optional[list[Task]] = None,
        unscheduledTasks: Optional[list[Task]] = None,
        ownerName: str = "",
    ) -> None:
        self.tasks: list[Task] = tasks if tasks is not None else []
        self.timeAvailable = timeAvailable
        self.dailyPlan: list[Task] = dailyPlan if dailyPlan is not None else []
        self.unscheduledTasks: list[Task] = (
            unscheduledTasks if unscheduledTasks is not None else []
        )
        self.ownerName = ownerName

    def addTask(self, task: Task) -> None:
        """Add a task to the scheduler and register it on the associated pet."""
        self.tasks.append(task)
        if task not in task.pet.tasks:
            task.pet.tasks.append(task)

    def editTask(self, task: Task) -> None:
        """Replace the stored task matching task.taskId in both the scheduler and the pet."""
        for i, stored_task in enumerate(self.tasks):
            if stored_task.taskId == task.taskId:
                self.tasks[i] = task

                for j, pet_task in enumerate(task.pet.tasks):
                    if pet_task.taskId == task.taskId:
                        task.pet.tasks[j] = task
                        break

                return

    def generatePlan(self) -> list[Task]:
        """Build a daily plan by greedily fitting highest-priority tasks within available time."""
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

        self.dailyPlan.sort(key=lambda task: task.preferredTime)
        return self.dailyPlan

    def sortTasksByPriority(self) -> list[Task]:
        """Return all tasks sorted from highest to lowest priority."""
        return sorted(
            self.tasks,
            key=lambda task: self._PRIORITY_ORDER.get(task.priority, 0),
            reverse=True,
        )

    def detectConflicts(self) -> list[Task]:
        """Return all tasks whose time windows overlap with at least one other task."""
        from datetime import datetime, timedelta

        def parse_time(time_string: str) -> Optional[datetime]:
            try:
                return datetime.strptime(time_string, "%H:%M")
            except ValueError:
                return None

        timed_tasks = [
            (task, parse_time(task.preferredTime))
            for task in self.tasks
        ]

        timed_tasks = [
            (task, start)
            for task, start in timed_tasks
            if start is not None
        ]

        conflicts: dict[str, Task] = {}

        for i, (task_a, start_a) in enumerate(timed_tasks):
            end_a = start_a + timedelta(minutes=task_a.durationMinutes)

            for task_b, start_b in timed_tasks[i + 1:]:
                end_b = start_b + timedelta(minutes=task_b.durationMinutes)

                if start_a < end_b and start_b < end_a:
                    conflicts[task_a.taskId] = task_a
                    conflicts[task_b.taskId] = task_b

        return list(conflicts.values())

    def explainPlan(self) -> str:
        """Return a daily plan grouped by pet, including unscheduled tasks."""
        if not self.dailyPlan:
            return "No plan generated yet. Call generatePlan() first."

        total_minutes = sum(task.durationMinutes for task in self.dailyPlan)

        if self.ownerName:
            heading = f"Daily plan for {self.ownerName}'s pets"
        else:
            heading = "Daily plan"

        lines = [
            f"{heading} — {len(self.dailyPlan)} task(s), "
            f"{total_minutes} of {self.timeAvailable} min used:"
        ]

        tasks_by_pet: dict[str, list[Task]] = {}
        pet_labels: dict[str, str] = {}

        for task in self.dailyPlan:
            pet_key = task.pet.name
            tasks_by_pet.setdefault(pet_key, []).append(task)

            if task.pet.breed:
                pet_labels[pet_key] = f"{task.pet.name} ({task.pet.breed})"
            else:
                pet_labels[pet_key] = f"{task.pet.name} ({task.pet.species})"

        for pet_key, pet_tasks in tasks_by_pet.items():
            lines.append(f"\n{pet_labels[pet_key]}:")

            sorted_pet_tasks = sorted(
                pet_tasks,
                key=lambda task: task.preferredTime
            )

            for task in sorted_pet_tasks:
                lines.append(
                    f"  {task.preferredTime} — {task.taskName} "
                    f"({task.durationMinutes} min) "
                    f"[priority: {task.priority.value}]"
                )

        if self.unscheduledTasks:
            lines.append(
                f"\nNot scheduled "
                f"({len(self.unscheduledTasks)} task(s) — insufficient time):"
            )

            for task in self.unscheduledTasks:
                lines.append(
                    f"  - {task.taskName} for {task.pet.name} "
                    f"({task.durationMinutes} min) "
                    f"[priority: {task.priority.value}]"
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
        """Add a pet to this owner's list of pets."""
        self.pets.append(pet)

    def updatePreferences(self, prefs: dict[str, str]) -> None:
        """Merge the given preferences into the owner's existing preferences."""
        self.preferences.update(prefs)

    def getAvailableTime(self) -> int:
        """Return the number of minutes the owner has available for pet care."""
        return self.availableMinutes
