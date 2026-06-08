#!/usr/bin/env python3
"""
AI Health Assistant - ENHANCED VERSION (No pip install needed!)
University of Engineering and Technology, Taxila
Student: Romaisa Abbasi (23-SE-036)
Supervisor: Dr. Kanwal Yousaf
"""

import http.server
import socketserver
import json
import re
from datetime import datetime

PORT = 5000

# ============================================
# MEDICAL KNOWLEDGE BASE (Full data)
# ============================================
MEDICAL_RANGES = {
    "hemoglobin": {"normal": "12.0-15.5", "unit": "g/dL", "low": "Anemia", "high": "Polycythemia"},
    "glucose": {"normal": "70-100", "unit": "mg/dL", "low": "Hypoglycemia", "high": "Hyperglycemia/Diabetes"},
    "blood sugar": {"normal": "70-100", "unit": "mg/dL", "low": "Hypoglycemia", "high": "Hyperglycemia/Diabetes"},
    "cholesterol": {"normal": "<200", "unit": "mg/dL", "low": "Low cholesterol", "high": "High cholesterol"},
    "total cholesterol": {"normal": "<200", "unit": "mg/dL", "low": "Low cholesterol", "high": "High cholesterol"},
    "ldl": {"normal": "<100", "unit": "mg/dL", "low": "Low LDL", "high": "High LDL"},
    "hdl": {"normal": ">40", "unit": "mg/dL", "low": "Low HDL", "high": "Good HDL"},
    "triglycerides": {"normal": "<150", "unit": "mg/dL", "low": "Low triglycerides", "high": "High triglycerides"},
    "wbc": {"normal": "4.0-11.0", "unit": "K/uL", "low": "Leukopenia", "high": "Leukocytosis"},
    "rbc": {"normal": "4.2-5.4", "unit": "M/uL", "low": "Anemia", "high": "Polycythemia"},
    "platelet": {"normal": "150-450", "unit": "K/uL", "low": "Thrombocytopenia", "high": "Thrombocytosis"},
    "creatinine": {"normal": "0.7-1.3", "unit": "mg/dL", "low": "Low creatinine", "high": "Kidney dysfunction"},
    "urea": {"normal": "7-20", "unit": "mg/dL", "low": "Low urea", "high": "Kidney issues"},
    "bun": {"normal": "7-20", "unit": "mg/dL", "low": "Low BUN", "high": "Kidney issues"},
    "uric acid": {"normal": "3.5-7.2", "unit": "mg/dL", "low": "Low uric acid", "high": "Gout risk"},
    "sodium": {"normal": "135-145", "unit": "mEq/L", "low": "Hyponatremia", "high": "Hypernatremia"},
    "potassium": {"normal": "3.5-5.0", "unit": "mEq/L", "low": "Hypokalemia", "high": "Hyperkalemia"},
    "calcium": {"normal": "8.5-10.5", "unit": "mg/dL", "low": "Hypocalcemia", "high": "Hypercalcemia"},
    "vitamin d": {"normal": "30-100", "unit": "ng/mL", "low": "Vitamin D deficiency", "high": "Vitamin D toxicity"},
    "vitamin b12": {"normal": "200-900", "unit": "pg/mL", "low": "B12 deficiency", "high": "High B12"},
    "ferritin": {"normal": "15-150", "unit": "ng/mL", "low": "Iron deficiency", "high": "Iron overload"},
    "tsh": {"normal": "0.4-4.0", "unit": "mIU/L", "low": "Hyperthyroidism", "high": "Hypothyroidism"},
    "alt": {"normal": "7-56", "unit": "U/L", "low": "Low ALT", "high": "Liver damage"},
    "ast": {"normal": "10-40", "unit": "U/L", "low": "Low AST", "high": "Liver damage"},
    "bilirubin": {"normal": "0.1-1.2", "unit": "mg/dL", "low": "Low bilirubin", "high": "Jaundice"},
    "hba1c": {"normal": "<5.7", "unit": "%", "low": "Low HbA1c", "high": "Diabetes/Prediabetes"},
    "bp": {"normal": "120/80", "unit": "mmHg", "low": "Hypotension", "high": "Hypertension"},
}

