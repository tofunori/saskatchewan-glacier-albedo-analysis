"""
Pixel Count Analysis for Saskatchewan Glacier Albedo Data
========================================================

This module provides comprehensive analysis of pixel counts and data quality
for each fraction and temporal period.
"""

import numpy as np
import pandas as pd
from datetime import datetime

# Import from package
from config import FRACTION_CLASSES, CLASS_LABELS, MONTH_NAMES
from utils.helpers import print_section_header, format_pvalue


class PixelCountAnalyzer:
    """
    Analyzer for pixel count statistics and data quality assessment
    """
    
    def __init__(self, data_handler, qa_csv_path=None):
        """
        Initialize the pixel count analyzer
        
        Args:
            data_handler: AlbedoDataHandler instance with loaded data
            qa_csv_path (str, optional): Path to quality distribution CSV file
        """
        self.data_handler = data_handler
        self.data = data_handler.data
        self.fraction_classes = FRACTION_CLASSES
        self.class_labels = CLASS_LABELS
        self.qa_csv_path = qa_csv_path
        self.qa_data = None
        
    def analyze_monthly_pixel_counts(self):
        """
        Analyze pixel counts by month and fraction
        
        Returns:
            dict: Monthly pixel count statistics
        """
        print_section_header("Analyse des comptages de pixels par mois", level=2)
        
        results = {}
        monthly_stats = []
        
        for month in [6, 7, 8, 9]:  # Melt season months
            month_name = MONTH_NAMES[month]
            month_data = self.data[self.data['month'] == month].copy()
            
            print(f"\n📅 Analyse pour {month_name} (mois {month})")
            
            month_result = {
                'month': month,
                'month_name': month_name,
                'total_observations': len(month_data),
                'fractions': {}
            }
            
            for fraction in self.fraction_classes:
                pixel_col = f"{fraction}_pixel_count"
                
                if pixel_col in month_data.columns:
                    pixel_counts = month_data[pixel_col].dropna()
                    
                    if len(pixel_counts) > 0:
                        stats = {
                            'mean': pixel_counts.mean(),
                            'median': pixel_counts.median(),
                            'std': pixel_counts.std(),
                            'min': pixel_counts.min(),
                            'max': pixel_counts.max(),
                            'total': pixel_counts.sum(),
                            'observations': len(pixel_counts),
                            'q25': pixel_counts.quantile(0.25),
                            'q75': pixel_counts.quantile(0.75)
                        }
                        
                        month_result['fractions'][fraction] = stats
                        
                        # Add to monthly stats list for easy DataFrame creation
                        monthly_stats.append({
                            'month': month,
                            'month_name': month_name,
                            'fraction': fraction,
                            'fraction_label': self.class_labels[fraction],
                            **stats
                        })
                        
                        print(f"  • {self.class_labels[fraction]}: "
                              f"Moyenne={stats['mean']:.1f}, "
                              f"Total={stats['total']:,}, "
                              f"Obs={stats['observations']}")
            
            results[month] = month_result
        
        # Create summary DataFrame
        self.monthly_pixel_stats = pd.DataFrame(monthly_stats)
        results['summary_dataframe'] = self.monthly_pixel_stats
        
        return results
    
    def load_qa_data(self):
        """
        Load and prepare QA distribution data (0-3 scores)
        
        Returns:
            pd.DataFrame: Loaded QA data
        """
        if self.qa_csv_path is None:
            print("❌ Aucun chemin de fichier QA fourni")
            return None
        
        try:
            print_section_header("Chargement des données QA (0-3)", level=2)
            
            # Load QA data
            qa_data = pd.read_csv(self.qa_csv_path)
            
            # Convert date
            qa_data['date'] = pd.to_datetime(qa_data['date'])
            qa_data['year'] = qa_data['date'].dt.year
            qa_data['month'] = qa_data['date'].dt.month
            qa_data['doy'] = qa_data['date'].dt.dayofyear
            
            # Filter for melt season only
            qa_data = qa_data[qa_data['month'].isin([6, 7, 8, 9])]
            
            self.qa_data = qa_data
            
            print(f"✅ Données QA chargées: {len(qa_data)} observations")
            print(f"📅 Période QA: {qa_data['date'].min()} à {qa_data['date'].max()}")
            
            return qa_data
            
        except Exception as e:
            print(f"❌ Erreur lors du chargement des données QA: {e}")
            return None
    
    def analyze_true_qa_statistics(self):
        """
        Analyze true QA statistics (0-3 scores) by melt season
        
        Returns:
            dict: True QA statistics analysis
        """
        print_section_header("Analyse des vraies statistiques QA (0-3)", level=2)
        
        if self.qa_data is None:
            if self.qa_csv_path:
                self.load_qa_data()
            else:
                print("❌ Pas de données QA disponibles")
                return {}
        
        if self.qa_data is None or self.qa_data.empty:
            print("❌ Pas de données QA valides")
            return {}
        
        results = {
            'by_month': {},
            'seasonal_summary': {},
            'qa_trends': {},
            'quality_distribution': {}
        }
        
        qa_monthly_stats = []
        
        # Define QA quality columns
        qa_columns = {
            'quality_0_best': 'QA 0 (Meilleur)',
            'quality_1_good': 'QA 1 (Bon)', 
            'quality_2_moderate': 'QA 2 (Modéré)',
            'quality_3_poor': 'QA 3 (Mauvais)'
        }
        
        # Group by year instead of month for better visualization
        years = sorted(self.qa_data['year'].unique())
        
        for year in years:
            year_data = self.qa_data[self.qa_data['year'] == year].copy()
            
            print(f"\n📅 Analyse QA pour l'année {year}")
            
            year_qa = {
                'year': year,
                'year_name': str(year),
                'total_observations': len(year_data),
                'qa_distribution': {}
            }
            
            if len(year_data) > 0:
                for qa_col, qa_label in qa_columns.items():
                    if qa_col in year_data.columns:
                        qa_values = year_data[qa_col].dropna()
                        
                        if len(qa_values) > 0:
                            qa_stats = {
                                'mean_count': qa_values.mean(),
                                'median_count': qa_values.median(),
                                'std_count': qa_values.std(),
                                'min_count': qa_values.min(),
                                'max_count': qa_values.max(),
                                'total_count': qa_values.sum(),
                                'observations': len(qa_values)
                            }
                            
                            year_qa['qa_distribution'][qa_col] = qa_stats
                            
                            # Add to yearly stats
                            qa_monthly_stats.append({
                                'year': year,
                                'year_name': str(year),
                                'qa_score': qa_col.split('_')[1],  # Extract score number
                                'qa_label': qa_label,
                                **qa_stats
                            })
                            
                            print(f"  • {qa_label}: "
                                  f"Moyenne={qa_stats['mean_count']:.1f} pixels, "
                                  f"Total={qa_stats['total_count']:.0f} pixels, "
                                  f"Obs={qa_stats['observations']}")
                
                # Calculate quality counts for this year (absolute counts)
                year_qa['quality_counts'] = {
                    'quality_0_best': year_data['quality_0_best'].mean() if 'quality_0_best' in year_data.columns else 0,
                    'quality_1_good': year_data['quality_1_good'].mean() if 'quality_1_good' in year_data.columns else 0,
                    'quality_2_moderate': year_data['quality_2_moderate'].mean() if 'quality_2_moderate' in year_data.columns else 0,
                    'quality_3_poor': year_data['quality_3_poor'].mean() if 'quality_3_poor' in year_data.columns else 0
                }
                
                # Also calculate ratios for compatibility
                total_pixels_year = year_data['total_pixels'].mean() if 'total_pixels' in year_data.columns else 0
                
                if total_pixels_year > 0:
                    year_qa['quality_ratios'] = {
                        'best_ratio': year_qa['quality_counts']['quality_0_best'] / total_pixels_year * 100,
                        'good_ratio': year_qa['quality_counts']['quality_1_good'] / total_pixels_year * 100,
                        'moderate_ratio': year_qa['quality_counts']['quality_2_moderate'] / total_pixels_year * 100,
                        'poor_ratio': year_qa['quality_counts']['quality_3_poor'] / total_pixels_year * 100
                    }
                    
                    print(f"  📊 Comptages absolus: "
                          f"QA0={year_qa['quality_counts']['quality_0_best']:.1f}, "
                          f"QA1={year_qa['quality_counts']['quality_1_good']:.1f}, "
                          f"QA2={year_qa['quality_counts']['quality_2_moderate']:.1f}, "
                          f"QA3={year_qa['quality_counts']['quality_3_poor']:.1f}")
            
            results['by_month'][year] = year_qa
        
        # Create QA DataFrame
        self.true_qa_stats_df = pd.DataFrame(qa_monthly_stats)
        results['qa_dataframe'] = self.true_qa_stats_df
        
        # Calculate seasonal summaries
        self._calculate_true_qa_seasonal_summaries(results)
        
        return results
    
    def _calculate_true_qa_seasonal_summaries(self, results):
        """
        Calculate seasonal summaries for true QA data
        """
        qa_df = results['qa_dataframe']
        
        if qa_df.empty:
            return
        
        # Seasonal summary by QA score
        seasonal_summary = {}
        for qa_score in ['0', '1', '2', '3']:
            score_data = qa_df[qa_df['qa_score'] == qa_score]
            if not score_data.empty:
                seasonal_summary[f'qa_{qa_score}'] = {
                    'seasonal_mean_count': score_data['mean_count'].mean(),
                    'seasonal_total_count': score_data['total_count'].sum(),
                    'seasonal_variability': score_data['mean_count'].std(),
                    'best_year': score_data.loc[score_data['mean_count'].idxmax(), 'year_name'] if len(score_data) > 0 else 'N/A',
                    'worst_year': score_data.loc[score_data['mean_count'].idxmin(), 'year_name'] if len(score_data) > 0 else 'N/A'
                }
        
        results['seasonal_summary'] = seasonal_summary
        
        # Overall quality trends
        results['quality_overview'] = {
            'total_observations': len(self.qa_data),
            'date_range': {
                'start': self.qa_data['date'].min(),
                'end': self.qa_data['date'].max()
            },
            'average_total_pixels': self.qa_data['total_pixels'].mean() if 'total_pixels' in self.qa_data.columns else 0
        }
    
    def analyze_seasonal_qa_statistics(self):
        """
        Analyze data quality statistics by melt season
        
        Returns:
            dict: Seasonal QA statistics
        """
        print_section_header("Analyse de la qualité des données par saison", level=2)
        
        results = {
            'by_month': {},
            'seasonal_summary': {},
            'qa_trends': {}
        }
        
        qa_stats = []
        
        for month in [6, 7, 8, 9]:
            month_name = MONTH_NAMES[month]
            month_data = self.data[self.data['month'] == month].copy()
            
            print(f"\n📅 Qualité des données pour {month_name}")
            
            month_qa = {
                'month': month,
                'month_name': month_name,
                'total_observations': len(month_data),
                'fractions': {}
            }
            
            for fraction in self.fraction_classes:
                qa_col = f"{fraction}_data_quality"
                pixel_col = f"{fraction}_pixel_count"
                
                if qa_col in month_data.columns:
                    qa_values = month_data[qa_col].dropna()
                    pixel_values = month_data[pixel_col].dropna()
                    
                    if len(qa_values) > 0:
                        qa_stats_frac = {
                            'qa_mean': qa_values.mean(),
                            'qa_median': qa_values.median(),
                            'qa_std': qa_values.std(),
                            'qa_min': qa_values.min(),
                            'qa_max': qa_values.max(),
                            'high_quality_ratio': (qa_values >= 80).mean(),
                            'medium_quality_ratio': ((qa_values >= 60) & (qa_values < 80)).mean(),
                            'low_quality_ratio': (qa_values < 60).mean(),
                            'pixel_availability': len(pixel_values) / len(month_data) if len(month_data) > 0 else 0,
                            'observations': len(qa_values)
                        }
                        
                        month_qa['fractions'][fraction] = qa_stats_frac
                        
                        # Add to overall stats
                        qa_stats.append({
                            'month': month,
                            'month_name': month_name,
                            'fraction': fraction,
                            'fraction_label': self.class_labels[fraction],
                            **qa_stats_frac
                        })
                        
                        print(f"  • {self.class_labels[fraction]}: "
                              f"QA={qa_stats_frac['qa_mean']:.1f}%, "
                              f"Haute qualité={qa_stats_frac['high_quality_ratio']:.1%}, "
                              f"Disponibilité={qa_stats_frac['pixel_availability']:.1%}")
            
            results['by_month'][month] = month_qa
        
        # Create QA summary DataFrame
        self.qa_stats_df = pd.DataFrame(qa_stats)
        results['qa_dataframe'] = self.qa_stats_df
        
        # Calculate seasonal summaries
        self._calculate_seasonal_summaries(results)
        
        return results
    
    def analyze_total_pixel_trends(self):
        """
        Analyze trends in total valid pixels over time
        
        Returns:
            dict: Total pixel trend analysis
        """
        print_section_header("Analyse des tendances de pixels totaux", level=2)
        
        if 'total_valid_pixels' not in self.data.columns:
            print("❌ Colonne 'total_valid_pixels' non trouvée")
            return {}
        
        # Prepare time series data
        pixel_data = self.data[['date', 'year', 'month', 'total_valid_pixels']].copy()
        pixel_data = pixel_data.dropna(subset=['total_valid_pixels'])
        
        results = {
            'time_series': pixel_data,
            'monthly_averages': {},
            'yearly_trends': {},
            'seasonal_patterns': {}
        }
        
        # Monthly averages
        for month in [6, 7, 8, 9]:
            month_pixels = pixel_data[pixel_data['month'] == month]['total_valid_pixels']
            if len(month_pixels) > 0:
                results['monthly_averages'][month] = {
                    'mean': month_pixels.mean(),
                    'median': month_pixels.median(),
                    'std': month_pixels.std(),
                    'min': month_pixels.min(),
                    'max': month_pixels.max(),
                    'observations': len(month_pixels)
                }
                
                print(f"• {MONTH_NAMES[month]}: Moyenne={month_pixels.mean():.0f} pixels")
        
        # Yearly trends
        yearly_means = pixel_data.groupby('year')['total_valid_pixels'].agg(['mean', 'std', 'count'])
        results['yearly_trends'] = yearly_means.to_dict('index')
        
        # Calculate simple trend
        years = yearly_means.index.values
        means = yearly_means['mean'].values
        if len(years) > 1:
            trend_slope = np.polyfit(years, means, 1)[0]
            results['overall_trend'] = {
                'slope_per_year': trend_slope,
                'slope_per_decade': trend_slope * 10,
                'start_year': years[0],
                'end_year': years[-1],
                'start_mean': means[0],
                'end_mean': means[-1],
                'relative_change': (means[-1] - means[0]) / means[0] * 100
            }
            
            print(f"📈 Tendance globale: {trend_slope:.1f} pixels/an "
                  f"({trend_slope*10:.0f} pixels/décennie)")
            print(f"📊 Changement relatif: {results['overall_trend']['relative_change']:.1f}%")
        
        return results
    
    def _calculate_seasonal_summaries(self, results):
        """
        Calculate seasonal summaries from monthly QA data
        """
        qa_df = results['qa_dataframe']
        
        # Overall seasonal summary
        seasonal_summary = {}
        for fraction in self.fraction_classes:
            frac_data = qa_df[qa_df['fraction'] == fraction]
            if not frac_data.empty:
                seasonal_summary[fraction] = {
                    'seasonal_qa_mean': frac_data['qa_mean'].mean(),
                    'seasonal_availability_mean': frac_data['pixel_availability'].mean(),
                    'high_quality_season_ratio': frac_data['high_quality_ratio'].mean(),
                    'qa_variability': frac_data['qa_mean'].std(),
                    'best_month': frac_data.loc[frac_data['qa_mean'].idxmax(), 'month_name'],
                    'worst_month': frac_data.loc[frac_data['qa_mean'].idxmin(), 'month_name']
                }
        
        results['seasonal_summary'] = seasonal_summary
    
    def create_pixel_count_summary_table(self):
        """
        Create a summary table for pixel counts
        
        Returns:
            pd.DataFrame: Summary table
        """
        if not hasattr(self, 'monthly_pixel_stats'):
            self.analyze_monthly_pixel_counts()
        
        # Create pivot table for easy reading
        summary = self.monthly_pixel_stats.pivot_table(
            index='fraction_label',
            columns='month_name',
            values=['mean', 'total', 'observations'],
            aggfunc='first'
        )
        
        return summary
    
    def create_qa_summary_table(self):
        """
        Create a summary table for QA statistics
        
        Returns:
            pd.DataFrame: QA summary table
        """
        if not hasattr(self, 'qa_stats_df'):
            self.analyze_seasonal_qa_statistics()
        
        # Create pivot table for QA statistics
        qa_summary = self.qa_stats_df.pivot_table(
            index='fraction_label',
            columns='month_name', 
            values=['qa_mean', 'high_quality_ratio', 'pixel_availability'],
            aggfunc='first'
        )
        
        return qa_summary
    
    def export_pixel_analysis_results(self, output_dir='.'):
        """
        Export all pixel analysis results to CSV files
        
        Args:
            output_dir (str): Output directory
            
        Returns:
            dict: Paths to exported files
        """
        import os
        
        exported_files = {}
        
        # Export pixel count summary
        if hasattr(self, 'monthly_pixel_stats'):
            pixel_path = os.path.join(output_dir, 'pixel_count_summary.csv')
            self.monthly_pixel_stats.to_csv(pixel_path, index=False)
            exported_files['pixel_counts'] = pixel_path
            print(f"📊 Comptages de pixels exportés: {pixel_path}")
        
        # Export QA summary
        if hasattr(self, 'qa_stats_df'):
            qa_path = os.path.join(output_dir, 'qa_statistics_summary.csv')
            self.qa_stats_df.to_csv(qa_path, index=False)
            exported_files['qa_stats'] = qa_path
            print(f"📊 Statistiques QA exportées: {qa_path}")
        
        return exported_files