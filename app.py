from shiny import App, render, ui, reactive
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import random

from plot_pain import plot_pain_over_time
from patientclass import patientPainGenerator

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h3("Pain & Treatment"),
        ui.input_numeric("patient_amount", "Patients", value=5, min=1, max=100),
        ui.input_numeric("days_to_display", "Days to Display", value=180, min=1, max=1000),
        ui.hr(),
        ui.h3("Condition"),
        ui.input_slider("noise", "Noise Amplitude", min=0, max=3, value=1.2, step=0.1),
        ui.hr(),
        ui.input_task_button("generate_data", "Generate Dataset"),
        ui.panel_conditional(
            "Object.keys(input).includes('generate_data') && input.generate_data",  # More robust check
            ui.hr(),
            ui.h3("Patient Selection"),
            ui.output_ui("patient_selector")
        ),
        ui.download_button("download_data", "Download Dataset"),
    ),
    ui.card(
        ui.card_header("Pain Over Time"),
        ui.output_plot("pain_plot"),        
    ),
    ui.card(
        ui.card_header("Data Table for Patient"),
        ui.output_data_frame("data_table"),
    ),
    title="Synthetic Data Generator"
)

def server(input, output, session):
    # Store all patient data in reactive values
    all_patients = reactive.value([])
    selected_patient_data = reactive.value(None)
    
    import random 

    @reactive.Effect
    @reactive.event(input.generate_data)
    def generate_patient_data():
        try:
            # Generate data for the specified number of patients
            patients = []
            patient_dataframes = []
            
            print(f"Generating data for {input.patient_amount()} patients")
            
            for i in range(1, input.patient_amount() + 1):
                # Generate a random DAS score for each patient
                das_score = random.triangular(1.6, 8, 4.3)
                print(f"Patient {i}: DAS score = {das_score}")
                
                # Initialize patient with selected parameters
                noise_amplitude = input.noise()
                print(f"Noise amplitude: {noise_amplitude}")
                
                try:
                    patient = patientPainGenerator(
                        id=i,
                        das_score=das_score,
                        noise_amplitude=noise_amplitude
                    )
                    patients.append(patient)
                    
                    # Get the data for this patient
                    df = patient.get_pain_dataframe()
                    if df is not None and not df.empty:
                        print(f"Patient {i} dataframe shape: {df.shape}")
                        patient_dataframes.append(df)
                    else:
                        print(f"Error: Patient {i} dataframe is empty or None")
                except Exception as e:
                    print(f"Error creating patient {i}: {str(e)}")
            
            print(f"Created {len(patient_dataframes)} patient dataframes")
            
            # Store all patient dataframes
            all_patients.set(patient_dataframes)
            
            # Initialize with first patient's data
            if patient_dataframes:
                selected_patient_data.set(patient_dataframes[0])
                print(f"Selected patient data set, shape: {patient_dataframes[0].shape}")
            else:
                print("No patient dataframes were created")
        except Exception as e:
            print(f"Error in generate_patient_data: {str(e)}")
            import traceback
            traceback.print_exc()
        
    @output
    @render.ui
    def patient_selector():
        # Create dropdown list of patients if data exists
        patients_data = all_patients()
        if not patients_data:
            return ui.p("No patient data available")
        
        # Create options for dropdown - Patient ID (DAS Score: X.X)
        options = [
            f"Patient {int(df['patient_id'].iloc[0])} (DAS: {df['das_score'].iloc[0]:.1f})"
            for df in patients_data
        ]
        
        # Create patient selector dropdown
        return ui.input_select(
            "selected_patient", 
            "Select Patient", 
            choices=options
        )
    
    @reactive.effect
    @reactive.event(input.selected_patient)
    def update_selected_patient():
        patients_data = all_patients()
        if not patients_data or not input.selected_patient():
            return
        
        # Extract patient index from selection (Patient X...)
        try:
            patient_idx = int(input.selected_patient().split()[1]) - 1
            if 0 <= patient_idx < len(patients_data):
                selected_patient_data.set(patients_data[patient_idx])
        except (ValueError, IndexError):
            pass
    
    @render.plot
    def pain_plot():
        df = selected_patient_data()
        if df is None:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, "Press 'Generate Dataset' to see data",
                   ha='center', va='center', fontsize=14)
            ax.axis('off')
            return fig
        
        # Limit to the number of days to display
        days_to_display = input.days_to_display()
        max_day = df['day'].max()
        min_day = max(0, max_day - days_to_display)
        filtered_df = df[df['day'] >= min_day]
        
        return plot_pain_over_time(filtered_df, show_plot=False)
    
    @render.data_frame
    def data_table():
        df = selected_patient_data()
        if df is None:
            return pd.DataFrame()
        return df.sort_values('day', ascending=False)
    
    @render.download(filename="pain_treatment_data.csv")
    def download_data():
        return selected_patient_data()

app = App(app_ui, server)
