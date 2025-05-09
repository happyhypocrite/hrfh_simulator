from shiny import App, render, ui, reactive
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

from plot_pain import plot_pain_over_time

# Define common treatment options
disease_activity = ["High", "Medium", "Low"]
treatment_options1 = ["None", "NSAID", "DMARD", "Biologic", "Steroids", "Exercise", "Rest", "Heat/Cold", "Other"]

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h3("Pain & Treatment"),
        ui.input_numeric("patients", "Patients", value=1, min=1, max=100),
        ui.input_date("date", "Date", value=datetime.now().strftime("%Y-%m-%d")),
        ui.input_numeric("days", "Days to Display", value=15, min=1, max=90),
        ui.input_checkbox_group(
            "display_options", 
            "Display Options",
            choices=["Show trend line", "Show data points", "Show treatments"],
            selected=["Show trend line", "Show data points", "Show treatments"]
        ),
        ui.hr(),
        ui.h3("Main Condition (RA)"),
        ui.input_slider("pain", "Pain Level", min=0, max=10, value=5, step=1),
        ui.input_slider("noise", "Noise Amplitude", min=0, max=10, value=5, step=1),
        ui.input_slider("disease_activity_Scalar", "Scaling Factor", min=0, max=10, value=5, step=1),
        ui.input_select("treatment", "Treatment Used", choices=treatment_options1),
        ui.input_select("disease_activity", "Disease Activity (eg, DAS)", choices=disease_activity),
        ui.hr(),
        ui.input_action_button("generate_data", "Generate Dataset"),
        ui.download_button("download_data", "Download Dataset"),
    ),
    ui.card(
        ui.card_header("Pain Over Time"),
        ui.output_plot("pain_plot"),        
    ),
    ui.card(
        ui.card_header("Data Table"),
        ui.output_data_frame("data_table"),
    ),
    ui.card(
        ui.card_header("Treatment Effectiveness"),
        ui.output_plot("treatment_plot"),
    ),
    title="Synthetic Data Generator"
)

