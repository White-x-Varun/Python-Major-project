"""Plain-text report and CSV export helpers built with Python's standard library."""

import csv
from datetime import datetime


def format_report(session, display_name="User"):
    assessment = session["assessment"]
    lines = [
        "MEDICAL SYMPTOM SIMULATOR",
        "For educational simulation purposes only - not a clinical diagnostic device.",
        "",
        "Participant: " + display_name,
        "Created: " + session.get("created_at", datetime.now().isoformat(timespec="minutes")),
        "Symptoms: " + (", ".join(session["symptoms"]) or "None selected"),
        "Severity: " + str(session["severity"]) + "/10",
        "Duration: " + str(session["duration_days"]) + " day(s)",
        "",
        "Example symptom patterns (match scores, not probabilities):",
    ]
    if assessment["patterns"]:
        for item in assessment["patterns"]:
            lines.append("  " + item["name"] + ": " + str(round(item["score"] * 100)) + "%")
    else:
        lines.append("  No matching example pattern")
    lines.extend(["", "Vital values:"])
    if assessment["vitals"]:
        for item in assessment["vitals"]:
            lines.append("  " + item["label"] + ": " + str(item["value"]) + " " + item["unit"] + " - " + item["status"])
    else:
        lines.append("  None entered")
    lines.extend(["", "Teaching risk index: " + assessment["risk_level"] + " (" + str(assessment["risk_score"]) + "/10)"])
    lines.append(assessment["risk_note"])
    if assessment["emergency_alerts"]:
        lines.extend(["", "URGENT ALERT PATTERNS:"])
        for alert in assessment["emergency_alerts"]:
            lines.append("  " + alert)
        lines.append("If this may be an emergency, contact local emergency services now.")
    lines.extend(["", "This report cannot diagnose or rule out a health condition."])
    return "\n".join(lines)


def export_history_csv(sessions, path):
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Created", "Pattern", "Risk level", "Risk score", "Symptoms"])
        for session in sessions:
            patterns = session["assessment"].get("patterns", [])
            writer.writerow([
                session["created_at"],
                patterns[0]["name"] if patterns else "None",
                session["assessment"]["risk_level"],
                session["assessment"]["risk_score"],
                ", ".join(session["symptoms"]),
            ])
