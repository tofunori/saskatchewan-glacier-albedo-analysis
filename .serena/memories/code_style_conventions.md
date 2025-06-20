# Code Style and Conventions

## Language and Documentation
- **Mixed Language Documentation**: French and English documentation coexist in the codebase
- **French Comments**: Many docstrings and comments are in French (e.g., "Initialise le gestionnaire de données")
- **Function Names**: English function and variable names with French documentation

## Python Style
### Naming Conventions:
- **Classes**: PascalCase (e.g., `AlbedoDataHandler`, `DatasetManager`)
- **Functions/Methods**: snake_case (e.g., `load_data`, `get_data_summary`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DEFAULT_DATASET`, `FRACTION_CLASSES`)
- **Private Methods**: Leading underscore (e.g., `_prepare_temporal_data`, `_filter_quality_data`)

### Code Organization:
- **Modular Design**: Code organized in logical modules (analysis, data, visualization, scripts)
- **Configuration-Driven**: All settings centralized in `config.py`
- **Class-Based Data Handling**: Main data operations encapsulated in classes
- **Functional Analysis**: Analysis functions are mostly standalone functions

### Docstring Style:
- **French Documentation**: Docstrings primarily in French
- **Args Section**: Standard Args/Returns documentation format
- **Type Hints**: Limited type annotation usage

### File Structure:
- **Module Imports**: Standard Python import patterns
- **Package Structure**: Proper `__init__.py` files for packages
- **Relative Imports**: Uses both absolute and relative imports

## Development Practices
### Error Handling:
- **Try-Except Blocks**: Comprehensive error handling in main scripts
- **Graceful Degradation**: Fallback to legacy mode when imports fail
- **User-Friendly Messages**: Error messages include emoji and French text

### Console Interface:
- **Interactive Menus**: Menu-driven command line interface
- **Emoji Usage**: Extensive use of emojis in user-facing messages
- **Bilingual Interface**: Mixed French/English user interface

## Design Patterns
- **Handler Pattern**: Data handling through dedicated handler classes
- **Config Pattern**: Centralized configuration management
- **Menu Pattern**: Hierarchical menu system for user interaction
- **Factory Pattern**: Dataset-specific configuration selection