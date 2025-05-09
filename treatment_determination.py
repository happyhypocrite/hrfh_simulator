import random
import numpy as np

def _responding_treatment_type(pain_score, pain_history=None, das_score=None, dmard_use=None, seed=None):
    """
    Determine which treatment to apply based on pain patterns
    
    Args:
        pain_score: Current pain level (1-10)
        pain_history: Dictionary of past pain scores by day # should give 'previous_pain' for integration
        das_score: Disease Activity Score
        
    Returns:
        tuple: (treatment_type, updated_dmard_use) - Treatment type to apply and updated DMARD counter   
    """

    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    
    # Define treatment thresholds
    if pain_history is None:
        return None, dmard_use
    
    recent_days = sorted(pain_history.keys())[-7:] if len(pain_history) >= 7 else sorted(pain_history.keys())
    recent_pain = [pain_history[day] for day in recent_days]
    
    # Calculate metrics to determine treatment
    avg_pain = sum(recent_pain) / len(recent_pain)
    max_pain = max(recent_pain)
    
    # Treatment decision logic
    if max_pain >= 8:  # Acute severe flare
        return "emergency_steroid", dmard_use
    elif max_pain >= 7.0:  # Significant pain
        return "nsaid", dmard_use
    elif avg_pain >= 5.0 and len(recent_pain) >= 7:  # Persistent moderate pain
        if dmard_use >= 2:  # High disease activity
            return "biologic", dmard_use
        else:
            return "dmard", dmard_use
    elif 4.0 <= avg_pain < 6.0 and len(recent_pain) >= 7:  # Chronic mild pain
        return "physical_therapy", dmard_use
    else:
        return None, dmard_use

def _treatment_effect(treatment_type, days_on_treatment=0, seed = None):
    """
    Calculate the effect of a treatment based on type and duration
    
    Args:
        treatment_type: Type of treatment being used
        days_on_treatment: How many days patient has been on this treatment
        
    Returns:
        float: Pain reduction effect (negative value to reduce pain)
    """

    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    
    # Treatment dictionary with effect profiles
    # Format: (max_effect, onset_days, duration_days, variability)
    treatment_dict = {
        # Immediate relief treatments
        "emergency_steroid": (-0.5, 1, 21, 0.1),    # Strong, quick, short duration
        "nsaid":            (-0.2, 1, 7, 0.3),    # Moderate, quick onset
        
        # Delayed effect treatments
        "dmard":            (-0.03, 14, 1800, 0.2),   # Stronger but takes 2 weeks
        "biologic":         (-0.04, 28, 1800, 0.3),  # Strongest but takes 4 weeks
        "physical_therapy": (-0.0015, 7, 28, 0.4)    # Mild effect, moderate onset
    }
    
    if treatment_type not in treatment_dict:
        return 0.0
    
    max_effect, onset_days, duration_days, variability = treatment_dict[treatment_type]
    
    # No effect before onset days
    if days_on_treatment < onset_days:
        # Gradual onset effect (linear ramp up)
        effect_strength = days_on_treatment / onset_days
    else:
        # Full effect after onset period
        effect_strength = 1.0
    
    # Effect diminishes after treatment duration
    if days_on_treatment > duration_days:
        return 0.0
    
    # Add random variation in treatment response
    patient_response = np.random.normal(1.0, variability)
    effect_strength *= max(0.1, min(patient_response, 1.5))  # Limit variation
    effect = max_effect * effect_strength
    return effect, treatment_dict