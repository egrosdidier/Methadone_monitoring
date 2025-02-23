import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

def calculate_methadone_concentration(dose, weight, half_life, time_since_last_dose):
    """
    Estime la concentration résiduelle de méthadone en fonction de la dose, du poids et du délai depuis la dernière prise.
    """
    volume_distribution = 4  # L/kg (valeur moyenne)
    clearance = (0.693 / half_life) * (volume_distribution * weight)
    concentration = (dose / (volume_distribution * weight)) * np.exp(-0.693 * time_since_last_dose / half_life)
    return concentration * 1000  # conversion en ng/mL

def evaluate_metabolism(methadone_measured, eddp_measured):
    """
    Évalue le profil de métabolisation selon le ratio méthadone/EDDP.
    """
    if eddp_measured == 0:
        return "Métabolisation très lente"
    ratio = methadone_measured / eddp_measured
    if ratio > 2:
        return "Métaboliseur lent"
    elif ratio < 0.5:
        return "Métaboliseur rapide"
    else:
        return "Métaboliseur normal"

def assess_risk(methadone_measured):
    """
    Évalue le risque de sous-dosage ou surdosage.
    """
    if methadone_measured < 100:
        return "Sous-dosage (risque de manque)"
    elif methadone_measured > 600:
        return "Risque de surdosage (toxicité)"
    else:
        return "Dose dans la zone thérapeutique"

def plot_methadone_curve(dose, weight, half_life):
    """
    Trace la courbe pharmacocinétique de la méthadone avec les zones de risque.
    """
    time = np.linspace(0, 48, 100)  # Temps en heures
    concentrations = calculate_methadone_concentration(dose, weight, half_life, time)
    
    fig, ax = plt.subplots()
    ax.plot(time, concentrations, label="Concentration plasmatique")
    ax.axhline(100, color='green', linestyle='--', label='Seuil bas (100 ng/mL)')
    ax.axhline(400, color='blue', linestyle='--', label='Zone thérapeutique (400 ng/mL)')
    ax.axhline(600, color='red', linestyle='--', label='Risque de toxicité (600 ng/mL)')
    ax.set_xlabel("Temps depuis la dernière prise (h)")
    ax.set_ylabel("Concentration de méthadone (ng/mL)")
    ax.set_title("Courbe pharmacocinétique de la méthadone")
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
    methadone_expected = calculate_methadone_concentration(dose, weight, half_life, time_since_last_dose)
    metabolism_type = evaluate_metabolism(methadone_measured, eddp_measured)
    risk_evaluation = assess_risk(methadone_measured)
    
    st.write(f"**Méthadonémie attendue**: {methadone_expected:.2f} ng/mL")
    st.write(f"**Profil métabolique**: {metabolism_type}")
    st.write(f"**Évaluation du risque**: {risk_evaluation}")
    
    plot_methadone_curve(dose, weight, half_life)

