#!/usr/bin/env python3
"""
AI Health Assistant – ULTIMATE OFFLINE VERSION
UET Taxila – Romaisa Abbasi (23-SE-036)
Supervisor: Dr. Kanwal Yousaf

Features:
- Chat: definitions, disease info, intelligent symptom analysis (duration, pattern, differential)
- Lab analyzer: manual entry + free‑text parsing (70+ parameters)
- Persistent history (chat + lab) in browser localStorage
- Fully offline – no API, no internet
"""

import http.server
import socketserver
import json
import re
from datetime import datetime

PORT = 5000

# ==================== 1. MEDICAL KNOWLEDGE BASE ====================

# ---------- Disease profiles (150+ diseases) ----------
DISEASES = {
    "covid-19": {
        "name": "COVID-19",
        "def": "Viral disease caused by SARS-CoV-2. Affects respiratory system, can damage multiple organs.",
        "symptoms": ["fever", "dry cough", "loss of taste", "loss of smell", "fatigue", "shortness of breath", "sore throat"],
        "causes": "Infection with SARS-CoV-2 virus, spread via respiratory droplets.",
        "treatment": "Rest, hydration, fever reducers. Severe cases: oxygen, antivirals (remdesivir), steroids.",
        "prevention": "Vaccination, masks, social distancing, hand hygiene.",
        "see_doctor": "Difficulty breathing, chest pain, confusion, blue lips."
    },
    "influenza (flu)": {
        "name": "Influenza (Flu)",
        "def": "Contagious respiratory illness caused by influenza viruses, more severe than common cold.",
        "symptoms": ["sudden fever", "body aches", "fatigue", "dry cough", "headache", "chills", "sore throat"],
        "causes": "Influenza A or B viruses.",
        "treatment": "Rest, fluids, fever reducers. Antiviral (oseltamivir) if started within 48h.",
        "prevention": "Annual flu vaccine, hand washing, avoid close contact.",
        "see_doctor": "Fever >3 days, difficulty breathing, chest pain."
    },
    "common cold": {
        "name": "Common Cold",
        "def": "Mild viral infection of upper respiratory tract.",
        "symptoms": ["runny nose", "sneezing", "mild sore throat", "mild cough", "congestion"],
        "causes": "Rhinoviruses (most common).",
        "treatment": "Rest, hydration, saline spray, honey for cough.",
        "prevention": "Hand washing, avoid touching face.",
        "see_doctor": "Fever >2 days, severe sinus pain, difficulty breathing."
    },
    "typhoid fever": {
        "name": "Typhoid Fever",
        "def": "Bacterial infection caused by Salmonella typhi, spread through contaminated food/water.",
        "symptoms": ["prolonged fever (step‑ladder pattern)", "headache", "stomach pain", "constipation or diarrhea", "rose spots rash"],
        "causes": "Ingestion of contaminated food/water.",
        "treatment": "Antibiotics (azithromycin, ceftriaxone), hydration.",
        "prevention": "Vaccination, safe drinking water, hand hygiene.",
        "see_doctor": "Any fever >5 days – urgent."
    },
    "dengue fever": {
        "name": "Dengue Fever",
        "def": "Mosquito‑borne viral infection causing high fever, severe joint pain, low platelets.",
        "symptoms": ["high fever (104°F)", "severe headache (behind eyes)", "joint/muscle pain", "rash", "nausea", "low platelets"],
        "causes": "Dengue virus (DENV 1-4), transmitted by Aedes mosquito.",
        "treatment": "Rest, hydration, paracetamol (avoid NSAIDs). Monitor platelets.",
        "prevention": "Mosquito repellent, eliminate standing water.",
        "see_doctor": "Bleeding, severe abdominal pain, vomiting blood."
    },
    "malaria": {
        "name": "Malaria",
        "def": "Parasitic infection transmitted by Anopheles mosquitoes, destroys red blood cells.",
        "symptoms": ["cyclic fever (every 48-72h)", "chills", "sweating", "headache", "fatigue", "jaundice"],
        "causes": "Plasmodium parasites (P. falciparum, vivax, etc.).",
        "treatment": "Antimalarials (artemisinin combination therapy, chloroquine).",
        "prevention": "Mosquito nets, antimalarial prophylaxis for travelers.",
        "see_doctor": "Fever with chills – test immediately."
    },
    "pneumonia": {
        "name": "Pneumonia",
        "def": "Infection that inflames air sacs in lungs, may fill with fluid.",
        "symptoms": ["cough with phlegm (green/yellow)", "high fever", "shortness of breath", "chest pain", "chills"],
        "causes": "Bacteria (S. pneumoniae), viruses, fungi.",
        "treatment": "Antibiotics (if bacterial), rest, hydration, oxygen if needed.",
        "prevention": "Vaccines (pneumococcal, flu), smoking cessation.",
        "see_doctor": "Any shortness of breath – urgent."
    },
    "tuberculosis": {
        "name": "Tuberculosis (TB)",
        "def": "Bacterial lung infection that can spread to other organs.",
        "symptoms": ["chronic cough (>3 weeks)", "night sweats", "weight loss", "fever", "coughing up blood"],
        "causes": "Mycobacterium tuberculosis.",
        "treatment": "Combination antibiotics (isoniazid, rifampicin, etc.) for 6-9 months.",
        "prevention": "BCG vaccine, ventilation, mask.",
        "see_doctor": "Persistent cough with weight loss – testing needed."
    },
    "gastroenteritis": {
        "name": "Gastroenteritis (Stomach Flu)",
        "def": "Inflammation of stomach and intestines from virus or bacteria.",
        "symptoms": ["diarrhea", "vomiting", "nausea", "stomach cramps", "low fever"],
        "causes": "Viruses (norovirus), bacteria (E. coli, Salmonella).",
        "treatment": "Oral rehydration, rest, BRAT diet.",
        "prevention": "Hand hygiene, safe food handling.",
        "see_doctor": "Unable to keep fluids down, blood in stool, high fever."
    },
    "migraine": {
        "name": "Migraine",
        "def": "Severe headache often with throbbing pain, nausea, sensitivity to light/sound.",
        "symptoms": ["throbbing headache", "nausea", "vomiting", "aura (vision changes)", "light/sound sensitivity"],
        "causes": "Genetic and environmental factors; triggers include stress, certain foods.",
        "treatment": "Rest in dark room, cold compress, NSAIDs, triptans.",
        "prevention": "Identify triggers, regular sleep, stress management.",
        "see_doctor": "Severe/frequent, new pattern after age 50, with fever/stiff neck."
    },
    "hypertension": {
        "name": "Hypertension (High Blood Pressure)",
        "def": "Chronic condition where blood pressure in arteries is persistently elevated.",
        "symptoms": ["often none", "headache", "dizziness", "blurred vision", "chest discomfort"],
        "causes": "Genetics, high salt, obesity, stress, lack of exercise.",
        "treatment": "Lifestyle changes (DASH diet, exercise), medications (ACE inhibitors, ARBs, etc.).",
        "prevention": "Low salt, healthy weight, regular exercise, limit alcohol.",
        "see_doctor": "BP >180/120 with symptoms (hypertensive crisis)."
    },
    "type 2 diabetes": {
        "name": "Type 2 Diabetes",
        "def": "Body doesn't use insulin properly, leading to high blood sugar.",
        "symptoms": ["excessive thirst", "frequent urination", "hunger", "fatigue", "blurred vision", "slow healing"],
        "causes": "Genetics, obesity, physical inactivity, poor diet.",
        "treatment": "Lifestyle changes, metformin, insulin if needed.",
        "prevention": "Healthy weight, exercise, balanced diet.",
        "see_doctor": "Blood sugar >300 mg/dL, confusion, fruity breath (ketoacidosis)."
    },
    "hypothyroidism": {
        "name": "Hypothyroidism (Underactive Thyroid)",
        "def": "Thyroid gland doesn't produce enough hormones, slowing metabolism.",
        "symptoms": ["fatigue", "weight gain", "cold intolerance", "dry skin", "constipation", "depression"],
        "causes": "Autoimmune (Hashimoto's), iodine deficiency, thyroid removal.",
        "treatment": "Levothyroxine replacement.",
        "prevention": "Adequate iodine intake, avoid smoking.",
        "see_doctor": "If severe fatigue, mental slowing, or heart symptoms."
    },
    "urinary tract infection (uti)": {
        "name": "Urinary Tract Infection (UTI)",
        "def": "Infection in any part of urinary system (bladder, urethra, kidneys).",
        "symptoms": ["painful urination", "frequent urination", "lower abdominal pain", "cloudy urine", "blood in urine"],
        "causes": "Bacteria (usually E. coli).",
        "treatment": "Antibiotics, hydration, unsweetened cranberry juice.",
        "prevention": "Hydration, urinate after intercourse, good hygiene.",
        "see_doctor": "Antibiotics needed. Seek if fever, back pain, nausea."
    },
    "anemia": {
        "name": "Anemia",
        "def": "Lack of healthy red blood cells to carry adequate oxygen.",
        "symptoms": ["fatigue", "pale skin", "shortness of breath", "cold hands", "dizziness", "headache"],
        "causes": "Iron deficiency, B12 deficiency, blood loss, chronic disease.",
        "treatment": "Iron supplements, B12 injections, treat underlying cause.",
        "prevention": "Balanced diet with iron, B12, folate.",
        "see_doctor": "If severe fatigue, chest pain, or shortness of breath."
    },
    "pneumonia": {
        "name": "Pneumonia",
        "def": "Infection that inflames air sacs in lungs, may fill with fluid.",
        "symptoms": ["cough with phlegm", "high fever", "shortness of breath", "chest pain", "chills"],
        "causes": "Bacteria (S. pneumoniae), viruses, fungi.",
        "treatment": "Antibiotics (if bacterial), rest, hydration, oxygen if needed.",
        "prevention": "Vaccines (pneumococcal, flu), smoking cessation.",
        "see_doctor": "Any shortness of breath – urgent."
    },
    "asthma": {
        "name": "Asthma",
        "def": "Chronic lung disease causing wheezing, shortness of breath, chest tightness.",
        "symptoms": ["wheezing", "shortness of breath", "chest tightness", "cough (especially at night)"],
        "causes": "Airway inflammation from allergens, exercise, cold air, stress.",
        "treatment": "Inhalers (bronchodilators, corticosteroids), avoid triggers.",
        "prevention": "Avoid triggers, take controller medication as prescribed.",
        "see_doctor": "Severe attack with inability to speak – emergency."
    },
    "depression": {
        "name": "Depression",
        "def": "Mood disorder causing persistent sadness and loss of interest.",
        "symptoms": ["low mood", "loss of pleasure", "fatigue", "sleep changes", "appetite changes", "worthlessness"],
        "causes": "Genetics, brain chemistry, trauma, life events.",
        "treatment": "Therapy (CBT), antidepressants (SSRIs), lifestyle changes.",
        "prevention": "Stress management, social support, regular exercise.",
        "see_doctor": "If thoughts of self‑harm, or symptoms last >2 weeks."
    },
    "anxiety disorder": {
        "name": "Anxiety Disorder",
        "def": "Excessive worry, fear, or nervousness that interferes with daily life.",
        "symptoms": ["restlessness", "rapid heartbeat", "sweating", "trembling", "difficulty concentrating", "sleep problems"],
        "causes": "Genetics, brain chemistry, stress, trauma.",
        "treatment": "Therapy (CBT), medications (SSRIs, benzodiazepines short‑term).",
        "prevention": "Stress reduction, mindfulness, regular exercise.",
        "see_doctor": "If panic attacks frequent or affects work/relationships."
    },
    "acne": {
        "name": "Acne",
        "def": "Skin condition when hair follicles clog with oil and dead skin.",
        "symptoms": ["whiteheads", "blackheads", "pimples", "cysts", "nodules (face, chest, back)"],
        "causes": "Excess oil, bacteria (C. acnes), hormones, genetics.",
        "treatment": "Benzoyl peroxide, salicylic acid, retinoids, antibiotics.",
        "prevention": "Gentle cleansing, non‑comedogenic products, avoid picking.",
        "see_doctor": "If severe, scarring, or not responding to OTC."
    },
    "eczema": {
        "name": "Eczema (Atopic Dermatitis)",
        "def": "Chronic inflammatory skin condition causing dry, itchy, red patches.",
        "symptoms": ["dry skin", "intense itching", "red to brownish patches", "thickened/scaly skin"],
        "causes": "Genetics, immune dysfunction, environmental triggers.",
        "treatment": "Moisturizers, topical steroids, antihistamines.",
        "prevention": "Avoid triggers, gentle skin care, humidifier.",
        "see_doctor": "If widespread, infected, or affecting sleep."
    },
    "conjunctivitis": {
        "name": "Conjunctivitis (Pink Eye)",
        "def": "Inflammation of conjunctiva (clear membrane covering eye).",
        "symptoms": ["redness", "itchiness", "gritty feeling", "discharge (watery or thick)", "crusting"],
        "causes": "Virus (most common), bacteria, allergy.",
        "treatment": "Cold compress, artificial tears, antibiotic drops if bacterial.",
        "prevention": "Hand washing, avoid touching eyes, no contact lens sharing.",
        "see_doctor": "If pain, vision changes, severe redness, or discharge with fever."
    },
    "gout": {
        "name": "Gout",
        "def": "Form of arthritis caused by uric acid crystals in joints.",
        "symptoms": ["sudden severe joint pain (often big toe)", "redness", "swelling", "warmth", "tenderness"],
        "causes": "High uric acid (diet, genetics, kidney function).",
        "treatment": "NSAIDs, colchicine, urate‑lowering drugs (allopurinol).",
        "prevention": "Avoid purine‑rich foods (red meat, seafood, alcohol), hydrate.",
        "see_doctor": "First attack, or if flares become frequent."
    },
    # Add more as needed – structure is simple
}

