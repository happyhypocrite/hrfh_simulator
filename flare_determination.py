import random
import numpy as np

def _flare_chance(baseline_chance=0.05, disease_activity=None):
    """
    Calculate chance of flare based on baseline chance and disease activity
    
    Args:
        baseline_chance: Base probability of flare (0-1)
        disease_activity: Patient's disease activity score
        
    Returns:
        float or None: Probability of flare if occurs, None otherwise
    """
    if disease_activity is None:
        return None
        
    rand_value = random.uniform(0.01, 0.75)
    
    # Adjust flare chance based on disease activity
    adjusted_chance = baseline_chance * disease_activity
    
    # Determine if flare occurs
    flare_occurs = rand_value < adjusted_chance

    if flare_occurs:
        return adjusted_chance
    else:
        return None

def _flare_longetivty(adjusted_chance):
    '''
    Grabs the adjust chance - if the value is greater than threshold then the longevity value is a random interger between 1 and 7 (indicating prolonged flare assuming now longer than a week)
     
    Args:
        adjusted_chance: the chance of a patient flare on a given day
    
    Returns:
        tuple or None: (flare_extend, flare_duration) if prolonged flare, None otherwise
    '''
    flare_continue_thresh = 0.5  # Lower threshold seems more realistic
    
    if flare_continue_thresh < adjusted_chance:
        flare_extend = True
        flare_duration = np.random.choice([1, 2, 3, 4, 5, 6], 
                             p=[0.4, 0.3, 0.1, 0.1, 0.05, 0.05])  # Probabilities sum to 1.0
    
        return flare_extend, flare_duration
    else:
        return False, 0  
