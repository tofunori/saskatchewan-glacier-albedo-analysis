"""
Debug version pour identifier le problème du graphique temporel
"""

from shiny import App, ui, render, reactive
from shinywidgets import output_widget, render_widget
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys, os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config import MCD43A3_CONFIG, MOD10A1_CONFIG, CLASS_LABELS

# Couleurs fixes
COLORS = {
    'mostly_ice': '#88ccff',
    'pure_ice': '#0066cc'
}

app_ui = ui.page_fluid(
    ui.h1("🔍 Debug Time Series"),
    
    ui.div(
        ui.input_radio_buttons(
            "dataset",
            "Dataset:",
            choices={
                "MCD43A3": "MCD43A3",
                "MOD10A1": "MOD10A1"
            },
            selected="MOD10A1"  # Commencer avec MOD10A1 comme dans votre capture
        ),
        
        ui.input_checkbox_group(
            "fractions",
            "Fractions:",
            choices={
                "mostly_ice": "75-90% (Majoritaire)",
                "pure_ice": "90-100% (Pur)"
            },
            selected=["mostly_ice", "pure_ice"]
        ),
        
        style="display: flex; gap: 20px; padding: 15px; background: #f5f5f5;"
    ),
    
    ui.div(
        ui.h3("📊 Debug Info"),
        ui.output_text_verbatim("debug_info"),
        style="background: #fff; padding: 15px; margin: 10px; border: 1px solid #ddd;"
    ),
    
    ui.div(
        ui.h3("📅 Date Info"),
        ui.output_text_verbatim("date_info"),
        style="background: #fff; padding: 15px; margin: 10px; border: 1px solid #ddd;"
    ),
    
    ui.div(
        ui.h3("📈 Plot Debug"),
        output_widget("debug_plot"),
        style="background: #fff; padding: 15px; margin: 10px; border: 1px solid #ddd;"
    )
)

def server(input, output, session):
    
    @reactive.Calc
    def load_raw_data():
        """Charger les données brutes"""
        dataset = input.dataset()
        
        try:
            if dataset == "MCD43A3":
                data = pd.read_csv(MCD43A3_CONFIG['csv_path'])
            else:
                data = pd.read_csv(MOD10A1_CONFIG['csv_path'])
            
            print(f"✅ Chargé {dataset}: {len(data)} lignes")
            
            # Conversion de date
            data['date'] = pd.to_datetime(data['date'])
            print(f"✅ Dates converties: {data['date'].min()} à {data['date'].max()}")
            
            return data
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return None
    
    @output
    @render.text
    def debug_info():
        """Info de debug général"""
        data = load_raw_data()
        
        if data is None:
            return "❌ Pas de données chargées"
        
        info = []
        info.append(f"Dataset: {input.dataset()}")
        info.append(f"Total lignes: {len(data):,}")
        info.append(f"Colonnes: {len(data.columns)}")
        
        info.append("\n📊 Données par fraction:")
        for fraction in input.fractions():
            col = f"{fraction}_mean"
            if col in data.columns:
                non_null = data[col].notna().sum()
                info.append(f"  {fraction}: {non_null:,} valeurs")
                if non_null > 0:
                    values = data[col].dropna()
                    info.append(f"    Min: {values.min():.4f}")
                    info.append(f"    Max: {values.max():.4f}")
                    info.append(f"    Première valeur: {values.iloc[0]:.4f}")
                    info.append(f"    Dernière valeur: {values.iloc[-1]:.4f}")
            else:
                info.append(f"  {fraction}: ❌ Colonne manquante")
        
        return "\n".join(info)
    
    @output
    @render.text
    def date_info():
        """Info détaillée sur les dates"""
        data = load_raw_data()
        
        if data is None:
            return "❌ Pas de données"
        
        info = []
        info.append("📅 Analyse des dates:")
        info.append(f"Type de colonne date: {data['date'].dtype}")
        info.append(f"Première date: {data['date'].min()}")
        info.append(f"Dernière date: {data['date'].max()}")
        info.append(f"Nombre de dates uniques: {data['date'].nunique():,}")
        
        # Échantillon de dates
        info.append("\n📅 Échantillon de dates:")
        sample_dates = data['date'].head(10).tolist()
        for i, date in enumerate(sample_dates):
            info.append(f"  {i+1}: {date}")
        
        # Vérifier l'année
        data['year'] = data['date'].dt.year
        years = sorted(data['year'].unique())
        info.append(f"\n📅 Années présentes: {years}")
        
        # Compter par année
        year_counts = data['year'].value_counts().sort_index()
        info.append("\n📅 Nombre d'observations par année:")
        for year, count in year_counts.items():
            info.append(f"  {year}: {count} observations")
        
        return "\n".join(info)
    
    @render_widget
    def debug_plot():
        """Graphique de debug"""
        data = load_raw_data()
        
        if data is None:
            return go.Figure().add_annotation(
                text="❌ Pas de données à afficher",
                xref="paper", yref="paper", x=0.5, y=0.5
            )
        
        fig = go.Figure()
        
        total_points = 0
        
        for fraction in input.fractions():
            col = f"{fraction}_mean"
            if col in data.columns:
                # Données non-nulles seulement
                mask = data[col].notna()
                plot_data = data[mask].copy()
                
                if len(plot_data) > 0:
                    color = COLORS.get(fraction, '#666666')
                    name = f"{fraction} ({len(plot_data)} points)"
                    total_points += len(plot_data)
                    
                    print(f"📊 {fraction}: {len(plot_data)} points")
                    print(f"   Première date: {plot_data['date'].min()}")
                    print(f"   Dernière date: {plot_data['date'].max()}")
                    print(f"   Première valeur: {plot_data[col].iloc[0]:.4f}")
                    print(f"   Dernière valeur: {plot_data[col].iloc[-1]:.4f}")
                    
                    fig.add_trace(go.Scatter(
                        x=plot_data['date'],
                        y=plot_data[col],
                        mode='lines+markers',
                        name=name,
                        line=dict(color=color, width=3),
                        marker=dict(size=6, opacity=0.8),
                        hovertemplate=f'<b>{fraction}</b><br>' +
                                     'Date: %{x}<br>' +
                                     'Valeur: %{y:.4f}<br>' +
                                     '<extra></extra>'
                    ))
        
        print(f"📊 Total points dans le graphique: {total_points}")
        
        if total_points == 0:
            fig.add_annotation(
                text="⚠️ AUCUN POINT DE DONNÉES!\nVérifiez la sélection des fractions",
                xref="paper", yref="paper", x=0.5, y=0.5,
                font=dict(size=16, color="red")
            )
        else:
            fig.update_layout(
                title=f"Debug Plot - {input.dataset()} - {total_points} points total",
                xaxis_title="Date",
                yaxis_title="Mean Albedo",
                height=500,
                template="plotly_white",
                showlegend=True
            )
        
        return fig

app = App(app_ui, server)

if __name__ == "__main__":
    print("🔍 Lancement du debug time series...")
    app.run(host="127.0.0.1", port=8005)