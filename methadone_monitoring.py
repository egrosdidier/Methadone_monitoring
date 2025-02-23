import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

def calculate_methadone_concentration(dose, weight, half_life, time_since_last_dose, steady_state=True):
    """
    Estime la concentration résiduelle de méthadone en fonction de la dose, du poids et du délai depuis la dernière prise.
    """
    volume_distribution = 4  # L/kg (valeur moyenne)
    clearance = (0.693 / half_life) * (volume_distribution * weight)
    
    if steady_state:
        # Ajustement pour un patient à l'équilibre plasmatique (prise chronique)
        accumulation_factor = 1 / (1 - np.exp(-0.693 * 24 / half_life))
        concentration = (dose * accumulation_factor / (volume_distribution * weight)) * np.exp(-0.693 * time_since_last_dose / half_life)
    else:
        # Concentration pour une seule prise
        concentration = (dose / (volume_distribution * weight)) * np.exp(-0.693 * time_since_last_dose / half_life)
    
    return max(concentration * 1000, 0)  # conversion en ng/mL et éviter valeurs négatives

def calculate_eddp_concentration(methadone_expected):
    """
    Estime la concentration attendue d'EDDP en fonction de la méthadonémie attendue.
    """
    expected_eddp = methadone_expected * 0.3  # Ratio moyen EDDP/Méthadone ajusté
    return expected_eddp

def confidence_interval(value, error_percentage=20):
    """
    Retourne une fourchette autour d'une valeur donnée avec un pourcentage d'erreur défini.
    """
    error_margin = value * (error_percentage / 100)
    return value - error_margin, value + error_margin

def evaluate_metabolism_probabilities(methadone_measured, eddp_measured):
    """
    Retourne les probabilités d'être métaboliseur normal, lent ou rapide selon le ratio méthadone/EDDP.
    """
    if eddp_measured == 0:
        return {"Métabolisation très lente": 1.0, "Métaboliseur lent": 0.0, "Métaboliseur normal": 0.0, "Métaboliseur rapide": 0.0}
    
    ratio = methadone_measured / eddp_measured
    
    # Définition des probabilités en fonction des seuils flous
    if ratio > 2.5:
        probabilities = {"Métaboliseur lent": 0.8, "Métaboliseur normal": 0.15, "Métaboliseur rapide": 0.05}
    elif 1.0 <= ratio <= 2.5:
        probabilities = {"Métaboliseur lent": 0.2, "Métaboliseur normal": 0.7, "Métaboliseur rapide": 0.1}
    else:
        probabilities = {"Métaboliseur lent": 0.05, "Métaboliseur normal": 0.2, "Métaboliseur rapide": 0.75}
    
    return probabilities

def assess_risk(methadone_measured, expected_methadone):
    """
    Évalue le risque de sous-dosage ou surdosage en comparant la méthadonémie mesurée à celle attendue.
    """
    lower_bound, upper_bound = confidence_interval(expected_methadone)
    if methadone_measured < lower_bound:
        return "Sous-dosage (risque de manque)"
    elif methadone_measured > upper_bound:
        return "Risque de surdosage (toxicité)"
    else:
        return "Dose dans la zone thérapeutique"

def plot_methadone_curves(dose, weight, half_life, time_since_last_dose, methadone_measured):
    """
    Trace les courbes pharmacocinétiques de la méthadone pour le patient et une courbe standard.
    """
    time = np.linspace(0, 48, 100)  # Temps en heures
    patient_concentrations = [calculate_methadone_concentration(dose, weight, half_life, t) for t in time]
    standard_concentrations = [calculate_methadone_concentration(dose, weight, 24, t) for t in time]  # Demi-vie standard de 24h
    expected_methadone = calculate_methadone_concentration(dose, weight, half_life, time_since_last_dose)
    
    fig, ax = plt.subplots()
    ax.plot(time, patient_concentrations, label="Courbe du patient", color='blue')
    ax.plot(time, standard_concentrations, label="Courbe standard (Demi-vie 24h)", linestyle='dashed', color='gray')
    ax.axhline(100, color='green', linestyle='--', label='Seuil bas (100 ng/mL)')
    ax.axhline(400, color='blue', linestyle='--', label='Zone thérapeutique (400 ng/mL)')
    ax.axhline(600, color='red', linestyle='--', label='Risque de toxicité (600 ng/mL)')
    ax.axvline(time_since_last_dose, color='purple', linestyle='--', label='Moment du prélèvement')
    ax.scatter([time_since_last_dose], [methadone_measured], color='red', label='Méthadonémie mesurée')
    ax.scatter([time_since_last_dose], [expected_methadone], color='orange', marker='o', label='Méthadonémie attendue')
    ax.set_xlabel("Temps depuis la dernière prise (h)")
    ax.set_ylabel("Concentration de méthadone (ng/mL)")
    ax.set_title("Courbes pharmacocinétiques : Patient vs Standard")
    ax.legend()
    st.pyplot(fig)

# Interface Streamlit
st.title("Évaluation de la Méthadonémie")

dose = st.number_input("Dose quotidienne de méthadone (mg)", min_value=1, max_value=300, value=60)
weight = st.number_input("Poids du patient (kg)", min_value=30, max_value=150, value=70)
half_life = st.slider("Demi-vie de la méthadone (h)", min_value=10, max_value=60, value=24)
time_since_last_dose = st.number_input("Temps depuis la dernière prise (h)", min_value=1, max_value=48, value=12)
methadone_measured = st.number_input("Méthadonémie mesurée (ng/mL)", min_value=0, max_value=2000, value=350)
eddp_measured = st.number_input("EDDP mesuré (ng/mL)", min_value=0, max_value=2000, value=120)

if st.button("Évaluer"):
    methadone_expected = calculate_methadone_concentration(dose, weight, half_life, time_since_last_dose, steady_state=True)
    eddp_expected = calculate_eddp_concentration(methadone_expected)
    methadone_range = confidence_interval(methadone_expected)
    eddp_range = confidence_interval(eddp_expected)
    metabolism_probabilities = evaluate_metabolism_probabilities(methadone_measured, eddp_measured)
    risk_evaluation = assess_risk(methadone_measured, methadone_expected)
    
    st.write(f"**Méthadonémie attendue (à l'équilibre)**: {methadone_range[0]:.2f} - {methadone_range[1]:.2f} ng/mL")
    st.write(f"**EDDP attendu**: {eddp_range[0]:.2f} - {eddp_range[1]:.2f} ng/mL")
    st.write("**Probabilités de métabolisation**:")
    for key, value in metabolism_probabilities.items():
        st.write(f"{key}: {value*100:.1f}%")
    st.write(f"**Évaluation du risque**: {risk_evaluation}")
    
    plot_methadone_curves(dose, weight, half_life, time_since_last_dose, methadone_measured)
