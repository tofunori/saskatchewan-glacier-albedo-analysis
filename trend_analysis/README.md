# Saskatchewan Albedo Trend Analysis Package

Package Python modulaire pour l'analyse statistique des tendances d'albédo du glacier Saskatchewan à partir des données Google Earth Engine.

## 🆕 Nouvelles fonctionnalités (v2.0)

- **📊 Graphiques de statistiques mensuelles** : Visualisations détaillées par mois avec moyennes, variabilité et distributions
- **🧩 Structure modulaire** : Code organisé en modules clairs et réutilisables
- **🚀 Fonctions d'analyse rapide** : Options pour analyses complètes, rapides ou par fraction
- **💾 Exports multiples** : Rapports Excel, texte et CSV
- **🔧 Gestion d'erreurs robuste** : Import sécurisé et validation des données

## 📁 Structure du package

```
trend_analysis/
├── __init__.py              # Point d'entrée du package
├── config.py               # Configuration et constantes
├── utils.py                # Fonctions utilitaires partagées
├── data_loader.py          # Chargement et préparation des données
├── basic_trends.py         # Tests Mann-Kendall et Sen's slope
├── seasonal_analysis.py    # Analyses saisonnières et mensuelles
├── advanced_analysis.py    # Autocorrélation, bootstrap, tests avancés
├── spatial_analysis.py     # Cartographie et analyses spatiales
├── visualizations.py       # Graphiques et visualisations
├── exports.py             # Exports Excel, texte et CSV
└── main.py                # Orchestration et fonctions principales
```

## 🚀 Utilisation rapide

### Installation des dépendances

```bash
pip install pandas numpy matplotlib seaborn scipy scikit-learn openpyxl
pip install pymannkendall  # Optionnel, implémentation manuelle disponible
```

### Analyse complète (recommandée)

```python
from trend_analysis import run_complete_analysis

results = run_complete_analysis(
    csv_path='your_data.csv',
    output_dir='analysis_output',
    variable='mean'
)
```

### Utilisation modulaire

```python
from trend_analysis import (
    SaskatchewanDataLoader,
    BasicTrendAnalyzer,
    SeasonalAnalyzer,
    AlbedoVisualizer
)

# Chargement des données
data_loader = SaskatchewanDataLoader('your_data.csv')
data_loader.load_data()

# Analyses de base
analyzer = BasicTrendAnalyzer(data_loader)
results = analyzer.calculate_trends('mean')

# Graphiques mensuels (NOUVEAU!)
seasonal = SeasonalAnalyzer(data_loader)
monthly_graph = seasonal.create_monthly_statistics_graphs('mean')

# Visualisations
visualizer = AlbedoVisualizer(data_loader)
overview = visualizer.create_trend_overview_graph(results, 'mean')
```

## 📊 Analyses disponibles

### Tests statistiques
- **Mann-Kendall** : Détection de tendances non-paramétriques
- **Sen's slope** : Estimation robuste de la magnitude des tendances
- **Autocorrélation** : Contrôle des effets de corrélation temporelle
- **Bootstrap** : Intervalles de confiance robustes

### Analyses temporelles
- **Tendances annuelles** : Sur toute la période d'étude
- **Analyses mensuelles** : Tendances pour chaque mois de la saison de fonte
- **Patterns saisonniers** : Évolution intra-saisonnière

### Visualisations
- **📈 Graphiques de tendances** : Vue d'ensemble par fraction
- **📅 Statistiques mensuelles** : Moyennes, variabilité, distributions par mois
- **🗺️ Cartographie spatiale** : Distribution des pentes de Sen
- **📊 Dashboard de résumé** : Vue d'ensemble complète

### Exports
- **📄 Rapport texte** : Analyse complète en format texte
- **📊 Fichier Excel** : Toutes les données dans des feuilles séparées
- **📈 CSV de résumé** : Tableau simple pour usage externe

## 🔧 Configuration

Le fichier `config.py` contient tous les paramètres configurables :

```python
# Fractions analysées
FRACTION_CLASSES = ['border', 'mixed_low', 'mixed_high', 'mostly_ice', 'pure_ice']

# Paramètres d'analyse
ANALYSIS_CONFIG = {
    'bootstrap_iterations': 1000,
    'min_observations': 10,
    'significance_levels': [0.001, 0.01, 0.05]
}

# Couleurs pour les graphiques
FRACTION_COLORS = {
    'border': 'red',
    'mixed_low': 'orange',
    'pure_ice': 'blue'
}
```

