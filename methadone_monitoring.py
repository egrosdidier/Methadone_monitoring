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

def plot_methadone_curves(dose, weight, half_life, time_since_last_dose, methadone_measured):
    """
    Trace les courbes pharmacocinétiques de la méthadone pour le patient et une courbe attendue (modèle).
    """
    time = np.linspace(0, 48, 100)
    expected_concentrations = [calculate_methadone_concentration(dose, weight, half_life, t, steady_state=True) for t in time]
    patient_concentrations = [calculate_methadone_concentration(dose, weight, half_life, t, steady_state=False) for t in time]
    
    fig, ax = plt.subplots()
    ax.plot(time, expected_concentrations, label="Courbe attendue (modèle)", linestyle='dashed', color='gray')
    ax.plot(time, patient_concentrations, label="Courbe du patient (observée)", color='blue')
    ax.axhline(100, color='green', linestyle='--', label='Seuil bas (100 ng/mL)')
    ax.axhline(400, color='blue', linestyle='--', label='Zone thérapeutique (400 ng/mL)')
    ax.axhline(600, color='red', linestyle='--', label='Risque de toxicité (600 ng/mL)')
    ax.axvline(time_since_last_dose, color='purple', linestyle='--', label='Moment du prélèvement')
    ax.scatter([time_since_last_dose], [methadone_measured], color='red', label='Méthadonémie mesurée')
    ax.set_xlabel("Temps depuis la dernière prise (h)")
    ax.set_ylabel("Concentration de méthadone (ng/mL)")
    ax.set_title("Courbes pharmacocinétiques : Patient vs Modèle")
    ax.legend()
    st.pyplot(fig)
    
    return expected_concentrations[-1], calculate_eddp_concentration(expected_concentrations[-1])

# Interface Streamlit
st.title("Évaluation de la Méthadonémie")

dose = st.number_input("Dose quotidienne de méthadone (mg)", min_value=1, max_value=300, value=60)
weight = st.number_input("Poids du patient (kg)", min_value=30, max_value=150, value=70)
half_life = st.slider("Demi-vie de la méthadone (h)", min_value=10, max_value=60, value=24)
time_since_last_dose = st.number_input("Temps depuis la dernière prise (h)", min_value=1, max_value=48, value=12)
methadone_measured = st.number_input("Méthadonémie mesurée (ng/mL)", min_value=0, max_value=2000, value=350)
eddp_measured = st.number_input("EDDP mesuré (ng/mL)", min_value=0, max_value=2000, value=120)

if st.button("Évaluer"):
    expected_methadone, expected_eddp = plot_methadone_curves(dose, weight, half_life, time_since_last_dose, methadone_measured)
    st.write(f"**Méthadonémie attendue**: {expected_methadone:.2f} ng/mL")
    st.write(f"**EDDP attendu**: {expected_eddp:.2f} ng/mL")
    
    st.write("## Tableau de classification du métabolisme")
    st.write("| Situation clinique | Méthadone plasmatique | EDDP | Interprétation |")
    st.write("|-------------------|----------------------|------|----------------|")
    st.write("| **Réponse normale** | 100-400 ng/mL | 30-300 ng/mL | Métabolisation standard |")
    st.write("| **Métabolisation rapide** | < 100 ng/mL | > 300 ng/mL | Fort métabolisme hépatique → risque de manque en fin de journée → besoin de dose fractionnée |")
    st.write("| **Métabolisation lente** | > 400-600 ng/mL | < 30 ng/mL | Accumulation de méthadone → risque de sédation et QT long → réduire la dose |")
