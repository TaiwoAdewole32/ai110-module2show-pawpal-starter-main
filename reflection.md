# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

My initial UML design includes four main classes: Owner, Pet, Task, and Scheduler. The Owner class is responsible for storing basic owner information, preferences, available time, and the pets that belong to the owner. The Pet class is responsible for storing pet information such as name, breed, food needs, medication notes, and other care details. The Task class represents one care activity that needs to be completed, such as feeding, walking, grooming, or medication, and stores details like duration, priority, task type, and completion status. The Scheduler class is responsible for organizing tasks into a daily plan based on priority, available time, and possible conflicts between tasks. Overall, the design separates information storage from scheduling logic so that each class has a clear responsibility.


**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

I did change my design during implementation. A change I made was adding a unique ID to the task case because editTask() method would not be able to locate the task to make changes. 

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