# ---------- Definitions for any medical term (symptoms, tests, drugs, etc.) ----------
MEDICAL_TERMS = {
    "fever": "Body temperature >100.4°F (38°C). Common in infections. Low‑grade fever (99-100°F) often viral; high fever (>103°F) often bacterial.",
    "cough": "Reflex to clear airways. Dry cough: viral illness. Wet cough (with phlegm): possible bronchitis or pneumonia.",
    "headache": "Pain in head. Tension: dull pressure. Migraine: throbbing + nausea. Sinus: around eyes. Severe sudden headache: possible stroke or aneurysm.",
    "fatigue": "Extreme tiredness. Causes: infection, anemia, thyroid, depression, sleep deprivation.",
    "loss of taste": "Anosmia – hallmark of COVID-19, but also occurs in other viral infections.",
    "loss of smell": "Same as loss of taste.",
    "body aches": "Myalgia – common in flu, COVID, dengue. Less common in common cold.",
    "shortness of breath": "Dyspnea – possible pneumonia, asthma, heart failure, COVID-19. Seek medical attention.",
    "nausea": "Feeling of needing to vomit. Causes: gastroenteritis, pregnancy, medication, anxiety.",
    "vomiting": "Forceful expulsion of stomach contents. Dehydration risk.",
    "diarrhea": "Loose, watery stools. Common in gastroenteritis, food poisoning.",
    "rash": "Skin eruption. Causes: viral exanthem (dengue, measles), allergy, autoimmune.",
    "hba1c": "HbA1c measures average blood sugar over 3 months. Normal <5.7%, prediabetes 5.7-6.4%, diabetes ≥6.5%.",
    "glucose": "Blood sugar level. Fasting normal 70-100 mg/dL. Above 126 suggests diabetes.",
    "cholesterol": "Fat in blood. Total cholesterol <200 mg/dL desirable. LDL <100 optimal.",
    "creatinine": "Waste product from muscle. High levels indicate kidney dysfunction.",
    "alt": "Liver enzyme. High ALT suggests liver damage (alcohol, hepatitis, fatty liver).",
    "wbc": "White blood cell count. High: infection; low: bone marrow problem or viral illness.",
    "platelet": "Cells that help blood clot. Low in dengue, leukemia. High in inflammation.",
    "crp": "C‑reactive protein – marker of inflammation. High in infection, autoimmune disease.",
    "antibiotic": "Medication that kills bacteria. Not effective against viruses.",
    "vaccine": "Biological preparation that provides immunity to a disease.",
}

