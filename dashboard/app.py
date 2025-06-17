"""
Saskatchewan Glacier Albedo Analysis Dashboard
=============================================

Simple Shiny dashboard for interactive exploration of albedo data.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shiny import App, render, ui, reactive
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from scipy import stats

# Global variables to store data (loaded on demand)
global_data_cache = {}

def transform_elevation_data(df):
    """Transform elevation data from wide format to dashboard-friendly format"""
    elevation_data = []
    
    # Define elevation zones and fraction classes
    elevation_zones = ['above_median', 'at_median', 'below_median']
    fraction_classes = ['mostly_ice', 'pure_ice']
    
    print(f"Transforming elevation data: {len(df)} rows")
    
    for _, row in df.iterrows():
        base_info = {
            'date': row['date'],
            'year': row.get('year', 0),
            'doy': row.get('doy', 0),
            'season': row.get('season', 'unknown'),
            'glacier_median_elevation': row.get('glacier_median_elevation', 2626.75),
            'above_median_threshold': row.get('above_median_threshold', 2726.75),
            'below_median_threshold': row.get('below_median_threshold', 2526.75),
            'dataset': 'MOD10A1_Elevation'
        }
        
        # Create separate rows for each elevation zone and fraction combination
        for zone in elevation_zones:
            for fraction in fraction_classes:
                col_prefix = f"{fraction}_{zone}"
                mean_col = f"{col_prefix}_mean"
                
                if mean_col in df.columns and pd.notna(row.get(mean_col)):
                    elevation_row = base_info.copy()
                    elevation_row.update({
                        'elevation_zone': zone,
                        'fraction_class': fraction,
                        'albedo_mean': row[mean_col],
                        'albedo_median': row.get(f"{col_prefix}_median"),
                        'pixel_count': row.get(f"{col_prefix}_count", 0),
                        'stddev': row.get(f"{col_prefix}_stddev"),
                        'min_value': row.get(f"{col_prefix}_min"),
                        'max_value': row.get(f"{col_prefix}_max"),
                        'data_quality': row.get(f"{col_prefix}_data_quality"),
                        'spatial_fraction': row.get(f"{col_prefix}_spatial_fraction")
                    })
                    elevation_data.append(elevation_row)
    
    result_df = pd.DataFrame(elevation_data)
    print(f"Transformed to {len(result_df)} rows with columns: {result_df.columns.tolist()}")
    return result_df

def load_dashboard_data(dataset_type='MCD43A3'):
    """Load data with proper error handling for dashboard use"""
    global global_data_cache
    
    if dataset_type in global_data_cache:
        return global_data_cache[dataset_type]
    
    try:
        # Import here to avoid circular imports
        from config import MCD43A3_CONFIG, MOD10A1_CONFIG, ELEVATION_CONFIG
        
        # Select dataset configuration
        if dataset_type == 'MOD10A1':
            config = MOD10A1_CONFIG
        elif dataset_type == 'MOD10A1_Elevation':
            config = ELEVATION_CONFIG
        else:
            config = MCD43A3_CONFIG
        
        # Load data with correct path
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        csv_path = os.path.join(project_root, config['csv_path'])
        
        print(f"Loading {dataset_type} data from: {csv_path}")
        
        # Simple CSV loading for dashboard (avoid complex aggregations)
        df = pd.read_csv(csv_path)
        
        # Basic data preparation
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Convert numeric columns and handle mixed types
        for col in df.columns:
            if col.endswith('_mean') or col.endswith('_median') or col.endswith('_pixel_count'):
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Remove rows with invalid dates
        df = df.dropna(subset=['date'])
        
        # Special processing for elevation data
        if dataset_type == 'MOD10A1_Elevation':
            # Transform elevation data into a more dashboard-friendly format
            df = transform_elevation_data(df)
        
        # Add temporal aggregation columns for stacked bar charts
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['year_month'] = df['date'].dt.to_period('M').astype(str)
        df['season'] = df['month'].map({
            6: 'Early Summer', 7: 'Early Summer',
            8: 'Mid Summer', 9: 'Late Summer'
        }).fillna('Other')
        
        # Add dataset type for reference
        df['dataset'] = dataset_type
        df['temporal_resolution'] = config.get('temporal_resolution', 'Unknown')
        
        print(f"✓ {dataset_type} data loaded successfully: {len(df)} rows, {len(df.columns)} columns")
        global_data_cache[dataset_type] = df
        return df
        
    except Exception as e:
        print(f"Error loading {dataset_type} data: {e}")
        # Return empty dataframe with expected structure
        if dataset_type == 'MOD10A1_Elevation':
            empty_df = pd.DataFrame({
                'date': pd.to_datetime([]),
                'elevation_zone': [],
                'fraction_class': [],
                'albedo_mean': [],
                'dataset': [],
                'temporal_resolution': []
            })
        else:
            empty_df = pd.DataFrame({
                'date': pd.to_datetime([]),
                'pure_ice_mean': [],
                'mostly_ice_mean': [],
                'mixed_high_mean': [],
                'mixed_low_mean': [],
                'border_mean': [],
                'dataset': [],
                'temporal_resolution': []
            })
        global_data_cache[dataset_type] = empty_df
        return empty_df

# Load configuration
try:
    from config import FRACTION_CLASSES, CLASS_LABELS, FRACTION_COLORS
except ImportError:
    # Fallback configuration
    FRACTION_CLASSES = ['pure_ice', 'mostly_ice', 'mixed_high', 'mixed_low', 'border']
    CLASS_LABELS = {
        'pure_ice': '90-100% (Pure Ice)',
        'mostly_ice': '75-90% (Mostly Ice)', 
        'mixed_high': '50-75% (Mixed High)',
        'mixed_low': '25-50% (Mixed Low)',
        'border': '0-25% (Border)'
    }
    FRACTION_COLORS = {
        'pure_ice': 'blue',
        'mostly_ice': 'lightblue',
        'mixed_high': 'gold',
        'mixed_low': 'orange',
        'border': 'red'
    }

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h3("Dataset Selection"),
        ui.input_radio_buttons(
            "dataset_type",
            "Choose Dataset:",
            choices={
                "MCD43A3": "General Albedo (16-day composite)",
                "MOD10A1": "Snow Albedo (Daily)",
                "MOD10A1_Elevation": "Snow Albedo by Elevation (Daily)"
            },
            selected="MCD43A3"
        ),
        
        ui.h3("Visualization"),
        ui.output_ui("plot_type_selector"),
        
        ui.input_selectize(
            "fraction_class",
            "Select Fraction Class:",
            choices={fc: CLASS_LABELS[fc] for fc in FRACTION_CLASSES},
            selected="pure_ice"
        ),
        
        ui.output_ui("elevation_controls"),
        
        ui.input_selectize(
            "time_aggregation",
            "Time Aggregation:",
            choices={
                "daily": "Daily",
                "monthly": "Monthly", 
                "seasonal": "Seasonal",
                "yearly": "Yearly"
            },
            selected="daily"
        ),
        
        ui.p("Period: 2010-2024"),
        width=300
    ),
    ui.h1("Saskatchewan Glacier Albedo Analysis Dashboard"),
    ui.p("Interactive exploration of MODIS albedo data (2010-2024)"),
    ui.output_ui("dataset_info"),
    ui.h3("Albedo Visualization"),
    ui.output_ui("main_plot"),
    ui.h4("Data Summary"),
    ui.output_table("data_summary"),
    title="Saskatchewan Glacier Albedo Dashboard"
)

def server(input, output, session):
    
    @reactive.calc
    def current_data():
        """Get current dataset based on selection"""
        try:
            dataset_type = input.dataset_type()
            df = load_dashboard_data(dataset_type)
            return df
        except Exception as e:
            print(f"Error in current_data: {e}")
            dataset_type = input.dataset_type()
            if dataset_type == 'MOD10A1_Elevation':
                return pd.DataFrame({
                    'date': pd.to_datetime([]),
                    'elevation_zone': [],
                    'fraction_class': [],
                    'albedo_mean': []
                })
            else:
                return pd.DataFrame({
                    'date': pd.to_datetime([]),
                    'pure_ice_mean': [],
                    'mostly_ice_mean': [],
                    'mixed_high_mean': [],
                    'mixed_low_mean': [],
                    'border_mean': []
                })
    
    @reactive.calc
    def processed_data():
        """Process data based on time aggregation"""
        try:
            df = current_data()
            time_agg = input.time_aggregation()
            
            if df.empty or time_agg == "daily":
                return df
            
            # Aggregate data for stacked bar charts
            fraction_cols = [f"{fc}_mean" for fc in FRACTION_CLASSES 
                           if f"{fc}_mean" in df.columns]
            
            if time_agg == "monthly":
                agg_data = df.groupby('year_month')[fraction_cols].mean().reset_index()
                agg_data['date'] = pd.to_datetime(agg_data['year_month'])
            elif time_agg == "seasonal":
                agg_data = df.groupby(['year', 'season'])[fraction_cols].mean().reset_index()
                agg_data['date'] = pd.to_datetime(agg_data['year'].astype(str) + '-07-01')
            elif time_agg == "yearly":
                agg_data = df.groupby('year')[fraction_cols].mean().reset_index()
                agg_data['date'] = pd.to_datetime(agg_data['year'].astype(str) + '-07-01')
            else:
                return df
            
            return agg_data
            
        except Exception as e:
            print(f"Error in processed_data: {e}")
            return current_data()
    
    @render.ui
    def plot_type_selector():
        """Dynamic plot type selector based on dataset"""
        dataset_type = input.dataset_type()
        
        if dataset_type == 'MOD10A1_Elevation':
            choices = {
                "line": "Line Plot (Trends)",
                "scatter": "Scatter Plot (All Points)",
                "elevation_comparison": "Elevation Zones Comparison",
                "elevation_trends": "Elevation Trends (Bar Chart)",
                "transient_snowline": "Transient Snowline Analysis"
            }
        else:
            choices = {
                "line": "Line Plot (Trends)",
                "scatter": "Scatter Plot (All Points)",
                "stacked_bar": "Stacked Bar (Fractions)"
            }
        
        return ui.input_selectize(
            "plot_type",
            "Plot Type:",
            choices=choices,
            selected=list(choices.keys())[0]
        )
    
    @render.ui
    def elevation_controls():
        """Show elevation controls only for elevation dataset"""
        dataset_type = input.dataset_type()
        
        if dataset_type == 'MOD10A1_Elevation':
            return ui.div(
                ui.input_selectize(
                    "elevation_zone",
                    "Elevation Zone:",
                    choices={
                        "all": "All Zones",
                        "above_median": "Above Median (>2727m)",
                        "at_median": "At Median (±100m)",
                        "below_median": "Below Median (<2527m)"
                    },
                    selected="all"
                ),
                ui.input_selectize(
                    "elevation_fraction",
                    "Elevation Fraction:",
                    choices={
                        "both": "Both Fractions",
                        "mostly_ice": "Mostly Ice (75-90%)",
                        "pure_ice": "Pure Ice (90-100%)"
                    },
                    selected="pure_ice"
                )
            )
        else:
            return ui.div()
    
    @render.ui
    def dataset_info():
        """Display current dataset information"""
        try:
            df = current_data()
            dataset_type = input.dataset_type()
            
            if df.empty:
                return ui.p("No data available")
            
            # Get dataset configuration info
            try:
                from config import MCD43A3_CONFIG, MOD10A1_CONFIG
                config = MOD10A1_CONFIG if dataset_type == 'MOD10A1' else MCD43A3_CONFIG
                description = f"{config['name']}: {config['description']}"
                resolution = f"Resolution: {config.get('temporal_resolution', 'Unknown')}"
            except:
                description = f"Dataset: {dataset_type}"
                resolution = ""
            
            return ui.div(
                ui.p(f"📊 {description}"),
                ui.p(f"⏱️ {resolution}"),
                ui.p(f"📈 Data points: {len(df):,}")
            )
        except Exception as e:
            return ui.p(f"Error displaying dataset info: {e}")
    
    @render.ui
    def main_plot():
        """Render the main visualization based on plot type"""
        try:
            df = processed_data()
            dataset_type = input.dataset_type()
            
            # Handle plot_type safely
            try:
                plot_type = input.plot_type()
            except:
                plot_type = "line"  # Default fallback
            
            # Handle fraction_class safely
            try:
                fraction = input.fraction_class()
            except:
                fraction = "pure_ice"  # Default fallback
            
            print(f"Creating plot: dataset={dataset_type}, plot_type={plot_type}, fraction={fraction}")
            
            if df.empty:
                return ui.p("No data available for visualization")
            
            # Create different plot types
            if dataset_type == 'MOD10A1_Elevation':
                # Get elevation-specific inputs safely
                try:
                    elevation_zone = input.elevation_zone()
                except:
                    elevation_zone = "all"
                
                try:
                    elevation_fraction = input.elevation_fraction()
                except:
                    elevation_fraction = "pure_ice"
                
                # Elevation-specific plots
                if plot_type == "elevation_comparison":
                    fig = create_elevation_comparison_plot(df, elevation_fraction)
                elif plot_type == "elevation_trends":
                    fig = create_elevation_trends_plot(df)
                elif plot_type == "transient_snowline":
                    fig = create_transient_snowline_plot(df)
                elif plot_type == "scatter":
                    fig = create_elevation_scatter_plot(df, elevation_zone, elevation_fraction)
                else:  # line plot
                    fig = create_elevation_line_plot(df, elevation_zone, elevation_fraction)
            else:
                # Standard plots
                if plot_type == "stacked_bar":
                    fig = create_stacked_bar_plot(df, input.time_aggregation())
                elif plot_type == "scatter":
                    fig = create_scatter_plot(df, fraction, dataset_type)
                else:  # line plot
                    fig = create_line_plot(df, fraction, dataset_type)
            
            if fig is None:
                return ui.p("Unable to create visualization")
            
            return ui.HTML(fig.to_html(include_plotlyjs="cdn"))
            
        except Exception as e:
            print(f"Error in main_plot: {e}")
            import traceback
            traceback.print_exc()
            return ui.p(f"Error creating plot: {str(e)}")

def create_line_plot(df, fraction, dataset_type):
    """Create line plot for trend visualization"""
    mean_col = f"{fraction}_mean"
    
    if mean_col not in df.columns:
        return None
    
    # Remove NaN values for cleaner plot
    plot_data = df[[mean_col, 'date']].dropna()
    
    fig = px.line(
        plot_data,
        x='date',
        y=mean_col,
        title=f"{dataset_type} - Mean Albedo Trend: {CLASS_LABELS.get(fraction, fraction)}",
        labels={
            'date': 'Date',
            mean_col: 'Mean Albedo'
        }
    )
    
    # Update traces with fraction color
    color = FRACTION_COLORS.get(fraction, 'blue')
    fig.update_traces(line_color=color)
    
    fig.update_layout(
        height=500,
        showlegend=False,
        hovermode='x unified'
    )
    
    return fig

def create_scatter_plot(df, fraction, dataset_type):
    """Create scatter plot for all individual observations"""
    mean_col = f"{fraction}_mean"
    
    if mean_col not in df.columns:
        return None
    
    # Remove NaN values for cleaner plot
    plot_data = df[[mean_col, 'date']].dropna()
    
    fig = px.scatter(
        plot_data,
        x='date',
        y=mean_col,
        title=f"{dataset_type} - Daily Albedo Observations: {CLASS_LABELS.get(fraction, fraction)}",
        labels={
            'date': 'Date',
            mean_col: 'Mean Albedo'
        },
        opacity=0.6
    )
    
    # Update traces with fraction color
    color = FRACTION_COLORS.get(fraction, 'blue')
    fig.update_traces(marker_color=color, marker_size=4)
    
    fig.update_layout(
        height=500,
        showlegend=False,
        hovermode='closest'
    )
    
    return fig

def create_stacked_bar_plot(df, time_aggregation):
    """Create stacked bar plot for fraction comparison"""
    fraction_cols = [f"{fc}_mean" for fc in FRACTION_CLASSES 
                    if f"{fc}_mean" in df.columns]
    
    if not fraction_cols:
        return None
    
    # Prepare data for stacking
    plot_data = df[['date'] + fraction_cols].dropna()
    
    if plot_data.empty:
        return None
    
    # Create stacked bar chart
    fig = go.Figure()
    
    for fc in FRACTION_CLASSES:
        mean_col = f"{fc}_mean"
        if mean_col in plot_data.columns:
            # Remove NaN values for this fraction
            valid_data = plot_data[[mean_col, 'date']].dropna()
            
            fig.add_trace(go.Bar(
                name=CLASS_LABELS.get(fc, fc),
                x=valid_data['date'],
                y=valid_data[mean_col],
                marker_color=FRACTION_COLORS.get(fc, 'gray'),
                hovertemplate=f'<b>{CLASS_LABELS.get(fc, fc)}</b><br>' +
                             'Date: %{x}<br>' +
                             'Albedo: %{y:.3f}<extra></extra>'
            ))
    
    fig.update_layout(
        title=f"Stacked Bar Chart - Albedo by Fraction ({time_aggregation.title()})",
        xaxis_title='Date',
        yaxis_title='Mean Albedo',
        barmode='stack',
        height=500,
        hovermode='x unified'
    )
    
    return fig

def create_elevation_line_plot(df, elevation_zone="all", elevation_fraction="pure_ice"):
    """Create line plot for elevation data"""
    try:
        
        # Filter data based on selections
        plot_data = df.copy()
        
        if elevation_zone != "all":
            plot_data = plot_data[plot_data['elevation_zone'] == elevation_zone]
        
        if elevation_fraction != "both":
            plot_data = plot_data[plot_data['fraction_class'] == elevation_fraction]
        
        if plot_data.empty:
            return None
        
        # Determine color column
        color_col = None
        if elevation_zone == "all" and 'elevation_zone' in plot_data.columns:
            color_col = 'elevation_zone'
        elif 'fraction_class' in plot_data.columns:
            color_col = 'fraction_class'
        
        # Create the plot
        fig = px.line(
            plot_data,
            x='date',
            y='albedo_mean',
            color=color_col,
            title=f"Elevation Analysis - Albedo Trends by {elevation_zone.replace('_', ' ').title() if elevation_zone != 'all' else 'All Zones'}",
            labels={
                'date': 'Date',
                'albedo_mean': 'Mean Albedo',
                'elevation_zone': 'Elevation Zone',
                'fraction_class': 'Fraction Class'
            }
        )
        
        fig.update_layout(
            height=500,
            hovermode='x unified'
        )
        
        return fig
        
    except Exception as e:
        print(f"Error in create_elevation_line_plot: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_elevation_comparison_plot(df, elevation_fraction="pure_ice"):
    """Create comparison plot showing all elevation zones"""
    try:
        
        # Filter by fraction if specified
        plot_data = df.copy()
        if elevation_fraction != "both":
            plot_data = plot_data[plot_data['fraction_class'] == elevation_fraction]
        
        if plot_data.empty:
            return None
        
        # Create separate line for each elevation zone
        fig = px.line(
            plot_data,
            x='date',
            y='albedo_mean',
            color='elevation_zone',
            facet_col='fraction_class' if elevation_fraction == "both" else None,
            title="Elevation Zones Comparison - Saskatchewan Glacier Albedo Trends",
            labels={
                'date': 'Date',
                'albedo_mean': 'Mean Albedo',
                'elevation_zone': 'Elevation Zone'
            },
            color_discrete_map={
                'above_median': 'red',
                'at_median': 'orange', 
                'below_median': 'green'
            }
        )
        
        fig.update_layout(
            height=500,
            hovermode='x unified'
        )
        
        return fig
        
    except Exception as e:
        print(f"Error in create_elevation_comparison_plot: {e}")
        return None

def create_elevation_trends_plot(df):
    """Create bar chart showing elevation trends"""
    try:
        # Calculate trends for each elevation zone and fraction
        trends_data = []
        
        for zone in ['above_median', 'at_median', 'below_median']:
            for fraction in ['mostly_ice', 'pure_ice']:
                zone_data = df[(df['elevation_zone'] == zone) & (df['fraction_class'] == fraction)]
                
                if len(zone_data) > 10:  # Need sufficient data for trend
                    # Simple linear regression for trend
                    x = np.arange(len(zone_data))
                    y = zone_data['albedo_mean'].values
                    
                    # Remove NaN values
                    valid_mask = ~np.isnan(y)
                    if np.sum(valid_mask) > 5:
                        x_valid = x[valid_mask]
                        y_valid = y[valid_mask]
                        
                        slope, intercept, r_value, p_value, std_err = stats.linregress(x_valid, y_valid)
                        
                        # Convert slope to yearly trend (approximate)
                        yearly_slope = slope * 365.25 / len(zone_data) * (zone_data['date'].max() - zone_data['date'].min()).days
                        
                        trends_data.append({
                            'elevation_zone': zone.replace('_', ' ').title(),
                            'fraction_class': fraction.replace('_', ' ').title(),
                            'trend_slope': yearly_slope,
                            'r_squared': r_value**2,
                            'p_value': p_value,
                            'zone_fraction': f"{zone} - {fraction}"
                        })
        
        if not trends_data:
            return None
        
        trends_df = pd.DataFrame(trends_data)
        
        fig = px.bar(
            trends_df,
            x='zone_fraction',
            y='trend_slope',
            color='elevation_zone',
            title="Elevation Trends Analysis - Sen's Slope per Zone",
            labels={
                'zone_fraction': 'Zone - Fraction',
                'trend_slope': 'Trend Slope (per year)',
                'elevation_zone': 'Elevation Zone'
            },
            color_discrete_map={
                'Above Median': 'red',
                'At Median': 'orange',
                'Below Median': 'green'
            }
        )
        
        fig.update_layout(
            height=500,
            xaxis_tickangle=-45
        )
        
        return fig
        
    except Exception as e:
        print(f"Error in create_elevation_trends_plot: {e}")
        return None

def create_transient_snowline_plot(df):
    """Create plot testing transient snowline hypothesis"""
    try:
        # Calculate mean albedo by elevation zone
        zone_means = df.groupby(['elevation_zone', 'fraction_class'])['albedo_mean'].agg(['mean', 'std', 'count']).reset_index()
        
        # Create scatter plot
        fig = px.scatter(
            zone_means,
            x='elevation_zone',
            y='mean',
            color='fraction_class',
            size='count',
            error_y='std',
            title="Transient Snowline Analysis - Mean Albedo by Elevation Zone",
            labels={
                'elevation_zone': 'Elevation Zone',
                'mean': 'Mean Albedo',
                'fraction_class': 'Fraction Class',
                'count': 'Number of Observations'
            }
        )
        
        # Add annotation about the hypothesis
        fig.add_annotation(
            text="Hypothesis: Strongest albedo decline expected at median elevation<br>(transient snowline zone)",
            x=1, y=0.95,
            xref="paper", yref="paper",
            showarrow=False,
            font=dict(size=12),
            bgcolor="lightgray",
            bordercolor="black",
            borderwidth=1
        )
        
        fig.update_layout(
            height=500,
            showlegend=True
        )
        
        return fig
        
    except Exception as e:
        print(f"Error in create_transient_snowline_plot: {e}")
        return None

def create_elevation_scatter_plot(df, elevation_zone="all", elevation_fraction="pure_ice"):
    """Create scatter plot for elevation data"""
    try:
        
        # Filter data
        plot_data = df.copy()
        
        if elevation_zone != "all":
            plot_data = plot_data[plot_data['elevation_zone'] == elevation_zone]
        
        if elevation_fraction != "both":
            plot_data = plot_data[plot_data['fraction_class'] == elevation_fraction]
        
        if plot_data.empty:
            return None
        
        # Determine color column
        color_col = None
        if elevation_zone == "all" and 'elevation_zone' in plot_data.columns:
            color_col = 'elevation_zone'
        elif 'fraction_class' in plot_data.columns:
            color_col = 'fraction_class'
        
        fig = px.scatter(
            plot_data,
            x='date',
            y='albedo_mean',
            color=color_col,
            title=f"Elevation Scatter Plot - Daily Observations",
            labels={
                'date': 'Date',
                'albedo_mean': 'Mean Albedo'
            },
            opacity=0.6
        )
        
        fig.update_layout(
            height=500,
            hovermode='closest'
        )
        
        return fig
        
    except Exception as e:
        print(f"Error in create_elevation_scatter_plot: {e}")
        import traceback
        traceback.print_exc()
        return None

    @render.table
    def data_summary():
        """Render summary statistics table"""
        try:
            df = current_data()
            fraction = input.fraction_class()
            plot_type = input.plot_type()
            dataset_type = input.dataset_type()
            
            if df.empty:
                return pd.DataFrame({
                    "Statistic": ["Error"], 
                    "Value": ["No data available"]
                })
            
            # Special handling for elevation data
            if dataset_type == 'MOD10A1_Elevation':
                # Show elevation-specific statistics
                if 'elevation_zone' in df.columns and 'fraction_class' in df.columns:
                    stats_list = []
                    
                    for zone in ['above_median', 'at_median', 'below_median']:
                        for fraction in ['mostly_ice', 'pure_ice']:
                            zone_data = df[(df['elevation_zone'] == zone) & (df['fraction_class'] == fraction)]
                            if len(zone_data) > 0 and 'albedo_mean' in zone_data.columns:
                                series = zone_data['albedo_mean'].dropna()
                                if len(series) > 0:
                                    stats_list.append({
                                        'Zone': zone.replace('_', ' ').title(),
                                        'Fraction': fraction.replace('_', ' ').title(),
                                        'Count': f"{len(series):.0f}",
                                        'Mean': f"{series.mean():.4f}",
                                        'Std': f"{series.std():.4f}",
                                        'Min': f"{series.min():.4f}",
                                        'Max': f"{series.max():.4f}"
                                    })
                    
                    if stats_list:
                        return pd.DataFrame(stats_list)
                    else:
                        return pd.DataFrame({"Error": ["No valid elevation data"]})
                else:
                    return pd.DataFrame({"Error": ["Invalid elevation data structure"]})
            
            # For stacked bar, show all fractions
            if plot_type == "stacked_bar":
                stats_list = []
                for fc in FRACTION_CLASSES:
                    mean_col = f"{fc}_mean"
                    if mean_col in df.columns:
                        series = df[mean_col].dropna()
                        if len(series) > 0:
                            stats_list.append({
                                'Fraction': CLASS_LABELS.get(fc, fc),
                                'Count': f"{len(series):.0f}",
                                'Mean': f"{series.mean():.4f}",
                                'Std': f"{series.std():.4f}",
                                'Min': f"{series.min():.4f}",
                                'Max': f"{series.max():.4f}"
                            })
                
                if stats_list:
                    return pd.DataFrame(stats_list)
                else:
                    return pd.DataFrame({"Error": ["No valid data for any fraction"]})
            
            # For single fraction plots
            mean_col = f"{fraction}_mean"
            
            if mean_col not in df.columns:
                return pd.DataFrame({
                    "Statistic": ["Error"], 
                    "Value": [f"No data available for {CLASS_LABELS.get(fraction, fraction)}"]
                })
            
            # Calculate summary statistics with error handling
            series = df[mean_col].dropna()
            if len(series) == 0:
                return pd.DataFrame({
                    "Statistic": ["Error"], 
                    "Value": ["No valid data points"]
                })
            
            stats = series.describe()
            summary_df = pd.DataFrame({
                'Statistic': ['Dataset', 'Fraction', 'Count', 'Mean', 'Std Dev', 'Min', '25%', '50%', '75%', 'Max'],
                'Value': [
                    dataset_type,
                    CLASS_LABELS.get(fraction, fraction),
                    f"{stats['count']:.0f}",
                    f"{stats['mean']:.4f}" if pd.notna(stats['mean']) else "N/A",
                    f"{stats['std']:.4f}" if pd.notna(stats['std']) else "N/A",
                    f"{stats['min']:.4f}" if pd.notna(stats['min']) else "N/A",
                    f"{stats['25%']:.4f}" if pd.notna(stats['25%']) else "N/A",
                    f"{stats['50%']:.4f}" if pd.notna(stats['50%']) else "N/A",
                    f"{stats['75%']:.4f}" if pd.notna(stats['75%']) else "N/A",
                    f"{stats['max']:.4f}" if pd.notna(stats['max']) else "N/A"
                ]
            })
            
            return summary_df
            
        except Exception as e:
            print(f"Error in data_summary: {e}")
            return pd.DataFrame({
                "Statistic": ["Error"], 
                "Value": [f"Error calculating summary: {str(e)}"]
            })

app = App(app_ui, server)

if __name__ == "__main__":
    app.run()