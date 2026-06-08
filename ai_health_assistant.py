#!/usr/bin/env python3
"""
AI Health Assistant - ENHANCED VERSION (No pip install needed!)
Works with ONLY Python standard library
University of Engineering and Technology, Taxila
Student: Romaisa Abbasi (23-SE-036)
Supervisor: Dr. Kanwal Yousaf

Enhancements:
- Disease detection from symptoms in chat
- Properly responsive design (mobile friendly)
- Maintains original beautiful GUI
- Enhanced health advice
"""

import http.server
import socketserver
import json
import re
from datetime import datetime

PORT = 5000

# ============================================
# MEDICAL KNOWLEDGE BASE (Original + Enhanced)
# ============================================
MEDICAL_RANGES = {
    "hemoglobin": {"normal": "12.0-15.5", "unit": "g/dL", "low": "Anemia", "high": "Polycythemia"},
    "glucose": {"normal": "70-100", "unit": "mg/dL", "low": "Hypoglycemia", "high": "Hyperglycemia/Diabetes"},
    "blood sugar": {"normal": "70-100", "unit": "mg/dL", "low": "Hypoglycemia", "high": "Hyperglycemia/Diabetes"},
    "cholesterol": {"normal": "<200", "unit": "mg/dL", "low": "Low cholesterol", "high": "High cholesterol/Hyperlipidemia"},
    "total cholesterol": {"normal": "<200", "unit": "mg/dL", "low": "Low cholesterol", "high": "High cholesterol"},
    "ldl": {"normal": "<100", "unit": "mg/dL", "low": "Low LDL", "high": "High LDL (Bad cholesterol)"},
    "hdl": {"normal": ">40", "unit": "mg/dL", "low": "Low HDL", "high": "Good HDL level"},
    "triglycerides": {"normal": "<150", "unit": "mg/dL", "low": "Low triglycerides", "high": "High triglycerides"},
    "wbc": {"normal": "4.0-11.0", "unit": "K/uL", "low": "Leukopenia", "high": "Leukocytosis/Infection"},
    "white blood cell": {"normal": "4.0-11.0", "unit": "K/uL", "low": "Leukopenia", "high": "Leukocytosis"},
    "rbc": {"normal": "4.2-5.4", "unit": "M/uL", "low": "Anemia", "high": "Polycythemia"},
    "red blood cell": {"normal": "4.2-5.4", "unit": "M/uL", "low": "Anemia", "high": "Polycythemia"},
    "platelet": {"normal": "150-450", "unit": "K/uL", "low": "Thrombocytopenia", "high": "Thrombocytosis"},
    "creatinine": {"normal": "0.7-1.3", "unit": "mg/dL", "low": "Low creatinine", "high": "Kidney dysfunction"},
    "urea": {"normal": "7-20", "unit": "mg/dL", "low": "Low urea", "high": "Kidney issues/Dehydration"},
    "bun": {"normal": "7-20", "unit": "mg/dL", "low": "Low BUN", "high": "Kidney issues"},
    "uric acid": {"normal": "3.5-7.2", "unit": "mg/dL", "low": "Low uric acid", "high": "Gout risk"},
    "sodium": {"normal": "135-145", "unit": "mEq/L", "low": "Hyponatremia", "high": "Hypernatremia"},
    "potassium": {"normal": "3.5-5.0", "unit": "mEq/L", "low": "Hypokalemia", "high": "Hyperkalemia"},
    "calcium": {"normal": "8.5-10.5", "unit": "mg/dL", "low": "Hypocalcemia", "high": "Hypercalcemia"},
    "vitamin d": {"normal": "30-100", "unit": "ng/mL", "low": "Vitamin D deficiency", "high": "Vitamin D toxicity"},
    "vitamin b12": {"normal": "200-900", "unit": "pg/mL", "low": "B12 deficiency", "high": "High B12"},
    "ferritin": {"normal": "15-150", "unit": "ng/mL", "low": "Iron deficiency", "high": "Iron overload"},
    "tsh": {"normal": "0.4-4.0", "unit": "mIU/L", "low": "Hyperthyroidism", "high": "Hypothyroidism"},
    "thyroid stimulating hormone": {"normal": "0.4-4.0", "unit": "mIU/L", "low": "Hyperthyroidism", "high": "Hypothyroidism"},
    "alt": {"normal": "7-56", "unit": "U/L", "low": "Low ALT", "high": "Liver damage"},
    "sgpt": {"normal": "7-56", "unit": "U/L", "low": "Low SGPT", "high": "Liver damage"},
    "ast": {"normal": "10-40", "unit": "U/L", "low": "Low AST", "high": "Liver damage"},
    "sgot": {"normal": "10-40", "unit": "U/L", "low": "Low SGOT", "high": "Liver damage"},
    "bilirubin": {"normal": "0.1-1.2", "unit": "mg/dL", "low": "Low bilirubin", "high": "Jaundice/Liver issues"},
    "esr": {"normal": "0-20", "unit": "mm/hr", "low": "Low ESR", "high": "Inflammation/Infection"},
    "crp": {"normal": "<10", "unit": "mg/L", "low": "Normal", "high": "Inflammation/Infection"},
    "hba1c": {"normal": "<5.7", "unit": "%", "low": "Low HbA1c", "high": "Diabetes/Prediabetes"},
    "a1c": {"normal": "<5.7", "unit": "%", "low": "Low A1c", "high": "Diabetes"},
    "bp": {"normal": "120/80", "unit": "mmHg", "low": "Hypotension", "high": "Hypertension"},
    "blood pressure": {"normal": "120/80", "unit": "mmHg", "low": "Hypotension", "high": "Hypertension"},
}

RECOMMENDATIONS_LOW = {
    "hemoglobin": "Increase iron-rich foods: spinach, red meat, lentils, fortified cereals. Take Vitamin C with iron meals. Consider iron supplements after consulting doctor.",
    "glucose": "Consume quick sugar sources (fruit juice, candy) immediately. Eat small, frequent meals. Include complex carbs and protein in every meal. Monitor blood sugar regularly.",
    "blood sugar": "Consume quick sugar sources immediately. Eat small, frequent meals with complex carbs and protein. Monitor blood sugar regularly.",
    "cholesterol": "Include healthy fats: avocados, nuts, olive oil. Eat fatty fish (salmon, mackerel). Maintain moderate exercise. Consult doctor if persistently low.",
    "wbc": "Practice good hygiene. Avoid crowded places. Eat immune-boosting foods: citrus fruits, garlic, ginger. Get adequate sleep. Consult hematologist if severely low.",
    "white blood cell": "Boost immunity with vitamin C, zinc, and probiotics. Maintain good hygiene. Consult doctor if recurrent infections occur.",
    "rbc": "Eat iron-rich foods and folate sources (leafy greens, beans). Stay hydrated. Consider B12 supplements. Consult doctor for anemia workup.",
    "red blood cell": "Eat iron-rich foods and folate sources. Stay hydrated. Consider B12 supplements. Consult doctor for anemia workup.",
    "platelet": "Avoid alcohol and NSAIDs. Eat vitamin K rich foods (leafy greens). Avoid activities with injury risk. Consult hematologist urgently if very low.",
    "sodium": "Add moderate salt to meals. Drink oral rehydration solutions. Eat sodium-rich foods in moderation. Avoid excessive water intake. Consult doctor.",
    "potassium": "Eat bananas, oranges, potatoes, spinach, yogurt. Avoid excessive sweating without electrolyte replacement. Consult doctor if on diuretics.",
    "calcium": "Consume dairy products, fortified plant milk, leafy greens. Take Vitamin D supplements. Do weight-bearing exercises. Consult doctor for bone health assessment.",
    "vitamin d": "Get 15-30 minutes sunlight daily. Eat fatty fish, egg yolks, fortified foods. Take Vitamin D3 supplements (1000-2000 IU). Recheck levels in 3 months.",
    "vitamin b12": "Eat meat, fish, eggs, dairy. For vegetarians: fortified cereals, nutritional yeast. Take B12 supplements or injections if deficient. Recheck in 2-3 months.",
    "ferritin": "Eat iron-rich foods: red meat, spinach, lentils. Pair with Vitamin C. Avoid tea/coffee with meals. Consider iron supplements. Check for blood loss causes.",
    "tsh": "May indicate hyperthyroidism. Avoid excessive iodine. Eat selenium-rich foods (Brazil nuts). Consult endocrinologist for thyroid function tests.",
    "thyroid stimulating hormone": "May indicate hyperthyroidism. Avoid excessive iodine. Eat selenium-rich foods. Consult endocrinologist.",
    "hdl": "Exercise regularly (aerobic 30 min/day). Eat healthy fats: olive oil, nuts, avocado. Avoid trans fats. Quit smoking. Maintain healthy weight.",
}

