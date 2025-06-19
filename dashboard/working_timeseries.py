"""
Version avec time series qui fonctionne vraiment
===============================================

Cette version force l'affichage correct du graphique temporel.
"""

from shiny import App, ui, render, reactive
from shinywidgets import output_widget, render_widget
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
import sys, os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config import MCD43A3_CONFIG, MOD10A1_CONFIG, CLASS_LABELS

# Couleurs fixes et visibles
COLORS = {
    'border': '#FF4444',
    'mixed_low': '#FF8800', 
    'mixed_high': '#FFDD00',
    'mostly_ice': '#4488FF',
    'pure_ice': '#0066CC'
}

app_ui = ui.page_fluid(
    ui.div(
        ui.h1("🏔️ Saskatchewan Glacier - Time Series Working"),
        ui.p("Version qui fonctionne pour les graphiques temporels"),
        style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; padding: 20px; margin: -15px -15px 20px -15px; text-align: center;"
    ),
    
    ui.layout_sidebar(
        ui.sidebar(
            ui.div(
                ui.h4("📊 Dataset"),
                ui.input_radio_buttons(
                    "dataset",
                    "",
                    choices={
                        "MCD43A3": "🛰️ MCD43A3",
                        "MOD10A1": "❄️ MOD10A1"
                    },
                    selected="MOD10A1"
                ),
                style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px;"
            ),
            
            ui.div(
                ui.h4("🎯 Fractions"),
                ui.input_checkbox_group(
                    "fractions",
                    "",
                    choices={k: v for k, v in CLASS_LABELS.items()},
                    selected=["mostly_ice", "pure_ice"]
                ),
                style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px;"
            ),
            
            ui.div(
                ui.h4("📊 Variable"),
                ui.input_select(
                    "variable",
                    "",
                    choices={"mean": "Mean", "median": "Median"},
                    selected="mean"
                ),
                style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px;"
            ),
            
            ui.div(
                ui.h4("🔬 Options"),
                ui.input_checkbox("trends", "Show Trends", True),
                ui.input_checkbox("points", "Show Points", True),
                style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px;"
            ),
            
            width=280
        ),
        
        ui.div(
            # Status
            ui.div(
                ui.h3("📊 Status"),
                ui.output_text_verbatim("status_info"),
                style="background: white; border: 2px solid #e8e9ea; border-radius: 8px; padding: 15px; margin-bottom: 15px;"
            ),
            
            # Main time series plot
            ui.div(
                ui.h3("📈 Interactive Time Series"),
                output_widget("main_timeseries"),
                style="background: white; border: 2px solid #e8e9ea; border-radius: 8px; padding: 15px; margin-bottom: 15px;"
            ),
            
            # Alternative simple plot
            ui.div(
                ui.h3("📉 Simple Plot (Backup)"),
                output_widget("simple_plot"),
                style="background: white; border: 2px solid #e8e9ea; border-radius: 8px; padding: 15px; margin-bottom: 15px;"
            )
        )
    )
)

