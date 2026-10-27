"""Rule-based symptom pattern matching and transparent teaching risk score."""

from .catalog import FOLLOW_UPS, PATTERNS, VITALS


def rank_patterns(symptoms):
    """Return up to three example patterns ranked by symptom overlap."""
    selected = set(symptoms)
    if not selected:
        return []
    results = []
    for name, example_symptoms in PATTERNS.items():
        overlap = len(selected & example_symptoms)
        score = overlap / len(example_symptoms)
        if overlap:
            results.append({"name": name, "score": round(score, 3)})
    results.sort(key=lambda result: result["score"], reverse=True)
    return results[:3]


def check_vitals(vitals):
    """Classify entered values against broad adult reference ranges."""
    results = []
    for key, value in vitals.items():
        reference = VITALS[key]
        if value < reference["low"]:
            status = "Below reference range"
        elif value > reference["high"]:
            status = "Above reference range"
        else:
            status = "Within reference range"
        results.append({
            "key": key,
            "label": reference["label"],
            "value": value,
            "unit": reference["unit"],
            "status": status,
        })
    return results


def check_emergencies(symptoms, vitals):
    """Find a few demo red-flag combinations from entered data."""
    symptoms = set(symptoms)
    alerts = []
    if vitals.get("spo2_percent", 100) < 90 and symptoms & {"chest pain", "shortness of breath"}:
        alerts.append("Very low oxygen with chest or breathing symptoms was entered.")
    if vitals.get("temperature_c", 0) >= 39.5 and "confusion" in symptoms:
        alerts.append("High fever with confusion was entered.")
    if {"chest pain", "shortness of breath"} <= symptoms:
        alerts.append("Chest pain together with shortness of breath was selected.")
    if vitals.get("systolic_bp", 100) < 90 and symptoms & {"fainting", "severe dizziness"}:
        alerts.append("Low blood pressure with fainting or severe dizziness was entered.")
    return alerts


def assess(symptoms, severity, duration_days, vitals):
    """Combine example patterns, vital checks, alerts, and a simple score."""
    vital_results = check_vitals(vitals)
    abnormal_count = sum(item["status"] != "Within reference range" for item in vital_results)
    alerts = check_emergencies(symptoms, vitals)
    score = 0.0
    if symptoms:
        score += severity * 0.3
    score += min(1.0, max(0, duration_days - 1) * 0.08)
    score += min(4.0, abnormal_count * 0.8)
    if alerts:
        score += 2.0
    score = round(min(score, 10.0), 1)
    if alerts or score >= 6.5:
        level = "High"
    elif score >= 3.5:
        level = "Moderate"
    else:
        level = "Low"
    return {
        "patterns": rank_patterns(symptoms),
        "vitals": vital_results,
        "abnormal_vitals": [item for item in vital_results if item["status"] != "Within reference range"],
        "risk_score": score,
        "risk_level": level,
        "emergency_alerts": alerts,
        "risk_note": "This simple teaching score is not medically validated.",
    }


def follow_up_questions(symptoms):
    """Suggest up to four questions based on selected symptoms."""
    questions = []
    for symptom in symptoms:
        questions.extend(FOLLOW_UPS.get(symptom, []))
    if not questions and symptoms:
        questions = ["When did the symptom begin?", "Has it changed or become worse?"]
    return questions[:4]

