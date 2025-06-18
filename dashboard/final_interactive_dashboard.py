"""
Final Interactive Saskatchewan Glacier Albedo Dashboard
======================================================

Version finale qui fonctionne avec toutes les fonctionnalités interactives.
"""

from shiny import App, ui, render, reactive
from shinywidgets import output_widget, render_widget
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
import sys, os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config import MCD43A3_CONFIG, MOD10A1_CONFIG, CLASS_LABELS

# Couleurs fixes pour éviter les erreurs
COLORS = {
    'border': '#ff4444',
    'mixed_low': '#ff8800', 
    'mixed_high': '#ffdd00',
    'mostly_ice': '#88ccff',
    'pure_ice': '#0066cc'
}

# ==========================================
# CSS ACADÉMIQUE
# ==========================================

academic_css = """
.header {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    color: white;
    padding: 20px;
    margin: -15px -15px 20px -15px;
    border-radius: 0 0 10px 10px;
    text-align: center;
}

.panel {
    background: white;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 15px;
    margin: 10px 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.sidebar-panel {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 15px;
}

.metric {
    display: inline-block;
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border: 1px solid #dee2e6;
    border-radius: 6px;
    padding: 12px;
    margin: 5px;
    text-align: center;
    min-width: 120px;
}

.metric-title {
    font-size: 12px;
    color: #666;
    margin-bottom: 5px;
}

.metric-value {
    font-size: 18px;
    font-weight: bold;
    color: #1e3c72;
}

.metric-sub {
    font-size: 10px;
    color: #888;
    margin-top: 3px;
}
"""

# ==========================================
# UI
# ==========================================

app_ui = ui.page_fluid(
    ui.tags.head(ui.tags.style(academic_css)),
    
    ui.div(
        ui.h1("🏔️ Saskatchewan Glacier Albedo Analysis"),
        ui.p("Interactive Dashboard • 15 Years of MODIS Data (2010-2024)"),
        ui.p("Zoom • Pan • Hover • Select • Range Navigation"),
        class_="header"
    ),
    
    ui.layout_sidebar(
        ui.sidebar(
            ui.div(
                ui.h4("📊 Dataset"),
                ui.input_radio_buttons(
                    "dataset",
                    "",
                    choices={
                        "MCD43A3": "🛰️ MCD43A3 (General Albedo)",
                        "MOD10A1": "❄️ MOD10A1 (Snow Albedo)",
                        "COMPARISON": "📈 Compare Both"
                    },
                    selected="MCD43A3"
                ),
                class_="sidebar-panel"
            ),
            
            ui.div(
                ui.h4("🎯 Fractions"),
                ui.input_checkbox_group(
                    "fractions",
                    "",
                    choices={k: v for k, v in CLASS_LABELS.items()},
                    selected=["pure_ice", "mostly_ice"]
                ),
                class_="sidebar-panel"
            ),
            
            ui.div(
                ui.h4("📊 Variable"),
                ui.input_select(
                    "variable",
                    "",
                    choices={"mean": "Mean Albedo", "median": "Median Albedo"},
                    selected="mean"
                ),
                class_="sidebar-panel"
            ),
            
            ui.div(
                ui.h4("📅 Time Period"),
                ui.input_date_range(
                    "date_range",
                    "",
                    start="2010-01-01",
                    end="2024-12-31",
                    min="2010-01-01",
                    max="2024-12-31"
                ),
                ui.input_select(
                    "season",
                    "Season:",
                    choices={
                        "all": "All Seasons",
                        "summer": "Summer (JJA)", 
                        "melt_season": "Melt Season (May-Sep)"
                    },
                    selected="all"
                ),
                class_="sidebar-panel"
            ),
            
            ui.div(
                ui.h4("🔬 Options"),
                ui.input_checkbox("trends", "Show Trends", True),
                ui.input_checkbox("confidence", "Confidence Bands", False),
                ui.input_checkbox("stats", "Show Statistics", True),
                class_="sidebar-panel"
            ),
            
            width=300
        ),
        
        ui.div(
            # Summary
            ui.div(
                ui.h3("📊 Summary"),
                ui.output_ui("summary"),
                class_="panel"
            ),
            
            # Tabs
            ui.navset_tab(
                ui.nav_panel(
                    "📈 Time Series",
                    ui.div(
                        output_widget("timeseries_plot"),
                        class_="panel"
                    ),
                    ui.row(
                        ui.column(6,
                            ui.div(
                                ui.h4("📊 Trend Analysis"),
                                ui.output_table("trends"),
                                class_="panel"
                            )
                        ),
                        ui.column(6,
                            ui.div(
                                ui.h4("📅 Seasonal"),
                                output_widget("seasonal_plot"),
                                class_="panel"
                            )
                        )
                    )
                ),
                
                ui.nav_panel(
                    "📊 Analysis",
                    ui.row(
                        ui.column(6,
                            ui.div(
                                ui.h4("📈 Distributions"),
                                output_widget("dist_plot"),
                                class_="panel"
                            )
                        ),
                        ui.column(6,
                            ui.div(
                                ui.h4("🔗 Correlations"),
                                output_widget("corr_plot"),
                                class_="panel"
                            )
                        )
                    )
                ),
                
                ui.nav_panel(
                    "🔄 Comparison", 
                    ui.div(
                        output_widget("comparison_plot"),
                        class_="panel"
                    )
                )
            )
        )
    )
)

