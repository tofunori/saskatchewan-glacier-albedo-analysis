"""
Interactive Plotting Functions for Dashboard
==========================================

Plotly-based visualization functions for the Saskatchewan Glacier Albedo Dashboard.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from scipy import stats
import pymannkendall as mk

from config import (
    FRACTION_COLORS, CLASS_LABELS, ANALYSIS_CONFIG,
    SIGNIFICANCE_MARKERS, MONTH_NAMES
)

def create_timeseries_plot(data, fractions, variable, show_trends=True, show_seasonal=False):
    """
    Create interactive time series plot
    
    Args:
        data (pd.DataFrame): Data with date column and fraction columns
        fractions (list): List of fraction classes to plot
        variable (str): Variable to plot (mean/median)
        show_trends (bool): Whether to show trend lines
        show_seasonal (bool): Whether to highlight seasonal patterns
    
    Returns:
        plotly.graph_objects.Figure: Interactive time series plot
    """
    fig = go.Figure()
    
    # Ensure date column is datetime
    if 'date' in data.columns:
        data['date'] = pd.to_datetime(data['date'])
    
    for fraction in fractions:
        col_name = f"{fraction}_{variable}"
        if col_name not in data.columns:
            continue
            
        color = FRACTION_COLORS.get(fraction, '#1f77b4')
        label = CLASS_LABELS.get(fraction, fraction)
        
        # Filter out NaN values
        mask = data[col_name].notna()
        plot_data = data[mask]
        
        if len(plot_data) == 0:
            continue
        
        # Main time series line
        fig.add_trace(go.Scatter(
            x=plot_data['date'],
            y=plot_data[col_name],
            mode='lines+markers',
            name=label,
            line=dict(color=color, width=2),
            marker=dict(size=4, opacity=0.7),
            hovertemplate=f'<b>{label}</b><br>' +
                         'Date: %{x}<br>' +
                         f'{variable.title()}: %{y:.3f}<br>' +
                         '<extra></extra>'
        ))
        
        # Add trend line if requested
        if show_trends and len(plot_data) > 10:
            try:
                # Simple linear trend for visualization
                x_numeric = (plot_data['date'] - plot_data['date'].min()).dt.days
                slope, intercept, r_value, p_value, std_err = stats.linregress(
                    x_numeric, plot_data[col_name]
                )
                
                trend_y = slope * x_numeric + intercept
                
                # Add trend line
                fig.add_trace(go.Scatter(
                    x=plot_data['date'],
                    y=trend_y,
                    mode='lines',
                    name=f'{label} Trend',
                    line=dict(color=color, width=3, dash='dash'),
                    showlegend=False,
                    hovertemplate=f'<b>{label} Trend</b><br>' +
                                 f'Slope: {slope:.6f}/day<br>' +
                                 f'R²: {r_value**2:.3f}<br>' +
                                 f'p-value: {p_value:.4f}<br>' +
                                 '<extra></extra>'
                ))
            except Exception as e:
                print(f"Could not calculate trend for {fraction}: {e}")
    
    # Customize layout
    fig.update_layout(
        title=dict(
            text="Albedo Time Series Analysis",
            x=0.5,
            font=dict(size=20)
        ),
        xaxis=dict(
            title="Date",
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.2)'
        ),
        yaxis=dict(
            title=f"{variable.title()} Albedo",
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.2)'
        ),
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=600,
        template="plotly_white"
    )
    
    return fig

def create_seasonal_plot(data, fractions, variable):
    """
    Create seasonal analysis plots
    
    Args:
        data (pd.DataFrame): Data with temporal columns
        fractions (list): List of fraction classes
        variable (str): Variable to analyze
    
    Returns:
        plotly.graph_objects.Figure: Seasonal analysis plot
    """
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=['Monthly Averages', 'Day of Year Distribution', 
                       'Seasonal Boxplots', 'Year-over-Year Comparison'],
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    colors = px.colors.qualitative.Set1
    
    for i, fraction in enumerate(fractions):
        col_name = f"{fraction}_{variable}"
        if col_name not in data.columns:
            continue
            
        color = FRACTION_COLORS.get(fraction, colors[i % len(colors)])
        label = CLASS_LABELS.get(fraction, fraction)
        
        # Monthly averages (subplot 1)
        if 'month' in data.columns:
            monthly_avg = data.groupby('month')[col_name].mean()
            fig.add_trace(
                go.Scatter(
                    x=monthly_avg.index,
                    y=monthly_avg.values,
                    mode='lines+markers',
                    name=f'{label}',
                    line=dict(color=color),
                    showlegend=True
                ),
                row=1, col=1
            )
        
        # Day of year scatter (subplot 2)
        if 'day_of_year' in data.columns:
            fig.add_trace(
                go.Scatter(
                    x=data['day_of_year'],
                    y=data[col_name],
                    mode='markers',
                    name=f'{label}',
                    marker=dict(color=color, size=3, opacity=0.5),
                    showlegend=False
                ),
                row=1, col=2
            )
        
        # Seasonal boxplots (subplot 3)
        if 'season' in data.columns:
            for season in data['season'].unique():
                season_data = data[data['season'] == season][col_name].dropna()
                if len(season_data) > 0:
                    fig.add_trace(
                        go.Box(
                            y=season_data,
                            name=f'{season}',
                            boxpoints='outliers',
                            showlegend=False,
                            marker=dict(color=color)
                        ),
                        row=2, col=1
                    )
        
        # Year-over-year comparison (subplot 4)
        if 'year' in data.columns:
            yearly_avg = data.groupby('year')[col_name].mean()
            fig.add_trace(
                go.Scatter(
                    x=yearly_avg.index,
                    y=yearly_avg.values,
                    mode='lines+markers',
                    name=f'{label}',
                    line=dict(color=color),
                    showlegend=False
                ),
                row=2, col=2
            )
    
    fig.update_layout(
        height=800,
        title_text="Seasonal Patterns Analysis",
        template="plotly_white"
    )
    
    return fig

def create_comparison_plot(data1, data2, fractions, variable, dataset1_name, dataset2_name):
    """
    Create dataset comparison plots
    
    Args:
        data1, data2 (pd.DataFrame): Datasets to compare
        fractions (list): Fraction classes to compare
        variable (str): Variable to compare
        dataset1_name, dataset2_name (str): Dataset names
    
    Returns:
        plotly.graph_objects.Figure: Comparison plot
    """
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=['Scatter Comparison', 'Time Series Overlay',
                       'Difference Time Series', 'Correlation Matrix'],
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Prepare data for comparison
    data1['date'] = pd.to_datetime(data1['date'])
    data2['date'] = pd.to_datetime(data2['date'])
    
    correlations = {}
    
    for i, fraction in enumerate(fractions):
        col_name = f"{fraction}_{variable}"
        if col_name not in data1.columns or col_name not in data2.columns:
            continue
            
        color = FRACTION_COLORS.get(fraction, px.colors.qualitative.Set1[i])
        label = CLASS_LABELS.get(fraction, fraction)
        
        # Merge datasets on date
        merged = pd.merge(
            data1[['date', col_name]].rename(columns={col_name: f'{col_name}_1'}),
            data2[['date', col_name]].rename(columns={col_name: f'{col_name}_2'}),
            on='date',
            how='inner'
        )
        
        if len(merged) == 0:
            continue
        
        # Calculate correlation
        correlation = merged[f'{col_name}_1'].corr(merged[f'{col_name}_2'])
        correlations[fraction] = correlation
        
        # Scatter plot (subplot 1)
        fig.add_trace(
            go.Scatter(
                x=merged[f'{col_name}_1'],
                y=merged[f'{col_name}_2'],
                mode='markers',
                name=f'{label} (r={correlation:.3f})',
                marker=dict(color=color, size=5, opacity=0.6)
            ),
            row=1, col=1
        )
        
        # Time series overlay (subplot 2)
        fig.add_trace(
            go.Scatter(
                x=merged['date'],
                y=merged[f'{col_name}_1'],
                mode='lines',
                name=f'{label} ({dataset1_name})',
                line=dict(color=color, width=2)
            ),
            row=1, col=2
        )
        
        fig.add_trace(
            go.Scatter(
                x=merged['date'],
                y=merged[f'{col_name}_2'],
                mode='lines',
                name=f'{label} ({dataset2_name})',
                line=dict(color=color, width=2, dash='dash')
            ),
            row=1, col=2
        )
        
        # Difference time series (subplot 3)
        difference = merged[f'{col_name}_1'] - merged[f'{col_name}_2']
        fig.add_trace(
            go.Scatter(
                x=merged['date'],
                y=difference,
                mode='lines+markers',
                name=f'{label} Difference',
                line=dict(color=color, width=2),
                marker=dict(size=3)
            ),
            row=2, col=1
        )
    
    # Add 1:1 line to scatter plot
    if len(merged) > 0:
        min_val = min(merged[f'{col_name}_1'].min(), merged[f'{col_name}_2'].min())
        max_val = max(merged[f'{col_name}_1'].max(), merged[f'{col_name}_2'].max())
        
        fig.add_trace(
            go.Scatter(
                x=[min_val, max_val],
                y=[min_val, max_val],
                mode='lines',
                name='1:1 Line',
                line=dict(color='red', dash='dash', width=2),
                showlegend=False
            ),
            row=1, col=1
        )
    
    # Add zero line to difference plot
    if 'date' in merged.columns:
        fig.add_hline(y=0, line_dash="dash", line_color="red", row=2, col=1)
    
    # Correlation heatmap (subplot 4)
    if correlations:
        fraction_names = list(correlations.keys())
        corr_matrix = np.array([[correlations.get(f, 0) for f in fraction_names]])
        
        fig.add_trace(
            go.Heatmap(
                z=corr_matrix,
                x=fraction_names,
                y=[f'{dataset1_name} vs {dataset2_name}'],
                colorscale='RdYlBu',
                zmid=0,
                showscale=True
            ),
            row=2, col=2
        )
    
    fig.update_layout(
        height=800,
        title_text=f"Dataset Comparison: {dataset1_name} vs {dataset2_name}",
        template="plotly_white"
    )
    
    # Update axis labels
    fig.update_xaxes(title_text=f"{dataset1_name} Albedo", row=1, col=1)
    fig.update_yaxes(title_text=f"{dataset2_name} Albedo", row=1, col=1)
    fig.update_xaxes(title_text="Date", row=1, col=2)
    fig.update_yaxes(title_text="Albedo", row=1, col=2)
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Difference", row=2, col=1)
    
    return fig

def create_trend_analysis_plot(data, fractions, variable):
    """
    Create comprehensive trend analysis visualization
    
    Args:
        data (pd.DataFrame): Data with temporal information
        fractions (list): Fraction classes to analyze
        variable (str): Variable to analyze
    
    Returns:
        plotly.graph_objects.Figure: Trend analysis plot
    """
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=['Trend Slopes', 'P-values', 'Trend Significance', 'Autocorrelation'],
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    trend_results = []
    
    for fraction in fractions:
        col_name = f"{fraction}_{variable}"
        if col_name not in data.columns:
            continue
            
        # Get clean data
        clean_data = data[col_name].dropna()
        if len(clean_data) < 10:
            continue
        
        try:
            # Mann-Kendall trend test
            mk_result = mk.original_test(clean_data)
            
            trend_results.append({
                'fraction': fraction,
                'label': CLASS_LABELS.get(fraction, fraction),
                'trend': mk_result.trend,
                'slope': mk_result.slope,
                'p_value': mk_result.p,
                'significance': get_significance_level(mk_result.p)
            })
            
        except Exception as e:
            print(f"Error in trend analysis for {fraction}: {e}")
    
    if not trend_results:
        return go.Figure().add_annotation(
            text="No trend analysis available for current selection",
            xref="paper", yref="paper", x=0.5, y=0.5
        )
    
    # Convert to DataFrame for easier plotting
    trends_df = pd.DataFrame(trend_results)
    
    # Subplot 1: Trend slopes
    fig.add_trace(
        go.Bar(
            x=trends_df['label'],
            y=trends_df['slope'],
            marker_color=[FRACTION_COLORS.get(f, 'blue') for f in trends_df['fraction']],
            name='Slope'
        ),
        row=1, col=1
    )
    
    # Subplot 2: P-values
    fig.add_trace(
        go.Bar(
            x=trends_df['label'],
            y=trends_df['p_value'],
            marker_color=[FRACTION_COLORS.get(f, 'blue') for f in trends_df['fraction']],
            name='P-value'
        ),
        row=1, col=2
    )
    
    # Add significance threshold line
    fig.add_hline(y=0.05, line_dash="dash", line_color="red", row=1, col=2)
    
    # Subplot 3: Trend direction
    trend_colors = {'increasing': 'green', 'decreasing': 'red', 'no trend': 'gray'}
    fig.add_trace(
        go.Bar(
            x=trends_df['label'],
            y=[1] * len(trends_df),
            marker_color=[trend_colors.get(t, 'gray') for t in trends_df['trend']],
            name='Trend Direction'
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        height=600,
        title_text="Statistical Trend Analysis",
        template="plotly_white",
        showlegend=False
    )
    
    return fig

def get_significance_level(p_value):
    """Get significance level from p-value"""
    if p_value < 0.001:
        return "***"
    elif p_value < 0.01:
        return "**"
    elif p_value < 0.05:
        return "*"
    else:
        return "ns"