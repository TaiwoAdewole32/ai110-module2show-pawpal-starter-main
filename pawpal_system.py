from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    foodType: str
    medication: str
    energyLevel: int
    careNeeds: list[str] = field(default_factory=list)

    def addCareNeed(self, need: str) -> None:
        pass

    def getPetSummary(self) -> str:
        pass


@dataclass
class Task:
    taskName: str
    taskType: str
    durationMinutes: int
    priority: str
    pet: Pet
    preferredTime: str
    completed: bool = False
    notes: str = ""

    def markComplete(self) -> None:
        pass

    def updateTask(self, field: str, value: str) -> None:
        pass

    def getTaskSummary(self) -> str:
        pass


class Owner:
    def __init__(
        self,
        name: str,
        availableMinutes: int,
        preferences: dict[str, str],
        pets: Optional[list[Pet]] = None,
    ) -> None:
        self.name = name
        self.availableMinutes = availableMinutes
        self.preferences = preferences
        self.pets: list[Pet] = pets if pets is not None else []

    def addPet(self, pet: Pet) -> None:
        pass

    def updatePreferences(self, prefs: dict[str, str]) -> None:
        pass

    def getAvailableTime(self) -> int:
        pass


class Scheduler:
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
        pass

    def editTask(self, task: Task) -> None:
        pass

    def generatePlan(self) -> list[Task]:
        pass

    def sortTasksByPriority(self) -> list[Task]:
        pass

    def detectConflicts(self) -> list[Task]:
        pass

    def explainPlan(self) -> str:
        pass
