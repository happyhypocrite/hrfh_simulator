import random
import numpy as np

def _responding_treatment_type(pain_score, pain_history=None, das_score=None):
    """
    Determine which treatment to apply based on pain patterns
    
    Args:
        pain_score: Current pain level (1-10)
        pain_history: Dictionary of past pain scores by day # should give 'previous_pain' for integration
        das_score: Disease Activity Score
        
    Returns:
        str: Treatment type to apply, or None if no new treatment needed
    """
    # Define treatment thresholds
    if pain_history is None:
        return None
    
    recent_days = sorted(pain_history.keys())[-7:] if len(pain_history) >= 7 else sorted(pain_history.keys())
    recent_pain = [pain_history[day] for day in recent_days]
    
    # Calculate metrics to determine treatment
    avg_pain = sum(recent_pain) / len(recent_pain)
    max_pain = max(recent_pain)
    
    # Treatment decision logic
    if max_pain >= 8.5:  # Acute severe flare
        return "emergency_steroid"
    elif max_pain >= 7.0:  # Significant pain
        return "nsaid" 
    elif avg_pain >= 6.0 and len(recent_pain) >= 5:  # Persistent moderate pain
        if das_score and das_score >= 5.1:  # High disease activity
            return "biologic"
        else:
            return "dmard"
    elif 4.0 <= avg_pain < 6.0 and len(recent_pain) >= 7:  # Chronic mild pain
        return "physical_therapy"
    else:
        return None

def _treatment_effect(treatment_type, days_on_treatment=0):
    """
    Calculate the effect of a treatment based on type and duration
    
    Args:
        treatment_type: Type of treatment being used
        days_on_treatment: How many days patient has been on this treatment
        
    Returns:
        float: Pain reduction effect (negative value to reduce pain)
    """
    # Treatment dictionary with effect profiles
    # Format: (max_effect, onset_days, duration_days, variability)
    treatment_dict = {
        # Immediate relief treatments
        "emergency_steroid": (-4.0, 1, 7, 0.1),    # Strong, quick, short duration
        "nsaid":            (-1.5, 1, 14, 0.3),    # Moderate, quick onset
        
        # Delayed effect treatments
        "dmard":            (-2.0, 14, 90, 0.2),   # Stronger but takes 2 weeks
        "biologic":         (-3.0, 28, 180, 0.3),  # Strongest but takes 4 weeks
        "physical_therapy": (-1.0, 7, 28, 0.4)     # Mild effect, moderate onset
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