# ==========================================
# SERVER
# ==========================================

def server(input, output, session):
    
    @reactive.Calc
    def load_data():
        """Charger les données selon le dataset sélectionné"""
        dataset = input.dataset()
        
        if dataset == "COMPARISON":
            # Charger les deux datasets
            data = {}
            try:
                mcd = pd.read_csv(MCD43A3_CONFIG['csv_path'])
                mcd['date'] = pd.to_datetime(mcd['date'])
                data['MCD43A3'] = mcd
            except:
                data['MCD43A3'] = None
                
            try:
                mod = pd.read_csv(MOD10A1_CONFIG['csv_path'])
                mod['date'] = pd.to_datetime(mod['date'])
                data['MOD10A1'] = mod
            except:
                data['MOD10A1'] = None
                
            return data
        else:
            # Charger un seul dataset
            try:
                if dataset == "MCD43A3":
                    data = pd.read_csv(MCD43A3_CONFIG['csv_path'])
                else:
                    data = pd.read_csv(MOD10A1_CONFIG['csv_path'])
                
                data['date'] = pd.to_datetime(data['date'])
                return data
            except Exception as e:
                print(f"Erreur chargement {dataset}: {e}")
                return None
    
    @reactive.Calc
    def filtered_data():
        """Filtrer les données selon les paramètres"""
        data = load_data()
        
        if data is None:
            return None
            
        if input.dataset() == "COMPARISON":
            return data  # Retourner le dict tel quel pour comparison
            
        # Filtrer par date
        start_date = pd.to_datetime(input.date_range()[0])
        end_date = pd.to_datetime(input.date_range()[1])
        mask = (data['date'] >= start_date) & (data['date'] <= end_date)
        filtered = data[mask].copy()
        
        # Filtrer par saison
        if input.season() != "all":
            filtered['month'] = filtered['date'].dt.month
            if input.season() == "summer":
                filtered = filtered[filtered['month'].isin([6, 7, 8])]
            elif input.season() == "melt_season":
                filtered = filtered[filtered['month'].isin([5, 6, 7, 8, 9])]
        
        return filtered
    
    @output
    @render.ui
    def summary():
        """Résumé statistique"""
        data = filtered_data()
        
        if data is None or input.dataset() == "COMPARISON":
            return ui.div("Select a dataset for summary")
        
        metrics = []
        for fraction in input.fractions():
            col = f"{fraction}_{input.variable()}"
            if col in data.columns:
                values = data[col].dropna()
                if len(values) > 0:
                    metrics.append(
                        ui.div(
                            ui.div(CLASS_LABELS.get(fraction, fraction), class_="metric-title"),
                            ui.div(f"{values.mean():.3f}", class_="metric-value"),
                            ui.div(f"σ={values.std():.3f} • n={len(values):,}", class_="metric-sub"),
                            class_="metric"
                        )
                    )
        
        return ui.div(*metrics, style="text-align: center;") if metrics else ui.div("No data")
    
    @render_widget
    def timeseries_plot():
        """Graphique temporel interactif principal"""
        data = filtered_data()
        
        if data is None or input.dataset() == "COMPARISON":
            return go.Figure().add_annotation(
                text="Select MCD43A3 or MOD10A1 for time series",
                xref="paper", yref="paper", x=0.5, y=0.5
            )
        
        fig = go.Figure()
        
        # Ajouter chaque fraction
        total_points = 0
        for fraction in input.fractions():
            col = f"{fraction}_{input.variable()}"
            if col in data.columns:
                mask = data[col].notna()
                plot_data = data[mask]
                
                if len(plot_data) == 0:
                    continue
                
                total_points += len(plot_data)
                print(f"📊 Ajout de {fraction}: {len(plot_data)} points")
                
                color = COLORS.get(fraction, '#666666')
                name = CLASS_LABELS.get(fraction, fraction)
                
                # Série principale
                fig.add_trace(go.Scatter(
                    x=plot_data['date'],
                    y=plot_data[col],
                    mode='lines+markers',
                    name=f'{name} ({len(plot_data)} pts)',
                    line=dict(color=color, width=2),
                    marker=dict(size=4, opacity=0.8),
                    hovertemplate=f'<b>{name}</b><br>' +
                                 'Date: %{x}<br>' +
                                 f'{input.variable().title()}: %{{y:.4f}}<br>' +
                                 '<extra></extra>'
                ))
                
                # Ligne de tendance
                if input.trends() and len(plot_data) > 10:
                    try:
                        x_num = (plot_data['date'] - plot_data['date'].min()).dt.days
                        slope, intercept, r_val, p_val, std_err = stats.linregress(x_num, plot_data[col])
                        trend_y = slope * x_num + intercept
                        
                        fig.add_trace(go.Scatter(
                            x=plot_data['date'],
                            y=trend_y,
                            mode='lines',
                            name=f'{name} Trend',
                            line=dict(color=color, width=3, dash='dash'),
                            showlegend=False,
                            hovertemplate=f'<b>{name} Trend</b><br>' +
                                         f'Slope: {slope:.6f}/day<br>' +
                                         f'R²: {r_val**2:.3f}<br>' +
                                         f'p: {p_val:.4f}<br>' +
                                         '<extra></extra>'
                        ))
                    except:
                        pass
        
        # Vérification finale
        print(f"📊 Total points dans le graphique: {total_points}")
        if total_points == 0:
            fig.add_annotation(
                text="⚠️ Aucune donnée à afficher\nVérifiez la sélection des fractions",
                xref="paper", yref="paper", x=0.5, y=0.5,
                font=dict(size=16, color="orange")
            )
            return fig
        
        # Layout avec fonctionnalités interactives
        fig.update_layout(
            title=dict(
                text=f"Interactive Time Series Analysis - {input.dataset()}",
                x=0.5,
                font=dict(size=18)
            ),
            xaxis=dict(
                title="Date",
                showgrid=True,
                gridcolor='rgba(128,128,128,0.2)',
                range=['2010-01-01', '2024-12-31'],  # Forcer la plage correcte
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1Y", step="year", stepmode="backward"),
                        dict(count=5, label="5Y", step="year", stepmode="backward"),
                        dict(count=10, label="10Y", step="year", stepmode="backward"),
                        dict(step="all")
                    ])
                ),
                rangeslider=dict(
                    visible=True,
                    range=['2010-01-01', '2024-12-31']  # Forcer la plage du slider aussi
                ),
                type="date"
            ),
            yaxis=dict(
                title=f"{input.variable().title()} Albedo",
                showgrid=True,
                gridcolor='rgba(128,128,128,0.2)'
            ),
            hovermode='x unified',
            height=600,
            template="plotly_white"
        )
        
        return fig
    
    @render_widget
    def seasonal_plot():
        """Analyse saisonnière"""
        data = filtered_data()
        
        if data is None or input.dataset() == "COMPARISON":
            return go.Figure().add_annotation(
                text="Select dataset for seasonal analysis",
                xref="paper", yref="paper", x=0.5, y=0.5
            )
        
        data['month'] = data['date'].dt.month
        fig = go.Figure()
        
        for fraction in input.fractions():
            col = f"{fraction}_{input.variable()}"
            if col in data.columns:
                monthly = data.groupby('month')[col].mean()
                color = COLORS.get(fraction, '#666666')
                name = CLASS_LABELS.get(fraction, fraction)
                
                fig.add_trace(go.Scatter(
                    x=monthly.index,
                    y=monthly.values,
                    mode='lines+markers',
                    name=name,
                    line=dict(color=color, width=3),
                    marker=dict(size=8)
                ))
        
        fig.update_layout(
            title="Seasonal Patterns",
            xaxis=dict(
                title="Month",
                tickmode='array',
                tickvals=list(range(1, 13)),
                ticktext=['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D']
            ),
            yaxis_title=f"{input.variable().title()} Albedo",
            height=400,
            template="plotly_white"
        )
        
        return fig
    
    @output
    @render.table
    def trends():
        """Table d'analyse des tendances"""
        data = filtered_data()
        
        if data is None or input.dataset() == "COMPARISON":
            return pd.DataFrame()
        
        results = []
        for fraction in input.fractions():
            col = f"{fraction}_{input.variable()}"
            if col in data.columns:
                values = data[col].dropna()
                if len(values) > 2:
                    x = np.arange(len(values))
                    slope, intercept, r_val, p_val, std_err = stats.linregress(x, values)
                    
                    results.append({
                        'Fraction': CLASS_LABELS.get(fraction, fraction),
                        'Slope': f"{slope:.6f}",
                        'R²': f"{r_val**2:.3f}",
                        'P-value': f"{p_val:.4f}",
                        'Significance': '***' if p_val < 0.001 else '**' if p_val < 0.01 else '*' if p_val < 0.05 else 'ns',
                        'N': len(values)
                    })
        
        return pd.DataFrame(results)
    
    @render_widget
    def dist_plot():
        """Graphique de distribution"""
        data = filtered_data()
        
        if data is None or input.dataset() == "COMPARISON":
            return go.Figure().add_annotation(
                text="Select dataset for distribution",
                xref="paper", yref="paper", x=0.5, y=0.5
            )
        
        fig = go.Figure()
        
        for fraction in input.fractions():
            col = f"{fraction}_{input.variable()}"
            if col in data.columns:
                values = data[col].dropna()
                color = COLORS.get(fraction, '#666666')
                name = CLASS_LABELS.get(fraction, fraction)
                
                fig.add_trace(go.Histogram(
                    x=values,
                    name=name,
                    opacity=0.7,
                    marker_color=color,
                    nbinsx=30
                ))
        
        fig.update_layout(
            title="Distribution Analysis",
            xaxis_title=f"{input.variable().title()} Albedo",
            yaxis_title="Frequency",
            barmode='overlay',
            height=400,
            template="plotly_white"
        )
        
        return fig
    
    @render_widget
    def corr_plot():
        """Matrice de corrélation"""
        data = filtered_data()
        
        if data is None or input.dataset() == "COMPARISON":
            return go.Figure().add_annotation(
                text="Select dataset for correlation",
                xref="paper", yref="paper", x=0.5, y=0.5
            )
        
        # Construire matrice de corrélation
        corr_data = []
        labels = []
        
        for fraction in input.fractions():
            col = f"{fraction}_{input.variable()}"
            if col in data.columns:
                corr_data.append(data[col].dropna())
                labels.append(CLASS_LABELS.get(fraction, fraction))
        
        if len(corr_data) < 2:
            return go.Figure().add_annotation(
                text="Select at least 2 fractions",
                xref="paper", yref="paper", x=0.5, y=0.5
            )
        
        # Calculer corrélations
        df_corr = pd.DataFrame(dict(zip(labels, corr_data)))
        corr_matrix = df_corr.corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=np.round(corr_matrix.values, 3),
            texttemplate="%{text}",
            textfont={"size": 12}
        ))
        
        fig.update_layout(
            title="Correlation Matrix",
            height=400,
            template="plotly_white"
        )
        
        return fig
    
    @render_widget
    def comparison_plot():
        """Comparaison des datasets"""
        if input.dataset() != "COMPARISON":
            return go.Figure().add_annotation(
                text="Switch to 'Compare Both' mode",
                xref="paper", yref="paper", x=0.5, y=0.5
            )
        
        data = filtered_data()
        if not data or 'MCD43A3' not in data or 'MOD10A1' not in data:
            return go.Figure().add_annotation(
                text="Both datasets required",
                xref="paper", yref="paper", x=0.5, y=0.5
            )
        
        fig = go.Figure()
        
        mcd = data['MCD43A3']
        mod = data['MOD10A1']
        
        for fraction in input.fractions():
            col = f"{fraction}_{input.variable()}"
            
            if col in mcd.columns and col in mod.columns:
                # Fusionner les données
                merged = pd.merge(
                    mcd[['date', col]].rename(columns={col: 'mcd'}),
                    mod[['date', col]].rename(columns={col: 'mod'}),
                    on='date'
                )
                
                if len(merged) > 0:
                    color = COLORS.get(fraction, '#666666')
                    name = CLASS_LABELS.get(fraction, fraction)
                    corr = merged['mcd'].corr(merged['mod'])
                    
                    fig.add_trace(go.Scatter(
                        x=merged['mcd'],
                        y=merged['mod'],
                        mode='markers',
                        name=f'{name} (r={corr:.3f})',
                        marker=dict(color=color, size=6, opacity=0.7)
                    ))
        
        # Ligne 1:1
        if len(fig.data) > 0:
            all_x = []
            all_y = []
            for trace in fig.data:
                all_x.extend(trace.x)
                all_y.extend(trace.y)
            
            min_val = min(min(all_x), min(all_y))
            max_val = max(max(all_x), max(all_y))
            
            fig.add_trace(go.Scatter(
                x=[min_val, max_val],
                y=[min_val, max_val],
                mode='lines',
                name='1:1 Line',
                line=dict(color='red', dash='dash', width=2)
            ))
        
        fig.update_layout(
            title="Dataset Comparison: MCD43A3 vs MOD10A1",
            xaxis_title="MCD43A3 Albedo",
            yaxis_title="MOD10A1 Albedo", 
            height=500,
            template="plotly_white"
        )
        
        return fig

app = App(app_ui, server)

if __name__ == "__main__":
    print("🚀 Lancement du dashboard interactif final...")
    app.run(host="127.0.0.1", port=8004)