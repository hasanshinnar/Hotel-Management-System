# Hotel Management System — IBM Dev Day: Bob Edition

> **Forked & modernized from [idaljeetsingh/Hotel-Management-System](https://github.com/idaljeetsingh/Hotel-Management-System)** as part of the **[IBM](https://www.linkedin.com/company/ibm/) Dev Day: Bob Edition Hackathon**.
>
> The original project was a C++ console application using TurboC++ and flat-file (`.DAT`) storage. This fork transforms it into a modern, AI-powered Python system with an autonomous agent architecture built using IBM's Bob.

---

## What Changed

| Area           | Original (C++)         | This Fork (Python + AI)    |
| -------------- | ---------------------- | -------------------------- |
| Language       | C++ (TurboC++)         | Python 3                   |
| Storage        | Flat `.DAT` files      | Structured data layer      |
| Architecture   | Monolithic console app | Modular, agent-based       |
| AI Integration | None                   | IBM Bob autonomous agent   |
| Resolution     | Fixed 640×480          | Terminal/platform agnostic |
| Extensibility  | Limited                | Pluggable agent core       |

---

## Features

- **Room Booking** — Check in guests with full record tracking
- **Customer Lookup** — Retrieve guest records by room number
- **Room Overview** — View all currently allocated rooms at a glance
- **Record Editing** — Update customer information seamlessly
- **Autonomous Agent** — IBM Bob-powered agent core for intelligent task handling
- **Configuration-driven** — Central `config.py` for easy environment setup

---

## Project Structure

```
Hotel-Management-System/
├── src/                              # Core application source
├── autonomous_agent/
│   └── core/                         # IBM Bob agent integration
├── Screenshots/                      # UI screenshots (original C++ app)
├── config.py                         # App configuration
├── example_usage.py                  # Usage examples & demos
├── requirements.txt                  # Python dependencies
├── AI_AGENT_GUIDE.md                 # Guide to the agent system
├── ARCHITECTURE.md                   # System architecture overview
├── AUTONOMOUS_AGENT_ARCHITECTURE.md  # Agent architecture deep-dive
├── MODERNIZATION_ANALYSIS.md         # C++ → Python analysis
├── MODERNIZATION_JOURNEY_SUMMARY.md  # Full modernization journey
└── SOURCE.CPP                        # Original C++ source (preserved)
```

---

### Prerequisites

- Python 3.8+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/hasanshinnar/Hotel-Management-System.git
cd Hotel-Management-System

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
python example_usage.py
```

To customize behavior, edit `config.py` before running.

---

## 🤖 IBM Bob Agent

This project was built for the **IBM Dev Day: Bob Edition** hackathon. The autonomous agent layer lives in `autonomous_agent/core/` and leverages IBM's Bob to handle hotel management tasks intelligently.

For a full breakdown of the agent system, see:

- [`AI_AGENT_GUIDE.md`](./AI_AGENT_GUIDE.md)
- [`AUTONOMOUS_AGENT_ARCHITECTURE.md`](./AUTONOMOUS_AGENT_ARCHITECTURE.md)

---

## 📸 Screenshots (Original C++ App)

These screenshots are from the original TurboC++ interface, preserved here for reference.

| Main Menu               | Room Booking            | Room Records            |
| ----------------------- | ----------------------- | ----------------------- |
| ![1](Screenshots/1.png) | ![2](Screenshots/2.png) | ![3](Screenshots/3.png) |

---

## 📖 Modernization Journey

Curious how a 640×480 TurboC++ app became a Python AI system? Read the full story:

- [`MODERNIZATION_ANALYSIS.md`](./MODERNIZATION_ANALYSIS.md) — Technical comparison and decisions
- [`MODERNIZATION_JOURNEY_SUMMARY.md`](./MODERNIZATION_JOURNEY_SUMMARY.md) — The full journey, challenges, and outcomes
- [`ARCHITECTURE.md`](./ARCHITECTURE.md) — Final system architecture

---

## 🙌 Credits

- **Original project:** [idaljeetsingh/Hotel-Management-System](https://github.com/idaljeetsingh/Hotel-Management-System)
- **Modernized by:** [hasanshinnar](https://github.com/hasanshinnar) for the IBM Dev Day: Bob Edition Hackathon
- **Powered by:** [IBM](https://www.linkedin.com/company/ibm/) Bob

---

## 📄 License

This project is based on an open-source C++ project. Modernized code is provided as-is for hackathon and educational purposes.