RECOMMENDATIONS_LOW = {
    "hemoglobin": "Increase iron-rich foods: spinach, red meat, lentils. Take Vitamin C. Consult doctor.",
    "glucose": "Consume quick sugar immediately. Eat small frequent meals. Monitor blood sugar.",
    "vitamin d": "Get 15-30 min sunlight daily. Take Vitamin D3 supplements (1000-2000 IU).",
    "vitamin b12": "Eat meat, fish, eggs, dairy. For vegetarians: fortified cereals, nutritional yeast.",
    "ferritin": "Eat iron-rich foods with Vitamin C. Avoid tea/coffee with meals.",
    "tsh": "May indicate hyperthyroidism. Consult endocrinologist.",
}

RECOMMENDATIONS_HIGH = {
    "hemoglobin": "Stay hydrated. Avoid iron supplements. Consult hematologist.",
    "glucose": "Reduce sugar and refined carbs. Exercise 30 min daily. Consult doctor.",
    "cholesterol": "Reduce saturated fats. Increase fiber. Exercise daily. Consider statins if >190.",
    "ldl": "Avoid trans fats. Eat soluble fiber (oats, beans). Exercise daily.",
    "triglycerides": "Avoid alcohol and sugary foods. Exercise 30-45 min daily. Eat omega-3 fish.",
    "creatinine": "Reduce protein. Stay hydrated. Avoid NSAIDs. Consult nephrologist.",
    "uric acid": "Limit purine foods, avoid alcohol, drink 3L water daily.",
    "alt": "Avoid alcohol. Reduce fatty foods. Check for hepatitis. Consult gastroenterologist.",
    "bp": "Reduce sodium. Exercise daily. DASH diet. Monitor BP. Consult doctor.",
}

# ============================================
# SYMPTOM-BASED DISEASE DETECTION
# ============================================
SYMPTOM_DISEASE_MAP = {
    "common cold": {"symptoms": ["runny nose", "sneezing", "sore throat", "mild cough", "congestion"], "advice": "Rest, hydrate, use saline spray. See doctor if fever >3 days.", "see_doctor": "High fever, difficulty breathing.", "prevention": "Wash hands frequently."},
    "flu": {"symptoms": ["fever", "body aches", "fatigue", "dry cough", "headache", "chills"], "advice": "Rest, fluids, fever reducers. Antiviral if within 48 hours.", "see_doctor": "Fever >3 days, difficulty breathing.", "prevention": "Annual flu vaccine."},
    "covid-19": {"symptoms": ["fever", "cough", "loss of taste", "loss of smell", "shortness of breath"], "advice": "Isolate, test, rest, monitor oxygen.", "see_doctor": "Difficulty breathing, chest pain.", "prevention": "Vaccination, mask."},
    "migraine": {"symptoms": ["throbbing headache", "light sensitivity", "nausea", "aura"], "advice": "Rest in dark quiet room. Cold compress.", "see_doctor": "Severe/frequent migraines.", "prevention": "Regular sleep, stress management."},
    "uti": {"symptoms": ["painful urination", "frequent urination", "lower abdominal pain", "cloudy urine"], "advice": "Drink plenty water, cranberry juice. Avoid caffeine.", "see_doctor": "Antibiotics needed. Fever or back pain.", "prevention": "Stay hydrated, urinate after intercourse."},
    "acid reflux": {"symptoms": ["stomach pain", "nausea", "bloating", "heartburn", "burning sensation"], "advice": "Small frequent meals. Avoid spicy/fried foods. Don't lie down after eating.", "see_doctor": "Vomiting blood, black stools.", "prevention": "Manage stress, avoid NSAIDs."},
    "hypertension": {"symptoms": ["headache", "dizziness", "blurred vision", "chest discomfort"], "advice": "Reduce sodium (<1500mg/day), DASH diet, exercise 30 min daily.", "see_doctor": "BP >180/120 with symptoms.", "prevention": "Regular BP monitoring."},
    "allergy": {"symptoms": ["sneezing", "itchy eyes", "runny nose", "rash", "hives"], "advice": "Antihistamines, saline rinse. Avoid allergens.", "see_doctor": "Severe reaction, difficulty breathing.", "prevention": "Identify triggers."},
    "anemia": {"symptoms": ["fatigue", "pale skin", "shortness of breath", "cold hands", "dizziness"], "advice": "Eat iron-rich foods with vitamin C. Consider supplements.", "see_doctor": "Chest pain, severe fatigue.", "prevention": "Balanced diet with iron and B12."},
    "diabetes symptoms": {"symptoms": ["excessive thirst", "frequent urination", "blurred vision", "fatigue", "slow healing"], "advice": "Check blood sugar. Reduce sugar and refined carbs. Exercise.", "see_doctor": "Very high blood sugar, confusion.", "prevention": "Healthy weight, regular exercise."},
    "dehydration": {"symptoms": ["thirst", "dry mouth", "dark urine", "dizziness", "fatigue"], "advice": "Drink water or oral rehydration solution.", "see_doctor": "Unable to keep fluids down, confusion.", "prevention": "Drink water regularly."},
}

