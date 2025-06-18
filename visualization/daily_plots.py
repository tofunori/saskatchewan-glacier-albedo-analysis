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
        fig.suptitle(f'Composition Albédo Quotidien - Saison de Fonte {year}', 
                     fontsize=16, fontweight='bold')
        
        # Prepare data for stacked bar plot
        dates = year_data['date'].unique()
        dates = pd.to_datetime(dates).sort_values()
        
        # Create a matrix for stacked bars
        fraction_data = {}
        for fraction in FRACTION_CLASSES:
            col_mean = f"{fraction}_{ANALYSIS_VARIABLE}"
            if col_mean in year_data.columns:
                # Align data with dates
                fraction_values = []
                for date in dates:
                    day_data = year_data[year_data['date'] == date]
                    if len(day_data) > 0 and not day_data[col_mean].isna().all():
                        fraction_values.append(day_data[col_mean].iloc[0])
                    else:
                        fraction_values.append(0)  # Fill missing with 0 for stacking
                fraction_data[fraction] = fraction_values
            else:
                fraction_data[fraction] = [0] * len(dates)
        
        # Create stacked bar chart
        bar_width = 1.0  # Full width for daily bars
        bottom_values = np.zeros(len(dates))
        
        for i, fraction in enumerate(FRACTION_CLASSES):
            values = fraction_data[fraction]
            color = FRACTION_COLORS.get(fraction, f'C{i}')
            
            # Only plot bars where there's actual data
            non_zero_mask = np.array(values) > 0
            if np.any(non_zero_mask):
                ax.bar(dates, values, bottom=bottom_values, 
                      width=bar_width, label=CLASS_LABELS[fraction],
                      color=color, alpha=0.8, edgecolor='white', linewidth=0.5)
            
            bottom_values += np.array(values)
        
        # Configure the plot
        ax.set_xlabel('Date', fontsize=12, fontweight='bold')
        ax.set_ylabel(f'Composition Albédo ({ANALYSIS_VARIABLE.capitalize()})', fontsize=12, fontweight='bold')
        ax.set_ylim([0, 1])
        ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=10)
        ax.grid(True, alpha=0.3, axis='y')  # Only horizontal grid for better readability
        
        # Improve date formatting on x-axis
        import matplotlib.dates as mdates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        # Add vertical lines to separate months with better styling
        month_colors = {'Jun': '#ffeeee', 'Jul': '#eeffee', 'Aug': '#eeeeff', 'Sep': '#ffffee'}
        month_names = {6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep'}
        
        for month in [7, 8, 9]:
            month_start = year_data[year_data['month'] == month]['date'].min()
            if not pd.isna(month_start):
                ax.axvline(x=month_start, color='gray', linestyle='--', alpha=0.7, linewidth=1.5)
                
        # Add month labels at the top
        for month in [6, 7, 8, 9]:
            month_data = year_data[year_data['month'] == month]
            if len(month_data) > 0:
                month_center = month_data['date'].mean()
                ax.text(month_center, 0.95, month_names[month], 
                       ha='center', va='center', transform=ax.get_xaxis_transform(),
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8),
                       fontsize=10, fontweight='bold')
        
        # Add enhanced statistics for composition analysis
        stats_text = f"Période: {year_data['date'].min().strftime('%Y-%m-%d')} à {year_data['date'].max().strftime('%Y-%m-%d')}\n"
        stats_text += f"Observations: {len(year_data)} jours\n"
        
        # Calculate composition statistics
        total_albedo_mean = sum([np.mean([v for v in fraction_data[f] if v > 0]) if any(v > 0 for v in fraction_data[f]) else 0 
                                for f in FRACTION_CLASSES])
        if total_albedo_mean > 0:
            stats_text += "\nComposition moyenne:"
            for fraction in FRACTION_CLASSES:
                values = [v for v in fraction_data[fraction] if v > 0]
                if values:
                    mean_val = np.mean(values)
                    percentage = (mean_val / total_albedo_mean) * 100 if total_albedo_mean > 0 else 0
                    stats_text += f"\n• {CLASS_LABELS[fraction]}: {percentage:.1f}%"
        
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