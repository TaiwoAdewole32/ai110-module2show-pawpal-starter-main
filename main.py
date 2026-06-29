from pawpal_system import Pet, Priority, Task, Owner

def main():
    # Create an owner with available time and preferences
    owner = Owner(
        name="Alice",
        availableMinutes=120,
        preferences={"morning": "walk", "afternoon": "feed"}
    )

    # Create pets
    pet1 = Pet(name="Buddy", species="Dog", breed="Golden Retriever", age=5, foodType="Dry", medication="None", energyLevel=7)
    pet2 = Pet(name="Mittens", species="Cat", breed="", age=3, foodType="Wet", medication="None", energyLevel=2)

    # Add pets to the owner
    owner.addPet(pet1)
    owner.addPet(pet2)

    # Create tasks for the pets
    task1 = Task(taskId="1", taskType="walk", taskName="Walk Buddy", durationMinutes=30, priority=Priority.HIGH, preferredTime="07:00", pet=pet1)
    task2 = Task(taskId="2", taskType="feed", taskName="Feed Mittens", durationMinutes=15, priority=Priority.MEDIUM, preferredTime="12:00", pet=pet2)
    task3 = Task(taskId="3", taskType="play", taskName="Play with Buddy", durationMinutes=20, priority=Priority.LOW, preferredTime="18:00", pet=pet1)

    # Add tasks to the scheduler
    owner.scheduler.addTask(task1)
    owner.scheduler.addTask(task2)
    owner.scheduler.addTask(task3)

    # Generate the daily plan
    owner.scheduler.generatePlan()

    # Print the explanation of the plan
    print(owner.scheduler.explainPlan())

if __name__ == "__main__":
    main()

