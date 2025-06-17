"""
Streamlit Plot Generators
=========================

Functions to generate Plotly plots optimized for Streamlit display.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import streamlit as st
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import CLASS_LABELS, FRACTION_COLORS


def create_time_series_plot(
    data_dict: Dict[str, Any],
    fractions: List[str],
    title: str = "Albedo Time Series",
    show_trends: bool = False,
    show_confidence: bool = False,
    height: int = 600
) -> go.Figure:
    """
    Create an interactive time series plot.
    
    Parameters:
    -----------
    data_dict : dict
        Dictionary with dataset names as keys and AlbedoDataHandler objects as values
    fractions : list
        List of fraction classes to plot
    title : str
        Plot title
    show_trends : bool
        Whether to show trend lines
    show_confidence : bool
        Whether to show confidence intervals
    height : int
        Plot height in pixels
    
    Returns:
    --------
    plotly.graph_objects.Figure
        Interactive time series plot
    """
    fig = go.Figure()
    
    for dataset_name, data_handler in data_dict.items():
        for fraction in fractions:
            col_name = f"{fraction}_mean"
            
            if col_name in data_handler.data.columns:
                # Main time series line
                line_style = 'solid' if dataset_name == 'MCD43A3' else 'dash'
                color = FRACTION_COLORS.get(fraction, '#000000')
                
                fig.add_trace(go.Scatter(
                    x=data_handler.data['date'],
                    y=data_handler.data[col_name],
                    mode='lines',
                    name=f"{dataset_name} - {CLASS_LABELS[fraction]}",
                    line=dict(color=color, width=2, dash=line_style),
                    opacity=0.8,
                    hovertemplate=f"<b>{dataset_name} - {CLASS_LABELS[fraction]}</b><br>" +
                                  "Date: %{x}<br>" +
                                  "Albedo: %{y:.4f}<extra></extra>"
                ))
                
                # Add confidence intervals if requested
                if show_confidence and f"{fraction}_std" in data_handler.data.columns:
                    std_col = f"{fraction}_std"
                    upper = data_handler.data[col_name] + data_handler.data[std_col]
                    lower = data_handler.data[col_name] - data_handler.data[std_col]
                    
                    # Upper bound (invisible)
                    fig.add_trace(go.Scatter(
                        x=data_handler.data['date'],
                        y=upper,
                        mode='lines',
                        line=dict(width=0),
                        showlegend=False,
                        hoverinfo='skip'
                    ))
                    
                    # Lower bound with fill
                    fig.add_trace(go.Scatter(
                        x=data_handler.data['date'],
                        y=lower,
                        mode='lines',
                        line=dict(width=0),
                        fill='tonexty',
                        fillcolor=f'rgba{tuple(list(px.colors.hex_to_rgb(color)) + [0.2])}',
                        showlegend=False,
                        hoverinfo='skip'
                    ))
                
                # Add trend line if requested
                if show_trends:
                    try:
                        from analysis.trends import TrendCalculator
                        trend_calc = TrendCalculator(data_handler)
                        trends = trend_calc.calculate_basic_trends(fraction)
                        
                        if trends and 'slope' in trends and 'intercept' in trends:
                            # Create trend line
                            x_numeric = pd.to_numeric(data_handler.data['date']).values
                            x_normalized = (x_numeric - x_numeric.min()) / (365.25 * 24 * 3600 * 1e9)
                            trend_line = trends['intercept'] + trends['slope'] * x_normalized
                            
                            fig.add_trace(go.Scatter(
                                x=data_handler.data['date'],
                                y=trend_line,
                                mode='lines',
                                name=f"{dataset_name} - {CLASS_LABELS[fraction]} Trend",
                                line=dict(color=color, width=1.5, dash='dot'),
                                opacity=0.7,
                                hovertemplate=f"<b>Trend Line</b><br>Slope: {trends['slope']:.6f}/year<extra></extra>"
                            ))
                    except Exception:
                        pass  # Skip trend if calculation fails
    
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Albedo",
        height=height,
        hovermode='x unified',
        template="plotly_white",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig


def create_correlation_matrix(
    data_handler: Any,
    fractions: List[str],
    title: str = "Fraction Correlation Matrix"
) -> go.Figure:
    """
    Create a correlation matrix heatmap.
    
    Parameters:
    -----------
    data_handler : AlbedoDataHandler
        Data handler object
    fractions : list
        List of fraction classes
    title : str
        Plot title
    
    Returns:
    --------
    plotly.graph_objects.Figure
        Correlation matrix heatmap
    """
    # Prepare data
    fraction_cols = [f"{f}_mean" for f in fractions if f"{f}_mean" in data_handler.data.columns]
    
    if len(fraction_cols) < 2:
        # Create empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="Need at least 2 fraction classes for correlation matrix",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font_size=16
        )
        fig.update_layout(
            title=title,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            height=400
        )
        return fig
    
    # Calculate correlation matrix
    corr_matrix = data_handler.data[fraction_cols].corr()
    
    # Create display labels
    display_labels = [CLASS_LABELS[col.replace('_mean', '')] for col in fraction_cols]
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=display_labels,
        y=display_labels,
        colorscale='RdBu_r',
        zmid=0,
        zmin=-1,
        zmax=1,
        text=np.round(corr_matrix.values, 3),
        texttemplate="%{text}",
        textfont={"size": 12},
        hovertemplate="<b>%{x} vs %{y}</b><br>Correlation: %{z:.3f}<extra></extra>"
    ))
    
    fig.update_layout(
        title=title,
        width=500,
        height=500,
        template="plotly_white"
    )
    
    return fig


def create_seasonal_comparison(
    data_dict: Dict[str, Any],
    fraction: str,
    title: str = "Seasonal Patterns Comparison"
) -> go.Figure:
    """
    Create seasonal pattern comparison plot.
    
    Parameters:
    -----------
    data_dict : dict
        Dictionary with dataset names as keys and AlbedoDataHandler objects as values
    fraction : str
        Fraction class to analyze
    title : str
        Plot title
    
    Returns:
    --------
    plotly.graph_objects.Figure
        Seasonal comparison plot
    """
    fig = go.Figure()
    
    for dataset_name, data_handler in data_dict.items():
        col_name = f"{fraction}_mean"
        
        if col_name in data_handler.data.columns:
            # Calculate monthly statistics
            data = data_handler.data[['date', col_name]].dropna()
            data['month'] = data['date'].dt.month
            monthly_stats = data.groupby('month')[col_name].agg(['mean', 'std']).reset_index()
            
            color = 'blue' if dataset_name == 'MCD43A3' else 'red'
            
            fig.add_trace(go.Scatter(
                x=monthly_stats['month'],
                y=monthly_stats['mean'],
                mode='lines+markers',
                name=dataset_name,
                line=dict(color=color, width=2),
                marker=dict(size=8),
                error_y=dict(
                    type='data',
                    array=monthly_stats['std'],
                    visible=True,
                    color=color
                ),
                hovertemplate=f"<b>{dataset_name}</b><br>" +
                              "Month: %{x}<br>" +
                              "Mean Albedo: %{y:.4f}<br>" +
                              "Std Dev: %{error_y.array:.4f}<extra></extra>"
            ))
    
    fig.update_layout(
        title=f"{title} - {CLASS_LABELS[fraction]}",
        xaxis=dict(
            title="Month",
            tickmode='array',
            tickvals=list(range(1, 13)),
            ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        ),
        yaxis_title="Mean Albedo",
        height=400,
        template="plotly_white",
        hovermode='x unified'
    )
    
    return fig


def create_scatter_plot(
    data_dict: Dict[str, Any],
    fraction: str,
    x_dataset: str,
    y_dataset: str,
    show_regression: bool = True,
    title: str = "Dataset Comparison"
) -> go.Figure:
    """
    Create scatter plot comparing two datasets.
    
    Parameters:
    -----------
    data_dict : dict
        Dictionary with dataset names as keys
    fraction : str
        Fraction class to compare
    x_dataset : str
        Dataset name for x-axis
    y_dataset : str
        Dataset name for y-axis
    show_regression : bool
        Whether to show regression line
    title : str
        Plot title
    
    Returns:
    --------
    plotly.graph_objects.Figure
        Scatter plot
    """
    if x_dataset not in data_dict or y_dataset not in data_dict:
        # Return empty figure with error message
        fig = go.Figure()
        fig.add_annotation(
            text=f"Missing data for {x_dataset} or {y_dataset}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font_size=16
        )
        return fig
    
    # Align datasets by date
    x_data = data_dict[x_dataset].data[['date', f"{fraction}_mean"]].dropna()
    y_data = data_dict[y_dataset].data[['date', f"{fraction}_mean"]].dropna()
    
    # Merge on date
    merged = pd.merge(x_data, y_data, on='date', suffixes=('_x', '_y'))
    
    if len(merged) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="No overlapping data points found",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font_size=16
        )
        return fig
    
    fig = go.Figure()
    
    # Add scatter points
    fig.add_trace(go.Scatter(
        x=merged[f"{fraction}_mean_x"],
        y=merged[f"{fraction}_mean_y"],
        mode='markers',
        name='Data points',
        marker=dict(
            size=6,
            color=merged.index,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Time Index"),
            opacity=0.7
        ),
        hovertemplate=f"<b>{CLASS_LABELS[fraction]}</b><br>" +
                      f"{x_dataset}: %{{x:.4f}}<br>" +
                      f"{y_dataset}: %{{y:.4f}}<br>" +
                      "Date: %{customdata}<extra></extra>",
        customdata=merged['date']
    ))
    
    # Add regression line if requested
    if show_regression and len(merged) > 2:
        from scipy import stats
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            merged[f"{fraction}_mean_x"], merged[f"{fraction}_mean_y"]
        )
        
        # Create regression line
        x_range = np.linspace(merged[f"{fraction}_mean_x"].min(), 
                             merged[f"{fraction}_mean_x"].max(), 100)
        y_pred = slope * x_range + intercept
        
        fig.add_trace(go.Scatter(
            x=x_range,
            y=y_pred,
            mode='lines',
            name=f'Regression (R²={r_value**2:.3f})',
            line=dict(color='red', width=2, dash='dash'),
            hovertemplate=f"<b>Regression Line</b><br>" +
                          f"R²: {r_value**2:.3f}<br>" +
                          f"p-value: {p_value:.4f}<extra></extra>"
        ))
    
    # Add 1:1 line
    min_val = min(merged[f"{fraction}_mean_x"].min(), merged[f"{fraction}_mean_y"].min())
    max_val = max(merged[f"{fraction}_mean_x"].max(), merged[f"{fraction}_mean_y"].max())
    
    fig.add_trace(go.Scatter(
        x=[min_val, max_val],
        y=[min_val, max_val],
        mode='lines',
        name='1:1 Line',
        line=dict(color='gray', width=1, dash='dot'),
        hoverinfo='skip'
    ))
    
    fig.update_layout(
        title=f"{title} - {CLASS_LABELS[fraction]}",
        xaxis_title=f"{x_dataset} Albedo",
        yaxis_title=f"{y_dataset} Albedo",
        height=500,
        template="plotly_white"
    )
    
    return fig


def create_elevation_profile(
    data: pd.DataFrame,
    fraction: str,
    elevation_bands: List[str],
    title: str = "Elevation Profile"
) -> go.Figure:
    """
    Create elevation profile plot.
    
    Parameters:
    -----------
    data : pd.DataFrame
        Elevation data
    fraction : str
        Fraction class
    elevation_bands : list
        List of elevation band identifiers
    title : str
        Plot title
    
    Returns:
    --------
    plotly.graph_objects.Figure
        Elevation profile plot
    """
    fig = go.Figure()
    
    # This would need to be implemented based on your elevation data structure
    # For now, create a placeholder
    fig.add_annotation(
        text="Elevation profile functionality to be implemented",
        xref="paper", yref="paper",
        x=0.5, y=0.5, xanchor='center', yanchor='middle',
        showarrow=False, font_size=16
    )
    
    fig.update_layout(
        title=title,
        height=400,
        template="plotly_white"
    )
    
    return fig


def create_trend_summary_plot(
    trend_results: List[Dict],
    title: str = "Trend Summary"
) -> go.Figure:
    """
    Create trend summary bar plot.
    
    Parameters:
    -----------
    trend_results : list
        List of trend analysis results
    title : str
        Plot title
    
    Returns:
    --------
    plotly.graph_objects.Figure
        Trend summary plot
    """
    if not trend_results:
        fig = go.Figure()
        fig.add_annotation(
            text="No trend results available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font_size=16
        )
        return fig
    
    # Convert to DataFrame for easier handling
    df = pd.DataFrame(trend_results)
    
    # Determine colors based on significance and trend direction
    colors = []
    for _, row in df.iterrows():
        if row.get('p_value', 1) < 0.05:  # Significant
            colors.append('green' if row.get('slope', 0) > 0 else 'red')
        else:  # Not significant
            colors.append('lightgray')
    
    fig = go.Figure(data=[
        go.Bar(
            x=df['fraction'] if 'fraction' in df.columns else df.index,
            y=df['slope'] if 'slope' in df.columns else [0] * len(df),
            marker_color=colors,
            text=[f"p={row.get('p_value', 'N/A'):.3f}" if isinstance(row.get('p_value'), (int, float)) else "N/A" 
                  for _, row in df.iterrows()],
            textposition='outside',
            hovertemplate="<b>%{x}</b><br>" +
                         "Slope: %{y:.6f}/year<br>" +
                         "P-value: %{text}<extra></extra>"
        )
    ])
    
    # Add horizontal line at y=0
    fig.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.5)
    
    fig.update_layout(
        title=title,
        xaxis_title="Fraction Class",
        yaxis_title="Trend (per year)",
        height=400,
        template="plotly_white"
    )
    
    return fig


def create_distribution_plot(
    data_dict: Dict[str, Any],
    fractions: List[str],
    plot_type: str = "histogram",
    title: str = "Albedo Distribution"
) -> go.Figure:
    """
    Create distribution plot (histogram or box plot).
    
    Parameters:
    -----------
    data_dict : dict
        Dictionary with dataset names as keys
    fractions : list
        List of fraction classes
    plot_type : str
        Type of plot ('histogram' or 'box')
    title : str
        Plot title
    
    Returns:
    --------
    plotly.graph_objects.Figure
        Distribution plot
    """
    if plot_type == "histogram":
        fig = go.Figure()
        
        for dataset_name, data_handler in data_dict.items():
            for fraction in fractions:
                col_name = f"{fraction}_mean"
                if col_name in data_handler.data.columns:
                    data = data_handler.data[col_name].dropna()
                    
                    fig.add_trace(go.Histogram(
                        x=data,
                        name=f"{dataset_name} - {CLASS_LABELS[fraction]}",
                        opacity=0.7,
                        nbinsx=50,
                        hovertemplate="<b>%{fullData.name}</b><br>" +
                                     "Albedo: %{x}<br>" +
                                     "Count: %{y}<extra></extra>"
                    ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Albedo",
            yaxis_title="Frequency",
            barmode='overlay',
            height=400,
            template="plotly_white"
        )
    
    else:  # box plot
        fig = go.Figure()
        
        for dataset_name, data_handler in data_dict.items():
            for fraction in fractions:
                col_name = f"{fraction}_mean"
                if col_name in data_handler.data.columns:
                    data = data_handler.data[col_name].dropna()
                    
                    fig.add_trace(go.Box(
                        y=data,
                        name=f"{dataset_name} - {CLASS_LABELS[fraction]}",
                        boxpoints='outliers',
                        hovertemplate="<b>%{fullData.name}</b><br>" +
                                     "Q1: %{q1}<br>" +
                                     "Median: %{median}<br>" +
                                     "Q3: %{q3}<br>" +
                                     "Value: %{y}<extra></extra>"
                    ))
        
        fig.update_layout(
            title=title,
            yaxis_title="Albedo",
            height=400,
            template="plotly_white"
        )
    
    return fig