RECOMMENDATIONS_HIGH = {
    "hemoglobin": "Stay well hydrated. Avoid iron supplements unless prescribed. Consider phlebotomy if severely high. Check for sleep apnea or lung disease. Consult hematologist.",
    "glucose": "Reduce sugar and refined carbs. Eat low glycemic index foods. Exercise 30 min daily. Monitor blood sugar. Consider metformin after consulting doctor. Check HbA1c.",
    "blood sugar": "Reduce sugar and refined carbs. Eat low GI foods. Exercise daily. Monitor levels. Consider medication after consulting doctor.",
    "cholesterol": "Reduce saturated fats (red meat, butter). Increase fiber (oats, beans). Exercise 30 min daily. Consider statins after consulting doctor. Eat nuts and fatty fish.",
    "total cholesterol": "Reduce saturated fats. Increase soluble fiber. Exercise regularly. Consider statins if very high. Eat omega-3 rich foods.",
    "ldl": "Avoid trans fats and saturated fats. Eat soluble fiber (oats, beans, apples). Exercise daily. Consider statin therapy if >190 mg/dL. Consult cardiologist.",
    "triglycerides": "Avoid alcohol and sugary foods. Reduce refined carbs. Exercise 30-45 min daily. Eat omega-3 rich fish. Consider fibrates if >500 mg/dL. Consult doctor.",
    "wbc": "May indicate infection. Stay hydrated. Rest adequately. Monitor for fever. If persistent elevation, consult doctor to rule out leukemia or other conditions.",
    "white blood cell": "May indicate infection. Stay hydrated, rest. Monitor for fever. Consult doctor if persistent or very high.",
    "rbc": "Stay hydrated. Avoid iron supplements. Check for dehydration, lung disease, or sleep apnea. Consult hematologist if persistently high.",
    "red blood cell": "Stay hydrated. Check for underlying conditions. Consult doctor if persistently high.",
    "platelet": "Stay hydrated. Avoid strenuous activity if very high. Consult hematologist to rule out essential thrombocythemia or other conditions.",
    "creatinine": "Reduce protein intake temporarily. Stay hydrated. Avoid NSAIDs. Check kidney function (eGFR). Consult nephrologist if >2.0 mg/dL.",
    "urea": "Reduce protein intake. Stay well hydrated. Check kidney function. Consult doctor if elevated with high creatinine.",
    "bun": "Reduce protein intake. Stay hydrated. Check kidney function. Consult doctor if elevated with other abnormal markers.",
    "uric acid": "Limit purine-rich foods (red meat, organ meats, seafood). Avoid alcohol (especially beer). Drink 3+ liters water daily. Consider allopurinol if >9 mg/dL. Consult doctor.",
    "sodium": "Reduce salt intake. Avoid processed foods. Drink adequate water. Check for dehydration or hormonal issues. Consult doctor if >155 mEq/L.",
    "potassium": "Avoid potassium-rich foods (bananas, oranges, potatoes) temporarily. Avoid salt substitutes. Check kidney function. Consult doctor urgently if >6.0 mEq/L (heart risk).",
    "calcium": "Reduce calcium supplements. Stay hydrated. Check parathyroid and Vitamin D levels. Consult endocrinologist if >11 mg/dL.",
    "vitamin d": "Stop Vitamin D supplements temporarily. Reduce fortified foods. Check calcium and parathyroid levels. Consult doctor if >150 ng/mL (toxicity risk).",
    "vitamin b12": "Usually not harmful. May indicate liver disease or certain cancers if very high. Consult doctor for further evaluation if >2000 pg/mL.",
    "ferritin": "Reduce iron-rich foods. Avoid vitamin C with iron meals. Check for hemochromatosis. Consider phlebotomy if very high. Consult hematologist.",
    "tsh": "May indicate hypothyroidism. Increase iodine (seaweed, iodized salt). Exercise regularly. Consider levothyroxine after consulting endocrinologist. Recheck T3, T4, antibodies.",
    "thyroid stimulating hormone": "May indicate hypothyroidism. Increase iodine intake. Exercise regularly. Consider thyroid medication after consulting doctor.",
    "alt": "Avoid alcohol completely. Reduce fatty foods. Check for hepatitis, fatty liver, or medication side effects. Consult gastroenterologist if >3x normal.",
    "sgpt": "Avoid alcohol. Reduce fatty foods. Check for liver conditions. Consult gastroenterologist if >3x normal.",
    "ast": "Avoid alcohol. Check for liver damage, muscle injury, or medication effects. Consult doctor if >3x normal.",
    "sgot": "Avoid alcohol. Check for liver conditions. Consult doctor if >3x normal.",
    "bilirubin": "Check for hepatitis, gallstones, or hemolysis. Avoid alcohol. Eat liver-friendly foods. Consult gastroenterologist if >3 mg/dL or with jaundice.",
    "esr": "Indicates inflammation. Check for infection, autoimmune disease, or malignancy. Anti-inflammatory diet: turmeric, ginger, omega-3. Consult doctor for workup.",
    "crp": "Indicates inflammation. Anti-inflammatory diet: fatty fish, berries, leafy greens. Exercise regularly. Manage stress. Consult doctor if >100 mg/L (severe infection).",
    "hba1c": "Indicates diabetes/prediabetes. Strict carb control. Exercise 30 min daily. Monitor blood sugar. Consider metformin if >6.5%. Consult endocrinologist.",
    "a1c": "Indicates diabetes control. Strict diet and exercise. Monitor daily. Consider medication adjustment. Consult doctor if >7%.",
    "bp": "Reduce sodium. Exercise 30 min daily. Manage stress. Limit alcohol. Consider antihypertensives if >140/90 consistently. Monitor daily. Consult cardiologist.",
    "blood pressure": "DASH diet (fruits, vegetables, low sodium). Exercise regularly. Limit alcohol. Consider medication if >140/90. Monitor daily.",
}

CHAT_RESPONSES = {
    "cholesterol": "High cholesterol means you have too much LDL (bad cholesterol) in your blood. This can build up in arteries and increase heart disease risk.\n\nWhat to do:\n- Reduce saturated fats (red meat, butter, fried foods)\n- Eat more fiber (oats, beans, apples)\n- Exercise 30 min daily\n- Consider statins if LDL >190 mg/dL (consult doctor)\n- Eat omega-3 rich fish (salmon, mackerel) 2x/week",
    "vitamin d": "Vitamin D is essential for bone health, immunity, and mood. Low levels cause fatigue, bone pain, and weak immunity.\n\nHow to improve:\n- Get 15-30 min sunlight daily\n- Eat fatty fish, egg yolks, fortified milk/cereals\n- Take Vitamin D3 supplements (1000-2000 IU daily)\n- Recheck levels in 3 months\n- Normal range: 30-100 ng/mL",
    "anemia": "Anemia means low hemoglobin or red blood cells, reducing oxygen delivery. Causes fatigue, weakness, pale skin.\n\nBest foods for anemia:\n- Iron-rich: Spinach, red meat, lentils, fortified cereals\n- Vitamin C: Oranges, strawberries (helps iron absorption)\n- Folate: Leafy greens, beans, peanuts\n- B12: Meat, fish, eggs, dairy\n- Avoid tea/coffee with iron meals",
    "diabetes": "Diabetes is high blood sugar due to insulin resistance. Type 2 is lifestyle-related and manageable.\n\nManagement tips:\n- Diet: Low glycemic index foods (oats, quinoa, legumes)\n- Avoid: Sugar, white bread, sugary drinks\n- Exercise: 30 min walking daily improves insulin sensitivity\n- Monitor: Check fasting glucose and HbA1c regularly\n- Medication: Metformin commonly prescribed (consult doctor)",
    "thyroid": "Thyroid disorders affect metabolism. Hypothyroidism causes weight gain, fatigue. Hyperthyroidism causes weight loss, anxiety.\n\nThyroid health:\n- Iodine: Seaweed, iodized salt, dairy (for hypothyroid)\n- Selenium: Brazil nuts, tuna, eggs (supports thyroid)\n- Avoid: Excessive soy if hypothyroid\n- Exercise: Regular activity helps metabolism\n- Consult: Endocrinologist for medication",
    "blood pressure": "High blood pressure (hypertension) strains heart and arteries, increasing stroke/heart attack risk.\n\nNatural ways to lower BP:\n- DASH Diet: Fruits, vegetables, whole grains, low sodium\n- Reduce sodium: <1500mg/day, avoid processed foods\n- Exercise: 30 min aerobic daily (walking, swimming)\n- Limit: Alcohol, caffeine, smoking\n- Manage: Stress through meditation, yoga\n- Monitor: Home BP monitor, check daily",
    "liver": "Liver enzymes (ALT, AST) indicate liver health. High levels suggest liver stress from alcohol, fatty liver, hepatitis, or medications.\n\nLiver-friendly habits:\n- Avoid alcohol completely until levels normalize\n- Diet: Leafy greens, beets, garlic, turmeric, green tea\n- Avoid: Fried foods, processed sugars, excess protein\n- Hydrate: 3+ liters water daily\n- Recheck: Liver function in 4-6 weeks",
    "kidney": "Kidney markers (creatinine, BUN, urea) show how well kidneys filter waste. High levels indicate reduced kidney function.\n\nKidney protection:\n- Hydrate: Drink 2-3 liters water daily\n- Reduce protein: Moderate intake (0.8g/kg body weight)\n- Avoid: NSAIDs (ibuprofen), high-salt foods\n- Monitor: Blood pressure (kidneys are sensitive to BP)\n- Consult: Nephrologist if creatinine >1.5 mg/dL",
}

