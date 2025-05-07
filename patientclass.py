class patientPainGenerator:
    '''Patient class to generate per day pain score data '''
    def __init__(self, id, das_score, seed = None, pain_persistence= 0.7, noise_amplitude = 0.2, disease_activity_scalar = 1.2):
        import random
        import numpy as np
        from flare_determination import _flare_chance, _flare_longetivty
        from treatment_determination import _responding_treatment_type, _treatment_effect
        active_flare = 0
        flare_days_remaining = 0
        days = 180

        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        # Initial values for pain data generations
        self.id = str(id)
        self.das_score = float(das_score)
        self.a = pain_persistence # persistence factor (how much previous pain influences current)
        self.b = noise_amplitude # random fluctuation amplitude
        self.c = disease_activity_scalar  # scaling factor based on disease activity
        self.pain_data = {} # dictionary to store pain data
        self.treatments = {} #Active treatment dictionary, Key = treatment_type, Value = days_on_treatment 
        self.treatment_history = []
        self.pain_data[0] = min(10, max(1, self.das_score * 1.5))  #Initialise the pain for day 1

        # For loop in order to model pain data and store within patient class
        for day in range(1,days):
            previous_pain = self.pain_data[day-1] # defining how much pain is carried across
            random_factor = random.uniform(-1, 1) # introducing noise

        #------------- FLARE MODULE #-------------#
        # Active flare maintain the same pain level, end on duration time-out
            if active_flare and flare_days_remaining > 0:
                new_pain = flare_pain_level
                flare_days_remaining -= 1
                if flare_days_remaining == 0:
                    active_flare = False    

            # Flare calculations
            adjusted_chance_flare = _flare_chance(disease_activity = self.das_score)
            
            # Flare instance
            if adjusted_chance_flare is not None: 
                flare_extend, flare_duration = _flare_longetivty(adjusted_chance_flare)
                
                # Pain adjust on flare
                new_pain = (self.a * previous_pain) + (self.b * random_factor * self.c * self.das_score/28) + (adjusted_chance_flare * 2)
                
                # Flare duration and timeout
                if flare_extend:
                    active_flare = True
                    flare_days_remaining = flare_duration
                    flare_pain_level = new_pain  # Store the pain level to maintain during flare
            else:
                # No flare therefore normal pain calculation
                new_pain = (self.a * previous_pain) + (self.b * random_factor * self.c * self.das_score/28)


            #------------- TREATMENT MODULE #-------------#
            # Treatment start on pain threshold
            if day > 7:
                new_treatment = _responding_treatment_type(
                    new_pain, 
                    self.pain_data,
                    self.das_score
                )
                
                # Start new treatment if recommended and not already on it - MAYBE WE ADD IN THAT ONLY CERTAIN # OF TREATMENTS AT ANYONE TIME?
                if new_treatment and new_treatment not in self.treatments:
                    self.treatments[new_treatment] = 0
                    self.treatment_history.append(new_treatment)
            
            # Apply treatment effects to pain (inc. duration of effect)
            treatment_effect = 0
            for treatment, days_used in list(self.treatments.items()):
                effect, treatment_dict = _treatment_effect(treatment, days_used)
                max_effect, onset_days, duration_days, variability = treatment_dict[treatment]
                # Treatment kicks in after the onset_days amoutn
                if days_used >= onset_days:
                    treatment_effect += effect
                # Add 1 to value of days_used for onset days and treament duration logic
                self.treatments[treatment] += 1
                # Treatment duration logic - deleted at end of duration
                if days_used >= duration_days:
                    del self.treatments[treatment]
            
            # Apply treatment effect to pain
            new_pain += treatment_effect # Added as a *feature* to the linear model
            new_pain = min(10, max(1, new_pain)) # Keep pain to the 1 - 10 scale

            # New Pain Data added for this day
            self.pain_data[day] = new_pain 

    # Class method to generate the dataframe of patient pain
    def get_pain_dataframe(self):
        """
        Convert the pain_data dictionary to a pandas DataFrame
        
        Returns:
            pandas.DataFrame: DataFrame containing patient pain data
        """
        import pandas as pd
        
        # Create dataframe from dictionary
        df = pd.DataFrame({
            'day': list(self.pain_data.keys()),
            'pain_score': list(self.pain_data.values())
        })
        
        # Add patient metadata
        df['patient_id'] = self.id
        df['das_score'] = self.das_score
        
        return df

from plot_pain import plot_pain_over_time

p1 = patientPainGenerator('p1', 28)
df = p1.get_pain_dataframe()
print(df)

plot_pain_over_time(df)