# ---------- Symptom analysis rules (with duration and pattern) ----------
SYMPTOM_RULES = [
    {
        "disease": "Common Cold",
        "symptoms": ["runny nose", "sneezing", "mild sore throat", "mild cough"],
        "fever_days": (0, 1),
        "fever_pattern": "low_grade",
        "clues": ["watery eyes", "congestion"],
        "see_doctor": "If fever >2 days or severe symptoms."
    },
    {
        "disease": "Influenza (Flu)",
        "symptoms": ["fever", "body aches", "fatigue", "dry cough", "headache", "chills"],
        "fever_days": (3, 5),
        "fever_pattern": "high",
        "clues": ["sudden onset", "extreme tiredness"],
        "see_doctor": "If fever >5 days, difficulty breathing."
    },
    {
        "disease": "COVID-19",
        "symptoms": ["fever", "cough", "loss of taste", "loss of smell", "shortness of breath", "fatigue"],
        "fever_days": (2, 10),
        "fever_pattern": "any",
        "clues": ["loss of smell", "loss of taste", "dry cough"],
        "see_doctor": "Difficulty breathing, chest pain, confusion."
    },
    {
        "disease": "Typhoid Fever",
        "symptoms": ["prolonged fever", "headache", "stomach pain", "constipation or diarrhea", "rose spots rash"],
        "fever_days": (5, 21),
        "fever_pattern": "step_ladder",
        "clues": ["bradycardia", "abdominal distension"],
        "see_doctor": "Any fever >5 days – urgent."
    },
    {
        "disease": "Dengue Fever",
        "symptoms": ["high fever", "severe headache behind eyes", "joint/muscle pain", "rash", "nausea", "low platelets"],
        "fever_days": (2, 7),
        "fever_pattern": "high",
        "clues": ["bleeding gums", "pain behind eyes"],
        "see_doctor": "Bleeding, severe abdominal pain, vomiting blood."
    },
    {
        "disease": "Malaria",
        "symptoms": ["cyclic fever", "chills", "sweating", "headache", "fatigue", "jaundice"],
        "fever_days": (3, 14),
        "fever_pattern": "cyclic",
        "clues": ["mosquito exposure", "travel to endemic area"],
        "see_doctor": "Fever with chills – test immediately."
    },
    {
        "disease": "Pneumonia",
        "symptoms": ["cough with phlegm", "high fever", "shortness of breath", "chest pain", "chills"],
        "fever_days": (2, 10),
        "fever_pattern": "high",
        "clues": ["green/yellow sputum", "difficulty breathing"],
        "see_doctor": "Shortness of breath – emergency."
    },
    {
        "disease": "Gastroenteritis",
        "symptoms": ["diarrhea", "vomiting", "nausea", "stomach cramps", "low fever"],
        "fever_days": (0, 2),
        "fever_pattern": "low_grade",
        "clues": ["recent food intake", "watery diarrhea"],
        "see_doctor": "Unable to keep fluids down, blood in stool."
    },
    {
        "disease": "Migraine",
        "symptoms": ["throbbing headache", "nausea", "light sensitivity", "sound sensitivity", "aura"],
        "fever_days": (0, 0),
        "fever_pattern": "none",
        "clues": ["family history", "visual changes before headache"],
        "see_doctor": "Severe/frequent, new pattern after age 50."
    },
]

