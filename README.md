# 🤖 AI Health Assistant - STANDALONE VERSION (No pip install!)

> **Works with ONLY Python standard library - NO internet needed!**
> 
> **University of Engineering and Technology, Taxila**  
> **Student:** Romaisa Abbasi (23-SE-036)  
> **Supervisor:** Dr. Kanwal Yousaf

---

## ⚡ QUICK START (Just 2 Steps!)

### Step 1: Open in VS Code
1. Download and extract the ZIP
2. Open VS Code
3. Go to **File → Open Folder** → Select the extracted folder

### Step 2: Run (NO pip install needed!)
1. Open terminal in VS Code: `` Ctrl + ` ``
2. Type:
```bash
python app.py
```
3. Open browser: `http://127.0.0.1:5000`

That's it! 🎉

---

## ❓ Why Standalone?

Your university/lab computer has **no internet access** for pip. This version:
- ✅ **NO pip install required**
- ✅ **NO external packages** (Flask, Gemini API, etc.)
- ✅ **Uses only Python built-in libraries**
- ✅ **Works completely offline**
- ✅ **Same features as the full version!**

---

## 🎯 Features

| Feature | Description |
|---------|-------------|
| **🗨️ Health Chat** | Ask health questions, get AI-powered answers |
| **🔬 Lab Report Analyzer** | Paste lab report → get structured analysis |
| **📊 25+ Parameters** | Hemoglobin, Glucose, Cholesterol, LDL, HDL, WBC, RBC, Platelet, Creatinine, BUN, Uric Acid, Sodium, Potassium, Calcium, Vitamin D, B12, Ferritin, TSH, ALT, AST, Bilirubin, ESR, CRP, HbA1c, BP |
| **✅ Status Detection** | Normal / High / Low with color coding |
| **📈 Deviation %** | Percentage deviation from normal range |
| **💡 Explanations** | Simple, easy-to-understand medical explanations |
| **🥗 Recommendations** | Dietary and lifestyle advice for each parameter |
| **📋 Sample Reports** | 6 pre-loaded templates (Anemia, Diabetes, Lipid, Thyroid, Liver, Comprehensive) |
| **💾 History** | Saves analyses locally in browser |
| **📱 Responsive** | Works on desktop, tablet, mobile |

---

## 📝 How to Use

### 1. Health Chat
- Type any health question
- Press **Enter** to send
- Get instant AI response

### 2. Lab Report Analysis
- Click **"Lab Analyzer"** in sidebar
- Paste your lab report OR click a **Sample Report**
- Click **"Analyze Report"**
- View structured results with:
  - Color-coded status (Green=Normal, Yellow=Low, Red=High)
  - Deviation percentage
  - Medical explanation
  - Dietary recommendations
  - Lifestyle advice

### 3. Input Format
```
Hemoglobin: 11.5 g/dL
Glucose: 95 mg/dL
Cholesterol: 220 mg/dL
WBC: 8.5 K/uL
Platelet: 180 K/uL
Creatinine: 1.2 mg/dL
ALT: 45 U/L
Vitamin D: 18 ng/mL
TSH: 5.2 mIU/L
Blood Pressure: 140/90 mmHg
```

---

## 🏗️ System Architecture

```
User Input (Lab Report Text)
        ↓
Text Preprocessing (Regex Parsing)
        ↓
Medical Knowledge Base (25+ Parameters)
        ↓
AI Analysis Engine (Python Logic)
        ↓
Response Generation (Structured Output)
        ↓
Formatted Display (Web Interface)
```

---

## 🛠️ Technologies (All Built-in!)

| Technology | Purpose | Built-in? |
|------------|---------|-----------|
| **Python 3** | Backend logic | ✅ Yes |
| **http.server** | Web server | ✅ Yes |
| **socketserver** | TCP handling | ✅ Yes |
| **json** | Data exchange | ✅ Yes |
| **re** | Text parsing (NLP) | ✅ Yes |
| **datetime** | Timestamps | ✅ Yes |
| **HTML5/CSS3** | Frontend UI | ✅ Yes (embedded) |
| **JavaScript** | Interactivity | ✅ Yes (embedded) |

**Zero external dependencies!**

---

## 📁 File Structure

```
ai-health-assistant-standalone/
│
└── app.py          ← SINGLE FILE with everything!
                    (Python backend + embedded HTML/CSS/JS)
```

---

## 🎓 Academic Details

- **Institution:** University of Engineering and Technology, Taxila
- **Faculty:** Telecommunication and Information Engineering
- **Department:** Software Engineering
- **Course:** Artificial Intelligence (AI)
- **Assignment:** Task-2 (Project Module-2)
- **CLO Mapping:** CLO-2, CLO-3
- **Student:** Romaisa Abbasi (23-SE-036)
- **Supervisor:** Dr. Kanwal Yousaf

---

## ⚠️ Medical Disclaimer

This AI Health Assistant is for **informational and educational purposes ONLY**. It is **NOT** a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider.

---

**Made with ❤️ at UET Taxila**