## 📈 Format des données d'entrée

Le CSV d'entrée doit contenir :

```
date,year,month,doy,decimal_year,border_mean,border_median,mixed_low_mean,...
2010-06-01,2010,6,152,2010.416,0.15,0.14,0.18,...
```

**Colonnes requises :**
- `date` : Date au format YYYY-MM-DD
- Colonnes d'albédo : `{fraction}_{variable}` (ex: `pure_ice_mean`)

**Colonnes optionnelles :**
- `min_pixels_threshold` : Filtre de qualité booléen
- Variables temporelles (générées automatiquement si absentes)

## 🎯 Exemples d'utilisation

### Analyse d'une fraction spécifique

```python
from trend_analysis import analyze_single_fraction

result = analyze_single_fraction(
    csv_path='data.csv',
    fraction='pure_ice',
    variable='mean',
    save_graphs=True
)
```

### Analyse rapide (sans graphiques)

```python
from trend_analysis import run_quick_analysis

results = run_quick_analysis('data.csv', variable='mean')
summary = results['summary_table']
```

### Export personnalisé

```python
from trend_analysis import ResultsExporter, SaskatchewanDataLoader

data_loader = SaskatchewanDataLoader('data.csv')
data_loader.load_data()

exporter = ResultsExporter(data_loader)
excel_file = exporter.export_excel_report(all_results, 'mean')
text_file = exporter.export_text_report(all_results, 'mean')
```

## 🔬 Méthodologie statistique

### Tests de tendances
1. **Test Mann-Kendall original** pour séries sans autocorrélation
2. **Test Mann-Kendall modifié** avec correction de variance pour autocorrélation modérée
3. **Pré-blanchiment + Mann-Kendall** pour autocorrélation forte

### Estimation des pentes
- **Pente de Sen** : Médiane des pentes entre toutes les paires de points
- **Intervalles de confiance** : Méthode de Theil (95%) + Bootstrap optionnel

### Contrôle de qualité
- Validation du nombre minimum d'observations
- Détection et gestion des valeurs manquantes
- Évaluation de l'autocorrélation temporelle

## 🎨 Nouveaux graphiques mensuels

La v2.0 inclut des visualisations mensuelles complètes :

1. **Moyennes mensuelles** : Évolution par fraction et par mois
2. **Variabilité mensuelle** : Écarts-types pour chaque mois
3. **Distributions mensuelles** : Boxplots des valeurs par mois  
4. **Comptages d'observations** : Disponibilité des données par mois

```python
seasonal_analyzer = SeasonalAnalyzer(data_loader)
monthly_graph = seasonal_analyzer.create_monthly_statistics_graphs('mean')
# Sauvegarde automatique: monthly_statistics_mean.png
```

## 🐛 Dépannage

### Erreurs courantes

**ImportError lors de l'import du package :**
```bash
pip install pandas numpy matplotlib seaborn scipy scikit-learn
```

**Données insuffisantes :**
- Vérifiez le format du CSV
- Minimum 10 observations par fraction recommandé

**Graphiques non affichés :**
- Vérifiez l'installation de matplotlib
- Utilisez `plt.show()` si nécessaire

### Support

Pour signaler des bugs ou demander des fonctionnalités :
- Consultez les messages d'erreur détaillés
- Vérifiez le format des données d'entrée
- Testez avec l'exemple fourni (`example_usage.py`)

## 📝 Changelog

### v2.0.0 (Actuel)
- ✅ Structure modulaire complète
- ✅ Graphiques de statistiques mensuelles
- ✅ Exports Excel et texte améliorés
- ✅ Fonctions d'analyse rapide
- ✅ Gestion d'erreurs robuste

### v1.0.0 (Précédent)
- Script monolithique `albedo_trend_analysis.py`
- Tests de base Mann-Kendall et Sen
- Analyses avancées (autocorrélation, bootstrap, spatial)

## 📄 Licence

Code développé pour l'analyse des données d'albédo du glacier Saskatchewan.
Utilisation libre pour la recherche académique.

---

**Développé avec Claude Code Analysis**  
*Package modulaire pour une analyse robuste des tendances d'albédo*