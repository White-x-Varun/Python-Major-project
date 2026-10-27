"""A small offline keyword-based health education helper."""


def answer(question):
    text = question.lower()
    if "confidence" in text or "match score" in text:
        return "The match score compares selected symptoms with made-up examples. It is not the chance that you have a condition."
    if "blood pressure" in text or "hypertension" in text:
        return "Blood pressure measures blood pushing against artery walls. A health professional can interpret readings in context."
    if "heart rate" in text or "pulse" in text:
        return "Pulse can change with activity, stress, fever, medicines, and other factors. This simulator cannot tell you why."
    if "spo2" in text or "oxygen" in text:
        return "SpO2 is an estimate of blood oxygen saturation. A single home reading should not be interpreted by this simulator."
    if "risk" in text or "score" in text:
        return "The educational risk score combines selected severity, duration, and out-of-range vital values. It is not validated."
    if "diagnos" in text or "do i have" in text:
        return "I cannot diagnose symptoms. For personal health concerns, speak with a qualified healthcare professional."
    if "emergency" in text or "chest pain" in text or "cannot breathe" in text:
        return "If this may be a medical emergency, contact your local emergency number or seek urgent medical care now."
    return "I can explain match scores, blood pressure, heart rate, oxygen readings, and the educational risk score."

