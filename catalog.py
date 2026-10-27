"""Small in-code catalog for symptom examples and vital references."""

SYMPTOM_GROUPS = {
    "Respiratory": ["cough", "mucus", "shortness of breath", "chest pain", "chest discomfort", "wheezing", "sore throat", "runny nose", "congestion", "sneezing"],
    "General": ["fever", "chills", "fatigue", "weakness", "muscle aches", "headache", "dizziness", "severe dizziness", "confusion", "fainting"],
    "Eyes and senses": ["itchy eyes", "watery eyes", "light sensitivity", "sound sensitivity"],
    "Digestive": ["nausea", "vomiting", "diarrhea", "stomach pain"],
    "Other": ["painful urination", "frequent urination", "lower abdominal pain"],
}

# Made-up teaching examples, not a medical training dataset.
PATTERNS = {
    "Common cold-like pattern": {"runny nose", "sore throat", "cough", "sneezing", "congestion"},
    "Flu-like pattern": {"fever", "chills", "muscle aches", "fatigue", "headache", "cough"},
    "Pneumonia-like pattern": {"fever", "cough", "shortness of breath", "chest pain", "fatigue"},
    "Bronchitis-like pattern": {"cough", "mucus", "chest discomfort", "wheezing", "fatigue"},
    "Allergy-like pattern": {"sneezing", "runny nose", "itchy eyes", "congestion"},
    "Migraine-like pattern": {"headache", "light sensitivity", "nausea", "dizziness"},
    "Stomach illness-like pattern": {"nausea", "vomiting", "diarrhea", "stomach pain", "fever"},
    "Urinary symptom pattern": {"painful urination", "frequent urination", "lower abdominal pain"},
}

VITALS = {
    "temperature_c": {"label": "Temperature", "unit": "C", "low": 36.0, "high": 37.5, "min": 30, "max": 45},
    "heart_rate_bpm": {"label": "Heart rate", "unit": "bpm", "low": 60, "high": 100, "min": 20, "max": 250},
    "systolic_bp": {"label": "Systolic blood pressure", "unit": "mmHg", "low": 90, "high": 120, "min": 40, "max": 300},
    "diastolic_bp": {"label": "Diastolic blood pressure", "unit": "mmHg", "low": 60, "high": 80, "min": 20, "max": 200},
    "spo2_percent": {"label": "Oxygen saturation", "unit": "%", "low": 95, "high": 100, "min": 50, "max": 100},
    "glucose_mg_dl": {"label": "Blood glucose", "unit": "mg/dL", "low": 70, "high": 140, "min": 20, "max": 700},
}

SAMPLE_PROFILES = {
    "Typical example": {"temperature_c": 36.8, "heart_rate_bpm": 76, "systolic_bp": 118, "diastolic_bp": 76, "spo2_percent": 98, "glucose_mg_dl": 95},
    "Fever example": {"temperature_c": 39.2, "heart_rate_bpm": 112, "systolic_bp": 108, "diastolic_bp": 70, "spo2_percent": 96, "glucose_mg_dl": 112},
    "Cardiovascular example": {"temperature_c": 36.9, "heart_rate_bpm": 118, "systolic_bp": 154, "diastolic_bp": 94, "spo2_percent": 94, "glucose_mg_dl": 120},
}

FOLLOW_UPS = {
    "cough": ["Is the cough dry or productive?", "When did the cough begin?"],
    "fever": ["When did you first feel feverish?", "Have you measured your temperature?"],
    "shortness of breath": ["Did the breathing change begin suddenly?", "Does it happen at rest or with activity?"],
    "chest pain": ["When did the chest pain begin?", "Is it severe or getting worse?"],
    "headache": ["When did the headache begin?", "Is light or sound unusually uncomfortable?"],
    "stomach pain": ["Where do you feel the stomach discomfort?", "When did it begin?"],
}

