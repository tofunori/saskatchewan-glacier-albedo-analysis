# Analyse de Tendances d'Albédo - Glacier Saskatchewan

Script Python pour analyser les tendances temporelles dans les données d'albédo du glacier Saskatchewan en utilisant les tests de Mann-Kendall et la pente de Sen.

## 🚀 Installation

```bash
# Installer les dépendances
pip install -r requirements_trend_analysis.txt

# Ou installation manuelle
pip install pandas numpy matplotlib seaborn scipy pymannkendall openpyxl
```

## 📊 Utilisation

1. **Exporter les données depuis Google Earth Engine**
   - Exécuter le script `saskatchewan_glacier_albedo_analysis_with_fractions.js`
   - Télécharger le fichier `daily_albedo_mann_kendall_ready_2010_2024.csv`

2. **Placer le fichier CSV dans le dossier du projet**

3. **Exécuter l'analyse**
   ```bash
   python albedo_trend_analysis.py
   ```

## 📈 Fonctionnalités

### Tests Statistiques Standards
- **Test de Mann-Kendall**: Détection de tendances monotones (non-paramétrique)
- **Pente de Sen**: Estimation robuste de la magnitude du changement
- **Analyse saisonnière**: Tendances par période (début/mi/fin été)
- **Filtrage qualité**: Utilise le seuil minimum de pixels

### ⭐ Analyses Avancées (NOUVEAU!)
- **Cartographie des pentes**: Visualisation spatiale des tendances par fraction
- **Analyse mensuelle**: Mann-Kendall détaillé mois par mois (juin-septembre)
- **Contrôle autocorrélation**: Modified Mann-Kendall et pré-blanchiment
- **Intervalles de confiance**: Bootstrap pour quantifier l'incertitude des pentes

### Fractions Analysées
- **0-25% (Bordure)**: Pixels de bordure
- **25-50% (Mixte bas)**: Pixels mixtes faible
- **50-75% (Mixte haut)**: Pixels mixtes élevé  
- **75-90% (Majoritaire)**: Pixels majoritairement glacier
- **90-100% (Pur)**: Pixels quasi-purs glacier

### Outputs Générés
- **Graphiques standards**: `saskatchewan_albedo_trends_*.png`
- **Cartographie spatiale**: `spatial_slope_analysis_*.png`
- **Tableau Excel standard**: `saskatchewan_albedo_trend_analysis.xlsx`
- **Tableau Excel avancé**: `saskatchewan_albedo_trend_analysis_advanced.xlsx`
- **Résultats console**: Tendances avec significativité et analyses avancées

## 📋 Interprétation des Résultats

### Significativité
- `***`: p < 0.001 (très significatif)
- `**`: p < 0.01 (significatif)
- `*`: p < 0.05 (faiblement significatif)
- `ns`: Non significatif

### Tendances
- `📈 increasing`: Albédo en augmentation
- `📉 decreasing`: Albédo en diminution  
- `➡️ no trend`: Pas de tendance détectée

### Pente de Sen
- **Unités**: Changement d'albédo par année
- **Exemple**: -0.002/an = diminution de 0.002 unités d'albédo par an
- **Décennie**: Changement sur 10 ans = pente × 10

## 🔬 Analyses Avancées - Guide d'Interprétation

### 1. Cartographie des Pentes
- **Visualisation spatiale** des tendances par fraction de couverture
- **Barres d'erreur bootstrap** pour quantifier l'incertitude
- **Projection décennale** pour planification long-terme

### 2. Analyse Mensuelle Détaillée  
- **Détection saisonnière** des changements (juin → septembre)
- **Intervalles de confiance** sur chaque pente mensuelle
- **Identification** des mois critiques (ex: août = pic de fonte)

### 3. Contrôle d'Autocorrélation
- **🟢 Faible**: |r| < 0.1 → Résultats MK standard fiables
- **🟡 Modérée**: 0.1 ≤ |r| < 0.3 → Utiliser MK modifié
- **🔴 Forte**: |r| ≥ 0.3 → Pré-blanchiment obligatoire

### 4. Intervalles de Confiance Bootstrap
- **IC 95%**: Plage de valeurs probables pour la pente
- **Écart-type**: Mesure de la précision de l'estimation
- **Exemple**: Pente = -0.004 ± 0.001 → Changement robuste

## 🔧 Personnalisation

### Modifier l'analyse
```python
# Changer le fichier d'entrée
csv_file = "votre_fichier.csv"

# Analyser d'autres variables
analyzer.calculate_trends('median')  # Au lieu de 'mean'

# Filtres personnalisés
analyzer.data = analyzer.data[analyzer.data['year'] >= 2015]
```

### Graphiques personnalisés
```python
# Sauver dans un dossier spécifique
analyzer.plot_trends('mean', 'graphs/tendances_albedo.png')
```

## 🧪 Validation Scientifique

Le script utilise des méthodes statistiques robustes:
- **Mann-Kendall**: Recommandé pour données hydro-climatiques
- **Sen's slope**: Résistant aux valeurs aberrantes
- **Tests saisonniers**: Compte la variabilité saisonnière
- **Filtrage qualité**: Assure la fiabilité des données

## 📚 Références

- Mann, H.B. (1945). Nonparametric tests against trend. Econometrica 13, 245-259.
- Sen, P.K. (1968). Estimates of the regression coefficient based on Kendall's tau. Journal of the American Statistical Association 63, 1379-1389.
- Hussain et al. (2019). pyMannKendall: a python package for non parametric Mann Kendall family of trend tests.

## 🐛 Dépannage

### Erreurs courantes
```bash
# Erreur: Fichier non trouvé
# Solution: Vérifier le nom et l'emplacement du CSV

# Erreur: pymannkendall non installé  
pip install pymannkendall

# Erreur: Pas assez de données
# Solution: Vérifier le filtrage des données (min_pixels_threshold)
```

### Support
- Vérifier que le CSV contient toutes les colonnes requises
- S'assurer que les dates sont au bon format
- Contrôler la qualité des données (NaN, valeurs aberrantes)