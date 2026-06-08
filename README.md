# AI-Health-Assistant
#  AI Health Assistant

**A standalone, offline AI agent for symptom checking and lab report interpretation**  
*University of Engineering and Technology, Taxila*  
**Student:** Romaisa Abbasi (23-SE-036)  
**Supervisor:** Dr. Kanwal Yousaf  

---

##  Overview

The AI Health Assistant is a rule‑based system that helps users:
- **Check symptoms** (e.g., fever, cough, fatigue) and get possible disease matches along with self‑care advice.
- **Interpret lab reports** – paste test results (e.g., `Hemoglobin: 11.2 g/dL`) and receive explanations, deviation percentages, and diet/lifestyle recommendations.

It runs entirely **offline**, requires **no internet** (after loading the page), and respects your privacy – no data leaves your computer.

---

##  Features

- Symptom‑based disease detection (11 common conditions: flu, UTI, migraine, diabetes, etc.)
- Lab test analysis (30+ parameters: glucose, cholesterol, vitamin D, TSH, liver enzymes, etc.)
- Personalised dietary & lifestyle advice
- Responsive web interface (works on desktop and mobile)
- History of past analyses (saved in browser localStorage)
- No external APIs – pure Python + HTML/CSS/JS

---

##  How to Run

### Prerequisites
- Windows (7/10/11) with **Python 3.7+** installed.  
  *To check: open Command Prompt and type `python --version`.*

### Steps

1. **Download or clone this repository**  
   ```bash
   git clone https://github.com/your-username/ai-health-assistant.git
   cd ai-health-assistant
