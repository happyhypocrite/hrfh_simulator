import matplotlib.pyplot as plt
import seaborn as sns 

def plot_pain_over_time(df, show_plot=True):
    plt.style.use('seaborn-v0_8')
    sns.set_palette("deep")

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot pain score over time
    ax.plot(df['day'], df['pain_score'], marker='o', markersize=3, linewidth=1)

    # Add labels and title
    ax.set_xlabel('Day')
    ax.set_ylabel('Pain Score')
    ax.set_title(f'Pain Score Over Time - Patient {df["patient_id"].iloc[0]} (DAS Score: {df["das_score"].iloc[0]})')

    # Add grid and legend
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 10.5)  # Assuming pain scale is 1-10

    # Finalize layout
    plt.tight_layout()
    
    # Display if requested
    if show_plot:
        plt.show()
    
    return fig