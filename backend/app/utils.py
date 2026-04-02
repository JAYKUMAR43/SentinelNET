# Attack label mapping
attack_map = {
    0: "Normal",
    1: "DoS",
    2: "Probe",
    3: "R2L",
    4: "U2R"
}


def format_results(predictions, probabilities):
    results = []

    for pred, prob in zip(predictions, probabilities):
        results.append({
            "attack_type": attack_map.get(int(pred), "Unknown"),
            "confidence": float(max(prob))
        })

    return results