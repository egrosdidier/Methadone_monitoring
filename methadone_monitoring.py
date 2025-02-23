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

def evaluate_metabolism_profile(methadone_measured, eddp_measured, time_since_last_dose):
    """
    Évalue le profil métabolique en fonction du temps écoulé depuis la dernière prise.
    """
    if 20 <= time_since_last_dose <= 24:
        if 100 <= methadone_measured <= 400 and 30 <= eddp_measured <= 300:
            return "Profil normal"
        elif methadone_measured < 100 and eddp_measured > 300:
            return "Métaboliseur rapide"
        elif methadone_measured > 600 and eddp_measured < 30:
            return "Métaboliseur lent"
    else:
        if methadone_measured > 400 and eddp_measured < 30:
            return "Métaboliseur lent"
        elif methadone_measured < 100 and eddp_measured > 300:
            return "Métaboliseur rapide"
        elif 100 <= methadone_measured <= 600 and 30 <= eddp_measured <= 300:
            return "Profil normal"
        elif methadone_measured > 600 and eddp_measured > 30:
            return "Possible accumulation (à surveiller)"
        elif methadone_measured < 100 and eddp_measured < 30:
            return "Mauvaise absorption ou problème hépatique"
    
    return "Interprétation non concluante"

def plot_methadone_curves(dose, weight, half_life, time_since_last_dose, methadone_measured):
    """
    Trace les courbes pharmacocinétiques de la méthadone pour le patient et une courbe standard.
    """
    time = np.linspace(0, 48, 100)
    patient_concentrations = [calculate_methadone_concentration(dose, weight, half_life, t) for t in time]
    standard_concentrations = [calculate_methadone_concentration(dose, weight, 24, t) for t in time]
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
    metabolism_profile = evaluate_metabolism_profile(methadone_measured, eddp_measured, time_since_last_dose)
    st.write(f"**Profil métabolique**: {metabolism_profile}")
    plot_methadone_curves(dose, weight, half_life, time_since_last_dose, methadone_measured)
