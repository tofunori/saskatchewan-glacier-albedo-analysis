"""
Pixel Count and QA Visualizations for Saskatchewan Glacier
=========================================================

This module creates comprehensive visualizations for pixel counts,
data quality statistics, and availability patterns.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
from scipy.interpolate import make_interp_spline

# Import from parent package
from ..config import (FRACTION_CLASSES, CLASS_LABELS, MONTH_NAMES, FRACTION_COLORS,
                      PLOT_STYLES, OUTPUT_DIR)
from ..utils.helpers import print_section_header, ensure_directory_exists


class PixelVisualizer:
    """
    Visualizer for pixel count and QA statistics
    """
    
    def __init__(self, data_handler):
        """
        Initialize the pixel visualizer
        
        Args:
            data_handler: AlbedoDataHandler instance with loaded data
        """
        self.data_handler = data_handler
        self.data = data_handler.data
        self.fraction_classes = FRACTION_CLASSES
        self.class_labels = CLASS_LABELS
        
        # Academic color scheme for publication
        self.academic_colors = {
            'border': '#d62728',      # Red
            'mixed_low': '#ff7f0e',   # Orange  
            'mixed_high': '#2ca02c',  # Green
            'mostly_ice': '#1f77b4',  # Blue
            'pure_ice': '#17becf'     # Cyan
        }
    
    def _create_smooth_line(self, x_data, y_data, num_points=300):
        """
        Create smooth interpolated line for plotting
        
        Args:
            x_data: X coordinates (dates converted to numeric)
            y_data: Y coordinates (values)
            num_points: Number of points for smooth line
            
        Returns:
            tuple: (x_smooth, y_smooth) for plotting
        """
        if len(x_data) < 3:  # Need at least 3 points for spline
            return x_data, y_data
        
        try:
            # Convert dates to numeric for interpolation
            x_numeric = np.arange(len(x_data))
            
            # Create spline interpolation
            spline = make_interp_spline(x_numeric, y_data, k=min(3, len(x_data)-1))
            
            # Generate smooth line
            x_smooth_numeric = np.linspace(x_numeric.min(), x_numeric.max(), num_points)
            y_smooth = spline(x_smooth_numeric)
            
            # Map back to original x scale
            x_smooth = np.interp(x_smooth_numeric, x_numeric, np.arange(len(x_data)))
            x_smooth_dates = [x_data.iloc[int(i)] if int(i) < len(x_data) else x_data.iloc[-1] 
                             for i in x_smooth]
            
            return x_smooth_dates, y_smooth
        except:
            # Fallback to original data if interpolation fails
            return x_data, y_data
    
    def _create_hybrid_albedo_analysis(self, ax, year, year_data, modern_colors):
        """
        Crée une analyse hybride avec box plots mensuels et barres empilées de fractions
        
        Args:
            ax: Matplotlib axes object
            year: Année analysée
            year_data: Données pour cette année
            modern_colors: Palette de couleurs
        """
        print(f"🎨 Création de l'analyse hybride albédo pour {year}...")
        
        # Préparer les données mensuelles
        monthly_data = {}
        monthly_fractions = {}
        
        # Ajouter la colonne de mois si elle n'existe pas
        if 'month' not in year_data.columns:
            year_data = year_data.copy()
            year_data['month'] = pd.to_datetime(year_data['date']).dt.month
        
        # Collecter les données par mois
        for month in [6, 7, 8, 9]:  # Juin à Septembre
            month_data = year_data[year_data['month'] == month].copy()
            
            if len(month_data) == 0:
                continue
            
            # Calcul de l'albédo global quotidien pour les box plots
            daily_albedos = []
            monthly_fraction_contributions = {fraction: [] for fraction in self.fraction_classes}
            
            for _, row in month_data.iterrows():
                total_weighted_albedo = 0
                total_pixels = 0
                
                # Calculer l'albédo pondéré total et les contributions par fraction
                for fraction in self.fraction_classes:
                    albedo_col = f"{fraction}_mean"
                    pixel_col = f"{fraction}_pixel_count"
                    
                    if (albedo_col in row.index and pixel_col in row.index and 
                        pd.notna(row[albedo_col]) and pd.notna(row[pixel_col]) and row[pixel_col] > 0):
                        
                        weighted_albedo = row[albedo_col] * row[pixel_col]
                        monthly_fraction_contributions[fraction].append(weighted_albedo)
                        total_weighted_albedo += weighted_albedo
                        total_pixels += row[pixel_col]
                
                # Ajouter l'albédo global si on a des données
                if total_pixels > 0:
                    daily_albedos.append(total_weighted_albedo / total_pixels)
            
            if daily_albedos:
                monthly_data[month] = daily_albedos
                
                # Calculer les contributions moyennes des fractions pour ce mois
                month_fraction_means = {}
                total_month_weighted = sum([sum(monthly_fraction_contributions[f]) for f in self.fraction_classes])
                
                if total_month_weighted > 0:
                    for fraction in self.fraction_classes:
                        contribution = sum(monthly_fraction_contributions[fraction])
                        month_fraction_means[fraction] = contribution / len(month_data) if contribution > 0 else 0
                
                monthly_fractions[month] = month_fraction_means
        
        if not monthly_data:
            ax.text(0.5, 0.5, 'No albedo data available for this year', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_title('A) Monthly Albedo Analysis (No Data)', 
                        fontsize=16, fontweight='bold', pad=15)
            return
        
        # Créer deux sous-axes dans l'axe principal en utilisant subplot division
        import matplotlib.pyplot as plt
        from matplotlib.gridspec import GridSpec
        
        # Diviser l'axe en deux sections verticales
        ax.set_position([ax.get_position().x0, ax.get_position().y0, 
                        ax.get_position().width, ax.get_position().height])
        
        # Calculer les positions pour les deux sous-graphiques
        fig = ax.figure
        pos = ax.get_position()
        
        # Section supérieure (60% de l'espace)
        box_height = pos.height * 0.6
        box_bottom = pos.y0 + pos.height * 0.4 + 0.02  # Petit espace entre les graphiques
        ax_box = fig.add_axes([pos.x0, box_bottom, pos.width, box_height])
        ax_box.set_facecolor('#fafafa')
        
        # Section inférieure (35% de l'espace)
        bar_height = pos.height * 0.35
        bar_bottom = pos.y0
        ax_bar = fig.add_axes([pos.x0, bar_bottom, pos.width, bar_height])
        ax_bar.set_facecolor('#fafafa')
        
        # PARTIE 1: BOX PLOTS AVEC STATISTIQUES
        month_colors = {6: '#e67e22', 7: '#27ae60', 8: '#e74c3c', 9: '#8e44ad'}
        month_names = {6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep'}
        month_positions = {6: 1, 7: 2, 8: 3, 9: 4}
        
        box_data = []
        box_positions = []
        box_colors = []
        
        for month in sorted(monthly_data.keys()):
            box_data.append(monthly_data[month])
            box_positions.append(month_positions[month])
            box_colors.append(month_colors[month])
        
        if box_data:
            # Créer les box plots
            bp = ax_box.boxplot(box_data, positions=box_positions, widths=0.6, 
                               patch_artist=True, showmeans=True, meanline=False,
                               meanprops={'marker': 'D', 'markerfacecolor': 'white', 'markeredgecolor': 'black', 'markersize': 6})
            
            # Colorer les boîtes
            for patch, color in zip(bp['boxes'], box_colors):
                patch.set_facecolor(color)
                patch.set_alpha(0.7)
            
            # Ajouter les annotations statistiques
            for i, (month, data) in enumerate(sorted(monthly_data.items())):
                if len(data) > 0:
                    stats = {
                        'mean': np.mean(data),
                        'median': np.median(data),
                        'std': np.std(data),
                        'min': np.min(data),
                        'max': np.max(data),
                        'p5': np.percentile(data, 5),
                        'p95': np.percentile(data, 95),
                        'n': len(data)
                    }
                    
                    pos = month_positions[month]
                    y_max = max(data)
                    
                    # Texte des statistiques
                    stats_text = f"Mean: {stats['mean']:.3f}\\n"
                    stats_text += f"Median: {stats['median']:.3f}\\n" 
                    stats_text += f"Std: {stats['std']:.3f}\\n"
                    stats_text += f"Min/Max: {stats['min']:.3f}/{stats['max']:.3f}\\n"
                    stats_text += f"5th/95th: {stats['p5']:.3f}/{stats['p95']:.3f}\\n"
                    stats_text += f"N: {stats['n']}"
                    
                    # Positionner l'annotation à droite du box plot
                    ax_box.text(pos + 0.4, y_max, stats_text, fontsize=8, 
                               verticalalignment='top', horizontalalignment='left',
                               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                                        edgecolor=month_colors[month], alpha=0.9))
        
        ax_box.set_title('A) Monthly Albedo Distribution with Statistics', 
                        fontsize=14, fontweight='bold', pad=15)
        ax_box.set_ylabel('Albedo', fontsize=12, fontweight='bold')
        ax_box.set_xticks(list(month_positions.values()))
        ax_box.set_xticklabels([month_names[m] for m in sorted(monthly_data.keys())])
        ax_box.grid(True, alpha=0.3, linestyle=':', linewidth=0.8)
        
        # PARTIE 2: BARRES EMPILÉES DES FRACTIONS
        if monthly_fractions:
            months_sorted = sorted(monthly_fractions.keys())
            bar_positions = [month_positions[m] for m in months_sorted]
            
            # Préparer les données empilées
            bottom_values = np.zeros(len(months_sorted))
            
            for fraction in self.fraction_classes:
                values = []
                for month in months_sorted:
                    if month in monthly_fractions and fraction in monthly_fractions[month]:
                        values.append(monthly_fractions[month][fraction])
                    else:
                        values.append(0)
                
                if any(v > 0 for v in values):
                    ax_bar.bar(bar_positions, values, width=0.6, bottom=bottom_values,
                              label=f'{self.class_labels[fraction]}',
                              color=modern_colors.get(fraction, '#7f8c8d'),
                              alpha=0.8, edgecolor='white', linewidth=0.8)
                    bottom_values += np.array(values)
        
        ax_bar.set_title('Monthly Fraction Contributions (Stacked)', 
                        fontsize=12, fontweight='bold', pad=10)
        ax_bar.set_ylabel('Weighted Albedo', fontsize=10, fontweight='bold')
        ax_bar.set_xlabel('Month', fontsize=10, fontweight='bold')
        ax_bar.set_xticks(list(month_positions.values()))
        ax_bar.set_xticklabels([month_names[m] for m in sorted(monthly_fractions.keys())])
        ax_bar.legend(loc='upper right', frameon=True, fancybox=True, shadow=True, 
                     fontsize=9, ncol=3)
        ax_bar.grid(True, alpha=0.3, linestyle=':', linewidth=0.8, axis='y')
        
        # Masquer l'axe principal pour éviter les conflits
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.set_facecolor('none')
        
        print(f"✅ Panel A: Analyse hybride avec {len(monthly_data)} mois de données")
        
    def create_monthly_pixel_count_plots(self, pixel_results, save_path=None):
        """
        Create comprehensive monthly pixel count visualizations
        
        Args:
            pixel_results (dict): Results from PixelCountAnalyzer.analyze_monthly_pixel_counts()
            save_path (str, optional): Path to save the plot
            
        Returns:
            str: Path to saved plot
        """
        print_section_header("Création des graphiques de comptages de pixels", level=2)
        
        monthly_stats = pixel_results['summary_dataframe']
        
        if monthly_stats.empty:
            print("❌ Pas de données pour créer les graphiques de pixels")
            return None
        
        # Create figure with 4 subplots
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Statistiques de Comptages de Pixels par Mois et Fraction', 
                     fontsize=16, fontweight='bold', y=0.98)
        
        # Plot 1: Average pixel counts by month and fraction
        self._plot_average_pixel_counts(axes[0, 0], monthly_stats)
        
        # Plot 2: Total pixel counts (stacked bar)
        self._plot_total_pixel_counts(axes[0, 1], monthly_stats)
        
        # Plot 3: Pixel count variability (std dev)
        self._plot_pixel_variability(axes[1, 0], monthly_stats)
        
        # Plot 4: Observation counts per month
        self._plot_observation_counts(axes[1, 1], monthly_stats)
        
        plt.tight_layout()
        
        # Save the plot
        if save_path is None:
            ensure_directory_exists(OUTPUT_DIR)
            save_path = os.path.join(OUTPUT_DIR, 'pixel_counts_by_month_fraction.png')
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Graphiques de pixels sauvegardés: {save_path}")
        
        plt.close()
        return save_path
    
    def create_qa_statistics_plots(self, qa_results, save_path=None):
        """
        Create QA statistics visualizations by melt season
        
        Args:
            qa_results (dict): Results from PixelCountAnalyzer.analyze_true_qa_statistics() or analyze_seasonal_qa_statistics()
            save_path (str, optional): Path to save the plot
            
        Returns:
            str: Path to saved plot
        """
        print_section_header("Création des graphiques de qualité des données", level=2)
        
        qa_stats = qa_results['qa_dataframe']
        
        if qa_stats.empty:
            print("❌ Pas de données QA pour créer les graphiques")
            return None
        
        # Check if this is true QA data (0-3 scores) or seasonal QA data (by fraction)
        has_qa_score_column = 'qa_score' in qa_stats.columns
        
        if has_qa_score_column:
            # This is true QA data (0-3 scores) - use the true_qa_plots logic
            print("🔍 Utilisation des données QA vraies (scores 0-3)")
            
            # Create figure with 4 subplots optimized for QA scores
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('Statistiques QA par Scores (0-3) - Saison de Fonte', 
                         fontsize=16, fontweight='bold', y=0.98)
            
            # Plot 1: QA scores distribution by month
            self._plot_qa_scores_distribution(axes[0, 0], qa_stats)
            
            # Plot 2: QA stacked bars
            self._plot_qa_stacked_bars(axes[0, 1], qa_stats)
            
            # Plot 3: QA trends by month
            self._plot_qa_trends_by_month(axes[1, 0], qa_stats)
            
            # Plot 4: QA quality ratios heatmap
            self._plot_qa_quality_heatmap(axes[1, 1], qa_results)
            
        else:
            # This is seasonal QA data (by fraction) - use the original logic
            print("🔍 Utilisation des données QA saisonnières (par fraction)")
            
            # Create figure with 4 subplots
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('Statistiques de Qualité des Données par Saison de Fonte', 
                         fontsize=16, fontweight='bold', y=0.98)
            
            # Plot 1: QA scores by month and fraction
            self._plot_qa_scores(axes[0, 0], qa_stats)
            
            # Plot 2: High quality data ratios
            self._plot_quality_ratios(axes[0, 1], qa_stats)
            
            # Plot 3: Pixel availability patterns
            self._plot_pixel_availability(axes[1, 0], qa_stats)
            
            # Plot 4: QA distribution heatmap
            self._plot_qa_heatmap(axes[1, 1], qa_stats)
        
        plt.tight_layout()
        
        # Save the plot
        if save_path is None:
            ensure_directory_exists(OUTPUT_DIR)
            save_path = os.path.join(OUTPUT_DIR, 'qa_statistics_by_season.png')
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Graphiques QA sauvegardés: {save_path}")
        
        plt.close()
        return save_path
    
    def create_pixel_availability_heatmap(self, pixel_results, qa_results, save_path=None):
        """
        Create a heatmap showing pixel availability across months and fractions
        
        Args:
            pixel_results (dict): Pixel count analysis results
            qa_results (dict): QA analysis results
            save_path (str, optional): Path to save the plot
            
        Returns:
            str: Path to saved plot
        """
        print_section_header("Création de la heatmap de disponibilité des pixels", level=2)
        
        qa_stats = qa_results['qa_dataframe']
        
        # Create availability matrix
        availability_matrix = qa_stats.pivot_table(
            index='fraction_label',
            columns='month_name',
            values='pixel_availability',
            aggfunc='first'
        )
        
        # Ensure correct month order
        month_order = ['Juin', 'Juillet', 'Août', 'Septembre']
        available_months = [m for m in month_order if m in availability_matrix.columns]
        availability_matrix = availability_matrix.reindex(columns=available_months)
        
        # Create the heatmap
        fig, ax = plt.subplots(figsize=(10, 8))
        
        im = sns.heatmap(availability_matrix, 
                        annot=True, 
                        fmt='.1%',
                        cmap='RdYlGn',
                        vmin=0, vmax=1,
                        cbar_kws={'label': 'Disponibilité des Pixels'},
                        ax=ax)
        
        ax.set_title('Disponibilité des Pixels par Fraction et Mois', 
                    fontweight='bold', fontsize=14)
        ax.set_xlabel('Mois')
        ax.set_ylabel('Fraction de Couverture')
        
        plt.tight_layout()
        
        # Save the plot
        if save_path is None:
            ensure_directory_exists(OUTPUT_DIR)
            save_path = os.path.join(OUTPUT_DIR, 'pixel_availability_heatmap.png')
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Heatmap de disponibilité sauvegardée: {save_path}")
        
        plt.close()
        return save_path
    
    def create_total_pixels_timeseries(self, total_pixel_results, save_path=None):
        """
        Create time series plot of total valid pixels
        
        Args:
            total_pixel_results (dict): Results from analyze_total_pixel_trends()
            save_path (str, optional): Path to save the plot
            
        Returns:
            str: Path to saved plot
        """
        print_section_header("Création du graphique temporel des pixels totaux", level=2)
        
        if 'time_series' not in total_pixel_results:
            print("❌ Pas de données temporelles pour les pixels totaux")
            return None
        
        time_data = total_pixel_results['time_series']
        
        # Create figure with 2 subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        fig.suptitle('Évolution Temporelle des Pixels Valides Totaux', 
                     fontsize=16, fontweight='bold')
        
        # Plot 1: Time series
        ax1.plot(time_data['date'], time_data['total_valid_pixels'], 
                'b-', alpha=0.7, linewidth=1, label='Pixels quotidiens')
        
        # Add monthly averages
        monthly_avg = time_data.groupby([time_data['date'].dt.year, time_data['date'].dt.month])['total_valid_pixels'].mean()
        monthly_dates = pd.to_datetime([f"{year}-{month:02d}-15" for (year, month) in monthly_avg.index])
        ax1.plot(monthly_dates, monthly_avg.values, 'r-', linewidth=2, 
                marker='o', markersize=4, label='Moyennes mensuelles')
        
        ax1.set_title('Série Temporelle des Pixels Valides')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Nombre de Pixels Valides')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Seasonal patterns
        for month in [6, 7, 8, 9]:
            month_data = time_data[time_data['month'] == month]
            if not month_data.empty:
                ax2.scatter(month_data['year'], month_data['total_valid_pixels'], 
                           label=MONTH_NAMES[month], alpha=0.6, s=30)
        
        ax2.set_title('Patterns Saisonniers par Année')
        ax2.set_xlabel('Année')
        ax2.set_ylabel('Nombre de Pixels Valides')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Add trend info if available
        if 'overall_trend' in total_pixel_results:
            trend = total_pixel_results['overall_trend']
            ax1.text(0.02, 0.98, 
                    f"Tendance: {trend['slope_per_decade']:.0f} pixels/décennie\n"
                    f"Changement: {trend['relative_change']:.1f}%", 
                    transform=ax1.transAxes, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        
        # Save the plot
        if save_path is None:
            ensure_directory_exists(OUTPUT_DIR)
            save_path = os.path.join(OUTPUT_DIR, 'total_pixels_timeseries.png')
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Série temporelle sauvegardée: {save_path}")
        
        plt.close()
        return save_path
    
    def create_true_qa_plots(self, true_qa_results, save_path=None):
        """
        Create visualizations for true QA scores (0-3) by melt season
        
        Args:
            true_qa_results (dict): Results from analyze_true_qa_statistics()
            save_path (str, optional): Path to save the plot
            
        Returns:
            str: Path to saved plot
        """
        print_section_header("Création des graphiques des vrais scores QA (0-3)", level=2)
        
        if 'qa_dataframe' not in true_qa_results or true_qa_results['qa_dataframe'].empty:
            print("❌ Pas de données QA vraies pour créer les graphiques")
            return None
        
        qa_stats = true_qa_results['qa_dataframe']
        
        # Create figure with 4 subplots
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Analyse des Scores de Qualité QA (0-3) par Saison de Fonte', 
                     fontsize=16, fontweight='bold', y=0.98)
        
        # Plot 1: QA scores distribution by month
        self._plot_qa_scores_distribution(axes[0, 0], qa_stats)
        
        # Plot 2: QA scores as stacked bars
        self._plot_qa_stacked_bars(axes[0, 1], qa_stats)
        
        # Plot 3: QA trends over months
        self._plot_qa_trends_by_month(axes[1, 0], qa_stats)
        
        # Plot 4: QA quality ratios heatmap
        self._plot_qa_quality_heatmap(axes[1, 1], true_qa_results)
        
        plt.tight_layout()
        
        # Save the plot
        if save_path is None:
            ensure_directory_exists(OUTPUT_DIR)
            save_path = os.path.join(OUTPUT_DIR, 'true_qa_scores_analysis.png')
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Graphiques QA vrais sauvegardés: {save_path}")
        
        plt.close()
        return save_path
    
    def create_daily_melt_season_plots(self, pixel_analyzer, save_dir=None, dataset_suffix=""):
        """
        Create daily QA and pixel count plots for each year's melt season
        
        Args:
            pixel_analyzer: PixelCountAnalyzer instance with loaded data
            save_dir (str, optional): Directory to save the plots
            dataset_suffix (str, optional): Suffix to add to filenames for dataset identification
            
        Returns:
            list: Paths to saved plots for each year
        """
        print_section_header("Création des graphiques quotidiens par saison de fonte", level=2)
        
        if save_dir is None:
            ensure_directory_exists(OUTPUT_DIR)
            save_dir = OUTPUT_DIR
        
        # Get available years from the data
        years = sorted(self.data['year'].unique())
        print(f"📅 Années disponibles: {years}")
        
        saved_plots = []
        
        for year in years:
            print(f"\n🎯 Création des graphiques pour l'année {year}")
            
            # Filter data for this year's melt season (June-September)
            year_data = self.data[
                (self.data['year'] == year) & 
                (self.data['month'].isin([6, 7, 8, 9]))
            ].copy()
            
            if len(year_data) == 0:
                print(f"⚠️ Pas de données pour {year}")
                continue
            
            # Create plot for this year
            plot_path = self._create_yearly_daily_plot(year, year_data, pixel_analyzer, save_dir, dataset_suffix)
            if plot_path:
                saved_plots.append(plot_path)
        
        print(f"\n✅ {len(saved_plots)} graphiques annuels créés")
        return saved_plots
    
    def _create_yearly_daily_plot(self, year, year_data, pixel_analyzer, save_dir, dataset_suffix=""):
        """
        Create daily plot for a specific year's melt season with improved design
        
        Args:
            year (int): Year to plot
            year_data (pd.DataFrame): Data for this year
            pixel_analyzer: PixelCountAnalyzer instance
            save_dir (str): Directory to save the plot
            dataset_suffix (str): Suffix to add to filename
            
        Returns:
            str: Path to saved plot
        """
        # Create figure with 3 vertically stacked subplots for better readability
        fig, axes = plt.subplots(3, 1, figsize=(16, 15))
        
        # Enhanced title with dataset info
        dataset_name = "MOD10A1" if "mod10a1" in dataset_suffix else "MCD43A3"
        fig.suptitle(f'Daily Melt Season Analysis {year} - {dataset_name}\nSaskatchewan Glacier Albedo Monitoring', 
                     fontsize=20, fontweight='bold', y=0.98)
        
        # Modern color palette - more distinct and professional
        modern_colors = {
            'border': '#e74c3c',      # Bright red
            'mixed_low': '#f39c12',   # Orange
            'mixed_high': '#2ecc71',  # Green  
            'mostly_ice': '#3498db',  # Blue
            'pure_ice': '#9b59b6'     # Purple
        }
        
        # Sort data by date
        year_data = year_data.sort_values('date')
        dates = year_data['date']
        
        # =================================================================
        # SUBPLOT A: Monthly Albedo Analysis - HYBRID (Box plots + Stacked bars)
        # =================================================================
        ax1 = axes[0]
        self._create_hybrid_albedo_analysis(ax1, year, year_data, modern_colors)
        
        # =================================================================
        # SUBPLOT B: Daily Pixel Count Composition - STACKED BARS
        # =================================================================
        ax2 = axes[1]
        
        # Prepare data for stacked pixel count bars
        pixel_data = {}
        pixel_valid_dates = []
        
        for _, row in year_data.iterrows():
            date = row['date']
            day_pixels = {}
            
            # Get pixel count for each fraction
            for fraction in self.fraction_classes:
                pixel_col = f"{fraction}_pixel_count"
                
                if pixel_col in row.index and pd.notna(row[pixel_col]) and row[pixel_col] > 0:
                    day_pixels[fraction] = row[pixel_col]
            
            # Only include days with pixel data
            if day_pixels:
                pixel_valid_dates.append(date)
                
                for fraction in self.fraction_classes:
                    if fraction not in pixel_data:
                        pixel_data[fraction] = []
                    
                    if fraction in day_pixels:
                        pixel_data[fraction].append(day_pixels[fraction])
                    else:
                        pixel_data[fraction].append(0)
        
        if pixel_valid_dates and pixel_data:
            # Create stacked bars for pixel counts
            bottom_values = np.zeros(len(pixel_valid_dates))
            width = 1.0  # Full width bars for daily data
            
            for fraction in self.fraction_classes:
                if fraction in pixel_data and len(pixel_data[fraction]) == len(pixel_valid_dates):
                    values = np.array(pixel_data[fraction])
                    
                    ax2.bar(pixel_valid_dates, values, width, bottom=bottom_values,
                           label=f'{self.class_labels[fraction]}',
                           color=modern_colors.get(fraction, '#7f8c8d'),
                           alpha=0.8, edgecolor='white', linewidth=0.5)
                    
                    bottom_values += values
            
            ax2.set_title('B) Daily Pixel Count Composition (Stacked by Ice Coverage Fraction)', 
                         fontsize=16, fontweight='bold', pad=15)
            ax2.set_ylabel('Number of Pixels', fontsize=14, fontweight='bold')
            ax2.legend(loc='upper left', frameon=True, fancybox=True, shadow=True, 
                      fontsize=11, ncol=2)
            ax2.grid(True, alpha=0.4, linestyle=':', linewidth=0.8, axis='y')
            ax2.set_facecolor('#fafafa')
            
            print(f"✅ Panel B: Stacked pixel count bars for {len(pixel_valid_dates)} days")
        else:
            ax2.text(0.5, 0.5, 'No pixel count data available for this year', 
                    ha='center', va='center', transform=ax2.transAxes, fontsize=14)
            ax2.set_title('B) Daily Pixel Count Composition (No Data)', 
                         fontsize=16, fontweight='bold', pad=15)
        
        # =================================================================
        # SUBPLOT C: Daily Quality Assessment Distribution - STACKED BARS
        # =================================================================
        ax3 = axes[2]
        qa_plotted = False
        
        # Enhanced QA color scheme with better contrast
        qa_colors = ['#27ae60', '#3498db', '#f39c12', '#e74c3c']  # Green, Blue, Orange, Red
        qa_labels = ['QA 0 (Excellent)', 'QA 1 (Good)', 'QA 2 (Fair)', 'QA 3 (Poor)']
        qa_columns = ['quality_0_best', 'quality_1_good', 'quality_2_moderate', 'quality_3_poor']
        
        # Try to plot QA data if available
        if pixel_analyzer.qa_data is not None:
            year_qa_data = pixel_analyzer.qa_data[
                pixel_analyzer.qa_data['year'] == year
            ].copy()
            
            if len(year_qa_data) > 0:
                year_qa_data = year_qa_data.sort_values('date')
                
                # Prepare data for stacked bars
                qa_valid_dates = []
                qa_stacked_data = {qa_col: [] for qa_col in qa_columns}
                
                for _, row in year_qa_data.iterrows():
                    has_data = False
                    for qa_col in qa_columns:
                        if qa_col in year_qa_data.columns and pd.notna(row[qa_col]) and row[qa_col] > 0:
                            has_data = True
                            break
                    
                    if has_data:
                        qa_valid_dates.append(row['date'])
                        for qa_col in qa_columns:
                            value = row[qa_col] if qa_col in year_qa_data.columns and pd.notna(row[qa_col]) else 0
                            qa_stacked_data[qa_col].append(max(0, value))
                
                if qa_valid_dates:
                    # Create stacked bars
                    width = pd.Timedelta(days=1)  # Bar width
                    bottom_values = np.zeros(len(qa_valid_dates))
                    
                    for i, (qa_col, qa_label, qa_color) in enumerate(zip(qa_columns, qa_labels, qa_colors)):
                        values = qa_stacked_data[qa_col]
                        if any(v > 0 for v in values):
                            ax3.bar(qa_valid_dates, values, width, bottom=bottom_values,
                                   label=f'{qa_label}',
                                   color=qa_color, alpha=0.8, edgecolor='white', linewidth=0.5)
                            bottom_values += np.array(values)
                    
                    qa_plotted = True
                    print(f"✅ Panel C: Stacked QA distribution bars for {len(qa_valid_dates)} days")
        
        if qa_plotted:
            ax3.set_title('C) Daily Quality Assessment Distribution (Stacked Bars)', 
                         fontsize=16, fontweight='bold', pad=15)
            ax3.set_ylabel('Number of Pixels', fontsize=14, fontweight='bold')
            ax3.set_xlabel('Date', fontsize=14, fontweight='bold')
            ax3.legend(loc='upper left', frameon=True, fancybox=True, shadow=True, 
                      fontsize=11, ncol=2)
            ax3.grid(True, alpha=0.4, linestyle=':', linewidth=0.8, axis='y')
            ax3.set_facecolor('#fafafa')
        else:
            ax3.text(0.5, 0.5, 'No quality assessment data available for this year', 
                    ha='center', va='center', transform=ax3.transAxes, fontsize=14)
            ax3.set_title('C) Daily Quality Assessment Distribution (Not Available)', 
                         fontsize=16, fontweight='bold', pad=15)
            ax3.set_xlabel('Date', fontsize=14, fontweight='bold')
        
        
        # =================================================================
        # FINAL FORMATTING AND LAYOUT
        # =================================================================
        
        # Add summary statistics text box
        stats_text = self._generate_year_summary_stats(year, year_data, pixel_analyzer)
        fig.text(0.02, 0.01, stats_text, fontsize=10, 
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                         edgecolor='lightgray', alpha=0.95))
        
        # Adjust layout with proper spacing for vertical stack
        plt.tight_layout(rect=[0.0, 0.08, 1.0, 0.96])
        
        # Apply consistent date formatting to all x-axes
        import matplotlib.dates as mdates
        for ax in axes:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.tick_params(axis='x', rotation=45, labelsize=12)
            ax.tick_params(axis='y', labelsize=12)
        
        # Create directory if it doesn't exist
        os.makedirs(save_dir, exist_ok=True)
        
        # Save the plot with high quality
        save_path = os.path.join(save_dir, f'daily_melt_season_{year}{dataset_suffix}.png')
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
        print(f"✅ Enhanced daily plot for {year} saved: {save_path}")
        
        plt.close()
        return save_path
    
    def _generate_year_summary_stats(self, year, year_data, pixel_analyzer):
        """
        Generate enhanced summary statistics text for a year
        
        Args:
            year (int): Year
            year_data (pd.DataFrame): Data for this year
            pixel_analyzer: PixelCountAnalyzer instance
            
        Returns:
            str: Enhanced summary statistics text
        """
        stats_lines = [f"📊 ANALYSIS SUMMARY {year}"]
        
        # Basic statistics
        total_days = len(year_data)
        date_range = f"{year_data['date'].min().strftime('%m/%d')} to {year_data['date'].max().strftime('%m/%d')}"
        stats_lines.append(f"• {total_days} observation days ({date_range})")
        
        # Albedo statistics
        albedo_cols = [f"{fraction}_mean" for fraction in self.fraction_classes 
                      if f"{fraction}_mean" in year_data.columns]
        if albedo_cols:
            avg_albedo = year_data[albedo_cols].mean().mean()
            max_albedo = year_data[albedo_cols].max().max()
            min_albedo = year_data[albedo_cols].min().min()
            stats_lines.append(f"• Albedo range: {min_albedo:.3f} - {max_albedo:.3f} (avg: {avg_albedo:.3f})")
        
        # Pixel count statistics
        pixel_cols = [f"{fraction}_pixel_count" for fraction in self.fraction_classes 
                     if f"{fraction}_pixel_count" in year_data.columns]
        if pixel_cols:
            total_pixels = year_data[pixel_cols].sum(axis=1)
            avg_pixels = total_pixels.mean()
            max_pixels = total_pixels.max()
            stats_lines.append(f"• Total pixels/day: {avg_pixels:.0f} avg, {max_pixels:.0f} max")
        
        # Data availability by month
        monthly_counts = year_data['month'].value_counts().sort_index()
        month_names = {6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep'}
        month_summary = ", ".join([f"{month_names.get(m, str(m))}({count})" for m, count in monthly_counts.items()])
        stats_lines.append(f"• Monthly distribution: {month_summary}")
        
        # Quality assessment summary if available
        if pixel_analyzer.qa_data is not None:
            year_qa = pixel_analyzer.qa_data[pixel_analyzer.qa_data['year'] == year]
            if not year_qa.empty:
                qa_cols = ['quality_0_best', 'quality_1_good', 'quality_2_moderate', 'quality_3_poor']
                available_qa_cols = [col for col in qa_cols if col in year_qa.columns]
                if available_qa_cols:
                    qa_totals = year_qa[available_qa_cols].sum()
                    best_qa_pct = (qa_totals.iloc[0] / qa_totals.sum()) * 100 if qa_totals.sum() > 0 else 0
                    stats_lines.append(f"• Data quality: {best_qa_pct:.1f}% excellent quality")
        
        return "\n".join(stats_lines)

