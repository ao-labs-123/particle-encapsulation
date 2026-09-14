# Current Phase:Particle Encapsulation
Deterministic engine that encapsulates structured context logs into algebraic particle objects.⁠

<img width="960" height="540" alt="image" src="https://github.com/user-attachments/assets/10de3e8f-6ca9-45a6-b8f8-269ce818a3f5" />


## Core Data Model (⁠Particle⁠)
Each encapsulated concept or relation is structured as a ⁠Particle⁠ dataclass with the following attributes:
- ⁠id⁠: Unique identifier (e.g., ⁠p_agent_f06dbc⁠)
- ⁠label⁠: Extracted text content (e.g., ⁠"I"⁠, ⁠"you helped"⁠, ⁠"i succeeded"⁠)
- ⁠type⁠: Entity classification (⁠Agent⁠, ⁠Cause⁠, ⁠Effect⁠, etc.)
- ⁠state⁠: Deterministic resolution state (⁠determined⁠ / ⁠unspecified⁠)
- ⁠constraints⁠: Logical rules applied during extraction
- ⁠properties⁠: Contextual properties and metadata
Quick Start
1. Prerequisites
 Python 3.10+
2. Execution
Run the main script to ingest ⁠log.json⁠ and generate ⁠particle.json⁠:
python main.py

3. Output
The engine will parse the input log and export the encapsulated particle cloud into ⁠particle.json⁠.
