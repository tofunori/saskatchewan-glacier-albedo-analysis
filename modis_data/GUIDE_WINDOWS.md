# Guide d'utilisation MODIS - Windows + WSL

## 🎯 Problème identifié
Vous utilisez VS Code depuis Windows avec un environnement conda, mais votre projet est stocké dans WSL Ubuntu.

## ✅ Solutions

### Option 1: Utilisation directe depuis Windows (Recommandée)

1. **Activez votre environnement conda:**
   ```cmd
   conda activate geo-env
   ```

2. **Installez modis-tools si nécessaire:**
   ```cmd
   conda install -c conda-forge modis-tools
   ```

3. **Lancez le downloader Windows:**
   ```cmd
   # Naviguez vers votre projet via WSL
   cd \\wsl.localhost\Ubuntu\home\tofunori\saskatchewan-glacier-albedo-analysis\modis_data
   
   # Exécutez le script Windows
   python modis_downloader_windows.py
   ```

   **Ou utilisez le script batch:**
   ```cmd
   run_modis_windows.bat
   ```

### Option 2: Debug depuis Windows

```cmd
cd \\wsl.localhost\Ubuntu\home\tofunori\saskatchewan-glacier-albedo-analysis\modis_data
python debug_spatial.py
```

### Option 3: Exécution dans WSL Terminal

1. **Ouvrez un terminal WSL:**
   ```cmd
   wsl -d Ubuntu
   ```

2. **Naviguez vers le projet:**
   ```bash
   cd /home/tofunori/saskatchewan-glacier-albedo-analysis/modis_data
   ```

3. **Installez les dépendances WSL:**
   ```bash
   sudo apt update
   sudo apt install python3-geopandas python3-shapely python3-gdal
   pip3 install --user modis-tools
   ```

4. **Exécutez le script:**
   ```bash
   python3 modis_downloader.py
   ```

## 🔧 Résolution des problèmes

### Problème: "Mask directory not found"
**Cause:** Chemins WSL incorrects depuis Windows

**Solution:** Utilisez `modis_downloader_windows.py` qui gère automatiquement les chemins WSL.

### Problème: "No collections found"
**Cause:** Problème d'authentification NASA Earthdata

**Solution:** 
1. Vérifiez vos identifiants dans le script
2. Essayez de créer un fichier `.netrc` :
   ```bash
   echo "machine urs.earthdata.nasa.gov login tofunori password ASDqwe1234!" > ~/.netrc
   chmod 600 ~/.netrc
   ```

### Problème: Download stalling
**Cause:** Connexion réseau ou serveur NASA surchargé

**Solution:**
1. Réduisez le nombre de téléchargements simultanés
2. Essayez à un autre moment
3. Utilisez `limit_per_product=1` pour tester

## 📁 Accès aux fichiers téléchargés

### Depuis Windows:
```
\\wsl.localhost\Ubuntu\home\tofunori\saskatchewan-glacier-albedo-analysis\modis_data\
├── MOD10A1_snow_cover/     # Données de couverture neigeuse
└── MCD43A3_albedo/         # Données d'albédo
```

### Depuis WSL:
```
/home/tofunori/saskatchewan-glacier-albedo-analysis/modis_data/
├── MOD10A1_snow_cover/
└── MCD43A3_albedo/
```

## 🚀 Utilisation recommandée

1. **Activez geo-env** dans votre terminal Windows
2. **Exécutez** `run_modis_windows.bat` 
3. **Vérifiez** les résultats dans le dossier WSL
4. **Analysez** les données avec vos notebooks Python depuis Windows

## 📝 Configuration

Modifiez les paramètres dans `modis_downloader_windows.py`:

```python
# Identifiants NASA Earthdata
username = "tofunori"
password = "ASDqwe1234!"

# Période de téléchargement
start_date = "2024-08-01"
end_date = "2024-08-15"

# Masque du glacier (GeoJSON recommandé pour Windows)
glacier_mask_path = "mask/saskatchewan_glacier_mask.geojson"
```

## ✨ Avantages de cette approche

- ✅ Utilise votre environnement conda existant
- ✅ Accès aux fichiers depuis Windows et WSL
- ✅ Gestion automatique des chemins
- ✅ Compatible avec VS Code Windows
- ✅ Détection automatique de l'environnement