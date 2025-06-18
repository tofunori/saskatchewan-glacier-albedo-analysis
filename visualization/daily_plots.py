"""
Daily Time Series Plots for Saskatchewan Glacier Analysis
=========================================================

This module creates daily time series visualizations for albedo values
during melt seasons.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from config import FRACTION_CLASSES, CLASS_LABELS, FRACTION_COLORS, ANALYSIS_VARIABLE
from utils.helpers import print_section_header


def create_daily_albedo_plots(data_handler, output_dir):
    """
    Create daily albedo plots for each year's melt season
    
    Args:
        data_handler: AlbedoDataHandler instance with loaded data
        output_dir (str): Directory to save the plots
        
    Returns:
        list: Paths to saved plots for each year
    """
    print_section_header("Création des graphiques d'albédo quotidiens", level=2)
    
    saved_plots = []
    data = data_handler.data
    years = sorted(data['year'].unique())
    
    print(f"📅 Années disponibles: {years}")
    
    for year in years:
        print(f"\n🎯 Création du graphique d'albédo pour {year}")
        
        # Filter data for this year's melt season
        year_data = data[
            (data['year'] == year) & 
            (data['month'].isin([6, 7, 8, 9]))
        ].copy()
        
        if len(year_data) == 0:
            print(f"⚠️ Pas de données pour {year}")
            continue
        
        # Sort by date
        year_data = year_data.sort_values('date')
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(16, 8))
        fig.suptitle(f'Albédo Quotidien par Fraction - Saison de Fonte {year}', 
                     fontsize=16, fontweight='bold')
        
        # Plot scatter points for each fraction
        for i, fraction in enumerate(FRACTION_CLASSES):
            col_mean = f"{fraction}_{ANALYSIS_VARIABLE}"
            if col_mean in year_data.columns:
                # Get valid data for this fraction
                fraction_data = year_data[year_data[col_mean].notna()].copy()
                
                if len(fraction_data) > 0:
                    color = FRACTION_COLORS.get(fraction, f'C{i}')
                    
                    # Create scatter plot
                    ax.scatter(fraction_data['date'], fraction_data[col_mean],
                             label=CLASS_LABELS[fraction], color=color, 
                             alpha=0.7, s=30, edgecolors='white', linewidth=0.5)
                    
                    # Optional: Add light trend line for each fraction
                    if len(fraction_data) > 5:
                        # Simple moving average for trend
                        window = min(7, len(fraction_data) // 3)  # 7-day or 1/3 of data
                        if window >= 2:
                            fraction_data_sorted = fraction_data.sort_values('date')
                            rolling_mean = fraction_data_sorted[col_mean].rolling(window=window, center=True).mean()
                            ax.plot(fraction_data_sorted['date'], rolling_mean, 
                                   color=color, alpha=0.3, linewidth=2, linestyle='-')
        
        # Configure the plot
        ax.set_xlabel('Date', fontsize=12, fontweight='bold')
        ax.set_ylabel(f'Albédo ({ANALYSIS_VARIABLE.capitalize()})', fontsize=12, fontweight='bold')
        ax.set_ylim([0, 1])
        ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=10)
        ax.grid(True, alpha=0.3)  # Grid for better readability
        
        # Improve date formatting on x-axis
        import matplotlib.dates as mdates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))  # More frequent for scatter
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        # Add vertical lines to separate months
        month_names = {6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep'}
        
        for month in [7, 8, 9]:
            month_start = year_data[year_data['month'] == month]['date'].min()
            if not pd.isna(month_start):
                ax.axvline(x=month_start, color='gray', linestyle='--', alpha=0.5, linewidth=1)
                
        # Add month labels at the top
        for month in [6, 7, 8, 9]:
            month_data = year_data[year_data['month'] == month]
            if len(month_data) > 0:
                month_center = month_data['date'].mean()
                ax.text(month_center, 0.95, month_names[month], 
                       ha='center', va='center', transform=ax.get_xaxis_transform(),
                       bbox=dict(boxstyle='round,pad=0.2', facecolor='lightgray', alpha=0.7),
                       fontsize=9, fontweight='bold')
        
        # Add simplified statistics
        stats_text = f"Période: {year_data['date'].min().strftime('%Y-%m-%d')} à {year_data['date'].max().strftime('%Y-%m-%d')}\n"
        stats_text += f"Observations: {len(year_data)} jours\n"
        
        # Calculate basic statistics for each fraction
        stats_text += "\nValeurs moyennes:"
        for fraction in FRACTION_CLASSES:
            col_mean = f"{fraction}_{ANALYSIS_VARIABLE}"
            if col_mean in year_data.columns:
                values = year_data[col_mean].dropna()
                if len(values) > 0:
                    mean_val = values.mean()
                    stats_text += f"\n• {CLASS_LABELS[fraction]}: {mean_val:.3f}"
        
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
                verticalalignment='top', fontsize=9,
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
        
        plt.tight_layout()
        
        # Save the plot
        save_path = os.path.join(output_dir, f'daily_albedo_melt_season_{year}.png')
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()  # Close figure to free memory
        
        print(f"✅ Graphique d'albédo {year} sauvegardé: {save_path}")
        saved_plots.append(save_path)
    
    return saved_plots

def create_daily_plots(data, variable='mean', output_dir='output'):
    """
    Fonction de création de graphiques quotidiens pour l'interface interactive
    
    Args:
        data: AlbedoDataHandler avec données chargées
        variable (str): Variable à analyser ('mean' ou 'median')
        output_dir (str): Répertoire de sortie
        
    Returns:
        dict: Chemins des graphiques créés
    """
    from utils.helpers import ensure_directory_exists
    
    # Créer le répertoire de sortie
    ensure_directory_exists(output_dir)
    
    # Créer les graphiques quotidiens
    saved_plots = create_daily_albedo_plots(data, output_dir)
    
    print(f"✅ {len(saved_plots)} graphiques quotidiens créés")
    
    return {
        'daily_plots': saved_plots,
        'count': len(saved_plots)
    }