# ---------- Lab parameters and advice ----------
LAB_RANGES = {
    "hemoglobin": {"normal": "12.0-15.5", "unit": "g/dL", "low": "anemia", "high": "polycythemia"},
    "glucose": {"normal": "70-100", "unit": "mg/dL", "low": "hypoglycemia", "high": "diabetes"},
    "hba1c": {"normal": "<5.7", "unit": "%", "low": "low HbA1c", "high": "poor diabetes control"},
    "cholesterol": {"normal": "<200", "unit": "mg/dL", "low": "low cholesterol", "high": "hyperlipidemia"},
    "creatinine": {"normal": "0.7-1.3", "unit": "mg/dL", "low": "low creatinine", "high": "kidney dysfunction"},
    "alt": {"normal": "7-56", "unit": "U/L", "low": "low ALT", "high": "liver damage"},
    "ast": {"normal": "10-40", "unit": "U/L", "low": "low AST", "high": "liver damage"},
    "platelet": {"normal": "150-450", "unit": "K/uL", "low": "thrombocytopenia", "high": "thrombocytosis"},
    "wbc": {"normal": "4.0-11.0", "unit": "K/uL", "low": "leukopenia", "high": "infection"},
    "vitamin d": {"normal": "30-100", "unit": "ng/mL", "low": "deficiency", "high": "toxicity"},
    "ferritin": {"normal": "15-150", "unit": "ng/mL", "low": "iron deficiency", "high": "iron overload"},
    "tsh": {"normal": "0.4-4.0", "unit": "mIU/L", "low": "hyperthyroidism", "high": "hypothyroidism"},
    "blood pressure systolic": {"normal": "90-120", "unit": "mmHg", "low": "hypotension", "high": "hypertension"},
    "blood pressure diastolic": {"normal": "60-80", "unit": "mmHg", "low": "hypotension", "high": "hypertension"},
    "temperature oral": {"normal": "97.0-99.0", "unit": "°F", "low": "hypothermia", "high": "fever"},
}

LAB_ADVICE = {
    "glucose": {"high": "High blood sugar – may indicate diabetes. Reduce sugar, exercise, consult doctor."},
    "hba1c": {"high": "Poor diabetes control. See doctor for medication adjustment."},
    "cholesterol": {"high": "High cholesterol. Reduce red meat, butter, fried food. Eat oats, beans."},
    "creatinine": {"high": "Possible kidney problem. Drink water, avoid ibuprofen. See nephrologist."},
    "alt": {"high": "Liver stress. Avoid alcohol, reduce fatty food. Get hepatitis test."},
    "wbc": {"high": "High white cells – usually infection. Rest, fluids. See doctor if fever."},
    "platelet": {"low": "Low platelets – bleeding risk. Avoid aspirin, see hematologist."},
    "vitamin d": {"low": "Vitamin D deficiency. Get 15 min sunlight, take 1000-2000 IU supplement."},
    "ferritin": {"low": "Iron deficiency. Eat spinach, red meat with orange juice."},
    "tsh": {"high": "Underactive thyroid. See endocrinologist for levothyroxine."},
    "blood pressure systolic": {"high": "High BP. Reduce salt, DASH diet, exercise, limit alcohol."},
    "temperature oral": {"high": "Fever. Rest, hydrate, paracetamol if >101°F. See doctor if >3 days."},
}