def server(input, output, session):
    
    @reactive.Calc
    def load_data():
        """Charger les données"""
        dataset = input.dataset()
        
        try:
            if dataset == "MCD43A3":
                data = pd.read_csv(MCD43A3_CONFIG['csv_path'])
            else:
                data = pd.read_csv(MOD10A1_CONFIG['csv_path'])
            
            data['date'] = pd.to_datetime(data['date'])
            print(f"✅ Chargé {dataset}: {len(data)} lignes")
            return data
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return None
    
    @output
    @render.text
    def status_info():
        """Informations de statut"""
        data = load_data()
        
        if data is None:
            return "❌ Erreur de chargement des données"
        
        info = []
        info.append(f"✅ Dataset: {input.dataset()}")
        info.append(f"✅ Total lignes: {len(data):,}")
        info.append(f"✅ Période: {data['date'].min().strftime('%Y-%m-%d')} à {data['date'].max().strftime('%Y-%m-%d')}")
        info.append(f"✅ Fractions sélectionnées: {', '.join(input.fractions())}")
        
        total_points = 0
        info.append("\n📊 Points de données:")
        for fraction in input.fractions():
            col = f"{fraction}_{input.variable()}"
            if col in data.columns:
                non_null = data[col].notna().sum()
                total_points += non_null
                info.append(f"  • {fraction}: {non_null:,} points")
        
        info.append(f"\n🎯 Total à afficher: {total_points:,} points")
        
        if total_points == 0:
            info.append("\n⚠️ ATTENTION: Aucun point à afficher!")
        else:
            info.append("\n✅ Graphique devrait être visible")
        
        return "\n".join(info)
    
    @render_widget
    def main_timeseries():
        """Graphique temporel principal avec toutes les fonctionnalités"""
        data = load_data()
        
        if data is None:
            fig = go.Figure()
            fig.add_annotation(
                text="❌ Erreur de chargement des données",
                xref="paper", yref="paper", x=0.5, y=0.5,
                font=dict(size=20, color="red")
            )
            return fig
        
        fig = go.Figure()
        total_points = 0
        
        for i, fraction in enumerate(input.fractions()):
            col = f"{fraction}_{input.variable()}"
            if col in data.columns:
                mask = data[col].notna()
                plot_data = data[mask].copy()
                
                if len(plot_data) == 0:
                    continue
                
                total_points += len(plot_data)
                color = COLORS.get(fraction, f'hsl({i * 60}, 70%, 50%)')
                name = CLASS_LABELS.get(fraction, fraction)
                
                # Mode d'affichage
                mode = 'lines+markers' if input.points() else 'lines'
                marker_size = 4 if input.points() else 0
                
                # Série principale - FORCER L'AFFICHAGE
                fig.add_trace(go.Scatter(
                    x=plot_data['date'],
                    y=plot_data[col],
                    mode=mode,
                    name=f'{name} ({len(plot_data)} pts)',
                    line=dict(color=color, width=3),
                    marker=dict(size=marker_size, opacity=0.8, color=color),
                    visible=True,  # FORCER LA VISIBILITÉ
                    hovertemplate=f'<b>{name}</b><br>' +
                                 'Date: %{x}<br>' +
                                 f'{input.variable().title()}: %{{y:.4f}}<br>' +
                                 '<extra></extra>'
                ))
                
                print(f"📊 Ajouté {fraction}: {len(plot_data)} points, couleur {color}")
                
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
                            name=f'{name} Trend (R²={r_val**2:.3f})',
                            line=dict(color=color, width=2, dash='dash'),
                            visible=True,  # FORCER LA VISIBILITÉ
                            hovertemplate=f'<b>{name} Trend</b><br>' +
                                         f'Slope: {slope:.6f}/day<br>' +
                                         f'R²: {r_val**2:.3f}<br>' +
                                         f'p: {p_val:.4f}<br>' +
                                         '<extra></extra>'
                        ))
                        print(f"📈 Ajouté tendance pour {fraction}")
                    except Exception as e:
                        print(f"⚠️ Erreur tendance {fraction}: {e}")
        
        print(f"📊 TOTAL FINAL: {total_points} points dans {len(fig.data)} traces")
        
        if total_points == 0:
            fig.add_annotation(
                text="⚠️ Aucune donnée à afficher\nVérifiez la sélection des fractions",
                xref="paper", yref="paper", x=0.5, y=0.5,
                font=dict(size=16, color="orange")
            )
        else:
            # Configuration complète du layout
            fig.update_layout(
                title=dict(
                    text=f"Time Series Analysis - {input.dataset()} - {total_points} points",
                    x=0.5,
                    font=dict(size=18, color="#1e3c72")
                ),
                xaxis=dict(
                    title="Date",
                    showgrid=True,
                    gridcolor='rgba(128,128,128,0.2)',
                    autorange=True,  # Laisser auto-range d'abord
                    type="date",
                    rangeselector=dict(
                        buttons=list([
                            dict(count=1, label="1Y", step="year", stepmode="backward"),
                            dict(count=5, label="5Y", step="year", stepmode="backward"),
                            dict(count=10, label="10Y", step="year", stepmode="backward"),
                            dict(step="all")
                        ]),
                        font=dict(size=10)
                    ),
                    rangeslider=dict(visible=True)
                ),
                yaxis=dict(
                    title=f"{input.variable().title()} Albedo",
                    showgrid=True,
                    gridcolor='rgba(128,128,128,0.2)',
                    autorange=True
                ),
                hovermode='x unified',
                height=600,
                template="plotly_white",
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right", 
                    x=1
                )
            )
        
        return fig
    
    @render_widget
    def simple_plot():
        """Graphique simple de secours"""
        data = load_data()
        
        if data is None:
            return go.Figure().add_annotation(
                text="Pas de données",
                xref="paper", yref="paper", x=0.5, y=0.5
            )
        
        fig = go.Figure()
        
        for i, fraction in enumerate(input.fractions()):
            col = f"{fraction}_{input.variable()}"
            if col in data.columns:
                mask = data[col].notna()
                plot_data = data[mask]
                
                if len(plot_data) > 0:
                    color = COLORS.get(fraction, f'hsl({i * 80}, 70%, 50%)')
                    
                    fig.add_trace(go.Scatter(
                        x=plot_data['date'],
                        y=plot_data[col],
                        mode='lines',
                        name=f'{fraction} ({len(plot_data)})',
                        line=dict(color=color, width=2)
                    ))
        
        fig.update_layout(
            title="Simple Time Series (Backup)",
            xaxis_title="Date",
            yaxis_title="Albedo", 
            height=400,
            template="plotly_white"
        )
        
        return fig

app = App(app_ui, server)

if __name__ == "__main__":
    print("🚀 Lancement de la version time series qui marche...")
    app.run(host="127.0.0.1", port=8006)