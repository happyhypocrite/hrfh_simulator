import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def plot_pain_over_time(df, show_plot=True):
    plt.style.use('seaborn-v0_8')
    sns.set_palette("deep")
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['Segoe UI', 'Arial', 'Helvetica', 'DejaVu Sans'],
        'font.size': 10,
    })

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot pain score over time
    ax.plot(df['day'], df['pain_score'], marker='o', markersize=3, linewidth=1, label='Pain Score')

    # Add labels and title
    ax.set_xlabel('Day')
    ax.set_ylabel('Pain Score')
    ax.set_title(f'Pain Score Over Time: Patient {df["patient_id"].iloc[0]} (DAS Score: {df["das_score"].iloc[0]})')

    # Treatment colors
    treatment_colors = {
        'emergency_steroid': '#E63946',  # Refined red
        'nsaid': '#F9A826',  # Warm amber
        'dmard': '#2A9D8F',  # Teal
        'biologic': '#9B5DE5',  # Soft purple
        'physical_therapy': '#4895EF'  # Sky blue
    }
    
    treatment_started_columns = [col for col in df.columns if col.startswith('started_')]
    treatment_labels_added = set()  # Track which treatments have been added to the legend
    
    for col in treatment_started_columns:
        treatment_name = col.replace('started_', '')
        color = treatment_colors.get(treatment_name, 'gray')
        
        # Find days where this treatment started
        treatment_days = df[df[col] == True]['day'].values
        
        for day in treatment_days:
            # Only add the treatment to the legend once
            if treatment_name not in treatment_labels_added:
                ax.axvline(x=day, color=color, linestyle='--', alpha=0.7, 
                          label=f'{treatment_name} started')
                treatment_labels_added.add(treatment_name)
            else:
                # For subsequent occurrences, don't add to legend but still show the line
                ax.axvline(x=day, color=color, linestyle='--', alpha=0.7)

    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 10.5)
    
    # Create legend 
    ax.legend(loc='upper right')

    plt.tight_layout()

    if show_plot:
        plt.show()
    
    return fig