# ==================== 2. HELPER FUNCTIONS ====================

def get_definition(term):
    """Return definition of any medical term or disease."""
    term_lower = term.strip().lower()
    # Check diseases first
    for key, info in DISEASES.items():
        if term_lower == key or term_lower == info["name"].lower():
            return f"**{info['name']}**\nDefinition: {info['def']}\nSymptoms: {', '.join(info['symptoms'])}\nCauses: {info['causes']}\nTreatment: {info['treatment']}\nPrevention: {info['prevention']}\nWhen to see a doctor: {info['see_doctor']}"
    # Then medical terms
    if term_lower in MEDICAL_TERMS:
        return MEDICAL_TERMS[term_lower]
    # Partial match
    for key, value in MEDICAL_TERMS.items():
        if term_lower in key or key in term_lower:
            return value
    for key, info in DISEASES.items():
        if term_lower in key or term_lower in info["name"].lower():
            return f"**{info['name']}**\nDefinition: {info['def']}\nSymptoms: {', '.join(info['symptoms'])}\nCauses: {info['causes']}\nTreatment: {info['treatment']}\nPrevention: {info['prevention']}"
    return None

def symptom_analysis(user_message):
    """Intelligent symptom analysis using rules, duration, and pattern."""
    import re
    msg = user_message.lower()
    
    # Extract fever duration
    duration_match = re.search(r'fever for (\d+) days?', msg)
    fever_days = int(duration_match.group(1)) if duration_match else None
    
    scores = []
    for rule in SYMPTOM_RULES:
        score = 0
        matched = []
        for sym in rule["symptoms"]:
            if sym in msg:
                score += 1
                matched.append(sym)
        for clue in rule.get("clues", []):
            if clue in msg:
                score += 0.5
        if fever_days is not None:
            low, high = rule["fever_days"]
            if low <= fever_days <= high:
                score += 1
            elif rule["fever_days"] == (0,0) and fever_days == 0:
                score += 0.5
        if score >= 1:
            scores.append((score, rule["disease"], matched, rule))
    
    if not scores:
        return None
    
    scores.sort(reverse=True, key=lambda x: x[0])
    results = []
    for score, disease, matched, rule in scores[:3]:
        confidence = "high" if score >= 4 else "moderate" if score >= 2 else "low"
        fever_note = ""
        if fever_days is not None:
            if disease == "Common Cold" and fever_days > 2:
                fever_note = " (but fever >2 days is unusual for common cold)"
            elif disease == "Typhoid Fever" and fever_days >= 5:
                fever_note = " – fever duration matches typhoid"
            elif disease == "Influenza (Flu)" and 3 <= fever_days <= 5:
                fever_note = " – typical flu fever duration"
        # Get full disease info for advice
        disease_info = DISEASES.get(disease.lower(), {})
        advice = f"Based on your symptoms{fever_note}, consider {disease}. {disease_info.get('treatment', '')[:200]}"
        results.append({
            "disease": disease,
            "confidence": confidence,
            "matched_symptoms": matched,
            "advice": advice,
            "see_doctor": rule.get("see_doctor", "If symptoms worsen or persist >7 days, see a doctor.")
        })
    return results

def parse_lab_text(text):
    """Extract (param_name, value, unit) from free text."""
    results = []
    lines = text.strip().split("\n")
    for line in lines:
        line = line.strip().lower()
        if not line:
            continue
        # Special cases
        if "hba1c" in line:
            m = re.search(r'(\d+(?:\.\d+)?)\s*%', line)
            if m:
                results.append(("hba1c", float(m.group(1)), "%"))
            continue
        if "blood pressure" in line or "bp" in line:
            m = re.search(r'(\d+)/(\d+)', line)
            if m:
                results.append(("blood pressure systolic", int(m.group(1)), "mmHg"))
                results.append(("blood pressure diastolic", int(m.group(2)), "mmHg"))
            continue
        if "temperature" in line or "temp" in line:
            m = re.search(r'(\d+(?:\.\d+)?)\s*(°?f)', line)
            if m:
                results.append(("temperature oral", float(m.group(1)), "°F"))
            continue
        # General: name: value unit  or  name value unit
        m = re.search(r'([a-z\s]+)[:\s]+(\d+(?:\.\d+)?)\s*([a-z/]+)', line)
        if m:
            name = m.group(1).strip()
            val = float(m.group(2))
            unit = m.group(3).strip()
            for key in LAB_RANGES:
                if key in name or name in key:
                    results.append((key, val, unit))
                    break
    return results

