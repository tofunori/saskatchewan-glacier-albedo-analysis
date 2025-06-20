"""
Test ultra-simple pour vérifier le chargement des données
"""

from shiny import App, ui, render, reactive
from shinywidgets import output_widget, render_widget
import pandas as pd
import plotly.graph_objects as go
import sys, os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config import MCD43A3_CONFIG, CLASS_LABELS

print("🔍 Test de chargement des données...")

# Test direct
def test_load():
    try:
        data = pd.read_csv(MCD43A3_CONFIG['csv_path'])
        data['date'] = pd.to_datetime(data['date'])
        print(f"✅ Données chargées: {len(data)} lignes")
        print(f"✅ pure_ice_mean: {data['pure_ice_mean'].notna().sum()} valeurs")
        return data
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

# Test initial
test_data = test_load()

app_ui = ui.page_fluid(
    ui.h1("🧪 Test Simple - Données Glacier"),
    
    ui.div(
        ui.input_radio_buttons(
            "dataset",
            "Dataset:",
            choices={"MCD43A3": "MCD43A3"},
            selected="MCD43A3"
        ),
        
        ui.input_checkbox_group(
            "fractions", 
            "Fractions:",
            choices={"pure_ice": "Pure Ice", "mostly_ice": "Mostly Ice"},
            selected=["pure_ice"]
        ),
        
        style="border: 1px solid #ccc; padding: 15px; margin: 10px;"
    ),
    
    ui.div(
        ui.h3("📊 Info de Debug"),
        ui.output_text_verbatim("debug_info"),
        style="background: #f5f5f5; padding: 15px; margin: 10px;"
    ),
    
    ui.div(
        ui.h3("📈 Graphique Test"),
        output_widget("test_plot"),
        style="border: 1px solid #ccc; padding: 15px; margin: 10px;"
    )
)

def server(input, output, session):
    
    @reactive.Calc
    def get_data():
        """Charger les données de façon réactive"""
        print(f"🔄 get_data() appelé - Dataset: {input.dataset()}")
        
        try:
            data = pd.read_csv(MCD43A3_CONFIG['csv_path'])
            data['date'] = pd.to_datetime(data['date'])
            print(f"✅ Données rechargées: {len(data)} lignes")
            return data
        except Exception as e:
            print(f"❌ Erreur dans get_data(): {e}")
            return None
    
    @output
    @render.text
    def debug_info():
        """Afficher les infos de debug"""
        data = get_data()
        
        if data is None:
            return "❌ AUCUNE DONNÉES CHARGÉES"
        
        info = []
        info.append(f"✅ Dataset: {input.dataset()}")
        info.append(f"✅ Total lignes: {len(data):,}")
        info.append(f"✅ Période: {data['date'].min()} à {data['date'].max()}")
        info.append(f"✅ Fractions sélectionnées: {', '.join(input.fractions())}")
        
        info.append("\n📊 Données par fraction:")
        for fraction in input.fractions():
            col_name = f"{fraction}_mean"
            if col_name in data.columns:
                non_null = data[col_name].notna().sum()
                info.append(f"  {fraction}: {non_null:,} valeurs non-nulles")
                if non_null > 0:
                    values = data[col_name].dropna()
                    info.append(f"    Min: {values.min():.4f}")
                    info.append(f"    Max: {values.max():.4f}")
                    info.append(f"    Moyenne: {values.mean():.4f}")
            else:
                info.append(f"  {fraction}: ❌ COLONNE INTROUVABLE")
        
        return "\n".join(info)
    
    @render_widget
    def test_plot():
        """Créer un graphique test"""
        data = get_data()
        
        if data is None:
            fig = go.Figure()
            fig.add_annotation(
                text="❌ AUCUNE DONNÉES À AFFICHER",
                xref="paper", yref="paper", x=0.5, y=0.5,
                font=dict(size=20, color="red")
            )
            return fig
        
        fig = go.Figure()
        
        points_count = 0
        for fraction in input.fractions():
            col_name = f"{fraction}_mean"
            if col_name in data.columns:
                # Filtrer les valeurs non-nulles
                mask = data[col_name].notna()
                plot_data = data[mask]
                
                if len(plot_data) > 0:
                    points_count += len(plot_data)
                    
                    fig.add_trace(go.Scatter(
                        x=plot_data['date'],
                        y=plot_data[col_name],
                        mode='lines+markers',
                        name=f'{fraction} ({len(plot_data)} points)',
                        line=dict(width=3),
                        marker=dict(size=5)
                    ))
        
        if points_count == 0:
            fig.add_annotation(
                text="⚠️ AUCUN POINT DE DONNÉES TROUVÉ\nVérifiez la sélection des fractions",
                xref="paper", yref="paper", x=0.5, y=0.5,
                font=dict(size=16, color="orange")
            )
        else:
            fig.update_layout(
                title=f"✅ Test Réussi - {points_count} points affichés",
                xaxis_title="Date",
                yaxis_title="Albedo Moyen",
                height=500
            )
        
        return fig

app = App(app_ui, server)

if __name__ == "__main__":
    print("🚀 Lancement du test simple...")
    app.run(host="127.0.0.1", port=8003)