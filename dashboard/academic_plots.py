"""
Academic Publication-Quality Visualization Module
===============================================

Professional plotting module for the Saskatchewan Glacier Albedo Analysis
dashboard, providing publication-ready visualizations with academic standards.

Features:
- Publication-quality figure styling (300 DPI)
- Academic color schemes and typography
- Statistical annotations and significance markers
- Error bars and confidence intervals
- Interactive plotly charts with professional aesthetics
- Comprehensive trend visualizations
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from config import (FRACTION_CLASSES, CLASS_LABELS, FRACTION_COLORS, 
                     TREND_SYMBOLS, get_significance_marker, MONTH_NAMES)

class AcademicPlotGenerator:
    """
    Professional visualization generator for academic publications
    """
    
    def __init__(self):
        """Initialize with academic styling configuration"""
        self.academic_colors = {
            'border': '#d62728',      # Red
            'mixed_low': '#ff7f0e',   # Orange
            'mixed_high': '#2ca02c',  # Green
            'mostly_ice': '#1f77b4',  # Blue
            'pure_ice': '#9467bd'     # Purple
        }
        
        self.significance_colors = {
            '***': '#d62728',  # Red for p < 0.001
            '**': '#ff7f0e',   # Orange for p < 0.01
            '*': '#2ca02c',    # Green for p < 0.05
            'ns': '#7f7f7f'    # Gray for non-significant
        }
        
        self.academic_template = {
            'layout': {
                'font': {'family': 'Arial, sans-serif', 'size': 12},
                'plot_bgcolor': 'white',
                'paper_bgcolor': 'white',
                'showlegend': True,
                'legend': {'x': 1.02, 'y': 1, 'xanchor': 'left'},
                'margin': {'l': 80, 'r': 120, 't': 100, 'b': 80}
            }
        }
    
    def create_comprehensive_trends_plot(self, trend_results, variable='mean'):
        """
        Create comprehensive trend analysis plot with statistical annotations
        
        Args:
            trend_results (dict): Results from statistical analysis
            variable (str): Variable being analyzed
            
        Returns:
            plotly.graph_objects.Figure: Academic-quality trend plot
        """
        n_fractions = len([f for f in FRACTION_CLASSES if f in trend_results and not trend_results[f].get('error', False)])
        
        if n_fractions == 0:
            return self._create_empty_plot("No valid trend data available")
        
        # Create subplots
        rows = (n_fractions + 2) // 3
        cols = min(3, n_fractions)
        
        fig = make_subplots(
            rows=rows, cols=cols,
            subplot_titles=[CLASS_LABELS[f] for f in FRACTION_CLASSES if f in trend_results and not trend_results[f].get('error', False)],
            vertical_spacing=0.12,
            horizontal_spacing=0.08
        )
        
        subplot_idx = 1
        
        for fraction in FRACTION_CLASSES:
            if fraction not in trend_results or trend_results[fraction].get('error', False):
                continue
            
            result = trend_results[fraction]
            times = result['data']['times']
            values = result['data']['values']
            
            row = ((subplot_idx - 1) // 3) + 1
            col = ((subplot_idx - 1) % 3) + 1
            
            # Scatter plot of data points
            fig.add_trace(
                go.Scatter(
                    x=times,
                    y=values,
                    mode='markers',
                    marker=dict(
                        size=4,
                        color=self.academic_colors.get(fraction, '#1f77b4'),
                        opacity=0.6
                    ),
                    name=f'{CLASS_LABELS[fraction]} Data',
                    showlegend=False
                ),
                row=row, col=col
            )
            
            # Trend line
            sen_slope = result['sen_slope']['slope']
            sen_intercept = result['sen_slope']['intercept']
            
            if not np.isnan(sen_slope):
                trend_line = sen_slope * times + sen_intercept
                
                # Add confidence interval if available from bootstrap
                if not result['bootstrap'].get('error', False):
                    bootstrap = result['bootstrap']
                    slope_low = bootstrap['slope_ci_95_low'] / 10  # Convert from per decade to per year
                    slope_high = bootstrap['slope_ci_95_high'] / 10
                    
                    ci_low = slope_low * times + sen_intercept
                    ci_high = slope_high * times + sen_intercept
                    
                    # Confidence interval fill
                    fig.add_trace(
                        go.Scatter(
                            x=np.concatenate([times, times[::-1]]),
                            y=np.concatenate([ci_high, ci_low[::-1]]),
                            fill='toself',
                            fillcolor=self.academic_colors.get(fraction, '#1f77b4'),
                            opacity=0.2,
                            line=dict(width=0),
                            name=f'{CLASS_LABELS[fraction]} 95% CI',
                            showlegend=False
                        ),
                        row=row, col=col
                    )
                
                # Trend line
                fig.add_trace(
                    go.Scatter(
                        x=times,
                        y=trend_line,
                        mode='lines',
                        line=dict(
                            color=self.academic_colors.get(fraction, '#1f77b4'),
                            width=3
                        ),
                        name=f'{CLASS_LABELS[fraction]} Trend',
                        showlegend=False
                    ),
                    row=row, col=col
                )
            
            # Statistical annotations
            mk = result['mann_kendall']
            trend_symbol = TREND_SYMBOLS.get(mk['trend'], '❓')
            significance = get_significance_marker(mk['p_value'])
            
            # Add annotation
            annotation_text = (
                f"{trend_symbol} {mk['trend']}<br>"
                f"p = {mk['p_value']:.2e} {significance}<br>"
                f"τ = {mk['tau']:.3f}<br>"
                f"Slope = {result['sen_slope']['slope_per_decade']:.6f}/decade"
            )
            
            fig.add_annotation(
                x=0.02, y=0.98,
                xref=f'x{subplot_idx} domain', yref=f'y{subplot_idx} domain',
                text=annotation_text,
                showarrow=False,
                bgcolor='rgba(255, 255, 255, 0.8)',
                bordercolor='black',
                borderwidth=1,
                font=dict(size=9)
            )
            
            subplot_idx += 1
        
        # Update layout
        fig.update_layout(
            title=dict(
                text=f'Comprehensive Trend Analysis - {variable.title()} Albedo<br>'
                     f'<sub>Mann-Kendall Tests with Sen\'s Slope and Bootstrap Confidence Intervals</sub>',
                x=0.5,
                font=dict(size=16)
            ),
            height=200 * rows + 100,
            **self.academic_template['layout']
        )
        
        # Update axes
        fig.update_xaxes(title_text="Year", showgrid=True, gridwidth=1, gridcolor='lightgray')
        fig.update_yaxes(title_text="Albedo", showgrid=True, gridwidth=1, gridcolor='lightgray')
        
        return fig
    
    def create_seasonal_analysis_plot(self, seasonal_results, variable='mean'):
        """
        Create seasonal trend analysis visualization
        
        Args:
            seasonal_results (dict): Seasonal analysis results
            variable (str): Variable being analyzed
            
        Returns:
            plotly.graph_objects.Figure: Seasonal analysis plot
        """
        if not seasonal_results:
            return self._create_empty_plot("No seasonal data available")
        
        # Create subplot figure
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=['Monthly Trends by Fraction', 'Significance Heatmap', 
                          'Slope Magnitudes', 'Temporal Patterns'],
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Plot 1: Monthly trends by fraction
        for fraction in FRACTION_CLASSES:
            months = []
            slopes = []
            significance_markers = []
            
            for month, month_data in seasonal_results.items():
                if fraction in month_data['fractions']:
                    months.append(MONTH_NAMES[month])
                    slopes.append(month_data['fractions'][fraction]['sen_slope']['slope_per_decade'])
                    significance_markers.append(
                        get_significance_marker(month_data['fractions'][fraction]['mann_kendall']['p_value'])
                    )
            
            if months:
                fig.add_trace(
                    go.Scatter(
                        x=months,
                        y=slopes,
                        mode='lines+markers',
                        name=CLASS_LABELS[fraction],
                        line=dict(color=self.academic_colors.get(fraction, '#1f77b4'), width=2),
                        marker=dict(size=8),
                        text=significance_markers,
                        textposition='top center'
                    ),
                    row=1, col=1
                )
        
        # Plot 2: Significance heatmap
        self._add_significance_heatmap(fig, seasonal_results, row=1, col=2)
        
        # Plot 3: Slope magnitudes
        self._add_slope_magnitude_plot(fig, seasonal_results, row=2, col=1)
        
        # Plot 4: Temporal patterns
        self._add_temporal_pattern_plot(fig, seasonal_results, row=2, col=2)
        
        # Update layout
        fig.update_layout(
            title=dict(
                text=f'Seasonal Trend Analysis - {variable.title()} Albedo<br>'
                     f'<sub>Monthly Patterns and Statistical Significance</sub>',
                x=0.5,
                font=dict(size=16)
            ),
            height=800,
            **self.academic_template['layout']
        )
        
        return fig
    
    def create_bootstrap_analysis_plot(self, trend_results, variable='mean'):
        """
        Create bootstrap analysis visualization with confidence intervals
        
        Args:
            trend_results (dict): Trend analysis results with bootstrap
            variable (str): Variable being analyzed
            
        Returns:
            plotly.graph_objects.Figure: Bootstrap analysis plot
        """
        valid_results = {f: r for f, r in trend_results.items() 
                        if not r.get('error', False) and not r['bootstrap'].get('error', False)}
        
        if not valid_results:
            return self._create_empty_plot("No valid bootstrap data available")
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=['Bootstrap Slope Distributions', 'Confidence Intervals Comparison',
                          'P-value Bootstrap Distributions', 'Statistical Power Analysis'],
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Plot 1: Bootstrap slope distributions
        for fraction, result in valid_results.items():
            bootstrap = result['bootstrap']
            
            fig.add_trace(
                go.Histogram(
                    x=bootstrap['slopes'],
                    name=CLASS_LABELS[fraction],
                    opacity=0.7,
                    nbinsx=30,
                    marker_color=self.academic_colors.get(fraction, '#1f77b4')
                ),
                row=1, col=1
            )
        
        # Plot 2: Confidence intervals comparison
        fractions = []
        slope_medians = []
        ci_lows = []
        ci_highs = []
        
        for fraction, result in valid_results.items():
            bootstrap = result['bootstrap']
            fractions.append(CLASS_LABELS[fraction])
            slope_medians.append(bootstrap['slope_median'])
            ci_lows.append(bootstrap['slope_ci_95_low'])
            ci_highs.append(bootstrap['slope_ci_95_high'])
        
        # Error bar plot
        fig.add_trace(
            go.Scatter(
                x=slope_medians,
                y=fractions,
                error_x=dict(
                    type='data',
                    symmetric=False,
                    array=[h - m for h, m in zip(ci_highs, slope_medians)],
                    arrayminus=[m - l for l, m in zip(ci_lows, slope_medians)]
                ),
                mode='markers',
                marker=dict(size=10, color='blue'),
                name='Bootstrap CI'
            ),
            row=1, col=2
        )
        
        # Plot 3: P-value distributions
        for fraction, result in valid_results.items():
            bootstrap = result['bootstrap']
            
            fig.add_trace(
                go.Histogram(
                    x=bootstrap['pvalues'],
                    name=f'{CLASS_LABELS[fraction]} p-values',
                    opacity=0.7,
                    nbinsx=20,
                    marker_color=self.academic_colors.get(fraction, '#1f77b4')
                ),
                row=2, col=1
            )
        
        # Plot 4: Statistical power
        power_data = []
        for fraction, result in valid_results.items():
            bootstrap = result['bootstrap']
            power_data.append({
                'Fraction': CLASS_LABELS[fraction],
                'Statistical Power': bootstrap['significant_proportion']
            })
        
        power_df = pd.DataFrame(power_data)
        
        fig.add_trace(
            go.Bar(
                x=power_df['Fraction'],
                y=power_df['Statistical Power'],
                marker_color=[self.academic_colors.get(f, '#1f77b4') for f in valid_results.keys()],
                name='Statistical Power'
            ),
            row=2, col=2
        )
        
        # Add significance threshold line
        fig.add_hline(y=0.8, line_dash="dash", line_color="red", 
                     annotation_text="80% Power Threshold", row=2, col=2)
        
        # Update layout
        fig.update_layout(
            title=dict(
                text=f'Bootstrap Analysis - {variable.title()} Albedo<br>'
                     f'<sub>Confidence Intervals and Statistical Power Assessment</sub>',
                x=0.5,
                font=dict(size=16)
            ),
            height=800,
            **self.academic_template['layout']
        )
        
        # Update axes labels
        fig.update_xaxes(title_text="Slope (per decade)", row=1, col=1)
        fig.update_xaxes(title_text="Slope (per decade)", row=1, col=2)
        fig.update_xaxes(title_text="P-value", row=2, col=1)
        fig.update_xaxes(title_text="Fraction Class", row=2, col=2)
        
        fig.update_yaxes(title_text="Frequency", row=1, col=1)
        fig.update_yaxes(title_text="Fraction Class", row=1, col=2)
        fig.update_yaxes(title_text="Frequency", row=2, col=1)
        fig.update_yaxes(title_text="Statistical Power", row=2, col=2)
        
        return fig
    
    def create_correlation_matrix_plot(self, data, variable='mean'):
        """
        Create correlation matrix with significance testing
        
        Args:
            data (pd.DataFrame): Albedo data
            variable (str): Variable to analyze
            
        Returns:
            plotly.graph_objects.Figure: Correlation matrix plot
        """
        # Prepare correlation data
        correlation_data = {}
        for fraction in FRACTION_CLASSES:
            col_name = f"{fraction}_{variable}"
            if col_name in data.columns:
                correlation_data[CLASS_LABELS[fraction]] = data[col_name].dropna()
        
        if len(correlation_data) < 2:
            return self._create_empty_plot("Insufficient data for correlation analysis")
        
        # Calculate correlation matrix and p-values
        corr_df = pd.DataFrame(correlation_data)
        correlation_matrix = corr_df.corr()
        
        # Calculate p-values for correlations
        n = len(corr_df)
        p_values = np.zeros_like(correlation_matrix)
        
        for i in range(len(correlation_matrix)):
            for j in range(len(correlation_matrix)):
                if i != j:
                    from scipy.stats import pearsonr
                    _, p_val = pearsonr(corr_df.iloc[:, i].dropna(), corr_df.iloc[:, j].dropna())
                    p_values[i, j] = p_val
        
        # Create annotations with correlation values and significance
        annotations = []
        for i in range(len(correlation_matrix)):
            for j in range(len(correlation_matrix)):
                corr_val = correlation_matrix.iloc[i, j]
                p_val = p_values[i, j] if i != j else 0
                
                if i == j:
                    text = f"{corr_val:.2f}"
                else:
                    sig_marker = get_significance_marker(p_val) if p_val < 0.05 else 'ns'
                    text = f"{corr_val:.2f}<br>{sig_marker}"
                
                annotations.append(
                    dict(
                        x=j, y=i,
                        text=text,
                        showarrow=False,
                        font=dict(color='white' if abs(corr_val) > 0.5 else 'black', size=10)
                    )
                )
        
        # Create heatmap
        fig = go.Figure(
            data=go.Heatmap(
                z=correlation_matrix.values,
                x=correlation_matrix.columns,
                y=correlation_matrix.index,
                colorscale='RdBu_r',
                zmid=0,
                zmin=-1,
                zmax=1,
                colorbar=dict(title="Correlation Coefficient")
            )
        )
        
        fig.update_layout(
            title=dict(
                text=f'Correlation Matrix - {variable.title()} Albedo<br>'
                     f'<sub>Pearson Correlations with Statistical Significance</sub>',
                x=0.5,
                font=dict(size=16)
            ),
            annotations=annotations,
            **self.academic_template['layout']
        )
        
        return fig
    
    def _add_significance_heatmap(self, fig, seasonal_results, row, col):
        """Add significance heatmap to subplot"""
        # Prepare significance matrix
        months = list(seasonal_results.keys())
        fractions = FRACTION_CLASSES
        
        significance_matrix = []
        for fraction in fractions:
            row_data = []
            for month in months:
                if fraction in seasonal_results[month]['fractions']:
                    p_val = seasonal_results[month]['fractions'][fraction]['mann_kendall']['p_value']
                    if p_val < 0.001:
                        row_data.append(3)
                    elif p_val < 0.01:
                        row_data.append(2)
                    elif p_val < 0.05:
                        row_data.append(1)
                    else:
                        row_data.append(0)
                else:
                    row_data.append(-1)  # No data
            significance_matrix.append(row_data)
        
        fig.add_trace(
            go.Heatmap(
                z=significance_matrix,
                x=[MONTH_NAMES[m] for m in months],
                y=[CLASS_LABELS[f] for f in fractions],
                colorscale=[[0, 'white'], [0.25, 'lightgray'], [0.5, 'yellow'], [0.75, 'orange'], [1, 'red']],
                showscale=False
            ),
            row=row, col=col
        )
    
    def _add_slope_magnitude_plot(self, fig, seasonal_results, row, col):
        """Add slope magnitude comparison"""
        slopes_data = []
        
        for month, month_data in seasonal_results.items():
            for fraction, fraction_data in month_data['fractions'].items():
                slopes_data.append({
                    'Month': MONTH_NAMES[month],
                    'Fraction': CLASS_LABELS[fraction],
                    'Slope': abs(fraction_data['sen_slope']['slope_per_decade'])
                })
        
        if slopes_data:
            slopes_df = pd.DataFrame(slopes_data)
            
            for fraction in slopes_df['Fraction'].unique():
                fraction_data = slopes_df[slopes_df['Fraction'] == fraction]
                
                fig.add_trace(
                    go.Bar(
                        x=fraction_data['Month'],
                        y=fraction_data['Slope'],
                        name=fraction,
                        marker_color=self.academic_colors.get(
                            [k for k, v in CLASS_LABELS.items() if v == fraction][0], '#1f77b4'
                        )
                    ),
                    row=row, col=col
                )
    
    def _add_temporal_pattern_plot(self, fig, seasonal_results, row, col):
        """Add temporal pattern analysis"""
        # Calculate consistency of trend directions across months
        consistency_data = []
        
        for fraction in FRACTION_CLASSES:
            trends = []
            for month_data in seasonal_results.values():
                if fraction in month_data['fractions']:
                    trend = month_data['fractions'][fraction]['mann_kendall']['trend']
                    if trend == 'increasing':
                        trends.append(1)
                    elif trend == 'decreasing':
                        trends.append(-1)
                    else:
                        trends.append(0)
            
            if trends:
                consistency = abs(np.mean(trends))  # How consistent is the trend direction
                consistency_data.append({
                    'Fraction': CLASS_LABELS[fraction],
                    'Consistency': consistency
                })
        
        if consistency_data:
            consistency_df = pd.DataFrame(consistency_data)
            
            fig.add_trace(
                go.Bar(
                    x=consistency_df['Fraction'],
                    y=consistency_df['Consistency'],
                    marker_color=[self.academic_colors.get(f, '#1f77b4') 
                                for f in [k for k, v in CLASS_LABELS.items() 
                                        if v in consistency_df['Fraction'].values]],
                    name='Trend Consistency'
                ),
                row=row, col=col
            )
    
    def _create_empty_plot(self, message):
        """Create empty plot with message"""
        fig = go.Figure()
        fig.add_annotation(
            x=0.5, y=0.5,
            text=message,
            showarrow=False,
            font=dict(size=16),
            xref='paper', yref='paper'
        )
        fig.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            **self.academic_template['layout']
        )
        return fig