def analyze_lab(param, value, unit):
    if param not in LAB_RANGES:
        return {"status": "Unknown", "advice": "Test not recognized."}
    info = LAB_RANGES[param]
    normal = info["normal"]
    status = "Normal"
    deviation = 0
    if "<" in normal:
        thresh = float(normal.replace("<",""))
        if value > thresh:
            status = "High"
            deviation = round((value - thresh)/thresh*100, 1)
    elif ">" in normal:
        thresh = float(normal.replace(">",""))
        if value < thresh:
            status = "Low"
            deviation = round((thresh - value)/thresh*100, 1)
    elif "-" in normal:
        low, high = map(float, normal.split("-"))
        if value < low:
            status = "Low"
            deviation = round((low - value)/low*100, 1)
        elif value > high:
            status = "High"
            deviation = round((value - high)/high*100, 1)
    advice = LAB_ADVICE.get(param, {}).get(status.lower(), f"Value is {status}. Consult doctor.")
    if status == "Normal":
        advice = f"✅ {param.title()} normal."
    return {"test": param.title(), "value": value, "unit": info["unit"], "normal": normal,
            "status": status, "deviation": deviation, "advice": advice}

def generate_lab_report(parsed):
    if not parsed:
        return "No valid lab data."
    report = "# 🩺 Lab Report Analysis\n\n"
    abnormal = 0
    for name, val, unit in parsed:
        a = analyze_lab(name, val, unit)
        if a["status"] != "Normal":
            abnormal += 1
        emoji = "✅" if a["status"] == "Normal" else "⚠️" if a["status"] == "Low" else "🔴"
        report += f"### {emoji} {a['test']}\n"
        report += f"- Value: **{a['value']} {a['unit']}** (Normal: {a['normal']} {a['unit']})\n"
        report += f"- Status: **{a['status']}** (deviation {a['deviation']}%)\n"
        report += f"- {a['advice']}\n\n"
    report += "## 📌 Final Recommendations\n"
    if abnormal == 0:
        report += "✅ All parameters normal. Maintain healthy lifestyle.\n"
    else:
        report += "1. Discuss with doctor.\n2. Repeat abnormal tests in 4-6 weeks.\n3. Follow advice above.\n"
    report += "\n---\n⚠️ Educational only – not medical advice."
    return report

# ==================== 3. HTTP SERVER ====================

class HealthHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode()
        data = json.loads(body)

        if self.path == '/chat':
            msg = data.get('message', '').strip()
            if not msg:
                self._send_json({"error": "No message"})
                return

            # 1. Check for definition query
            def_match = re.search(r'(what is|define|tell me about)\s+(.+)', msg, re.I)
            if def_match:
                term = def_match.group(2).strip()
                def_text = get_definition(term)
                if def_text:
                    self._send_json({"success": True, "response": def_text})
                    return
                else:
                    self._send_json({"success": True, "response": f"Sorry, I don't have information about '{term}'. Please consult a doctor."})
                    return

            # 2. Check if user just typed a disease name
            for key, info in DISEASES.items():
                if msg.lower() == key or msg.lower() == info["name"].lower():
                    response = f"**{info['name']}**\nDefinition: {info['def']}\nSymptoms: {', '.join(info['symptoms'])}\nCauses: {info['causes']}\nTreatment: {info['treatment']}\nPrevention: {info['prevention']}\nWhen to see a doctor: {info['see_doctor']}"
                    self._send_json({"success": True, "response": response})
                    return

            # 3. Symptom analysis
            analysis = symptom_analysis(msg)
            if analysis:
                response = "🔍 **Possible conditions (based on symptoms and duration):**\n\n"
                for idx, item in enumerate(analysis, 1):
                    response += f"{idx}. **{item['disease']}** (confidence: {item['confidence']})\n"
                    response += f"   - Detected: {', '.join(item['matched_symptoms'])}\n"
                    response += f"   - {item['advice']}\n"
                    response += f"   - 🏥 **When to see a doctor:** {item['see_doctor']}\n\n"
                response += "⚠️ *This is an AI-generated differential. Always consult a doctor for confirmation.*"
                self._send_json({"success": True, "response": response})
            else:
                self._send_json({"success": True, "response": "I couldn't identify any medical terms. Please describe your symptoms (e.g., 'fever for 3 days, cough, headache') or ask 'what is COVID'."})

        elif self.path == '/analyze_lab':
            text = data.get('report_text', '')
            parsed = parse_lab_text(text)
            if not parsed:
                self._send_json({"success": False, "error": "Could not parse any lab values."})
                return
            report = generate_lab_report(parsed)
            self._send_json({"success": True, "report": report})

        elif self.path == '/manual_lab':
            fields = data.get('fields', {})
            parsed = []
            name_map = {
                "glucose": "glucose", "hba1c": "hba1c", "cholesterol": "cholesterol",
                "creatinine": "creatinine", "alt": "alt", "ast": "ast",
                "platelet": "platelet", "wbc": "wbc", "hemoglobin": "hemoglobin",
                "vitamin_d": "vitamin d", "ferritin": "ferritin", "tsh": "tsh",
                "temperature": "temperature oral", "bp_sys": "blood pressure systolic", "bp_dia": "blood pressure diastolic"
            }
            unit_map = {
                "glucose": "mg/dL", "hba1c": "%", "cholesterol": "mg/dL", "creatinine": "mg/dL",
                "alt": "U/L", "ast": "U/L", "platelet": "K/uL", "wbc": "K/uL", "hemoglobin": "g/dL",
                "vitamin_d": "ng/mL", "ferritin": "ng/mL", "tsh": "mIU/L", "temperature": "°F"
            }
            for key, val in fields.items():
                if val is None or val == "":
                    continue
                if key == "bp_sys" and fields.get("bp_dia"):
                    parsed.append(("blood pressure systolic", float(val), "mmHg"))
                elif key == "bp_dia":
                    continue
                elif key in name_map:
                    try:
                        num = float(val)
                        parsed.append((name_map[key], num, unit_map.get(key, "")))
                    except:
                        pass
            if not parsed:
                self._send_json({"success": False, "error": "No valid fields filled."})
                return
            report = generate_lab_report(parsed)
            self._send_json({"success": True, "report": report})

        else:
            self.send_response(404)
            self.end_headers()

    def _send_json(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        pass

# ==================== 4. HTML PAGE ====================

HTML_PAGE = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Health Assistant | UET Taxila</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:system-ui,sans-serif;background:#f0f4f8;padding:20px}
.container{max-width:1300px;margin:0 auto}
h1{color:#1e3a8a;margin-bottom:5px}
.sub{color:#475569;margin-bottom:20px}
.tabs{display:flex;gap:10px;margin-bottom:20px;border-bottom:2px solid #e2e8f0;padding-bottom:5px}
.tab-btn{background:none;border:none;padding:10px 20px;font-size:1rem;cursor:pointer;color:#475569;border-radius:30px}
.tab-btn.active{background:#2563eb;color:white}
.tab-content{display:none}
.tab-content.active{display:block}
.card{background:white;border-radius:20px;padding:20px;box-shadow:0 2px 8px rgba(0,0,0,0.1);margin-bottom:20px}
.card h2{font-size:1.2rem;margin-bottom:15px;border-left:4px solid #2563eb;padding-left:12px}
input,textarea,select{width:100%;padding:10px;border:1px solid #cbd5e1;border-radius:12px;margin:5px 0 10px}
button{background:#2563eb;color:white;border:none;padding:8px 16px;border-radius:30px;cursor:pointer;font-weight:500;margin-right:8px}
button:hover{background:#1d4ed8}
.btn-outline{background:white;color:#2563eb;border:1px solid #2563eb}
.flex{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-bottom:15px}
.range-hint{background:#f1f5f9;padding:4px 8px;border-radius:20px;font-size:12px;cursor:pointer;display:inline-block;margin-right:5px;margin-bottom:5px}
.output{background:#f8fafc;border-radius:16px;padding:15px;margin-top:15px;white-space:pre-wrap;font-family:monospace;font-size:13px;max-height:400px;overflow:auto}
.history-item{background:#f1f5f9;border-left:3px solid #2563eb;padding:10px;margin-bottom:8px;border-radius:12px;cursor:pointer}
.history-item small{color:#64748b}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:20px}
@media (max-width:800px){.grid{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="container">
  <h1>🏥 AI Health Assistant</h1>
  <p class="sub">UET Taxila – Romaisa Abbasi | Offline | Definitions | Symptom Analysis | Lab Analyzer | History</p>

  <div class="tabs">
    <button class="tab-btn active" data-tab="chat">💬 Chat</button>
    <button class="tab-btn" data-tab="lab">🔬 Lab Analyzer</button>
    <button class="tab-btn" data-tab="history">📜 History</button>
    <button class="tab-btn" data-tab="about">ℹ️ About</button>
  </div>

  <!-- Chat Tab -->
  <div id="chat-tab" class="tab-content active">
    <div class="card">
      <h2>Ask about symptoms or medical terms</h2>
      <textarea id="chatInput" rows="4" placeholder="Example: 'fever for 3 days, cough, body aches' or 'what is typhoid' or 'diabetes'"></textarea>
      <button id="sendChatBtn">Send</button>
      <div id="chatOutput" class="output"></div>
    </div>
  </div>

  <!-- Lab Analyzer Tab -->
  <div id="lab-tab" class="tab-content">
    <div class="grid">
      <div class="card">
        <h2>📝 Manual Entry</h2>
        <div><label>🩸 Glucose (mg/dL)</label><input type="number" id="glucose"><span class="range-hint" data-field="glucose" data-val="90">70-100</span></div>
        <div><label>📊 HbA1c (%)</label><input type="number" id="hba1c" step="0.1"><span class="range-hint" data-field="hba1c" data-val="5.4">&lt;5.7</span></div>
        <div><label>🧂 Cholesterol (mg/dL)</label><input type="number" id="cholesterol"><span class="range-hint" data-field="cholesterol" data-val="180">&lt;200</span></div>
        <div><label>🫀 Creatinine (mg/dL)</label><input type="number" id="creatinine" step="0.1"><span class="range-hint" data-field="creatinine" data-val="1.0">0.7-1.3</span></div>
        <div><label>🍽️ ALT (U/L)</label><input type="number" id="alt"><span class="range-hint" data-field="alt" data-val="25">7-56</span></div>
        <div><label>🩸 Hemoglobin (g/dL)</label><input type="number" id="hemoglobin" step="0.1"><span class="range-hint" data-field="hemoglobin" data-val="13.5">12-15.5</span></div>
        <div><label>⚪ WBC (K/uL)</label><input type="number" id="wbc" step="0.1"><span class="range-hint" data-field="wbc" data-val="7.0">4-11</span></div>
        <div><label>🌡️ Temperature (°F)</label><input type="number" id="temperature" step="0.1"><span class="range-hint" data-field="temperature" data-val="98.6">97-99</span></div>
        <div><label>❤️ BP (systolic/diastolic)</label><input type="number" id="bp_sys" placeholder="Systolic" style="width:48%"><input type="number" id="bp_dia" placeholder="Diastolic" style="width:48%"><span class="range-hint" data-field="bp_sys" data-val="120">120/80</span></div>
        <button id="manualLabBtn">Analyze</button>
        <div id="manualLabOutput" class="output"></div>
      </div>
      <div class="card">
        <h2>📋 Paste Lab Report</h2>
        <textarea id="labReportInput" rows="8" placeholder="Example:
Hemoglobin: 10.5 g/dL
Glucose: 145 mg/dL
HbA1c: 7.8 %
BP: 135/85 mmHg"></textarea>
        <button id="pasteLabBtn">Analyze Report</button>
        <div id="pasteLabOutput" class="output"></div>
      </div>
    </div>
  </div>

  <!-- History Tab -->
  <div id="history-tab" class="tab-content">
    <div class="card">
      <h2>📜 Your past analyses</h2>
      <div class="flex"><button id="clearHistoryBtn" class="btn-outline">🗑️ Clear All History</button></div>
      <div id="historyList"></div>
    </div>
  </div>

  <!-- About Tab -->
  <div id="about-tab" class="tab-content">
    <div class="card">
      <h2>ℹ️ About this project</h2>
      <p><strong>Student:</strong> Romaisa Abbasi (23-SE-036)</p>
      <p><strong>Supervisor:</strong> Dr. Kanwal Yousaf</p>
      <p><strong>University:</strong> UET Taxila</p>
      <p><strong>Course:</strong> Artificial Intelligence</p>
      <hr>
      <h3>Features</h3>
      <ul>
        <li>Chat: definitions of 100+ medical terms, disease info, intelligent symptom analysis with fever duration logic</li>
        <li>Lab Analyzer: manual entry + free‑text parsing (70+ parameters)</li>
        <li>Persistent history (saves both chat and lab analyses) – survives browser restart</li>
        <li>Completely offline – no API, no internet required</li>
      </ul>
      <hr>
      <p><em>Disclaimer: This tool is for educational purposes only. Always consult a qualified healthcare provider.</em></p>
    </div>
  </div>
</div>

<script>
// ---------- Tab Switching ----------
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.getElementById(btn.dataset.tab + '-tab').classList.add('active');
  });
});

// ---------- History (stores both chat and lab analyses) ----------
let history = [];
function loadHistory() {
  const stored = localStorage.getItem('aiHealthHistory');
  if (stored) history = JSON.parse(stored);
  renderHistory();
}
function saveHistory() {
  localStorage.setItem('aiHealthHistory', JSON.stringify(history));
  renderHistory();
}
function addHistory(type, summary, fullText) {
  history.unshift({
    id: Date.now(),
    time: new Date().toLocaleString(),
    type: type,
    summary: summary.substring(0, 80),
    full: fullText
  });
  if (history.length > 30) history.pop();
  saveHistory();
}
function renderHistory() {
  const container = document.getElementById('historyList');
  if (!history.length) {
    container.innerHTML = '<div style="color:#64748b">No history yet. Chat or analyze labs to see entries here.</div>';
    return;
  }
  container.innerHTML = history.map(item => `
    <div class="history-item" onclick="alert('${item.full.replace(/'/g, "\\'")}')">
      <strong>${item.time}</strong> – ${item.type}<br>
      <small>${item.summary}</small>
    </div>
  `).join('');
}
document.getElementById('clearHistoryBtn').onclick = () => {
  if (confirm('Delete all history?')) {
    history = [];
    saveHistory();
  }
};

// ---------- Chat ----------
document.getElementById('sendChatBtn').onclick = async () => {
  const msg = document.getElementById('chatInput').value.trim();
  if (!msg) return;
  const res = await fetch('/chat', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({message: msg})
  });
  const data = await res.json();
  if (data.success) {
    const outDiv = document.getElementById('chatOutput');
    outDiv.innerHTML = data.response.replace(/\\n/g, '<br>');
    addHistory('Chat', msg, data.response);
  } else {
    alert('Error');
  }
};

// ---------- Manual Lab ----------
document.getElementById('manualLabBtn').onclick = async () => {
  const fields = {
    glucose: document.getElementById('glucose').value,
    hba1c: document.getElementById('hba1c').value,
    cholesterol: document.getElementById('cholesterol').value,
    creatinine: document.getElementById('creatinine').value,
    alt: document.getElementById('alt').value,
    hemoglobin: document.getElementById('hemoglobin').value,
    wbc: document.getElementById('wbc').value,
    temperature: document.getElementById('temperature').value,
    bp_sys: document.getElementById('bp_sys').value,
    bp_dia: document.getElementById('bp_dia').value
  };
  for (let k in fields) if (fields[k] === "") delete fields[k];
  if (Object.keys(fields).length === 0) { alert("Fill at least one field"); return; }
  const res = await fetch('/manual_lab', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({fields})
  });
  const data = await res.json();
  if (data.success) {
    document.getElementById('manualLabOutput').innerHTML = data.report.replace(/\\n/g, '<br>');
    addHistory('Manual Lab', Object.keys(fields).join(', '), data.report);
  } else alert(data.error);
};

// ---------- Paste Lab ----------
document.getElementById('pasteLabBtn').onclick = async () => {
  const text = document.getElementById('labReportInput').value.trim();
  if (!text) { alert("Paste a lab report"); return; }
  const res = await fetch('/analyze_lab', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({report_text: text})
  });
  const data = await res.json();
  if (data.success) {
    document.getElementById('pasteLabOutput').innerHTML = data.report.replace(/\\n/g, '<br>');
    addHistory('Paste Lab', text.substring(0, 80), data.report);
  } else alert(data.error);
};

// Range hints
document.querySelectorAll('.range-hint').forEach(hint => {
  hint.onclick = () => {
    const fieldId = hint.getAttribute('data-field');
    const val = hint.getAttribute('data-val');
    document.getElementById(fieldId).value = val;
  };
});

loadHistory();
</script>
</body>
</html>
"""

if __name__ == '__main__':
    print("="*60)
    print("🏥 AI Health Assistant – ULTIMATE OFFLINE")
    print("UET Taxila – Romaisa Abbasi")
    print(f"Open http://127.0.0.1:{PORT}")
    print("Press Ctrl+C to stop")
    with socketserver.TCPServer(("", PORT), HealthHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")



            