def server(input, output, session):

    # ----------------- PATIENT CLASS ----------------#
    import random
    import numpy as np
    class patientPainGenerator:
        '''Patient class to generate per day pain score data '''
        def __init__(self, id, das_score, seed = None, noise_amplitude = 1.2):
            
            from flare_determination import _flare_chance, _flare_longetivty
            from treatment_determination import _responding_treatment_type, _treatment_effect
            from das_score_changes import _reduce_das_on_dmard, _increase_das_on_flare

            active_flare = 0
            flare_days_remaining = 0
            days = 180

            if seed is not None:
                random.seed(seed)
                np.random.seed(seed)
            patient_pain_persistence = random.uniform(0.7,0.95)  

            # Initial values for pain data generations
            self.id = str(id)
            self.das_score = float(das_score)
            self.pain_persistence = patient_pain_persistence # persistence factor (how much previous pain influences current)
            self.noise_amplitude = noise_amplitude # random fluctuation amplitude
            self.pain_data = {} # dictionary to store pain data
            self.treatments = {} #Active treatment dictionary, Key = treatment_type, Value = days_on_treatment 
            self.treatment_history = []
            self.pain_data[0] = min(10, max(1, self.das_score * 1.8))  #Initialise the pain for day 1
            self.treatment_response = {
            "emergency_steroid": random.uniform(0.5, 1),
            "nsaid": random.uniform(0.5, 1),
            "dmard": random.uniform(0.7, 1),
            "biologic": random.uniform(0.7, 1),
            "physical_therapy": random.uniform(0, 1)
        } # random determination of scale of response to treatment
            self.treatment_start_days = {}
            
            #dmard Logic
            dmard_counter = 0
            dmard_response = self.treatment_response['dmard']

            # For loop in order to model pain data and store within patient class
            for day in range(1,days):
                previous_pain = self.pain_data[day-1] # defining how much pain is carried across
                random_factor = random.choice([-0.5, 0, 0.5]) # introducing noise

            #------------- FLARE MODULE -------------#
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
                    flare_pain_score = 4
                    
                    # Pain adjust on flare
                    new_pain = (previous_pain) + (self.noise_amplitude * random_factor) + (flare_pain_score)
                    
                    # Flare duration and timeout
                    if flare_extend:
                        active_flare = True
                        flare_days_remaining = flare_duration
                        flare_pain_level = new_pain  # Store the pain level to maintain during flare
                else:
                    # No flare therefore normal pain calculation
                    new_pain = (previous_pain) + (self.noise_amplitude * random_factor)

                #------------- TREATMENT MODULE -------------#
                # Treatment start on pain threshold
                if day > 7:
                    new_treatment, dmard_counter = _responding_treatment_type(
                        new_pain, 
                        self.pain_data,
                        self.das_score,
                        dmard_counter
                    )
                    
                    # Start new treatment logic - if recommended and not already on it - MAYBE WE ADD IN THAT ONLY CERTAIN # OF TREATMENTS AT ANYONE TIME?
                    if new_treatment and new_treatment not in self.treatments: # and len(self.treatments) < 5: # limit to 2 treatments at anyone time
                        self.treatments[new_treatment] = 0
                        self.treatment_history.append(new_treatment)
                        self.treatment_start_days[new_treatment] = day 
                        if new_treatment == 'dmard':
                            dmard_counter += 1

                # Apply treatment effects to pain (inc. duration of effect)
                treatment_effect = 0
                for treatment, days_used in list(self.treatments.items()):
                    effect, treatment_dict = _treatment_effect(treatment, days_used)
                    max_effect, onset_days, duration_days, variability = treatment_dict[treatment]

                    # Add 1 to value of days_used for onset days and treament duration logic
                    self.treatments[treatment] += 1
                    # Treatment duration logic - deleted at end of duration
                    if days_used >= duration_days:
                        del self.treatments[treatment]
                    # Chance to reduce response to treatment to low responder randomly
                    if treatment in ['dmard', 'biologic']:
                        if random.random() < 0.01 and self.treatment_response[treatment] > 0.3:  # 1% chance per month of becoming a lower responder
                            reduction = random.uniform(0.3, 0.5) # Reduce response by 30-50%
                            self.treatment_response[treatment] = max(0.2, self.treatment_response[treatment] - reduction)

                    # Normal treatment kicks in after the onset_days amoutn
                    if days_used >= onset_days:
                        treatment_effect += effect
                
                # Apply treatment effect to pain
                new_pain += treatment_effect # Added as a *feature* to the linear model
                new_pain = min(10, max(1, new_pain)) # Keep pain to the 1 - 10 scale

                # New Pain Data added for this day
                self.pain_data[day] = new_pain 

                #------------- DAS SCORE MODULE -------------#
                das_score = _reduce_das_on_dmard(self.treatments, self.das_score)
                das_score = _increase_das_on_flare(flare_days_remaining, self.das_score)



        # Class method to generate the dataframe of patient pain
        def get_pain_dataframe(self):
            """
            Convert the pain_data dictionary to a pandas DataFrame
            
            Returns:
                pandas.DataFrame: DataFrame containing patient pain data with treatment start indicators
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
            
            # Get all treatment types from treatment_response dictionary
            treatment_types = list(self.treatment_response.keys())
            
            # Add boolean columns for treatment starts
            for treatment in treatment_types:
                column_name = f"started_{treatment}"
                df[column_name] = False  # Initialize all as False
            
            # Treatment onset days mapping
            treatment_onset = {
                "emergency_steroid": 1,
                "nsaid": 1,
                "dmard": 14,
                "biologic": 28,
                "physical_therapy": 7
            }
            
            # Fill in treatment start information, adjusted for onset days
            for treatment, start_day in self.treatment_start_days.items():
                column_name = f"started_{treatment}"
                # Adjust start day to when effects actually begin
                effect_start_day = start_day - treatment_onset.get(treatment, 0)
                # Make sure the day exists in our data range
                if effect_start_day in df['day'].values:
                    mask = df['day'] == effect_start_day
                    df.loc[mask, column_name] = True
            
            return df

    # ---------------- REACTIVE CALCULATIONS ------------------------#

    pain_data = reactive.value(sample_data.copy())

    @render.plot
    def pain_plot():
        data = pain_data()

        # Convert date strings to datetime objects for proper plotting
        data['date'] = pd.to_datetime(data['date'])

        # Filter to the last N days
        days_to_show = input.days()
        if len(data) > 0:
            end_date = data['date'].max()
            start_date = end_date - timedelta(days=days_to_show)
            filtered_data = data[data['date'] >= start_date]
        else:
            filtered_data = data

        fig, ax = plt.subplots(figsize=(10, 6))

        # Plot based on display options
        if "Show data points" in input.display_options():
            ax.scatter(filtered_data['date'], filtered_data['pain_level'], color='blue', s=50)

        if "Show trend line" in input.display_options() and len(filtered_data) > 1:
            ax.plot(filtered_data['date'], filtered_data['pain_level'], color='red', linestyle='-', linewidth=2)

        # Add treatment annotations if selected
        if "Show treatments" in input.display_options():
            for idx, row in filtered_data.iterrows():
                if row['treatment'] != "None":
                    ax.annotate(row['treatment'],
                                (row['date'], row['pain_level']),
                                xytext=(0, 10),
                                textcoords='offset points',
                                fontsize=8,
                                rotation=45,
                                ha='center')

        # Setup the plot
        ax.set_ylabel('Pain Level (0-10)', fontsize=12)
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylim(0, 10)
        ax.grid(True, linestyle='--', alpha=0.7)

        # Format x-axis to show dates nicely
        fig.autofmt_xdate()

        return fig

    @render.plot
    def treatment_plot():
        data = pain_data()

        if len(data) < 2:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, "Not enough data to analyze treatments",
                   ha='center', va='center', fontsize=14)
            ax.axis('off')
            return fig

        # Calculate average pain level by treatment
        treatment_effectiveness = data.groupby('treatment')['pain_level'].agg(['mean', 'count']).reset_index()
        treatment_effectiveness = treatment_effectiveness.sort_values('mean')

        # Only include treatments that have been used at least once
        treatment_effectiveness = treatment_effectiveness[treatment_effectiveness['count'] > 0]

        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.barh(treatment_effectiveness['treatment'], treatment_effectiveness['mean'],
                color='skyblue')

        # Add labels for the count
        for i, (pain, count) in enumerate(zip(treatment_effectiveness['mean'], treatment_effectiveness['count'])):
            ax.text(pain + 0.1, i, f"n={count}", va='center')

        ax.set_xlabel('Average Pain Level (Lower is Better)', fontsize=12)
        ax.set_ylabel('Treatment Type', fontsize=12)
        ax.set_xlim(0, 10)
        ax.grid(True, axis='x', linestyle='--', alpha=0.7)

        # Add value labels on the bars
        for bar in bars:
            width = bar.get_width()
            ax.text(width - 0.5, bar.get_y() + bar.get_height()/2,
                   f'{width:.1f}', ha='center', va='center',
                   color='white', fontweight='bold')

        return fig

    @render.data_frame
    def data_table():
        data = pain_data()
        # Sort by date in descending order for display
        display_data = data.sort_values("date", ascending=False)
        return display_data

    @render.download(filename="pain_treatment_data.csv")
    def download():
        return pain_data()

app = App(app_ui, server)