def detect_disease_from_symptoms(message):
    msg_lower = message.lower()
    scores = {}
    for disease, info in SYMPTOM_DISEASE_MAP.items():
        score = sum(1 for s in info["symptoms"] if s in msg_lower)
        if score > 0:
            scores[disease] = {"score": score, "matched": [s for s in info["symptoms"] if s in msg_lower], "info": info}
    if not scores:
        return None
    best = max(scores, key=lambda d: scores[d]["score"])
    info = scores[best]["info"]
    matched = ", ".join(scores[best]["matched"])
    confidence = "high" if scores[best]["score"] >= 3 else "moderate" if scores[best]["score"] >= 2 else "low"
    return f"**Possible condition:** {best.title()} (confidence: {confidence})\n**Symptoms detected:** {matched}\n\n**What to do:** {info['advice']}\n\n**When to see a doctor:** {info['see_doctor']}\n\n**Prevention:** {info['prevention']}\n\n⚠️ This is AI-generated guidance. Always consult a healthcare professional."

def get_chat_response(message):
    msg_lower = message.lower()
    # Lab report detection
    if re.search(r'\d+\.?\d*\s*(mg/dl|g/dl|u/l|miu/l|mmol/l)', msg_lower):
        return None  # will be handled by lab analyzer
    # Symptom detection
    symptom_keywords = ["fever", "cough", "pain", "ache", "nausea", "vomit", "diarrhea", "fatigue", "headache", "dizzy", "rash", "sore throat", "runny nose", "congestion", "chills", "thirst", "urination"]
    if any(k in msg_lower for k in symptom_keywords):
        disease_response = detect_disease_from_symptoms(message)
        if disease_response:
            return disease_response
        return "I notice you're describing symptoms. Please consult a doctor for accurate diagnosis. Meanwhile, rest, stay hydrated, and monitor your symptoms."
    # General health queries
    if "cholesterol" in msg_lower:
        return "High cholesterol increases heart disease risk. Reduce saturated fats, increase fiber (oats, beans), exercise 30 min daily, and consider statins if LDL >190. Consult your doctor."
    if "vitamin d" in msg_lower:
        return "Vitamin D deficiency causes fatigue and bone pain. Get 15-30 min sunlight daily, eat fatty fish, take 1000-2000 IU supplement. Normal range: 30-100 ng/mL."
    if "anemia" in msg_lower:
        return "Anemia means low red blood cells. Eat iron-rich foods (spinach, red meat, lentils) with vitamin C. Avoid tea/coffee with meals. Consult doctor for blood test."
    if "diabetes" in msg_lower:
        return "Diabetes management: low glycemic index foods, avoid sugar, exercise 30 min daily, monitor blood sugar and HbA1c. Consult endocrinologist."
    if "thyroid" in msg_lower:
        return "Thyroid disorders affect metabolism. For hypothyroidism: iodine, selenium (Brazil nuts). For hyperthyroidism: avoid excess iodine. Consult endocrinologist."
    if "blood pressure" in msg_lower or "bp" in msg_lower:
        return "High BP: DASH diet, reduce sodium (<1500mg), exercise 30 min daily, limit alcohol. Monitor BP at home. See doctor if >140/90 consistently."
    if "liver" in msg_lower or "alt" in msg_lower or "ast" in msg_lower:
        return "High liver enzymes suggest liver stress. Avoid alcohol, reduce fatty foods, eat leafy greens, turmeric, green tea. Recheck in 4-6 weeks."
    return "I'm your AI Health Assistant! I can help with:\n- Lab report analysis (paste your test results)\n- Symptom checking (describe how you feel)\n- Health topics: cholesterol, diabetes, thyroid, anemia, vitamin D, BP, liver, kidney\n\nPlease ask a specific question or describe your symptoms."