# ============================================
# SYMPTOM-BASED DISEASE DETECTION (NEW)
# ============================================
SYMPTOM_DISEASE_MAP = {
    "common cold": {
        "symptoms": ["runny nose", "sneezing", "sore throat", "mild cough", "congestion", "stuffy nose"],
        "advice": "Get plenty of rest, stay hydrated. Use saline nasal spray, honey for cough, and over-the-counter cold remedies. Usually resolves in 7-10 days.",
        "see_doctor": "If symptoms persist >10 days, high fever (>101°F / 38.3°C), severe sinus pain, or difficulty breathing.",
        "prevention": "Wash hands frequently, avoid touching face, boost immunity with vitamin C and zinc."
    },
    "flu (influenza)": {
        "symptoms": ["fever", "body aches", "fatigue", "dry cough", "headache", "chills", "weakness"],
        "advice": "Rest, drink plenty of fluids, take fever reducers (acetaminophen/ibuprofen). Antiviral medications if started within 48 hours of symptoms.",
        "see_doctor": "If fever >3 days, difficulty breathing, chest pain, confusion, or worsening symptoms.",
        "prevention": "Annual flu vaccine, hand hygiene, avoid close contact with sick individuals."
    },
    "covid-19": {
        "symptoms": ["fever", "cough", "loss of taste", "loss of smell", "shortness of breath", "fatigue", "sore throat"],
        "advice": "Isolate immediately, take a COVID test, rest, monitor oxygen saturation with pulse oximeter. Stay hydrated and use fever reducers.",
        "see_doctor": "If difficulty breathing, persistent chest pain, confusion, inability to stay awake, or blue lips/face.",
        "prevention": "Vaccination, mask in crowded places, good ventilation, hand hygiene."
    },
    "migraine": {
        "symptoms": ["throbbing headache", "light sensitivity", "sound sensitivity", "nausea", "vomiting", "aura", "vision changes"],
        "advice": "Rest in a dark, quiet room. Apply cold compress to forehead. Stay hydrated. Identify triggers (foods, stress, sleep changes).",
        "see_doctor": "If severe/frequent migraines, new pattern after age 50, or with fever/stiff neck/seizure.",
        "prevention": "Regular sleep schedule, stress management, avoid triggers, consider preventive medications."
    },
    "urinary tract infection (uti)": {
        "symptoms": ["painful urination", "frequent urination", "lower abdominal pain", "cloudy urine", "strong smelling urine", "blood in urine"],
        "advice": "Drink plenty of water, unsweetened cranberry juice, avoid irritants (caffeine, alcohol, spicy foods). Urinate frequently.",
        "see_doctor": "Antibiotics needed. Seek care if fever, back pain, nausea/vomiting, or symptoms worsening.",
        "prevention": "Stay hydrated, urinate after intercourse, wipe front to back, avoid harsh soaps."
    },
    "gastritis / acid reflux": {
        "symptoms": ["stomach pain", "nausea", "bloating", "burning sensation", "indigestion", "belching", "heartburn"],
        "advice": "Eat small, frequent meals. Avoid spicy, acidic, fried foods. Don't lie down after eating. Elevate head while sleeping.",
        "see_doctor": "If vomiting blood, black/tarry stools, severe pain, or unintentional weight loss.",
        "prevention": "Manage stress, avoid NSAIDs, limit alcohol and caffeine, maintain healthy weight."
    },
    "hypertension (high blood pressure)": {
        "symptoms": ["headache", "dizziness", "blurred vision", "chest discomfort", "shortness of breath", "nosebleeds"],
        "advice": "Reduce sodium intake (<1500mg/day), follow DASH diet (fruits, veggies, whole grains), exercise 30 min daily, limit alcohol.",
        "see_doctor": "If BP >180/120 with symptoms (hypertensive crisis), or persistent high readings despite lifestyle changes.",
        "prevention": "Regular BP monitoring, stress reduction, maintain healthy weight, limit caffeine."
    },
    "allergy": {
        "symptoms": ["sneezing", "itchy eyes", "runny nose", "rash", "hives", "nasal congestion", "watery eyes"],
        "advice": "Take antihistamines (cetirizine, loratadine). Use saline rinse. Avoid known allergens. Keep windows closed during high pollen.",
        "see_doctor": "If severe reaction, difficulty breathing, swelling of face/throat (anaphylaxis - emergency!).",
        "prevention": "Identify triggers, allergy testing, air purifiers, hypoallergenic bedding."
    },
    "anemia": {
        "symptoms": ["fatigue", "pale skin", "shortness of breath", "cold hands", "dizziness", "weakness", "rapid heartbeat"],
        "advice": "Eat iron-rich foods (spinach, red meat, lentils) with vitamin C (citrus). Consider iron supplements after blood test confirmation.",
        "see_doctor": "For blood test (CBC, ferritin, B12). Seek care if chest pain, severe fatigue, or worsening symptoms.",
        "prevention": "Balanced diet with iron, B12, and folate. Regular checkups for at-risk individuals."
    },
    "diabetes symptoms": {
        "symptoms": ["excessive thirst", "frequent urination", "blurred vision", "fatigue", "slow healing wounds", "tingling hands/feet", "hunger"],
        "advice": "Check blood sugar. Reduce sugar and refined carbs. Eat fiber-rich foods. Exercise 30 min daily. Monitor symptoms.",
        "see_doctor": "For HbA1c test, fasting glucose. Urgent if very high blood sugar, confusion, or fruity breath.",
        "prevention": "Healthy weight, regular exercise, balanced diet, avoid sugary drinks."
    },
    "dehydration": {
        "symptoms": ["thirst", "dry mouth", "dark urine", "dizziness", "fatigue", "dry skin", "headache"],
        "advice": "Drink water or oral rehydration solution. Avoid caffeine/alcohol. Eat water-rich foods (cucumber, watermelon).",
        "see_doctor": "If unable to keep fluids down, severe diarrhea/vomiting, confusion, or no urination for 8+ hours.",
        "prevention": "Drink water regularly, especially in heat/illness. Monitor urine color (pale yellow = good)."
    },
    "sinusitis": {
        "symptoms": ["facial pain", "nasal congestion", "thick nasal discharge", "headache", "tooth pain", "reduced smell"],
        "advice": "Use saline spray, humidifier, warm compresses. Stay hydrated. Over-the-counter decongestants (short term).",
        "see_doctor": "If symptoms >10 days, fever >102°F, double vision, or severe headache.",
        "prevention": "Avoid allergens, treat colds promptly, use nasal rinses, avoid smoke."
    }
}

def detect_disease_from_symptoms(user_message):
    """Analyze user message for symptom patterns and return disease advice."""
    msg_lower = user_message.lower()
    scores = {}
    
    for disease, info in SYMPTOM_DISEASE_MAP.items():
        score = 0
        matched_symptoms = []
        for symptom in info["symptoms"]:
            if symptom in msg_lower:
                score += 1
                matched_symptoms.append(symptom)
        if score > 0:
            scores[disease] = {"score": score, "matched": matched_symptoms, "info": info}
    
    if not scores:
        return None
    
    # Get best match (highest symptom score)
    best_disease = max(scores, key=lambda d: scores[d]["score"])
    best = scores[best_disease]
    score = best["score"]
    total_symptoms = len(best["info"]["symptoms"])
    confidence = "high" if score >= 3 else "moderate" if score >= 2 else "low"
    
    # Format response
    matched_list = ", ".join(best["matched"])
    response = f"**Possible condition:** {best_disease.title()} (confidence: {confidence})\n"
    response += f"**Symptoms detected:** {matched_list}\n\n"
    response += f"**What to do:** {best['info']['advice']}\n\n"
    response += f"**When to see a doctor:** {best['info']['see_doctor']}\n\n"
    response += f"**Prevention tips:** {best['info']['prevention']}\n\n"
    response += "⚠️ **Important:** This is AI-generated guidance. Always consult a healthcare professional for accurate diagnosis and treatment."
    
    return response

def get_general_symptom_advice(message):
    """Fallback advice when no specific disease matches."""
    msg_lower = message.lower()
    # Extract key symptoms mentioned
    symptom_keywords = ["pain", "ache", "fever", "cough", "nausea", "vomit", "diarrhea", "fatigue", 
                        "headache", "dizzy", "rash", "sore throat", "congestion", "chills", "sweating"]
    found = [kw for kw in symptom_keywords if kw in msg_lower]
    
    advice = "I notice you're describing some symptoms. While I can't provide a specific diagnosis, here are general guidelines:\n\n"
    advice += "**Immediate steps:**\n"
    advice += "- Rest and stay hydrated\n"
    advice += "- Monitor your symptoms (fever, pain level, duration)\n"
    advice += "- Use over-the-counter remedies as appropriate (fever reducers, pain relievers)\n\n"
    advice += "**When to seek medical care:**\n"
    advice += "- High fever (>101°F / 38.3°C) lasting >3 days\n"
    advice += "- Severe or worsening pain\n"
    advice += "- Difficulty breathing\n"
    advice += "- Confusion or altered mental state\n"
    advice += "- Chest pain or pressure\n\n"
    advice += "**Please consult a doctor** if symptoms persist, worsen, or you're concerned.\n\n"
    advice += "For better assistance, describe specific symptoms like 'fever and cough' or 'stomach pain and nausea'."
    return advice

# ============================================
# PARSING & ANALYSIS FUNCTIONS (Original)
# ============================================

