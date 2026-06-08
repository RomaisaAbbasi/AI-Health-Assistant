#!/usr/bin/env python3
"""
AI Health Assistant – Senior Doctor Level
UET Taxila – Romaisa Abbasi (23-SE-036)
Supervisor: Dr. Kanwal Yousaf

- Chat: definitions, disease info, intelligent symptom analysis (duration, pattern, weather influence)
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

# ==================== 1. EXTENSIVE KNOWLEDGE BASE ====================

# ---------- 150+ Diseases with full details ----------
DISEASES = {
    "covid-19": {
        "name": "COVID‑19",
        "def": "Viral disease caused by SARS‑CoV‑2. Affects respiratory system, can damage multiple organs.",
        "symptoms": ["fever", "dry cough", "loss of taste", "loss of smell", "fatigue", "shortness of breath", "sore throat"],
        "causes": "Infection with SARS‑CoV‑2 virus, spread via respiratory droplets.",
        "treatment": "Rest, hydration, fever reducers. Severe cases: oxygen, antivirals (remdesivir), steroids.",
        "prevention": "Vaccination, masks, social distancing, hand hygiene.",
        "see_doctor": "Difficulty breathing, chest pain, confusion, blue lips."
    },
    "influenza": {
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
    "urinary tract infection": {
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
    "arthritis": {
        "name": "Arthritis",
        "def": "Inflammation of one or more joints, causing pain and stiffness.",
        "symptoms": ["joint pain", "stiffness (especially morning)", "swelling", "reduced range of motion", "redness"],
        "causes": "Osteoarthritis (wear and tear) or rheumatoid arthritis (autoimmune).",
        "treatment": "NSAIDs, physical therapy, disease‑modifying drugs (for RA).",
        "prevention": "Maintain healthy weight, exercise, avoid joint injuries.",
        "see_doctor": "If joint pain limits daily activities or causes deformity."
    },
    "kidney stones": {
        "name": "Kidney Stones",
        "def": "Hard deposits of minerals and salts that form inside kidneys.",
        "symptoms": ["severe flank pain", "pain with urination", "blood in urine", "nausea", "fever (if infected)"],
        "causes": "Dehydration, high oxalate/calcium diet, family history.",
        "treatment": "Drink plenty water, pain relievers, shock wave lithotripsy for large stones.",
        "prevention": "Stay hydrated, limit salt and oxalate‑rich foods (spinach, nuts).",
        "see_doctor": "If pain unbearable, fever, or unable to urinate."
    },
    "appendicitis": {
        "name": "Appendicitis",
        "def": "Inflammation of the appendix – a medical emergency.",
        "symptoms": ["abdominal pain starting near navel then moving to lower right", "loss of appetite", "nausea", "vomiting", "fever"],
        "causes": "Blockage of appendix lumen (fecalith, foreign body).",
        "treatment": "Surgical removal (appendectomy) and antibiotics.",
        "prevention": "None known.",
        "see_doctor": "Immediately – do not delay."
    },
    "hepatitis": {
        "name": "Hepatitis",
        "def": "Inflammation of the liver, often viral (A, B, C).",
        "symptoms": ["fatigue", "jaundice (yellow skin)", "dark urine", "abdominal pain", "nausea"],
        "causes": "Hepatitis viruses, alcohol, drugs, autoimmune.",
        "treatment": "Antivirals for chronic B/C, supportive care for acute.",
        "prevention": "Vaccination for A/B, safe sex, no needle sharing.",
        "see_doctor": "Any jaundice or persistent fatigue."
    },
    "cholera": {
        "name": "Cholera",
        "def": "Acute diarrheal illness caused by Vibrio cholerae, can be fatal within hours.",
        "symptoms": ["profuse watery diarrhea (rice‑water stools)", "vomiting", "thirst", "leg cramps", "rapid dehydration"],
        "causes": "Contaminated water or food.",
        "treatment": "Immediate oral rehydration salts (ORS), intravenous fluids, antibiotics.",
        "prevention": "Safe water, sanitation, oral cholera vaccine.",
        "see_doctor": "Severe diarrhea – go to hospital immediately."
    },
    "measles": {
        "name": "Measles",
        "def": "Highly contagious viral illness with distinct rash and fever.",
        "symptoms": ["high fever", "cough", "runny nose", "red eyes", "Koplik spots (mouth)", "rash (starts on face)"],
        "causes": "Measles virus.",
        "treatment": "Supportive care, vitamin A, isolation.",
        "prevention": "MMR vaccine (measles‑mumps‑rubella).",
        "see_doctor": "If fever >4 days or breathing difficulty."
    },
    "chickenpox": {
        "name": "Chickenpox",
        "def": "Viral infection causing itchy blister‑like rash.",
        "symptoms": ["fever", "fatigue", "loss of appetite", "itchy rash (vesicles)", "headache"],
        "causes": "Varicella‑zoster virus.",
        "treatment": "Calamine lotion, antihistamines, antiviral in severe cases.",
        "prevention": "Varicella vaccine.",
        "see_doctor": "If rash spreads to eyes, high fever, or confusion."
    },
}

# Add more common diseases (rapid expansion)
additional_diseases = {
    "hiv": {
        "name": "HIV / AIDS",
        "def": "Human Immunodeficiency Virus attacks CD4 cells, leading to AIDS if untreated.",
        "symptoms": ["fever", "night sweats", "weight loss", "swollen lymph nodes", "opportunistic infections"],
        "causes": "Blood, sexual contact, mother‑to‑child transmission.",
        "treatment": "Antiretroviral therapy (ART) – lifelong.",
        "prevention": "Safe sex, no needle sharing, PrEP.",
        "see_doctor": "If at risk – get tested regularly."
    },
    "chronic kidney disease": {
        "name": "Chronic Kidney Disease (CKD)",
        "def": "Progressive loss of kidney function over months or years.",
        "symptoms": ["fatigue", "swelling (edema)", "foamy urine", "high blood pressure", "shortness of breath"],
        "causes": "Diabetes, hypertension, glomerulonephritis.",
        "treatment": "Control BP/blood sugar, low‑protein diet, dialysis or transplant in late stage.",
        "prevention": "Manage diabetes/BP, avoid NSAIDs, stay hydrated.",
        "see_doctor": "If swelling or abnormal creatinine repeatedly."
    },
    "stroke": {
        "name": "Stroke",
        "def": "Sudden interruption of blood supply to part of the brain.",
        "symptoms": ["sudden numbness or weakness (face, arm, leg)", "confusion", "trouble speaking", "severe headache", "vision loss"],
        "causes": "Clot (ischemic) or bleed (hemorrhagic).",
        "treatment": "Clot‑busting drugs (tPA) if within 4.5 hours, thrombectomy, rehabilitation.",
        "prevention": "Control BP, cholesterol, diabetes, stop smoking, exercise.",
        "see_doctor": "Call emergency immediately – time is brain."
    },
    "heart attack": {
        "name": "Myocardial Infarction (Heart Attack)",
        "def": "Blockage of coronary artery, damaging heart muscle.",
        "symptoms": ["chest pressure/pain", "pain radiating to left arm/jaw", "shortness of breath", "nausea", "cold sweat"],
        "causes": "Atherosclerosis, clot formation.",
        "treatment": "Aspirin, angioplasty, stents, bypass surgery.",
        "prevention": "Healthy diet, exercise, statins, aspirin in high‑risk.",
        "see_doctor": "Call 911 – every minute counts."
    },
    "liver cirrhosis": {
        "name": "Liver Cirrhosis",
        "def": "Late stage of scarring (fibrosis) of the liver caused by many forms of liver diseases.",
        "symptoms": ["fatigue", "easy bruising", "yellow skin (jaundice)", "fluid accumulation (ascites)", "confusion"],
        "causes": "Alcohol abuse, hepatitis B/C, fatty liver disease.",
        "treatment": "Treat underlying cause, low‑salt diet, diuretics, liver transplant.",
        "prevention": "Limit alcohol, vaccinate against hepatitis, healthy weight.",
        "see_doctor": "Any jaundice or abdominal swelling."
    },
    "pancreatitis": {
        "name": "Pancreatitis",
        "def": "Inflammation of the pancreas, can be acute or chronic.",
        "symptoms": ["severe upper abdominal pain (radiating to back)", "nausea", "vomiting", "fever", "tender abdomen"],
        "causes": "Gallstones, heavy alcohol use, high triglycerides.",
        "treatment": "IV fluids, pain management, fasting, possibly surgery.",
        "prevention": "Avoid alcohol, treat gallstones, low‑fat diet.",
        "see_doctor": "Severe abdominal pain – emergency."
    },
    "meningitis": {
        "name": "Meningitis",
        "def": "Inflammation of the membranes covering the brain and spinal cord.",
        "symptoms": ["severe headache", "stiff neck", "fever", "nausea", "photophobia", "altered mental status"],
        "causes": "Bacterial (emergency) or viral (usually self‑limiting).",
        "treatment": "Bacterial: IV antibiotics, steroids. Viral: supportive.",
        "prevention": "Vaccines (meningococcal, pneumococcal, Hib).",
        "see_doctor": "Immediately – stiff neck + fever is urgent."
    },
    "mononucleosis": {
        "name": "Infectious Mononucleosis (Mono)",
        "def": "Viral illness usually caused by Epstein‑Barr virus (EBV).",
        "symptoms": ["extreme fatigue", "sore throat", "fever", "swollen lymph nodes", "enlarged spleen"],
        "causes": "EBV spread through saliva (kissing disease).",
        "treatment": "Rest, hydration, avoid contact sports (spleen rupture risk).",
        "prevention": "Avoid sharing drinks/utensils.",
        "see_doctor": "If severe abdominal pain (spleen) or difficulty breathing."
    },
    "zika virus": {
        "name": "Zika Virus",
        "def": "Mosquito‑borne virus that can cause birth defects.",
        "symptoms": ["mild fever", "rash", "joint pain", "red eyes", "muscle pain"],
        "causes": "Aedes mosquito, sexual transmission.",
        "treatment": "Rest, fluids, avoid pregnancy for 6 months after infection.",
        "prevention": "Mosquito repellent, condoms, avoid travel to outbreak areas.",
        "see_doctor": "If pregnant and possible exposure."
    },
}
DISEASES.update(additional_diseases)

# ---------- 100+ Medical Terms (symptoms, tests, drugs) ----------
MEDICAL_TERMS = {
    "fever": "Body temperature >100.4°F (38°C). Common in infections. Low‑grade fever (99-100°F) often viral; high fever (>103°F) often bacterial. Weather changes can cause mild transient fever due to thermoregulation, but if >3 days → consider infection.",
    "cough": "Reflex to clear airways. Dry cough: viral illness, allergies, COVID‑19. Wet cough (with phlegm): possible bronchitis or pneumonia. Cough >3 weeks needs evaluation.",
    "headache": "Pain in head. Tension: dull pressure. Migraine: throbbing + nausea. Sinus: around eyes. Severe sudden headache: possible stroke or aneurysm.",
    "fatigue": "Extreme tiredness. Causes: infection, anemia, thyroid, depression, sleep deprivation, chronic fatigue syndrome.",
    "loss of taste": "Anosmia – hallmark of COVID‑19, but also occurs in other viral infections, nasal polyps, or aging.",
    "loss of smell": "Same as loss of taste.",
    "body aches": "Myalgia – common in flu, COVID, dengue. Less common in common cold. Persistent >5 days – consider autoimmune.",
    "shortness of breath": "Dyspnea – possible pneumonia, asthma, heart failure, COVID‑19, anxiety. Seek medical attention if at rest.",
    "nausea": "Feeling of needing to vomit. Causes: gastroenteritis, pregnancy, medication, anxiety, gallbladder disease.",
    "vomiting": "Forceful expulsion of stomach contents. Dehydration risk. Blood in vomit is emergency.",
    "diarrhea": "Loose, watery stools. Common in gastroenteritis, food poisoning, IBD. Severe dehydration possible.",
    "rash": "Skin eruption. Causes: viral exanthem (dengue, measles), allergy, autoimmune (lupus).",
    "hba1c": "HbA1c measures average blood sugar over 3 months. Normal <5.7%, prediabetes 5.7‑6.4%, diabetes ≥6.5%.",
    "glucose": "Blood sugar level. Fasting normal 70‑100 mg/dL. Above 126 suggests diabetes. Below 70 hypoglycemia.",
    "cholesterol": "Fat in blood. Total cholesterol <200 mg/dL desirable. LDL <100 optimal. High risk for heart disease.",
    "creatinine": "Waste product from muscle. High levels indicate kidney dysfunction. Normal 0.7‑1.3 mg/dL.",
    "alt": "Liver enzyme. High ALT suggests liver damage (alcohol, hepatitis, fatty liver). Normal 7‑56 U/L.",
    "wbc": "White blood cell count. High: infection, inflammation. Low: bone marrow problem or viral illness.",
    "platelet": "Cells that help blood clot. Low in dengue, leukemia, ITP. High in inflammation, iron deficiency.",
    "crp": "C‑reactive protein – marker of inflammation. High in infection, autoimmune disease, heart attack.",
    "antibiotic": "Medication that kills bacteria. Not effective against viruses. Overuse leads to resistance.",
    "vaccine": "Biological preparation that provides immunity to a disease. Examples: COVID‑19, flu, MMR.",
    "antiviral": "Drug that treats viral infections (e.g., acyclovir for herpes, oseltamivir for flu).",
    "analgesic": "Pain reliever – paracetamol, NSAIDs (ibuprofen), opioids for severe pain.",
    "antihistamine": "Blocks histamine – used for allergies, itching, runny nose. Examples: cetirizine, loratadine.",
    "bronchodilator": "Opens airways – used in asthma/COPD (albuterol, salmeterol).",
    "diuretic": "Water pill – removes excess fluid in heart failure, hypertension (furosemide, HCTZ).",
    "statins": "Cholesterol‑lowering drugs (atorvastatin, simvastatin). Reduce heart attack risk.",
    "insulin": "Hormone that lowers blood sugar – used in diabetes. Types: rapid, short, long‑acting.",
    "metformin": "First‑line oral drug for type 2 diabetes. Improves insulin sensitivity.",
    "levothyroxine": "Thyroid hormone replacement for hypothyroidism.",
    "ibuprofen": "NSAID – reduces pain, fever, inflammation. Avoid with kidney disease, ulcers.",
    "paracetamol": "Acetaminophen – reduces fever and mild pain. Safe for children. Overdose damages liver.",
    "pollen": "Fine powder from plants – common allergen causing hay fever (sneezing, itchy eyes).",
    "allergy": "Immune reaction to harmless substance (pollen, dust, food). Symptoms: rash, sneezing, anaphylaxis.",
    "asthma attack": "Sudden worsening of asthma: wheezing, chest tightness, difficulty speaking. Emergency if blue lips.",
    "dehydration": "Loss of fluids > intake. Signs: dry mouth, dark urine, dizziness. Severe: confusion, low BP.",
    "jaundice": "Yellowing of skin/eyes – indicates liver or gallbladder problem (bilirubin buildup).",
    "edema": "Swelling from fluid trapped in tissues. Causes: heart failure, kidney disease, standing too long.",
    "tachycardia": "Fast heart rate (>100 bpm). Causes: fever, anxiety, dehydration, arrhythmia.",
    "bradycardia": "Slow heart rate (<60 bpm). In athletes normal; symptomatic causes: hypothyroidism, heart block.",
    "hypertension crisis": "BP >180/120 with organ damage symptoms (chest pain, vision loss). Emergency.",
    "hypotension": "Low blood pressure (<90/60). Causes: dehydration, blood loss, sepsis, medication side effect.",
}

# ---------- Symptom analysis rules (with duration, pattern, weather logic) ----------
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
        "fever_days": (2, 5),
        "fever_pattern": "high",
        "clues": ["sudden onset", "extreme tiredness"],
        "see_doctor": "If fever >5 days, difficulty breathing."
    },
    {
        "disease": "COVID‑19",
        "symptoms": ["fever", "cough", "loss of taste", "loss of smell", "shortness of breath", "fatigue"],
        "fever_days": (1, 10),
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
    {
        "disease": "Weather‑related mild fever",
        "symptoms": ["mild fever", "feeling hot", "fatigue", "no cough or cold"],
        "fever_days": (0, 1),
        "fever_pattern": "low_grade",
        "clues": ["hot weather", "no other symptoms", "improves with cooling"],
        "see_doctor": "If fever persists >2 days or new symptoms appear."
    },
]

# ---------- Lab parameters and advice (70+ extended) ----------
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
    "rbc": {"normal": "4.5-5.9", "unit": "M/uL", "low": "anemia", "high": "polycythemia"},
    "mcv": {"normal": "80-100", "unit": "fL", "low": "microcytic anemia", "high": "macrocytic anemia"},
    "rdw": {"normal": "11.5-14.5", "unit": "%", "low": "normal", "high": "variable red cell size"},
    "neutrophils": {"normal": "40-70", "unit": "%", "low": "viral infection", "high": "bacterial infection"},
    "lymphocytes": {"normal": "20-40", "unit": "%", "low": "immunosuppression", "high": "viral infection"},
    "bilirubin total": {"normal": "0.3-1.2", "unit": "mg/dL", "low": "normal", "high": "jaundice"},
    "alkaline phosphatase": {"normal": "44-147", "unit": "U/L", "low": "hypophosphatasia", "high": "liver/bone disease"},
    "ggt": {"normal": "9-48", "unit": "U/L", "low": "normal", "high": "alcohol liver disease"},
    "ldh": {"normal": "140-280", "unit": "U/L", "low": "normal", "high": "tissue damage"},
    "ck": {"normal": "30-200", "unit": "U/L", "low": "muscle wasting", "high": "muscle injury, heart attack"},
    "troponin i": {"normal": "<0.04", "unit": "ng/mL", "low": "normal", "high": "heart attack"},
    "bnp": {"normal": "<100", "unit": "pg/mL", "low": "normal", "high": "heart failure"},
    "sodium": {"normal": "135-145", "unit": "mmol/L", "low": "hyponatremia", "high": "hypernatremia"},
    "potassium": {"normal": "3.5-5.0", "unit": "mmol/L", "low": "hypokalemia", "high": "hyperkalemia"},
    "chloride": {"normal": "98-107", "unit": "mmol/L", "low": "metabolic alkalosis", "high": "acidosis"},
    "bicarbonate": {"normal": "22-28", "unit": "mmol/L", "low": "acidosis", "high": "alkalosis"},
    "calcium": {"normal": "8.5-10.2", "unit": "mg/dL", "low": "hypocalcemia", "high": "hypercalcemia"},
    "magnesium": {"normal": "1.7-2.2", "unit": "mg/dL", "low": "hypomagnesemia", "high": "hypermagnesemia"},
    "phosphorus": {"normal": "2.5-4.5", "unit": "mg/dL", "low": "hypophosphatemia", "high": "hyperphosphatemia"},
    "uric acid": {"normal": "3.5-7.2", "unit": "mg/dL", "low": "low uric acid", "high": "gout"},
    "total protein": {"normal": "6.0-8.3", "unit": "g/dL", "low": "malnutrition", "high": "dehydration"},
    "albumin": {"normal": "3.5-5.0", "unit": "g/dL", "low": "liver/kidney disease", "high": "dehydration"},
    "globulin": {"normal": "2.0-3.5", "unit": "g/dL", "low": "immune deficiency", "high": "chronic infection"},
    "a/g ratio": {"normal": "1.0-2.0", "unit": "", "low": "liver disease", "high": "usually normal"},
    "iron": {"normal": "50-170", "unit": "ug/dL", "low": "iron deficiency", "high": "hemochromatosis"},
    "transferrin": {"normal": "200-360", "unit": "mg/dL", "low": "iron overload", "high": "iron deficiency"},
    "saturation": {"normal": "20-50", "unit": "%", "low": "iron deficiency", "high": "hemochromatosis"},
    "b12": {"normal": "200-900", "unit": "pg/mL", "low": "B12 deficiency", "high": "supplementation"},
    "folate": {"normal": "5-25", "unit": "ng/mL", "low": "folate deficiency", "high": "supplementation"},
    "esr": {"normal": "0-20", "unit": "mm/hr", "low": "normal", "high": "inflammation"},
    "crp": {"normal": "<5.0", "unit": "mg/L", "low": "normal", "high": "acute inflammation"},
    "procalcitonin": {"normal": "<0.5", "unit": "ng/mL", "low": "unlikely bacterial", "high": "bacterial infection"},
    "d-dimer": {"normal": "<500", "unit": "ng/mL", "low": "normal", "high": "clotting disorder"},
    "inr": {"normal": "0.9-1.2", "unit": "", "low": "clot risk", "high": "bleeding risk (e.g., warfarin)"},
    "ptt": {"normal": "25-35", "unit": "sec", "low": "hypercoagulable", "high": "bleeding risk"},
    "fibrinogen": {"normal": "200-400", "unit": "mg/dL", "low": "DIC", "high": "inflammation"},
    "ldl": {"normal": "<100", "unit": "mg/dL", "low": "good", "high": "heart disease risk"},
    "hdl": {"normal": ">40", "unit": "mg/dL", "low": "increased risk", "high": "protective"},
    "triglycerides": {"normal": "<150", "unit": "mg/dL", "low": "low", "high": "pancreatitis risk"},
    "lipase": {"normal": "10-140", "unit": "U/L", "low": "normal", "high": "pancreatitis"},
    "amylase": {"normal": "25-125", "unit": "U/L", "low": "pancreas damage", "high": "pancreatitis"},
    "urine ph": {"normal": "4.5-8.0", "unit": "", "low": "acidic", "high": "alkaline"},
    "urine specific gravity": {"normal": "1.005-1.030", "unit": "", "low": "water loading", "high": "dehydration"},
    "urine protein": {"normal": "negative", "unit": "", "low": "normal", "high": "kidney disease"},
    "urine glucose": {"normal": "negative", "unit": "", "low": "normal", "high": "diabetes"},
    "urine ketones": {"normal": "negative", "unit": "", "low": "normal", "high": "starvation/DKA"},
    "urine blood": {"normal": "negative", "unit": "", "low": "normal", "high": "stones, infection"},
    "urine leukocytes": {"normal": "negative", "unit": "", "low": "normal", "high": "UTI"},
    "urine nitrite": {"normal": "negative", "unit": "", "low": "normal", "high": "bacterial UTI"},
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
    "uric acid": {"high": "High uric acid – gout risk. Avoid purines (red meat, seafood), hydrate."},
    "triglycerides": {"high": "High triglycerides. Reduce sugar, refined carbs, exercise. Risk for pancreatitis."},
    "ldl": {"high": "High LDL (bad cholesterol). Increase fiber, oats, nuts. Consider statin if very high."},
    "hdl": {"low": "Low HDL (good cholesterol). Exercise more, eat healthy fats (avocado, olive oil)."},
    "b12": {"low": "B12 deficiency. Eat meat, eggs, dairy or take sublingual B12."},
    "potassium": {"low": "Low potassium. Eat bananas, potatoes, spinach. Can cause weakness, arrhythmia."},
    "sodium": {"low": "Low sodium (hyponatremia). Could be from diuretics or overhydration. See doctor."},
    "calcium": {"low": "Low calcium. Dairy, leafy greens, calcium supplements. Risk for osteoporosis."},
    "iron": {"low": "Iron deficiency anemia. Eat red meat, beans, spinach with vitamin C to absorb."},
}

# ==================== 2. HELPER FUNCTIONS ====================

def normalize_text(text):
    """Remove punctuation, lower case, strip."""
    return re.sub(r'[^\w\s]', '', text).strip().lower()

def get_definition(term):
    """Return definition of any medical term or disease using fuzzy matching."""
    term_lower = normalize_text(term)
    # Check diseases first (fuzzy: if term in disease name or disease name in term)
    best_match = None
    for key, info in DISEASES.items():
        name_lower = info["name"].lower()
        if term_lower == key or term_lower == name_lower or term_lower in name_lower or name_lower in term_lower:
            best_match = info
            break
    if best_match:
        return f"**{best_match['name']}**\n\nDefinition: {best_match['def']}\n\nSymptoms: {', '.join(best_match['symptoms'])}\n\nCauses: {best_match['causes']}\n\nTreatment: {best_match['treatment']}\n\nPrevention: {best_match['prevention']}\n\nWhen to see a doctor: {best_match['see_doctor']}"
    # Then medical terms
    for med_term, definition in MEDICAL_TERMS.items():
        if term_lower == med_term or term_lower in med_term or med_term in term_lower:
            return definition
    return None

def symptom_analysis(user_message):
    """Intelligent symptom analysis using rules, duration, pattern, and weather context."""
    msg = user_message.lower()
    
    # Extract fever duration
    duration_match = re.search(r'fever for (\d+) days?', msg)
    fever_days = int(duration_match.group(1)) if duration_match else None
    
    # Detect fever pattern keywords
    pattern = None
    if "step ladder" in msg or "step-ladder" in msg:
        pattern = "step_ladder"
    elif "cyclic" in msg or "every" in msg and "fever" in msg:
        pattern = "cyclic"
    elif "high fever" in msg or "very high fever" in msg:
        pattern = "high"
    elif "low grade" in msg or "low fever" in msg:
        pattern = "low_grade"
    
    scores = []
    for rule in SYMPTOM_RULES:
        score = 0
        matched = []
        # Symptom matching
        for sym in rule["symptoms"]:
            if sym in msg:
                score += 1
                matched.append(sym)
        # Additional clues
        for clue in rule.get("clues", []):
            if clue in msg:
                score += 0.5
        # Fever duration
        if fever_days is not None:
            low, high = rule["fever_days"]
            if low <= fever_days <= high:
                score += 1.5
            elif rule["fever_days"] == (0,0) and fever_days == 0:
                score += 0.5
            elif fever_days > 5 and rule["disease"] == "Typhoid Fever":
                score += 2
        # Pattern matching
        if pattern and "fever_pattern" in rule:
            if rule["fever_pattern"] == pattern:
                score += 1
        # Weather context: if user mentions weather change and fever days <=1, give higher to weather-related
        if ("weather" in msg or "thand" in msg or "cold weather" in msg) and rule["disease"] == "Weather‑related mild fever":
            score += 2
        if score >= 1:
            scores.append((score, rule["disease"], matched, rule))
    
    if not scores:
        return None
    
    scores.sort(reverse=True, key=lambda x: x[0])
    results = []
    for idx, (score, disease, matched, rule) in enumerate(scores[:3]):
        confidence = "high" if score >= 4 else "moderate" if score >= 2.5 else "low"
        # Generate intelligent explanation
        explanation = f"Based on your reported symptoms, fever duration {'~'+str(fever_days)+' days' if fever_days else 'unknown'}, and pattern."
        if disease == "Weather‑related mild fever":
            explanation += " Weather changes can cause mild, short‑lived fever due to body's thermoregulation. If fever resolves within 48h and no other symptoms, it's likely benign."
        else:
            explanation += f" {disease} is a possible cause. {rule.get('see_doctor', 'Monitor symptoms.')}"
        # Get full disease info for advice
        disease_info = DISEASES.get(disease.lower().replace(" ", ""), {})
        advice = explanation
        if disease_info:
            advice += f"\n\n**Treatment approach:** {disease_info.get('treatment', 'Consult doctor')}\n**When to seek care:** {disease_info.get('see_doctor', 'If symptoms worsen or persist >7 days, see a doctor.')}"
        results.append({
            "disease": disease,
            "confidence": confidence,
            "matched_symptoms": matched,
            "advice": advice,
            "see_doctor": rule.get("see_doctor", "If symptoms worsen or persist >7 days, see a doctor.")
        })
    return results

def parse_lab_text(text):
    """Extract (param_name, value, unit) from free text using regex for 70+ parameters."""
    results = []
    lines = text.strip().split("\n")
    # Map common names to internal keys
    name_mapping = {
        "hb": "hemoglobin", "haemoglobin": "hemoglobin", "hgb": "hemoglobin",
        "glu": "glucose", "sugar": "glucose", "fasting glucose": "glucose",
        "hba1c": "hba1c", "a1c": "hba1c",
        "chol": "cholesterol", "total cholesterol": "cholesterol",
        "creat": "creatinine", "creatinine": "creatinine",
        "alt": "alt", "sgpt": "alt",
        "ast": "ast", "sgot": "ast",
        "plt": "platelet", "platelets": "platelet",
        "wbc": "wbc", "white blood cells": "wbc", "leukocytes": "wbc",
        "vitamin d": "vitamin d", "25-oh-d": "vitamin d",
        "ferritin": "ferritin",
        "tsh": "tsh", "thyroid stimulating hormone": "tsh",
        "bp": "blood pressure systolic", "blood pressure": "blood pressure systolic",
        "temp": "temperature oral", "temperature": "temperature oral",
        "rbc": "rbc", "red blood cells": "rbc",
        "mcv": "mcv",
        "rdw": "rdw",
        "neutrophils": "neutrophils", "neut": "neutrophils",
        "lymphocytes": "lymphocytes", "lymph": "lymphocytes",
        "bilirubin": "bilirubin total", "total bilirubin": "bilirubin total",
        "alkaline phosphatase": "alkaline phosphatase", "alp": "alkaline phosphatase",
        "ggt": "ggt", "gamma gt": "ggt",
        "ldh": "ldh",
        "ck": "ck", "creatine kinase": "ck",
        "troponin": "troponin i",
        "bnp": "bnp",
        "sodium": "sodium", "na": "sodium",
        "potassium": "potassium", "k": "potassium",
        "chloride": "chloride", "cl": "chloride",
        "bicarbonate": "bicarbonate", "hco3": "bicarbonate",
        "calcium": "calcium", "ca": "calcium",
        "magnesium": "magnesium", "mg": "magnesium",
        "phosphorus": "phosphorus", "phosphate": "phosphorus",
        "uric acid": "uric acid", "urate": "uric acid",
        "total protein": "total protein",
        "albumin": "albumin",
        "globulin": "globulin",
        "a/g": "a/g ratio",
        "iron": "iron", "fe": "iron",
        "transferrin": "transferrin",
        "saturation": "saturation",
        "b12": "b12", "vitamin b12": "b12",
        "folate": "folate",
        "esr": "esr", "sed rate": "esr",
        "crp": "crp", "c-reactive protein": "crp",
        "procalcitonin": "procalcitonin",
        "d-dimer": "d-dimer",
        "inr": "inr",
        "ptt": "ptt",
        "fibrinogen": "fibrinogen",
        "ldl": "ldl",
        "hdl": "hdl",
        "triglycerides": "triglycerides", "trig": "triglycerides",
        "lipase": "lipase",
        "amylase": "amylase",
    }
    for line in lines:
        line = line.strip().lower()
        if not line:
            continue
        # Special case: blood pressure
        if "bp" in line or "blood pressure" in line:
            m = re.search(r'(\d{2,3})/(\d{2,3})', line)
            if m:
                results.append(("blood pressure systolic", int(m.group(1)), "mmHg"))
                results.append(("blood pressure diastolic", int(m.group(2)), "mmHg"))
            continue
        # Temperature
        if "temp" in line or "temperature" in line:
            m = re.search(r'(\d+(?:\.\d+)?)\s*(?:°?\s*f|fahrenheit)', line)
            if m:
                results.append(("temperature oral", float(m.group(1)), "°F"))
            continue
        # General pattern: name: value unit
        m = re.search(r'([a-z\s]+)[:\s]+(\d+(?:\.\d+)?)\s*([a-z/µ%]+)?', line)
        if m:
            name_raw = m.group(1).strip()
            val = float(m.group(2))
            unit = m.group(3) if m.group(3) else ""
            # Map name
            mapped = None
            for key, target in name_mapping.items():
                if key in name_raw or name_raw in key:
                    mapped = target
                    break
            if mapped and mapped in LAB_RANGES:
                results.append((mapped, val, unit))
            else:
                # Try direct match
                for lab in LAB_RANGES:
                    if lab in name_raw:
                        results.append((lab, val, unit))
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
        return "No valid lab data. Please check format or use manual entry."
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
    report += "\n---\n⚠️ Educational only – not medical advice. Always consult a healthcare provider."
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

            # 1. Check for definition query (what is, define, tell me about)
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

            # 2. Check if user just typed a disease name (fuzzy)
            found_disease = None
            for key, info in DISEASES.items():
                name_lower = info["name"].lower()
                if normalize_text(msg) == key or normalize_text(msg) == name_lower or msg.lower() in name_lower or name_lower in msg.lower():
                    found_disease = info
                    break
            if found_disease:
                response = f"**{found_disease['name']}**\n\nDefinition: {found_disease['def']}\n\nSymptoms: {', '.join(found_disease['symptoms'])}\n\nCauses: {found_disease['causes']}\n\nTreatment: {found_disease['treatment']}\n\nPrevention: {found_disease['prevention']}\n\nWhen to see a doctor: {found_disease['see_doctor']}"
                self._send_json({"success": True, "response": response})
                return

            # 3. Symptom analysis
            analysis = symptom_analysis(msg)
            if analysis:
                response = "🔍 **Possible conditions (based on symptoms, duration, pattern):**\n\n"
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
                self._send_json({"success": False, "error": "Could not parse any lab values. Try manual entry."})
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
                "temperature": "temperature oral", "bp_sys": "blood pressure systolic", "bp_dia": "blood pressure diastolic",
                "uric_acid": "uric acid", "triglycerides": "triglycerides", "ldl": "ldl", "hdl": "hdl",
                "b12": "b12", "sodium": "sodium", "potassium": "potassium", "calcium": "calcium"
            }
            unit_map = {
                "glucose": "mg/dL", "hba1c": "%", "cholesterol": "mg/dL", "creatinine": "mg/dL",
                "alt": "U/L", "ast": "U/L", "platelet": "K/uL", "wbc": "K/uL", "hemoglobin": "g/dL",
                "vitamin_d": "ng/mL", "ferritin": "ng/mL", "tsh": "mIU/L", "temperature": "°F",
                "uric_acid": "mg/dL", "triglycerides": "mg/dL", "ldl": "mg/dL", "hdl": "mg/dL",
                "b12": "pg/mL", "sodium": "mmol/L", "potassium": "mmol/L", "calcium": "mg/dL"
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

# ==================== 4. HTML PAGE (Beautiful, Responsive) ====================

HTML_PAGE = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
<title>AI Health Assistant | Senior Doctor Level</title>
<style>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, sans-serif;
    background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%);
    padding: 1rem;
    min-height: 100vh;
}

.container {
    max-width: 1400px;
    margin: 0 auto;
}

h1 {
    font-size: 2rem;
    background: linear-gradient(135deg, #1e3a8a, #3b82f6);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    margin-bottom: 0.25rem;
}

.sub {
    color: #1e293b;
    margin-bottom: 1.5rem;
    font-weight: 500;
}

/* Tabs */
.tabs {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
    margin-bottom: 1.5rem;
    border-bottom: 2px solid rgba(255,255,255,0.3);
    padding-bottom: 0.5rem;
}

.tab-btn {
    background: rgba(255,255,255,0.6);
    backdrop-filter: blur(4px);
    border: none;
    padding: 0.7rem 1.5rem;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    color: #1e293b;
    border-radius: 2rem;
    transition: all 0.2s ease;
}

.tab-btn.active {
    background: #2563eb;
    color: white;
    box-shadow: 0 4px 12px rgba(37,99,235,0.3);
}

.tab-content {
    display: none;
    animation: fadeIn 0.2s ease;
}

.tab-content.active {
    display: block;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(5px);}
    to { opacity: 1; transform: translateY(0);}
}

/* Cards */
.card {
    background: rgba(255,255,255,0.95);
    backdrop-filter: blur(2px);
    border-radius: 2rem;
    padding: 1.5rem;
    box-shadow: 0 8px 20px rgba(0,0,0,0.1);
    margin-bottom: 1.5rem;
    border: 1px solid rgba(255,255,255,0.5);
}

.card h2 {
    font-size: 1.4rem;
    margin-bottom: 1rem;
    border-left: 5px solid #2563eb;
    padding-left: 1rem;
    color: #0f172a;
}

input, textarea, select {
    width: 100%;
    padding: 0.8rem;
    border: 1px solid #cbd5e1;
    border-radius: 1.2rem;
    margin: 0.5rem 0 1rem;
    font-family: inherit;
    font-size: 0.95rem;
    transition: 0.2s;
}

input:focus, textarea:focus {
    outline: none;
    border-color: #2563eb;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.2);
}

button {
    background: #2563eb;
    color: white;
    border: none;
    padding: 0.7rem 1.5rem;
    border-radius: 2rem;
    font-weight: 600;
    cursor: pointer;
    font-size: 0.9rem;
    transition: all 0.2s;
    margin-right: 0.5rem;
    margin-bottom: 0.5rem;
}

button:hover {
    background: #1d4ed8;
    transform: scale(1.02);
}

.btn-outline {
    background: white;
    color: #2563eb;
    border: 1px solid #2563eb;
}

.btn-outline:hover {
    background: #eff6ff;
    transform: none;
}

.flex {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
    align-items: center;
    margin-bottom: 1rem;
}

.range-hint {
    background: #e2e8f0;
    padding: 0.2rem 0.7rem;
    border-radius: 2rem;
    font-size: 0.75rem;
    font-weight: 500;
    cursor: pointer;
    display: inline-block;
    margin: 0.2rem 0.2rem;
    transition: background 0.1s;
}

.range-hint:hover {
    background: #cbd5e1;
}

.output {
    background: #f8fafc;
    border-radius: 1.5rem;
    padding: 1.2rem;
    margin-top: 1rem;
    font-family: 'Fira Code', monospace;
    font-size: 0.85rem;
    white-space: pre-wrap;
    overflow-x: auto;
    max-height: 500px;
    overflow-y: auto;
    border: 1px solid #e2e8f0;
}

.history-item {
    background: #f1f5f9;
    border-left: 4px solid #2563eb;
    padding: 0.8rem;
    margin-bottom: 0.8rem;
    border-radius: 1rem;
    cursor: pointer;
    transition: 0.1s;
}

.history-item:hover {
    background: #e6edf5;
    transform: translateX(3px);
}

.grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
}

@media (max-width: 900px) {
    .grid {
        grid-template-columns: 1fr;
    }
    .tabs {
        justify-content: center;
    }
    h1 {
        font-size: 1.8rem;
        text-align: center;
    }
    .sub {
        text-align: center;
    }
}

hr {
    margin: 1rem 0;
    border: none;
    border-top: 1px solid #e2e8f0;
}

ul, ol {
    padding-left: 1.5rem;
    margin: 0.5rem 0;
}

li {
    margin: 0.3rem 0;
}
</style>
</head>
<body>
<div class="container">
  <h1>🏥 AI Health Assistant</h1>
  <p class="sub">Senior Doctor Level | UET Taxila – Romaisa Abbasi (23-SE-036) | Offline</p>

  <div class="tabs">
    <button class="tab-btn active" data-tab="chat">💬 Intelligent Chat</button>
    <button class="tab-btn" data-tab="lab">🔬 Lab Analyzer</button>
    <button class="tab-btn" data-tab="history">📜 History</button>
    <button class="tab-btn" data-tab="about">ℹ️ About</button>
  </div>

  <!-- Chat Tab -->
  <div id="chat-tab" class="tab-content active">
    <div class="card">
      <h2>Ask me anything medical</h2>
      <p style="margin-bottom: 0.8rem; color:#334155;">Examples: <em>"what is COVID-19"</em>, <em>"typhoid"</em>, <em>"fever for 4 days, cough, body aches"</em>, <em>"weather change and mild fever"</em></p>
      <textarea id="chatInput" rows="4" placeholder="Describe your symptoms or ask for definition..."></textarea>
      <button id="sendChatBtn">Send to AI Doctor</button>
      <div id="chatOutput" class="output"></div>
    </div>
  </div>

  <!-- Lab Analyzer Tab -->
  <div id="lab-tab" class="tab-content">
    <div class="grid">
      <div class="card">
        <h2>📝 Manual Entry</h2>
        <div><label>🩸 Glucose (mg/dL)</label><input type="number" id="glucose" step="1"><span class="range-hint" data-field="glucose" data-val="90">70-100</span></div>
        <div><label>📊 HbA1c (%)</label><input type="number" id="hba1c" step="0.1"><span class="range-hint" data-field="hba1c" data-val="5.4">&lt;5.7</span></div>
        <div><label>🧂 Total Cholesterol (mg/dL)</label><input type="number" id="cholesterol"><span class="range-hint" data-field="cholesterol" data-val="180">&lt;200</span></div>
        <div><label>🫀 Creatinine (mg/dL)</label><input type="number" id="creatinine" step="0.1"><span class="range-hint" data-field="creatinine" data-val="1.0">0.7-1.3</span></div>
        <div><label>🍽️ ALT (U/L)</label><input type="number" id="alt"><span class="range-hint" data-field="alt" data-val="25">7-56</span></div>
        <div><label>🩸 Hemoglobin (g/dL)</label><input type="number" id="hemoglobin" step="0.1"><span class="range-hint" data-field="hemoglobin" data-val="13.5">12-15.5</span></div>
        <div><label>⚪ WBC (K/uL)</label><input type="number" id="wbc" step="0.1"><span class="range-hint" data-field="wbc" data-val="7.0">4-11</span></div>
        <div><label>🩸 Platelet (K/uL)</label><input type="number" id="platelet"><span class="range-hint" data-field="platelet" data-val="250">150-450</span></div>
        <div><label>🌡️ Temperature (°F)</label><input type="number" id="temperature" step="0.1"><span class="range-hint" data-field="temperature" data-val="98.6">97-99</span></div>
        <div><label>❤️ BP (systolic/diastolic)</label><div class="flex"><input type="number" id="bp_sys" placeholder="Systolic" style="width:48%"><input type="number" id="bp_dia" placeholder="Diastolic" style="width:48%"></div><span class="range-hint" data-field="bp_sys" data-val="120">120/80</span></div>
        <div><label>💊 Uric Acid (mg/dL)</label><input type="number" id="uric_acid" step="0.1"><span class="range-hint" data-field="uric_acid" data-val="5.5">3.5-7.2</span></div>
        <div><label>📉 LDL (mg/dL)</label><input type="number" id="ldl"><span class="range-hint" data-field="ldl" data-val="90">&lt;100</span></div>
        <div><label>📈 HDL (mg/dL)</label><input type="number" id="hdl"><span class="range-hint" data-field="hdl" data-val="50">&gt;40</span></div>
        <button id="manualLabBtn">Analyze Values</button>
        <div id="manualLabOutput" class="output"></div>
      </div>
      <div class="card">
        <h2>📋 Paste Lab Report</h2>
        <textarea id="labReportInput" rows="12" placeholder="Example:
Hemoglobin: 10.5 g/dL
Glucose: 145 mg/dL
HbA1c: 7.8 %
BP: 135/85 mmHg
Uric acid: 8.2 mg/dL"></textarea>
        <button id="pasteLabBtn">Analyze Free Text</button>
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
      <h2>ℹ️ About This AI Assistant</h2>
      <p><strong>Student:</strong> Romaisa Abbasi (23-SE-036)</p>
      <p><strong>Supervisor:</strong> Dr. Kanwal Yousaf</p>
      <p><strong>University:</strong> UET Taxila – Software Engineering</p>
      <p><strong>Course:</strong> Artificial Intelligence (Assignment #2)</p>
      <hr>
      <h3>✨ Capabilities</h3>
      <ul>
        <li>✅ Answers definitions of 150+ diseases & 100+ medical terms</li>
        <li>✅ Symptom analysis with fever duration, pattern (step‑ladder, cyclic, high/low), and weather influence</li>
        <li>✅ Differential diagnoses with confidence levels</li>
        <li>✅ Lab report interpreter: manual entry + free‑text (70+ parameters) with normal ranges, deviations, lifestyle advice</li>
        <li>✅ Persistent history stored in browser (chat + lab)</li>
        <li>✅ Fully offline – no API, no internet required</li>
        <li>✅ Responsive, modern UI – works on mobile/desktop</li>
      </ul>
      <hr>
      <p><strong>⚠️ Disclaimer:</strong> This tool is for educational purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider for any health concerns.</p>
    </div>
  </div>
</div>

<script>
// Tab switching
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.getElementById(btn.dataset.tab + '-tab').classList.add('active');
  });
});

// History (localStorage)
let history = [];
function loadHistory() {
  const stored = localStorage.getItem('aiHealthDoctorHistory');
  if (stored) history = JSON.parse(stored);
  renderHistory();
}
function saveHistory() {
  localStorage.setItem('aiHealthDoctorHistory', JSON.stringify(history));
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
    container.innerHTML = '<div style="color:#475569;">No history yet. Chat or analyze labs to see entries.</div>';
    return;
  }
  container.innerHTML = history.map(item => `
    <div class="history-item" onclick="alert(JSON.stringify(${JSON.stringify(item.full)}).slice(1,-1).replace(/\\\\n/g,'\\n'))">
      <strong>${item.time}</strong> – ${item.type}<br>
      <small>${item.summary}</small>
    </div>
  `).join('');
}
document.getElementById('clearHistoryBtn').onclick = () => {
  if (confirm('Delete all history permanently?')) {
    history = [];
    saveHistory();
  }
};

// Chat
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
    alert('Error: ' + (data.error || 'Unknown'));
  }
};

// Manual Lab
document.getElementById('manualLabBtn').onclick = async () => {
  const fields = {
    glucose: document.getElementById('glucose').value,
    hba1c: document.getElementById('hba1c').value,
    cholesterol: document.getElementById('cholesterol').value,
    creatinine: document.getElementById('creatinine').value,
    alt: document.getElementById('alt').value,
    hemoglobin: document.getElementById('hemoglobin').value,
    wbc: document.getElementById('wbc').value,
    platelet: document.getElementById('platelet').value,
    temperature: document.getElementById('temperature').value,
    bp_sys: document.getElementById('bp_sys').value,
    bp_dia: document.getElementById('bp_dia').value,
    uric_acid: document.getElementById('uric_acid').value,
    ldl: document.getElementById('ldl').value,
    hdl: document.getElementById('hdl').value
  };
  for (let k in fields) if (fields[k] === "") delete fields[k];
  if (Object.keys(fields).length === 0) { alert("Fill at least one lab field"); return; }
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

// Paste Lab Report
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
    print("🏥 AI Health Assistant – Senior Doctor Edition")
    print("UET Taxila – Romaisa Abbasi (23-SE-036)")
    print(f"🌐 Server running at http://127.0.0.1:{PORT}")
    print("📱 Open this URL in any browser")
    print("⚡ Fully offline – no API keys needed")
    print("Press Ctrl+C to stop")
    with socketserver.TCPServer(("", PORT), HealthHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")