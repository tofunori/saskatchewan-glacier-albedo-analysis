# Special Guidelines and Design Patterns

## Language and Documentation Guidelines
- **Bilingual Codebase**: Mix of French and English throughout
- **French Documentation**: Docstrings and comments primarily in French
- **English Code**: Function names, variables, and class names in English
- **User Interface**: French emoji-rich console messages

## Development Patterns

### Configuration Management
- **Centralized Config**: All settings in `config.py`
- **Dataset-Specific Configs**: `MCD43A3_CONFIG`, `MOD10A1_CONFIG`, etc.
- **Hierarchical Structure**: Nested configuration dictionaries
- **Function Access**: `get_dataset_config()`, `get_output_path()` helper functions

### Error Handling Patterns
```python
try:
    # Operation
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print("📝 Utilisation du mode de compatibilité...")
    # Fallback logic
```

### Menu System Pattern
- **Hierarchical Menus**: Main → Dataset → Analysis type
- **Emoji Usage**: Extensive use of emojis for user feedback
- **French Interface**: Menu options and messages in French
- **Error Recovery**: Graceful handling of invalid choices

### Data Handler Pattern
```python
class AlbedoDataHandler:
    def __init__(self, csv_path):
        # Initialize with configuration
    
    def load_data(self):
        # Load and validate data
    
    def _prepare_temporal_data(self):
        # Private method for data preparation
```

### Analysis Function Pattern
```python
def run_analysis_type(dataset='MCD43A3', **kwargs):
    """
    Standard pattern for analysis functions
    """
    # Get configuration
    config = get_dataset_config(dataset)
    
    # Initialize data handler
    handler = AlbedoDataHandler(config['csv_path'])
    
    # Run analysis
    # Save results
    # Generate visualizations
```

## File Organization Principles

### Module Responsibility
- **Scripts**: User interface and orchestration
- **Data**: Data loading, processing, and management
- **Analysis**: Statistical and scientific computations
- **Visualization**: Plot generation and styling
- **Config**: All parameters and settings

### Naming Conventions
- **Files**: snake_case.py
- **Classes**: PascalCase
- **Functions**: snake_case
- **Constants**: UPPER_SNAKE_CASE
- **Private Methods**: _leading_underscore

### Import Patterns
```python
# Standard library first
from pathlib import Path
import datetime

# Third-party libraries
import pandas as pd
import numpy as np

# Local imports
from config import get_dataset_config
from data.handler import AlbedoDataHandler
```

## Special Considerations

### Interactive Development
- **Menu-Driven**: Primary interface is interactive console
- **User Feedback**: Extensive progress indicators and status messages
- **Error Recovery**: Graceful degradation and fallback options

### Multi-Dataset Support
- **Unified Interface**: Same analysis functions work across datasets
- **Configuration-Driven**: Dataset differences handled through config
- **Comparison Tools**: Built-in cross-dataset analysis capabilities

### Result Management
- **Structured Output**: Dataset-specific result directories
- **Multiple Formats**: CSV, Excel, PNG exports
- **Metadata Tracking**: Processing logs and quality reports

### Google Earth Engine Integration
- **External Dependency**: Relies on GEE for data export
- **Asset Management**: Uses specific GEE asset paths
- **Quality Filtering**: Comprehensive data quality controls