def parse_lab_report(text):
    results = []
    lines = text.split("\n")
    for line in lines:
        line = line.strip().lower()
        if not line or len(line) < 3:
            continue
        patterns = [
            r'([a-zA-Z\s]+)[\s]*[:\-\=][\s]*([0-9.]+)[\s]*([a-zA-Z/%u]+)?',
            r'([a-zA-Z\s]+)[\s]+([0-9.]+)[\s]+([a-zA-Z/%u]+)',
            r'([a-zA-Z\s]+)[\s]*[:\-\=][\s]*([0-9.]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                test_name = match.group(1).strip().lower()
                value_str = match.group(2).strip()
                unit = match.group(3).strip() if len(match.groups()) > 2 and match.group(3) else ""
                try:
                    value = float(value_str)
                    found = False
                    for param_key, param_info in MEDICAL_RANGES.items():
                        if param_key in test_name or test_name in param_key:
                            results.append({
                                "test_name": test_name.title(),
                                "value": value,
                                "unit": unit if unit else param_info["unit"],
                                "normal_range": param_info["normal"],
                                "reference": param_info
                            })
                            found = True
                            break
                    if not found:
                        results.append({
                            "test_name": test_name.title(),
                            "value": value,
                            "unit": unit,
                            "normal_range": "Unknown",
                            "reference": None
                        })
                except ValueError:
                    continue
                break
    return results


def analyze_parameter(param):
    value = param["value"]
    normal_range = param["normal_range"]
    reference = param["reference"]

    if normal_range == "Unknown" or not reference:
        return {"status": "Unknown", "deviation": 0,
                "explanation": "Reference range not available for this parameter.",
                "recommendation": "Please consult a healthcare professional for interpretation."}

    status = "Normal"
    deviation = 0

    if "<" in normal_range:
        threshold = float(normal_range.replace("<", "").replace(">", "").strip())
        if ">" in normal_range:
            if value < threshold:
                status = "Low"
                deviation = ((threshold - value) / threshold) * 100 if threshold != 0 else 0
        else:
            if value > threshold:
                status = "High"
                deviation = ((value - threshold) / threshold) * 100 if threshold != 0 else 0
    elif "-" in normal_range:
        parts = normal_range.split("-")
        low = float(parts[0].strip())
        high = float(parts[1].strip())
        if value < low:
            status = "Low"
            deviation = ((low - value) / low) * 100 if low != 0 else 0
        elif value > high:
            status = "High"
            deviation = ((value - high) / high) * 100 if high != 0 else 0

    if status == "Normal":
        explanation = f"Your {param['test_name']} level of {value} {param['unit']} is within the normal range ({normal_range} {param['unit']})."
        recommendation = "Maintain your current healthy lifestyle. Continue regular exercise and balanced diet."
    elif status == "Low":
        condition = reference.get("low", "Low levels")
        explanation = f"Your {param['test_name']} level of {value} {param['unit']} is BELOW the normal range ({normal_range} {param['unit']}). This may indicate {condition}."
        recommendation = RECOMMENDATIONS_LOW.get(param['test_name'].lower(), "Consult a healthcare professional for personalized advice. Maintain balanced diet and regular exercise.")
    else:
        condition = reference.get("high", "High levels")
        explanation = f"Your {param['test_name']} level of {value} {param['unit']} is ABOVE the normal range ({normal_range} {param['unit']}). This may indicate {condition}."
        recommendation = RECOMMENDATIONS_HIGH.get(param['test_name'].lower(), "Consult a healthcare professional. Reduce processed foods, exercise regularly, stay hydrated, and maintain healthy weight.")

    return {"status": status, "deviation": round(deviation, 2), "explanation": explanation, "recommendation": recommendation}


def generate_full_report(lab_data, user_text):
    report = "# AI Health Report Analysis\n\n## Summary\nBased on your laboratory test report, I have analyzed the provided parameters. Here are my findings:\n\n"
    priority_concerns = []
    dietary_all = []
    lifestyle_all = []

    for param in lab_data:
        analysis = analyze_parameter(param)
        status_emoji = "OK" if analysis["status"] == "Normal" else "LOW" if analysis["status"] == "Low" else "HIGH"

        report += f"### {status_emoji} {param['test_name']}\n"
        report += f"- Value: {param['value']} {param['unit']}\n"
        report += f"- Normal Range: {param['normal_range']} {param['unit']}\n"
        report += f"- Status: {analysis['status']}\n"
        report += f"- Deviation: {analysis['deviation']}%\n"
        report += f"- Explanation: {analysis['explanation']}\n"
        report += f"- Recommendation: {analysis['recommendation']}\n\n"

        if analysis["status"] != "Normal" and analysis["deviation"] > 20:
            priority_concerns.append(f"{param['test_name']} ({analysis['status']}, {analysis['deviation']}% deviation)")

        if analysis["status"] != "Normal":
            if any(word in analysis["recommendation"].lower() for word in ["diet", "eat", "food", "consume"]):
                dietary_all.append(analysis["recommendation"])
            if any(word in analysis["recommendation"].lower() for word in ["exercise", "sleep", "stress", "hydrated"]):
                lifestyle_all.append(analysis["recommendation"])

    if priority_concerns:
        report += "## Priority Concerns\nThe following parameters require attention:\n"
        for c in priority_concerns:
            report += f"- {c}\n"
        report += "\n"

    if dietary_all:
        report += "## Dietary Recommendations\n"
        for tip in dietary_all[:3]:
            report += f"- {tip}\n"
        report += "\n"

    if lifestyle_all:
        report += "## Lifestyle Changes\n"
        for tip in lifestyle_all[:3]:
            report += f"- {tip}\n"
        report += "\n"

    report += """## Follow-Up Actions\n- Schedule an appointment with your primary care physician within 1-2 weeks\n- Bring this analysis to your doctor for discussion\n- Consider repeating abnormal tests in 4-6 weeks after lifestyle changes\n- Keep a health diary tracking symptoms and improvements\n\n## General Health Tips\n- Drink 8-10 glasses of water daily\n- Sleep 7-9 hours per night\n- Exercise at least 30 minutes, 5 days a week\n- Manage stress through meditation or yoga\n- Avoid smoking and limit alcohol consumption\n\n---\n\n**MEDICAL DISCLAIMER:** This AI-generated analysis is for informational purposes only and is NOT a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition."""
    return report


def get_chat_response(message):
    """Enhanced chat with disease detection from symptoms."""
    msg_lower = message.lower()
    
    # First, check if it's a lab report (contains numeric values with units)
    # Quick check: contains "mg/dL", "g/dL", "U/L", etc.
    lab_indicators = ["mg/dl", "g/dl", "u/l", "miu/l", "mmol/l", "k/ul", "m/ul"]
    is_likely_lab = any(ind in msg_lower for ind in lab_indicators) and re.search(r'\d+\.?\d*\s*(mg|g|u|mmol)', msg_lower)
    
    if is_likely_lab:
        # This will be handled by the lab analyzer in the main handler
        return None  # Signal to use lab analysis instead
    
    # Check for disease/condition keywords in existing knowledge base
    for keyword, response in CHAT_RESPONSES.items():
        if keyword in msg_lower:
            return response
    
    # Check for symptom-based disease detection
    symptom_indicators = ['fever', 'cough', 'pain', 'ache', 'nausea', 'vomit', 'diarrhea', 
                          'fatigue', 'headache', 'dizzy', 'rash', 'sore throat', 'runny nose', 
                          'congestion', 'chills', 'sweating', 'tired', 'weak', 'thirst', 'urination']
    
    if any(ind in msg_lower for ind in symptom_indicators):
        disease_response = detect_disease_from_symptoms(message)
        if disease_response:
            return disease_response
        else:
            # Fallback general symptom advice
            return get_general_symptom_advice(message)
    
    # Default response for non-symptom, non-keyword messages
    return f"I'm your AI Health Assistant! I can help with:\n\n✅ **Lab Report Analysis** - Paste your test results\n✅ **Disease Information** - Cholesterol, Diabetes, Thyroid, Anemia, Vitamin D, BP, Liver, Kidney\n✅ **Symptom Checker** - Describe your symptoms (e.g., 'I have fever and cough')\n\nFor your question about '{message}', please provide more details or consult a healthcare professional for personalized advice."


# ============================================
# HTML TEMPLATE (Fully Responsive, Unchanged GUI)
# ============================================

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
<title>AI Health Assistant - Lab Report Interpreter</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',system-ui,-apple-system,sans-serif;background:#f1f5f9;color:#1e293b;line-height:1.6}
.app-container{display:flex;height:100vh;width:100vw}
.sidebar{width:260px;background:#fff;border-right:1px solid #e2e8f0;display:flex;flex-direction:column;flex-shrink:0}
.sidebar-header{padding:20px 16px;border-bottom:1px solid #e2e8f0}
.logo{display:flex;align-items:center;gap:10px;font-size:1.1rem;font-weight:700;color:#2563eb}
.logo i{font-size:1.3rem;color:#ef4444;animation:hb 2s ease-in-out infinite}
@keyframes hb{0%,100%{transform:scale(1)}50%{transform:scale(1.1)}}
.subtitle{font-size:.7rem;color:#64748b;margin-top:2px;margin-left:30px}
.sidebar-nav{flex:1;padding:12px 10px;display:flex;flex-direction:column;gap:4px}
.nav-btn{display:flex;align-items:center;gap:10px;padding:10px 14px;border:none;background:transparent;color:#475569;font-size:.85rem;font-weight:500;border-radius:8px;cursor:pointer;transition:all .3s;text-align:left;width:100%}
.nav-btn:hover{background:#f1f5f9;color:#2563eb}
.nav-btn.active{background:#dbeafe;color:#2563eb;font-weight:600}
.nav-btn i{width:20px;text-align:center}
.sidebar-footer{padding:14px 16px;border-top:1px solid #e2e8f0;font-size:.75rem;color:#94a3b8}
.main-content{flex:1;display:flex;flex-direction:column;overflow:hidden;background:#f1f5f9}
.main-header{height:56px;background:#fff;border-bottom:1px solid #e2e8f0;display:flex;align-items:center;justify-content:space-between;padding:0 20px;flex-shrink:0}
.main-header h1{font-size:1.1rem;font-weight:600}
.tab-content{display:none;flex:1;overflow:hidden}
.tab-content.active{display:flex;flex-direction:column}
.chat-container{max-width:800px;margin:0 auto;width:100%;padding:0 16px;height:100%;display:flex;flex-direction:column}
.chat-messages{flex:1;overflow-y:auto;padding:16px 0;display:flex;flex-direction:column;gap:12px}
.welcome-message{text-align:center;padding:30px 16px}
.welcome-icon{width:64px;height:64px;background:linear-gradient(135deg,#dbeafe,#2563eb);border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 16px;font-size:1.5rem;color:#fff;animation:fl 3s ease-in-out infinite}
@keyframes fl{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}
.welcome-message h2{font-size:1.2rem;margin-bottom:6px}
.welcome-message>p{color:#64748b;font-size:.85rem;margin-bottom:20px}
.feature-cards{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:20px}
.feature-card{background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:16px 12px;transition:all .3s;cursor:pointer}
.feature-card:hover{transform:translateY(-3px);box-shadow:0 4px 12px rgba(0,0,0,.1);border-color:#dbeafe}
.feature-card h3{font-size:.8rem;font-weight:600;margin:8px 0 4px}
.feature-card p{font-size:.7rem;color:#64748b}
.quick-actions{margin-top:16px}
.quick-label{font-size:.8rem;color:#64748b;margin-bottom:8px}
.quick-btn{display:inline-block;padding:8px 14px;margin:4px;background:#fff;border:1px solid #cbd5e1;border-radius:16px;font-size:.75rem;color:#475569;cursor:pointer;transition:all .3s}
.quick-btn:hover{background:#dbeafe;border-color:#2563eb;color:#2563eb}
.message{display:flex;gap:10px;max-width:90%;animation:fi .3s ease}
@keyframes fi{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.message.user{align-self:flex-end;flex-direction:row-reverse}
.message.ai{align-self:flex-start}
.message-avatar{width:32px;height:32px;border-radius:50%;display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:.8rem}
.message.user .message-avatar{background:#2563eb;color:#fff}
.message.ai .message-avatar{background:#dbeafe;color:#2563eb}
.message-content{background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:12px 14px;font-size:.85rem;line-height:1.6;box-shadow:0 1px 2px rgba(0,0,0,.05)}
.message.user .message-content{background:#2563eb;color:#fff;border-color:#2563eb}
.message-time{font-size:.65rem;color:#94a3b8;margin-top:3px;text-align:right}
.chat-input-area{padding:12px 0 16px;flex-shrink:0}
.input-wrapper{display:flex;gap:8px;background:#fff;border:1px solid #cbd5e1;border-radius:10px;padding:6px 6px 6px 12px;box-shadow:0 1px 2px rgba(0,0,0,.05)}
.input-wrapper:focus-within{border-color:#2563eb;box-shadow:0 0 0 3px #dbeafe}
#chatInput{flex:1;border:none;outline:none;font-size:.85rem;resize:none;max-height:100px;font-family:inherit;background:transparent}
.send-btn{width:36px;height:36px;border-radius:8px;border:none;background:#2563eb;color:#fff;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all .3s}
.send-btn:hover{background:#1d4ed8;transform:scale(1.05)}
.send-btn:disabled{background:#cbd5e1;cursor:not-allowed;transform:none}
.input-hint{font-size:.7rem;color:#94a3b8;margin-top:6px;text-align:center}
.analyzer-container{display:grid;grid-template-columns:1fr 1fr;gap:20px;height:100%;padding:20px;overflow:hidden}
.analyzer-input-section,.analyzer-results{background:#fff;border-radius:10px;border:1px solid #e2e8f0;overflow:hidden;display:flex;flex-direction:column}
.input-header{padding:20px 20px 12px;border-bottom:1px solid #e2e8f0}
.input-header h2{font-size:1rem;font-weight:600;display:flex;align-items:center;gap:8px;margin-bottom:6px}
.input-header p{font-size:.8rem;color:#64748b}
.input-methods{flex:1;overflow-y:auto;padding:16px 20px}
.method-tabs{display:flex;gap:6px;margin-bottom:12px}
.method-tab{padding:6px 12px;border:1px solid #cbd5e1;background:#fff;border-radius:6px;font-size:.8rem;font-weight:500;color:#475569;cursor:pointer;transition:all .3s}
.method-tab.active{background:#2563eb;color:#fff;border-color:#2563eb}
#labReportInput{width:100%;border:1px solid #cbd5e1;border-radius:8px;padding:12px;font-size:.8rem;font-family:monospace;resize:vertical;min-height:160px;outline:none}
#labReportInput:focus{border-color:#2563eb;box-shadow:0 0 0 3px #dbeafe}
.sample-reports{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.sample-btn{display:flex;align-items:center;gap:10px;padding:12px;background:#f1f5f9;border:1px solid #e2e8f0;border-radius:8px;cursor:pointer;transition:all .3s;text-align:left;font-size:.8rem}
.sample-btn:hover{background:#dbeafe;border-color:#2563eb}
.analyze-btn{margin:0 20px 20px;padding:12px 20px;background:linear-gradient(135deg,#2563eb,#0ea5e9);color:#fff;border:none;border-radius:8px;font-size:.9rem;font-weight:600;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:8px;transition:all .3s;box-shadow:0 4px 12px rgba(37,99,235,.3)}
.analyze-btn:hover{transform:translateY(-2px);box-shadow:0 6px 16px rgba(37,99,235,.4)}
.analyze-btn:disabled{background:#cbd5e1;cursor:not-allowed;transform:none;box-shadow:none}
.results-placeholder{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;color:#94a3b8;padding:30px}
.results-placeholder i{font-size:2.5rem;margin-bottom:12px;opacity:.5}
.results-content{padding:20px;overflow-y:auto}
.results-summary{background:linear-gradient(135deg,#dbeafe,#eff6ff);border:1px solid #dbeafe;border-radius:8px;padding:16px;margin-bottom:20px}
.results-summary h3{font-size:.9rem;color:#1d4ed8;margin-bottom:10px}
.results-summary p{font-size:.8rem;color:#334155}
.param-card{background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:16px;margin-bottom:12px}
.param-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}
.param-name{font-size:.9rem;font-weight:600}
.param-status{padding:3px 10px;border-radius:12px;font-size:.7rem;font-weight:600;text-transform:uppercase}
.param-status.normal{background:#d1fae5;color:#065f46}
.param-status.low{background:#fef3c7;color:#92400e}
.param-status.high{background:#fee2e2;color:#991b1b}
.param-values{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:12px;padding:10px;background:#f8fafc;border-radius:6px}
.param-value-item{text-align:center}
.param-value-item .label{font-size:.7rem;color:#64748b;margin-bottom:2px}
.param-value-item .value{font-size:.85rem;font-weight:600}
.param-value-item .value.deviated{color:#ef4444}
.param-explanation{font-size:.8rem;color:#475569;line-height:1.5;margin-bottom:10px;padding:10px;background:#f8fafc;border-radius:6px;border-left:3px solid #06b6d4}
.param-recommendation{font-size:.75rem;color:#334155;line-height:1.5;padding:10px;background:#f0fdf4;border-radius:6px;border-left:3px solid #10b981}
.ai-analysis{margin-top:20px;padding:20px;background:#fff;border:1px solid #e2e8f0;border-radius:8px}
.ai-analysis h3{font-size:.95rem;margin-bottom:12px;display:flex;align-items:center;gap:8px;color:#1e293b}
.ai-analysis-content{font-size:.8rem;line-height:1.7;color:#334155}
.loading-overlay{position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(15,23,42,.7);display:none;align-items:center;justify-content:center;z-index:1000}
.loading-overlay.active{display:flex}
.loading-spinner{text-align:center;color:#fff}
.spinner{width:48px;height:48px;border:3px solid rgba(255,255,255,.3);border-top-color:#fff;border-radius:50%;animation:sp 1s linear infinite;margin:0 auto 16px}
@keyframes sp{to{transform:rotate(360deg)}}
.loading-spinner p{font-size:1rem;font-weight:500;margin-bottom:6px}
.loading-sub{font-size:.8rem;opacity:.8}
.toast{position:fixed;bottom:20px;right:20px;background:#1e293b;color:#fff;padding:12px 16px;border-radius:8px;display:flex;align-items:center;gap:8px;font-size:.85rem;box-shadow:0 4px 12px rgba(0,0,0,.2);transform:translateY(100px);opacity:0;transition:all .4s;z-index:1001}
.toast.show{transform:translateY(0);opacity:1}
.toast i{color:#10b981}
.history-container{max-width:800px;margin:0 auto;width:100%;padding:20px;height:100%;overflow-y:auto}
.history-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px}
.history-header h2{font-size:1.1rem;font-weight:600;display:flex;align-items:center;gap:8px}
.btn-secondary{padding:6px 12px;background:#fff;border:1px solid #cbd5e1;border-radius:6px;font-size:.8rem;color:#475569;cursor:pointer;display:flex;align-items:center;gap:6px;transition:all .3s}
.btn-secondary:hover{background:#f1f5f9;color:#ef4444;border-color:#ef4444}
.history-list{display:flex;flex-direction:column;gap:10px}
.history-item{background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:16px;cursor:pointer;transition:all .3s}
.history-item:hover{box-shadow:0 4px 12px rgba(0,0,0,.1);border-color:#dbeafe}
.history-item-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}
.history-item-title{font-size:.85rem;font-weight:600}
.history-item-date{font-size:.75rem;color:#94a3b8}
.history-item-preview{font-size:.8rem;color:#64748b;line-height:1.4;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.history-item-stats{display:flex;gap:12px;margin-top:10px;padding-top:10px;border-top:1px solid #f1f5f9}
.history-stat{display:flex;align-items:center;gap:4px;font-size:.75rem;color:#64748b}
.empty-state{text-align:center;padding:40px 16px;color:#94a3b8}
.empty-state i{font-size:2.5rem;margin-bottom:12px;opacity:.5}
.about-container{max-width:700px;margin:0 auto;width:100%;padding:20px;height:100%;overflow-y:auto}
.about-card{background:#fff;border-radius:10px;border:1px solid #e2e8f0;overflow:hidden}
.about-header{text-align:center;padding:30px 20px;background:linear-gradient(135deg,#dbeafe,#eff6ff);border-bottom:1px solid #e2e8f0}
.about-logo{width:64px;height:64px;background:linear-gradient(135deg,#2563eb,#0ea5e9);border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 16px;font-size:1.5rem;color:#fff}
.about-header h1{font-size:1.3rem;margin-bottom:6px}
.version{font-size:.8rem;color:#64748b;background:#fff;display:inline-block;padding:3px 10px;border-radius:12px;border:1px solid #e2e8f0}
.about-section{padding:20px;border-bottom:1px solid #e2e8f0}
.about-section:last-child{border-bottom:none}
.about-section h3{font-size:.9rem;font-weight:600;margin-bottom:12px;display:flex;align-items:center;gap:8px;color:#1e293b}
.about-section p{font-size:.8rem;color:#475569;line-height:1.6;margin-bottom:8px}
.info-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-top:12px}
.info-item{display:flex;flex-direction:column;gap:2px}
.info-label{font-size:.75rem;color:#64748b;font-weight:500}
.info-value{font-size:.8rem;color:#1e293b;font-weight:600}
.architecture-flow{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap;padding:16px;background:#f1f5f9;border-radius:8px}
.flow-step{display:flex;flex-direction:column;align-items:center;gap:6px;text-align:center}
.flow-icon{width:40px;height:40px;background:#fff;border:2px solid #dbeafe;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:1rem;color:#2563eb}
.flow-step span{font-size:.65rem;color:#475569;font-weight:500;max-width:70px}
.flow-arrow{color:#94a3b8;font-size:.8rem}
.disclaimer-box{display:flex;gap:12px;padding:16px;background:#fef3c7;border:1px solid #f59e0b;border-radius:8px}
.disclaimer-box i{font-size:1.2rem;color:#f59e0b;flex-shrink:0}
.disclaimer-box p{font-size:.75rem;color:#334155;line-height:1.6;margin:0}
.tech-tags{display:flex;flex-wrap:wrap;gap:6px}
.tech-tag{padding:4px 10px;background:#dbeafe;color:#1d4ed8;border-radius:12px;font-size:.75rem;font-weight:500}
@media(max-width:900px){.analyzer-container{grid-template-columns:1fr}.feature-cards{grid-template-columns:1fr}}
@media(max-width:600px){.sidebar{width:60px}.sidebar-header .logo span,.subtitle,.nav-btn span,.sidebar-footer{display:none}.nav-btn{justify-content:center;padding:10px}.nav-btn i{width:auto}.main-header h1{font-size:.9rem}.message{max-width:95%}.sample-reports{grid-template-columns:1fr}.param-values{grid-template-columns:1fr}.architecture-flow{flex-direction:column;gap:12px}.flow-arrow{transform:rotate(90deg)}}
::-webkit-scrollbar{width:5px}
::-webkit-scrollbar-thumb{background:#cbd5e1;border-radius:3px}
</style>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
</head>
<body>
<div class="app-container">
<aside class="sidebar">
<div class="sidebar-header">
<div class="logo"><i class="fas fa-heartbeat"></i><span>AI Health</span></div>
<p class="subtitle">Lab Report Interpreter + Symptom Checker</p>
</div>
<nav class="sidebar-nav">
<button class="nav-btn active" data-tab="chat"><i class="fas fa-comments"></i><span>Health Chat</span></button>
<button class="nav-btn" data-tab="analyzer"><i class="fas fa-flask"></i><span>Lab Analyzer</span></button>
<button class="nav-btn" data-tab="history"><i class="fas fa-history"></i><span>History</span></button>
<button class="nav-btn" data-tab="about"><i class="fas fa-info-circle"></i><span>About</span></button>
</nav>
<div class="sidebar-footer">
<div style="display:flex;align-items:center;gap:6px;margin-bottom:4px">
<span style="width:8px;height:8px;border-radius:50%;background:#10b981;display:inline-block"></span>
<span>AI Disease Detection</span>
</div>
<p>UET Taxila 2026</p>
</div>
</aside>
<main class="main-content">
<header class="main-header">
<h1 id="pageTitle">Health Chat</h1>
<div style="display:flex;gap:8px">
<button id="clearChat" style="width:32px;height:32px;border-radius:6px;border:1px solid #e2e8f0;background:#fff;color:#64748b;cursor:pointer"><i class="fas fa-trash-alt"></i></button>
</div>
</header>
<div class="tab-content active" id="chat-tab">
<div class="chat-container">
<div class="chat-messages" id="chatMessages">
<div class="welcome-message">
<div class="welcome-icon"><i class="fas fa-robot"></i></div>
<h2>Welcome to AI Health Assistant</h2>
<p>I can detect diseases from your symptoms and analyze lab reports!</p>
<div class="feature-cards">
<div class="feature-card" onclick="document.querySelector('[data-tab=\\'analyzer\\']').click()">
<i class="fas fa-flask" style="font-size:1.2rem;color:#2563eb"></i>
<h3>Analyze Lab Reports</h3>
<p>Paste your test results for detailed interpretation</p>
</div>
<div class="feature-card" onclick="sendQuick('I have fever, body aches, and cough')">
<i class="fas fa-stethoscope" style="font-size:1.2rem;color:#2563eb"></i>
<h3>Symptom Checker</h3>
<p>Describe your symptoms to get possible disease insights</p>
</div>
<div class="feature-card" onclick="sendQuick('What foods help with anemia?')">
<i class="fas fa-apple-alt" style="font-size:1.2rem;color:#2563eb"></i>
<h3>Dietary Advice</h3>
<p>Get personalized food recommendations</p>
</div>
</div>
<div class="quick-actions">
<p class="quick-label">Try asking:</p>
<button class="quick-btn" onclick="sendQuick('What does high cholesterol mean?')">What does high cholesterol mean?</button>
<button class="quick-btn" onclick="sendQuick('I have fever and headache')">I have fever and headache</button>
<button class="quick-btn" onclick="sendQuick('Feeling very thirsty and urinating often')">Feeling very thirsty and urinating often</button>
<button class="quick-btn" onclick="sendQuick('Painful urination and lower belly pain')">Painful urination and lower belly pain</button>
</div>
</div>
</div>
<div class="chat-input-area">
<div class="input-wrapper">
<textarea id="chatInput" placeholder="Ask a health question, describe symptoms, or paste lab report..." rows="1"></textarea>
<button class="send-btn" id="sendBtn" onclick="sendMessage()"><i class="fas fa-paper-plane"></i></button>
</div>
<p class="input-hint">Press Enter to send, Shift+Enter for new line</p>
</div>
</div>
</div>
<div class="tab-content" id="analyzer-tab">
<div class="analyzer-container">
<div class="analyzer-input-section">
<div class="input-header">
<h2><i class="fas fa-upload"></i> Upload Lab Report</h2>
<p>Paste your lab report text below. The AI will analyze each parameter.</p>
</div>
<div class="input-methods">
<div class="method-tabs">
<button class="method-tab active" data-method="text">Text Input</button>
<button class="method-tab" data-method="sample">Sample Reports</button>
</div>
<div class="method-content active" id="text-method">
<textarea id="labReportInput" placeholder="Paste your lab report here...&#10;&#10;Example:&#10;Hemoglobin: 11.5 g/dL&#10;Glucose: 95 mg/dL&#10;Cholesterol: 220 mg/dL&#10;WBC: 8.5 K/uL&#10;Platelet: 180 K/uL&#10;Creatinine: 1.2 mg/dL&#10;ALT: 45 U/L&#10;Vitamin D: 18 ng/mL&#10;TSH: 5.2 mIU/L&#10;Blood Pressure: 140/90 mmHg" rows="10"></textarea>
</div>
<div class="method-content" id="sample-method">
<div class="sample-reports">
<button class="sample-btn" onclick="loadSample('anemia')"><i class="fas fa-vial"></i><span>Anemia Profile</span></button>
<button class="sample-btn" onclick="loadSample('diabetes')"><i class="fas fa-vial"></i><span>Diabetes Screening</span></button>
<button class="sample-btn" onclick="loadSample('lipid')"><i class="fas fa-vial"></i><span>Lipid Panel</span></button>
<button class="sample-btn" onclick="loadSample('thyroid')"><i class="fas fa-vial"></i><span>Thyroid Function</span></button>
<button class="sample-btn" onclick="loadSample('liver')"><i class="fas fa-vial"></i><span>Liver Function</span></button>
<button class="sample-btn" onclick="loadSample('comprehensive')"><i class="fas fa-vial"></i><span>Comprehensive Panel</span></button>
</div>
</div>
</div>
<button class="analyze-btn" id="analyzeBtn" onclick="analyzeReport()"><i class="fas fa-microscope"></i>Analyze Report</button>
</div>
<div class="analyzer-results" id="analyzerResults">
<div class="results-placeholder">
<i class="fas fa-clipboard-list"></i>
<p>Analysis results will appear here after you analyze a report</p>
</div>
</div>
</div>
</div>
<div class="tab-content" id="history-tab">
<div class="history-container">
<div class="history-header">
<h2><i class="fas fa-history"></i> Analysis History</h2>
<button class="btn-secondary" onclick="clearHistory()"><i class="fas fa-trash"></i> Clear All</button>
</div>
<div class="history-list" id="historyList">
<div class="empty-state">
<i class="fas fa-inbox"></i>
<p>No history yet. Analyze a lab report to see it here.</p>
</div>
</div>
</div>
</div>
<div class="tab-content" id="about-tab">
<div class="about-container">
<div class="about-card">
<div class="about-header">
<div class="about-logo"><i class="fas fa-heartbeat"></i></div>
<h1>AI Health Assistant</h1>
<p class="version">Version 2.0 - Enhanced Disease Detection</p>
</div>
<div class="about-section">
<h3><i class="fas fa-graduation-cap"></i> Academic Project</h3>
<p>This project is developed as part of the <strong>Artificial Intelligence</strong> course assignment at <strong>University of Engineering and Technology, Taxila</strong>.</p>
<div class="info-grid">
<div class="info-item"><span class="info-label">Student</span><span class="info-value">Romaisa Abbasi (23-SE-036)</span></div>
<div class="info-item"><span class="info-label">Supervisor</span><span class="info-value">Dr. Kanwal Yousaf</span></div>
<div class="info-item"><span class="info-label">Department</span><span class="info-value">Software Engineering</span></div>
<div class="info-item"><span class="info-label">Faculty</span><span class="info-value">Telecom & Info Engineering</span></div>
</div>
</div>
<div class="about-section">
<h3><i class="fas fa-cogs"></i> System Architecture</h3>
<div class="architecture-flow">
<div class="flow-step"><div class="flow-icon"><i class="fas fa-user"></i></div><span>User Input</span></div>
<div class="flow-arrow"><i class="fas fa-arrow-right"></i></div>
<div class="flow-step"><div class="flow-icon"><i class="fas fa-filter"></i></div><span>Text Processing</span></div>
<div class="flow-arrow"><i class="fas fa-arrow-right"></i></div>
<div class="flow-step"><div class="flow-icon"><i class="fas fa-brain"></i></div><span>AI Analysis</span></div>
<div class="flow-arrow"><i class="fas fa-arrow-right"></i></div>
<div class="flow-step"><div class="flow-icon"><i class="fas fa-file-medical-alt"></i></div><span>Report & Recommendations</span></div>
</div>
</div>
<div class="about-section">
<h3><i class="fas fa-shield-alt"></i> Medical Disclaimer</h3>
<div class="disclaimer-box">
<i class="fas fa-exclamation-triangle"></i>
<p>This AI Health Assistant is for <strong>informational and educational purposes only</strong>. It is <strong>NOT</strong> a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider.</p>
</div>
</div>
<div class="about-section">
<h3><i class="fas fa-code"></i> Technologies Used</h3>
<div class="tech-tags">
<span class="tech-tag">Python</span><span class="tech-tag">HTTP Server</span><span class="tech-tag">NLP</span><span class="tech-tag">Symptom Matching</span><span class="tech-tag">HTML5/CSS3</span><span class="tech-tag">JavaScript</span><span class="tech-tag">No External APIs</span>
</div>
</div>
</div>
</div>
</div>
</main>
</div>
<div class="loading-overlay" id="loadingOverlay">
<div class="loading-spinner">
<div class="spinner"></div>
<p>Analyzing...</p>
<span class="loading-sub">Processing your request</span>
</div>
</div>
<div class="toast" id="toast"><i class="fas fa-check-circle"></i><span id="toastMessage">Done</span></div>
<script>
const samples={anemia:`Complete Blood Count (CBC)\nHemoglobin: 9.8 g/dL\nRBC: 3.2 M/uL\nWBC: 6.5 K/uL\nPlatelet: 220 K/uL\nMCV: 78 fL\nMCH: 27 pg\nIron: 45 ug/dL\nFerritin: 12 ng/mL\nVitamin B12: 180 pg/mL\nFolate: 3.2 ng/mL`,diabetes:`Diabetes Screening Panel\nGlucose (Fasting): 145 mg/dL\nGlucose (Post-Prandial): 195 mg/dL\nHbA1c: 7.2%\nInsulin: 18 uIU/mL\nC-Peptide: 2.8 ng/mL\nMicroalbumin: 35 mg/L\nCreatinine: 1.0 mg/dL\nBlood Pressure: 135/85 mmHg`,lipid:`Lipid Profile\nTotal Cholesterol: 245 mg/dL\nLDL Cholesterol: 165 mg/dL\nHDL Cholesterol: 32 mg/dL\nTriglycerides: 280 mg/dL\nTotal Cholesterol/HDL Ratio: 7.6\nLDL/HDL Ratio: 5.2\nVLDL: 56 mg/dL`,thyroid:`Thyroid Function Test\nTSH: 6.8 mIU/L\nT3: 0.9 ng/mL\nT4: 5.2 ug/dL\nFree T3: 2.1 pg/mL\nFree T4: 0.8 ng/dL\nAnti-TPO: 45 IU/mL\nThyroglobulin: 25 ng/mL`,liver:`Liver Function Test\nALT (SGPT): 85 U/L\nAST (SGOT): 72 U/L\nALP: 140 U/L\nBilirubin (Total): 2.1 mg/dL\nBilirubin (Direct): 0.8 mg/dL\nBilirubin (Indirect): 1.3 mg/dL\nAlbumin: 3.2 g/dL\nTotal Protein: 6.8 g/dL\nGGT: 65 U/L\nPT/INR: 1.2`,comprehensive:`Comprehensive Metabolic Panel\nGlucose: 110 mg/dL\nHemoglobin: 13.2 g/dL\nWBC: 9.2 K/uL\nPlatelet: 280 K/uL\nCholesterol: 210 mg/dL\nLDL: 130 mg/dL\nHDL: 38 mg/dL\nTriglycerides: 195 mg/dL\nCreatinine: 1.1 mg/dL\nBUN: 18 mg/dL\nSodium: 142 mEq/L\nPotassium: 4.8 mEq/L\nCalcium: 9.2 mg/dL\nVitamin D: 22 ng/mL\nTSH: 4.5 mIU/L\nALT: 55 U/L\nAST: 48 U/L\nBlood Pressure: 138/88 mmHg\nUric Acid: 7.5 mg/dL\nCRP: 15 mg/L`};
let analysisHistory=[];
function init(){setupNav();setupChat();setupMethods();loadHistory();}
function setupNav(){document.querySelectorAll('.nav-btn').forEach(btn=>{btn.addEventListener('click',()=>{const tab=btn.dataset.tab;document.querySelectorAll('.nav-btn').forEach(b=>b.classList.remove('active'));btn.classList.add('active');document.querySelectorAll('.tab-content').forEach(c=>c.classList.remove('active'));document.getElementById(tab+'-tab').classList.add('active');document.getElementById('pageTitle').textContent={chat:'Health Chat',analyzer:'Lab Report Analyzer',history:'Analysis History',about:'About Project'}[tab];if(tab==='history')renderHistory();});});document.getElementById('clearChat').addEventListener('click',()=>{if(confirm('Clear chat history?')){document.getElementById('chatMessages').innerHTML='<div class="welcome-message"><div class="welcome-icon"><i class="fas fa-robot"></i></div><h2>Chat Cleared</h2><p>Start a new conversation! Try describing your symptoms or ask health questions.</p></div>';}});}
function setupChat(){const input=document.getElementById('chatInput');input.addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();sendMessage();}});input.addEventListener('input',()=>{input.style.height='auto';input.style.height=Math.min(input.scrollHeight,100)+'px';});}
function setupMethods(){document.querySelectorAll('.method-tab').forEach(tab=>{tab.addEventListener('click',()=>{const method=tab.dataset.method;document.querySelectorAll('.method-tab').forEach(t=>t.classList.remove('active'));tab.classList.add('active');document.querySelectorAll('.method-content').forEach(c=>c.classList.remove('active'));document.getElementById(method+'-method').classList.add('active');});});}
function sendQuick(msg){document.getElementById('chatInput').value=msg;sendMessage();}
async function sendMessage(){const input=document.getElementById('chatInput');const msg=input.value.trim();if(!msg)return;input.value='';input.style.height='auto';addMsg('user',msg);const btn=document.getElementById('sendBtn');btn.disabled=true;btn.innerHTML='<i class="fas fa-spinner fa-spin"></i>';try{const res=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg})});const data=await res.json();if(data.success){if(data.is_lab_analysis && data.structured_results){let summary='\\n\\n**Quick Summary:**\\n';data.structured_results.forEach(p=>{const emoji=p.status==='Normal'?'✅':p.status==='Low'?'⚠️':'🔴';summary+=`${emoji} **${p.test_name}**: ${p.value} ${p.unit} (${p.status})\\n`;});addMsg('ai',data.ai_analysis+summary);saveHistory({type:'lab',timestamp:data.timestamp,results:data.structured_results,text:msg,analysis:data.ai_analysis});}else{addMsg('ai',data.response);}}else{addMsg('ai','⚠️ Error: '+(data.error||'Something went wrong'));}}catch(e){addMsg('ai','⚠️ Network error: '+e.message);}finally{btn.disabled=false;btn.innerHTML='<i class="fas fa-paper-plane"></i>';}}
function addMsg(sender,text){const container=document.getElementById('chatMessages');const welcome=container.querySelector('.welcome-message');if(welcome)welcome.remove();const div=document.createElement('div');div.className='message '+sender;const avatar=sender==='user'?'<i class="fas fa-user"></i>':'<i class="fas fa-robot"></i>';const time=new Date().toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'});let formatted=text.replace(/\\*\\*(.*?)\\*\\*/g,'<strong>$1</strong>').replace(/\\n/g,'<br>');div.innerHTML='<div class="message-avatar">'+avatar+'</div><div><div class="message-content">'+formatted+'</div><div class="message-time">'+time+'</div></div>';container.appendChild(div);container.scrollTop=container.scrollHeight;}
function loadSample(type){document.getElementById('labReportInput').value=samples[type]||'';document.querySelectorAll('.method-tab').forEach(t=>t.classList.remove('active'));document.querySelector('[data-method="text"]').classList.add('active');document.querySelectorAll('.method-content').forEach(c=>c.classList.remove('active'));document.getElementById('text-method').classList.add('active');showToast('Loaded '+type+' sample');}
async function analyzeReport(){const input=document.getElementById('labReportInput');const text=input.value.trim();if(!text){showToast('Please enter lab report data');return;}document.getElementById('loadingOverlay').classList.add('active');try{const res=await fetch('/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({report_text:text})});const data=await res.json();if(data.success){showResults(data,text);saveHistory({type:'lab',timestamp:data.timestamp,results:data.structured_results,text:text,analysis:data.ai_analysis});showToast('Analysis complete! '+data.parsed_count+' parameters found');}else{showToast(data.error||'Analysis failed');}}catch(e){showToast('Network error');}finally{document.getElementById('loadingOverlay').classList.remove('active');}}
function showResults(data,rawText){const container=document.getElementById('analyzerResults');let html='<div class="results-content">';const abnormal=data.structured_results.filter(r=>r.status!=='Normal').length;const normal=data.structured_results.length-abnormal;html+='<div class="results-summary"><h3><i class="fas fa-chart-pie"></i> Analysis Summary</h3><p><strong>'+data.parsed_count+'</strong> parameters | <strong style="color:#10b981">'+normal+'</strong> normal | <strong style="color:'+(abnormal>0?'#ef4444':'#10b981')+'">'+abnormal+'</strong> abnormal</p><p style="margin-top:6px;font-size:.75rem">Analyzed: '+data.timestamp+'</p></div>';data.structured_results.forEach(p=>{const a=p.status==='Normal'?'✅':p.status==='Low'?'⚠️':'🔴';const dev=p.deviation>0?'deviated':'';html+='<div class="param-card"><div class="param-header"><span class="param-name">'+a+' '+p.test_name+'</span><span class="param-status '+p.status.toLowerCase()+'">'+p.status+'</span></div><div class="param-values"><div class="param-value-item"><div class="label">Your Value</div><div class="value '+dev+'">'+p.value+' '+p.unit+'</div></div><div class="param-value-item"><div class="label">Normal Range</div><div class="value">'+p.normal_range+' '+p.unit+'</div></div><div class="param-value-item"><div class="label">Deviation</div><div class="value '+dev+'">'+p.deviation+'%</div></div></div><div class="param-explanation"><strong>💡 Explanation:</strong> '+p.explanation+'</div><div class="param-recommendation"><strong>🥗 Recommendation:</strong> '+p.recommendation+'</div></div>';});if(data.ai_analysis){let formatted=data.ai_analysis.replace(/\\*\\*(.*?)\\*\\*/g,'<strong>$1</strong>').replace(/\\n/g,'<br>');html+='<div class="ai-analysis"><h3><i class="fas fa-brain"></i> AI Detailed Analysis</h3><div class="ai-analysis-content">'+formatted+'</div></div>';}html+='</div>';container.innerHTML=html;}
function saveHistory(item){item.id=Date.now();analysisHistory.unshift(item);if(analysisHistory.length>50)analysisHistory=analysisHistory.slice(0,50);localStorage.setItem('aiHealthHistory',JSON.stringify(analysisHistory));}
function loadHistory(){const stored=localStorage.getItem('aiHealthHistory');if(stored)analysisHistory=JSON.parse(stored);}
function renderHistory(){const list=document.getElementById('historyList');if(analysisHistory.length===0){list.innerHTML='<div class="empty-state"><i class="fas fa-inbox"></i><p>No history yet. Analyze a lab report to see it here.</p></div>';return;}let html='';analysisHistory.forEach(item=>{const date=new Date(item.timestamp).toLocaleString();const ab=item.results?item.results.filter(r=>r.status!=='Normal').length:0;const nm=item.results?item.results.filter(r=>r.status==='Normal').length:0;html+='<div class="history-item" onclick="viewHistory('+item.id+')"><div class="history-item-header"><span class="history-item-title">Lab Analysis - '+(item.results?item.results.length:0)+' Parameters</span><span class="history-item-date">'+date+'</span></div><div class="history-item-preview">'+item.text.substring(0,100)+'...</div><div class="history-item-stats"><span class="history-stat"><i class="fas fa-check-circle" style="color:#10b981"></i> '+nm+' Normal</span><span class="history-stat"><i class="fas fa-exclamation-circle" style="color:'+(ab>0?'#ef4444':'#10b981')+'"></i> '+ab+' Abnormal</span></div></div>';});list.innerHTML=html;}
function viewHistory(id){const item=analysisHistory.find(h=>h.id===id);if(!item)return;document.querySelector('[data-tab="analyzer"]').click();document.getElementById('labReportInput').value=item.text;showResults({success:true,parsed_count:item.results.length,structured_results:item.results,ai_analysis:item.analysis||'',timestamp:item.timestamp},item.text);}
function clearHistory(){if(confirm('Clear all history?')){analysisHistory=[];localStorage.removeItem('aiHealthHistory');renderHistory();showToast('History cleared');}}
function showToast(msg){const toast=document.getElementById('toast');document.getElementById('toastMessage').textContent=msg;toast.classList.add('show');setTimeout(()=>toast.classList.remove('show'),3000);}
document.addEventListener('DOMContentLoaded',init);
</script>
</body>
</html>
"""

# ============================================
# HTTP SERVER (Enhanced)
# ============================================

class HealthHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path
        if path == '/' or path == '/index.html':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode('utf-8'))
        elif path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "healthy",
                "mode": "standalone_with_disease_detection",
                "api": "offline",
                "timestamp": datetime.now().isoformat()
            }).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        path = self.path
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        try:
            data = json.loads(body)
        except:
            data = {}

        if path == '/analyze':
            report_text = data.get('report_text', '').strip()
            if not report_text:
                self._send_json({"error": "No report text provided"}, 400)
                return
            lab_data = parse_lab_report(report_text)
            if not lab_data:
                self._send_json({"error": "Could not extract test parameters. Format: 'Hemoglobin: 11.5 g/dL'"}, 400)
                return
            structured_results = []
            for param in lab_data:
                analysis = analyze_parameter(param)
                structured_results.append({
                    "test_name": param["test_name"],
                    "value": param["value"],
                    "unit": param["unit"],
                    "normal_range": param["normal_range"],
                    "status": analysis["status"],
                    "deviation": analysis["deviation"],
                    "explanation": analysis["explanation"],
                    "recommendation": analysis["recommendation"]
                })
            ai_analysis = generate_full_report(lab_data, report_text)
            self._send_json({
                "success": True,
                "parsed_count": len(lab_data),
                "structured_results": structured_results,
                "ai_analysis": ai_analysis,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        
        elif path == '/chat':
            message = data.get('message', '').strip()
            if not message:
                self._send_json({"error": "No message provided"}, 400)
                return
            
            # Check if it's a lab report (has numeric values with units)
            lab_indicators = ["mg/dl", "g/dl", "u/l", "miu/l", "mmol/l", "k/ul", "m/ul"]
            is_likely_lab = any(ind in message.lower() for ind in lab_indicators) and re.search(r'\d+\.?\d*\s*(mg|g|u|mmol)', message.lower())
            
            if is_likely_lab:
                # Process as lab report
                lab_data = parse_lab_report(message)
                if lab_data and len(lab_data) >= 1:
                    structured_results = []
                    for param in lab_data:
                        analysis = analyze_parameter(param)
                        structured_results.append({
                            "test_name": param["test_name"],
                            "value": param["value"],
                            "unit": param["unit"],
                            "normal_range": param["normal_range"],
                            "status": analysis["status"],
                            "deviation": analysis["deviation"],
                            "explanation": analysis["explanation"],
                            "recommendation": analysis["recommendation"]
                        })
                    ai_analysis = generate_full_report(lab_data, message)
                    self._send_json({
                        "success": True,
                        "is_lab_analysis": True,
                        "parsed_count": len(lab_data),
                        "structured_results": structured_results,
                        "ai_analysis": ai_analysis,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    return
            
            # Otherwise, get chat response (with disease detection)
            response = get_chat_response(message)
            if response is None:
                # Fallback if response not generated (shouldn't happen)
                response = "I'm your AI Health Assistant! Please describe your symptoms or ask a specific health question."
            
            self._send_json({
                "success": True,
                "response": response,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        
        else:
            self.send_response(404)
            self.end_headers()

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        pass


if __name__ == '__main__':
    print("=" * 60)
    print("🏥 AI Health Assistant - ENHANCED VERSION")
    print("University of Engineering and Technology, Taxila")
    print("=" * 60)
    print("✅ NO pip install required!")
    print("✅ NO external dependencies!")
    print("✅ NEW: Symptom-based disease detection!")
    print("✅ Works with Python standard library only!")
    print("=" * 60)
    print(f"🌐 Open browser: http://127.0.0.1:{PORT}")
    print("=" * 60)
    print("🔍 Try these examples in chat:")
    print("   - 'I have fever, cough, and body aches'")
    print("   - 'Feeling very thirsty and urinating frequently'")
    print("   - 'Painful urination and lower belly pain'")
    print("=" * 60)
    print("Press CTRL+C to stop the server")
    print("=" * 60)
    with socketserver.TCPServer(("", PORT), HealthHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped. Stay healthy!")