def parse_lab_report(text):
    results = []
    lines = text.split("\n")
    for line in lines:
        line = line.strip().lower()
        if not line:
            continue
        patterns = [
            r'([a-zA-Z\s]+)[\s]*[:\-\=][\s]*([0-9.]+)[\s]*([a-zA-Z/%u]+)?',
            r'([a-zA-Z\s]+)[\s]+([0-9.]+)[\s]+([a-zA-Z/%u]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                test_name = match.group(1).strip()
                value_str = match.group(2).strip()
                unit = match.group(3).strip() if len(match.groups())>2 and match.group(3) else ""
                try:
                    value = float(value_str)
                    for key, info in MEDICAL_RANGES.items():
                        if key in test_name or test_name in key:
                            results.append({
                                "test_name": test_name.title(),
                                "value": value,
                                "unit": unit if unit else info["unit"],
                                "normal_range": info["normal"],
                                "reference": info
                            })
                            break
                    else:
                        results.append({"test_name": test_name.title(), "value": value, "unit": unit, "normal_range": "Unknown", "reference": None})
                except:
                    pass
                break
    return results

def analyze_parameter(param):
    value = param["value"]
    normal = param["normal_range"]
    ref = param["reference"]
    if normal == "Unknown" or not ref:
        return {"status": "Unknown", "deviation": 0, "explanation": "No reference range.", "recommendation": "Consult a doctor."}
    status = "Normal"
    deviation = 0
    if "<" in normal:
        thresh = float(normal.replace("<","").strip())
        if value > thresh:
            status = "High"
            deviation = round((value - thresh)/thresh*100, 2)
    elif ">" in normal:
        thresh = float(normal.replace(">","").strip())
        if value < thresh:
            status = "Low"
            deviation = round((thresh - value)/thresh*100, 2)
    elif "-" in normal:
        low, high = map(float, normal.split("-"))
        if value < low:
            status = "Low"
            deviation = round((low - value)/low*100, 2)
        elif value > high:
            status = "High"
            deviation = round((value - high)/high*100, 2)
    if status == "Normal":
        explanation = f"{param['test_name']} {value} {param['unit']} is within normal range ({normal} {param['unit']})."
        recommendation = "Maintain healthy lifestyle."
    elif status == "Low":
        condition = ref.get("low", "low levels")
        explanation = f"{param['test_name']} is low ({value} {param['unit']}). May indicate {condition}."
        recommendation = RECOMMENDATIONS_LOW.get(param['test_name'].lower(), "Consult your doctor.")
    else:
        condition = ref.get("high", "high levels")
        explanation = f"{param['test_name']} is high ({value} {param['unit']}). May indicate {condition}."
        recommendation = RECOMMENDATIONS_HIGH.get(param['test_name'].lower(), "Consult your doctor.")
    return {"status": status, "deviation": deviation, "explanation": explanation, "recommendation": recommendation}

def generate_full_report(lab_data, user_text):
    report = "# AI Health Report Analysis\n\n## Summary\n"
    for p in lab_data:
        a = analyze_parameter(p)
        emoji = "✅" if a["status"]=="Normal" else "⚠️" if a["status"]=="Low" else "🔴"
        report += f"### {emoji} {p['test_name']}\n- Value: {p['value']} {p['unit']}\n- Normal: {p['normal_range']} {p['unit']}\n- Status: {a['status']}\n- Explanation: {a['explanation']}\n- Recommendation: {a['recommendation']}\n\n"
    report += "---\n**Disclaimer:** This is for informational purposes only. Always consult a healthcare professional."
    return report

# ============================================
# HTML TEMPLATE (Full responsive UI)
# ============================================
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Health Assistant</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',sans-serif;background:#f1f5f9;color:#1e293b}
.app-container{display:flex;height:100vh}
.sidebar{width:260px;background:#fff;border-right:1px solid #e2e8f0;display:flex;flex-direction:column}
.sidebar-header{padding:20px;border-bottom:1px solid #e2e8f0}
.logo{display:flex;align-items:center;gap:10px;font-weight:700;color:#2563eb}
.logo i{color:#ef4444;animation:pulse 2s infinite}
@keyframes pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.1)}}
.subtitle{font-size:12px;color:#64748b;margin-left:30px}
.sidebar-nav{flex:1;padding:12px}
.nav-btn{display:flex;align-items:center;gap:10px;width:100%;padding:10px;border:none;background:transparent;border-radius:8px;cursor:pointer;font-size:14px;color:#475569;margin-bottom:4px}
.nav-btn.active{background:#dbeafe;color:#2563eb;font-weight:600}
.nav-btn:hover{background:#f1f5f9}
.sidebar-footer{padding:16px;border-top:1px solid #e2e8f0;font-size:12px;color:#94a3b8}
.main-content{flex:1;display:flex;flex-direction:column;overflow:hidden}
.main-header{height:56px;background:#fff;border-bottom:1px solid #e2e8f0;display:flex;align-items:center;justify-content:space-between;padding:0 20px}
.tab-content{display:none;flex:1;overflow:auto}
.tab-content.active{display:block}
.chat-container{max-width:800px;margin:0 auto;padding:20px;height:100%;display:flex;flex-direction:column}
.chat-messages{flex:1;overflow-y:auto;padding:10px}
.message{display:flex;gap:10px;margin-bottom:16px;animation:fadeIn 0.3s}
.message.user{flex-direction:row-reverse}
.message-avatar{width:32px;height:32px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:#dbeafe;color:#2563eb}
.message.user .message-avatar{background:#2563eb;color:#fff}
.message-content{max-width:70%;padding:12px;border-radius:12px;background:#fff;border:1px solid #e2e8f0;font-size:14px;line-height:1.5}
.message.user .message-content{background:#2563eb;color:#fff;border:none}
.chat-input-area{padding:12px 0}
.input-wrapper{display:flex;gap:8px;background:#fff;border:1px solid #cbd5e1;border-radius:12px;padding:8px}
#chatInput{flex:1;border:none;outline:none;resize:none;font-family:inherit;font-size:14px}
.send-btn{width:36px;height:36px;border-radius:8px;background:#2563eb;color:#fff;border:none;cursor:pointer}
.quick-actions{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}
.quick-btn{padding:6px 12px;background:#fff;border:1px solid #cbd5e1;border-radius:20px;font-size:12px;cursor:pointer}
.quick-btn:hover{background:#dbeafe}
.analyzer-container{display:grid;grid-template-columns:1fr 1fr;gap:20px;padding:20px;height:100%}
.analyzer-input-section,.analyzer-results{background:#fff;border-radius:12px;border:1px solid #e2e8f0;overflow:auto}
.input-header{padding:16px;border-bottom:1px solid #e2e8f0}
#labReportInput{width:100%;padding:12px;border:1px solid #cbd5e1;border-radius:8px;font-family:monospace;min-height:200px}
.analyze-btn{margin:16px;padding:10px;background:#2563eb;color:#fff;border:none;border-radius:8px;cursor:pointer;font-weight:600}
.results-placeholder{text-align:center;padding:40px;color:#94a3b8}
.param-card{padding:16px;border-bottom:1px solid #e2e8f0}
.param-status{display:inline-block;padding:2px 8px;border-radius:12px;font-size:12px;font-weight:600}
.status-normal{background:#d1fae5;color:#065f46}
.status-low{background:#fef3c7;color:#92400e}
.status-high{background:#fee2e2;color:#991b1b}
@media(max-width:700px){.sidebar{width:70px}.sidebar-header .logo span,.subtitle,.nav-btn span,.sidebar-footer{display:none}.nav-btn{justify-content:center}.analyzer-container{grid-template-columns:1fr}}
</style>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
</head>
<body>
<div class="app-container">
<aside class="sidebar">
<div class="sidebar-header"><div class="logo"><i class="fas fa-heartbeat"></i><span>AI Health</span></div><p class="subtitle">Symptom + Lab</p></div>
<nav class="sidebar-nav">
<button class="nav-btn active" data-tab="chat"><i class="fas fa-comments"></i><span>Chat</span></button>
<button class="nav-btn" data-tab="analyzer"><i class="fas fa-flask"></i><span>Lab Analyzer</span></button>
<button class="nav-btn" data-tab="about"><i class="fas fa-info-circle"></i><span>About</span></button>
</nav>
<div class="sidebar-footer"><p>UET Taxila 2026</p></div>
</aside>
<main class="main-content">
<header class="main-header"><h1 id="pageTitle">Health Chat</h1><button id="clearChat"><i class="fas fa-trash"></i></button></header>
<div class="tab-content active" id="chat-tab">
<div class="chat-container">
<div class="chat-messages" id="chatMessages"><div class="welcome-message" style="text-align:center;padding:40px"><i class="fas fa-robot" style="font-size:48px;color:#2563eb"></i><h2>AI Health Assistant</h2><p>Describe your symptoms or paste lab results</p><div class="quick-actions"><button class="quick-btn" onclick="sendQuick('I have fever and cough')">🤒 Fever + cough</button><button class="quick-btn" onclick="sendQuick('Feeling very thirsty and urinating often')">💧 Thirst + frequent urination</button><button class="quick-btn" onclick="sendQuick('Painful urination')">🔥 Painful urination</button><button class="quick-btn" onclick="sendQuick('What helps anemia?')">🥩 Anemia foods</button></div></div></div>
<div class="chat-input-area"><div class="input-wrapper"><textarea id="chatInput" placeholder="Type your symptoms or lab report..." rows="1"></textarea><button class="send-btn" onclick="sendMessage()"><i class="fas fa-paper-plane"></i></button></div></div>
</div>
</div>
<div class="tab-content" id="analyzer-tab">
<div class="analyzer-container"><div class="analyzer-input-section"><div class="input-header"><h3>📋 Paste Lab Report</h3></div><textarea id="labReportInput" placeholder="Hemoglobin: 11.5 g/dL&#10;Glucose: 145 mg/dL&#10;Cholesterol: 220 mg/dL" rows="12"></textarea><button class="analyze-btn" onclick="analyzeReport()">🔍 Analyze Report</button></div><div class="analyzer-results" id="analyzerResults"><div class="results-placeholder"><i class="fas fa-chart-line"></i><p>Results will appear here</p></div></div></div>
</div>
<div class="tab-content" id="about-tab"><div style="padding:20px;max-width:600px;margin:0 auto"><div class="about-card" style="background:#fff;border-radius:12px;padding:20px"><h2><i class="fas fa-graduation-cap"></i> AI Health Assistant</h2><p><strong>Student:</strong> Romaisa Abbasi (23-SE-036)<br><strong>Supervisor:</strong> Dr. Kanwal Yousaf<br><strong>University:</strong> UET Taxila</p><hr><h3>Features</h3><ul><li>Symptom-based disease detection</li><li>Lab report analysis (20+ parameters)</li><li>Dietary and lifestyle recommendations</li><li>Completely offline, no API required</li></ul><div class="disclaimer" style="background:#fef3c7;padding:12px;border-radius:8px;margin-top:16px"><i class="fas fa-exclamation-triangle"></i> This is for educational purposes only. Always consult a doctor.</div></div></div></div>
</main>
</div>
<script>
function init(){document.querySelectorAll('.nav-btn').forEach(btn=>{btn.addEventListener('click',()=>{document.querySelectorAll('.nav-btn').forEach(b=>b.classList.remove('active'));btn.classList.add('active');document.querySelectorAll('.tab-content').forEach(t=>t.classList.remove('active'));document.getElementById(btn.dataset.tab+'-tab').classList.add('active');});});document.getElementById('clearChat').addEventListener('click',()=>{document.getElementById('chatMessages').innerHTML='<div class="welcome-message" style="text-align:center;padding:40px"><i class="fas fa-robot" style="font-size:48px;color:#2563eb"></i><h2>Chat Cleared</h2><p>Ask a new question</p></div>';});}
async function sendMessage(){const input=document.getElementById('chatInput');const msg=input.value.trim();if(!msg)return;input.value='';addMessage('user',msg);const btn=document.querySelector('.send-btn');btn.disabled=true;btn.innerHTML='<i class="fas fa-spinner fa-spin"></i>';try{const res=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg})});const data=await res.json();if(data.success){if(data.is_lab_analysis && data.ai_analysis){addMessage('ai',data.ai_analysis);}else{addMessage('ai',data.response);}}else{addMessage('ai','Error: '+data.error);}}catch(e){addMessage('ai','Network error. Make sure server is running.');}finally{btn.disabled=false;btn.innerHTML='<i class="fas fa-paper-plane"></i>';}}
function addMessage(sender,text){const container=document.getElementById('chatMessages');const welcome=container.querySelector('.welcome-message');if(welcome)welcome.remove();const div=document.createElement('div');div.className='message '+sender;const avatar=sender==='user'?'<div class="message-avatar"><i class="fas fa-user"></i></div>':'<div class="message-avatar"><i class="fas fa-robot"></i></div>';const formatted=text.replace(/\\n/g,'<br>').replace(/\\*\\*(.*?)\\*\\*/g,'<strong>$1</strong>');div.innerHTML=avatar+'<div class="message-content">'+formatted+'</div>';container.appendChild(div);container.scrollTop=container.scrollHeight;}
function sendQuick(msg){document.getElementById('chatInput').value=msg;sendMessage();}
async function analyzeReport(){const text=document.getElementById('labReportInput').value.trim();if(!text){alert('Please paste lab report data');return;}const res=await fetch('/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({report_text:text})});const data=await res.json();if(data.success){let html='<div class="results-content">';data.structured_results.forEach(p=>{html+=`<div class="param-card"><strong>${p.test_name}</strong> <span class="param-status status-${p.status.toLowerCase()}">${p.status}</span><br>Value: ${p.value} ${p.unit} (Normal: ${p.normal_range})<br><em>${p.explanation}</em><br>💡 ${p.recommendation}</div>`;});html+=`<div class="ai-analysis" style="padding:16px;background:#f8fafc;margin-top:16px;border-radius:8px">${data.ai_analysis.replace(/\\n/g,'<br>')}</div>`;document.getElementById('analyzerResults').innerHTML=html;}else{document.getElementById('analyzerResults').innerHTML='<div class="results-placeholder">Error: '+data.error+'</div>';}}
init();
</script>
</body>
</html>
"""

# ============================================
# HTTP SERVER
# ============================================
class HealthHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode('utf-8')
        try:
            data = json.loads(body)
        except:
            data = {}
        if self.path == '/analyze':
            text = data.get('report_text', '')
            lab_data = parse_lab_report(text)
            if not lab_data:
                self._send_json({"error": "No valid test parameters found"})
                return
            structured = []
            for p in lab_data:
                a = analyze_parameter(p)
                structured.append({
                    "test_name": p["test_name"],
                    "value": p["value"],
                    "unit": p["unit"],
                    "normal_range": p["normal_range"],
                    "status": a["status"],
                    "deviation": a["deviation"],
                    "explanation": a["explanation"],
                    "recommendation": a["recommendation"]
                })
            self._send_json({"success": True, "parsed_count": len(lab_data), "structured_results": structured, "ai_analysis": generate_full_report(lab_data, text)})
        elif self.path == '/chat':
            msg = data.get('message', '')
            lab_data = parse_lab_report(msg)
            if lab_data and len(lab_data) >= 1:
                structured = []
                for p in lab_data:
                    a = analyze_parameter(p)
                    structured.append({"test_name": p["test_name"], "value": p["value"], "unit": p["unit"], "normal_range": p["normal_range"], "status": a["status"]})
                self._send_json({"success": True, "is_lab_analysis": True, "ai_analysis": generate_full_report(lab_data, msg)})
                return
            response = get_chat_response(msg)
            self._send_json({"success": True, "response": response})
        else:
            self.send_response(404)
            self.end_headers()
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    def log_message(self, format, *args):
        pass

if __name__ == '__main__':
    print("="*60)
    print("🏥 AI Health Assistant - ENHANCED VERSION")
    print("UET Taxila - Romaisa Abbasi (23-SE-036)")
    print("="*60)
    print(f"🌐 Open browser: http://127.0.0.1:{PORT}")
    print("💬 Try: 'I have fever and cough' or paste lab results")
    print("Press CTRL+C to stop")
    with socketserver.TCPServer(("", PORT), HealthHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped. Stay healthy!")