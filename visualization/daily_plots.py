"""
Daily Time Series Plots for Saskatchewan Glacier Analysis
=========================================================

This module creates daily time series visualizations for albedo values
during melt seasons.
"""

import os
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
        fig, ax = plt.subplots(figsize=(14, 8))
        fig.suptitle(f'Albédo Quotidien - Saison de Fonte {year}', 
                     fontsize=16, fontweight='bold')
        
        # Plot albedo for each fraction
        for fraction in FRACTION_CLASSES:
            col_mean = f"{fraction}_{ANALYSIS_VARIABLE}"
            if col_mean in year_data.columns:
                albedo_data = year_data[col_mean].dropna()
                if len(albedo_data) > 0:
                    # Plot only non-null values
                    valid_data = year_data[year_data[col_mean].notna()]
                    ax.plot(valid_data['date'], valid_data[col_mean], 
                           marker='o', markersize=3, linewidth=1.5, alpha=0.8,
                           label=CLASS_LABELS[fraction],
                           color=FRACTION_COLORS.get(fraction, 'gray'))
        
        # Configure the plot
        ax.set_xlabel('Date')
        ax.set_ylabel(f'Albédo ({ANALYSIS_VARIABLE.capitalize()})')
        ax.set_ylim([0, 1])
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        
        # Add vertical lines to separate months
        for month in [7, 8, 9]:
            month_start = year_data[year_data['month'] == month]['date'].min()
            if not pd.isna(month_start):
                ax.axvline(x=month_start, color='gray', linestyle='--', alpha=0.5)
        
        # Add statistics
        stats_text = f"Période: {year_data['date'].min().strftime('%Y-%m-%d')} à {year_data['date'].max().strftime('%Y-%m-%d')}\n"
        stats_text += f"Observations: {len(year_data)} jours"
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
                verticalalignment='top', fontsize=10,
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
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