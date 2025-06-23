#!/usr/bin/env python3
"""
Menu System for Saskatchewan Glacier Albedo Analysis
====================================================

Handles all user interface and menu interactions, separated from main logic.
"""

from typing import Optional, List, Tuple
from config import FRACTION_CLASSES, CLASS_LABELS


class MenuOption:
    """Represents a single menu option with validation."""
    
    def __init__(self, key: str, label: str, description: str = ""):
        self.key = key
        self.label = label
        self.description = description


class BaseMenu:
    """Base class for all menu interfaces."""
    
    def __init__(self, title: str, options: List[MenuOption]):
        self.title = title
        self.options = options
        self.valid_choices = [opt.key for opt in options]
    
    def display(self) -> None:
        """Display the menu to the user."""
        print("\n" + "=" * len(self.title))
        print(self.title)
        print("=" * len(self.title))
        print()
        
        for option in self.options:
            print(f"{option.key}️⃣  {option.label}")
            if option.description:
                print(f"    {option.description}")
        print()
        print("-" * len(self.title))
    
    def get_choice(self, prompt: str = "➤ Votre choix") -> str:
        """Get and validate user choice."""
        while True:
            try:
                choice = input(f"{prompt} ({'/'.join(self.valid_choices)}): ").strip()
                if choice in self.valid_choices:
                    return choice
                else:
                    print(f"❌ '{choice}' n'est pas valide. Tapez un chiffre parmi {'/'.join(self.valid_choices)}.")
            except KeyboardInterrupt:
                print("\n\n👋 Interruption.")
                return self.valid_choices[-1]  # Return last option (usually "quit")
            except Exception:
                print(f"❌ Erreur de saisie. Tapez un chiffre parmi {'/'.join(self.valid_choices)}.")


class MainMenu(BaseMenu):
    """Main application menu."""
    
    def __init__(self):
        options = [
            MenuOption("1", "MCD43A3 - Albédo général (MODIS Combined)"),
            MenuOption("2", "MOD10A1 - Albédo de neige (Terra Snow Cover)"),
            MenuOption("3", "Comparaison MCD43A3 vs MOD10A1"),
            MenuOption("4", "Quitter")
        ]
        super().__init__("🚀 MENU D'ANALYSE - SASKATCHEWAN GLACIER ALBEDO", options)


class DatasetMenu(BaseMenu):
    """Menu for dataset-specific analyses."""
    
    def __init__(self, dataset_name: str):
        self.dataset_name = dataset_name
        dataset_info = {
            'MCD43A3': '🌍 MCD43A3 - Albédo général (MODIS Combined)',
            'MOD10A1': '❄️ MOD10A1 - Albédo de neige (Terra Snow Cover)'
        }
        
        options = [
            MenuOption("1", "Analyse complète (toutes les étapes)"),
            MenuOption("2", "Tendances statistiques seulement"),
            MenuOption("3", "Visualisations seulement"),
            MenuOption("4", "Analyse pixels/QA seulement"),
            MenuOption("5", "Graphiques quotidiens (daily_melt_season)")
        ]
        
        # Add MOD10A1-specific options
        if dataset_name == 'MOD10A1':
            options.extend([
                MenuOption("6", "Comparaison entre fractions MOD10A1 🆕"),
                MenuOption("7", "Analyse fraction × élévation (Williamson & Menounos 2021) 🆕"),
                MenuOption("8", "Retour au menu principal")
            ])
        else:
            options.append(MenuOption("6", "Retour au menu principal"))
        
        title = f"ANALYSES POUR {dataset_info.get(dataset_name, dataset_name)}"
        super().__init__(title, options)
    
    def is_return_choice(self, choice: str) -> bool:
        """Check if choice is to return to main menu."""
        return choice == "8" if self.dataset_name == 'MOD10A1' else choice == "6"


class ComparisonMenu(BaseMenu):
    """Menu for comparison analyses."""
    
    def __init__(self):
        options = [
            MenuOption("1", "Comparaison complète (corrélations + différences + tendances)"),
            MenuOption("2", "Corrélations seulement"),
            MenuOption("3", "Visualisations comparatives seulement"),
            MenuOption("4", "Graphiques quotidiens par saison de fonte"),
            MenuOption("5", "Retour au menu principal")
        ]
        super().__init__("🔄 COMPARAISON MCD43A3 vs MOD10A1", options)


class FractionSelector(BaseMenu):
    """Menu for selecting fraction classes."""
    
    def __init__(self):
        options = [
            MenuOption(str(i), CLASS_LABELS[fraction])
            for i, fraction in enumerate(FRACTION_CLASSES, 1)
        ]
        super().__init__("🔍 CHOIX DE LA FRACTION À ANALYSER", options)
    
    def get_fraction_choice(self) -> str:
        """Get fraction choice and return the fraction key."""
        choice = self.get_choice()
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(FRACTION_CLASSES):
                selected_fraction = FRACTION_CLASSES[choice_num - 1]
                print(f"✅ Fraction sélectionnée: {CLASS_LABELS[selected_fraction]}")
                return selected_fraction
        except ValueError:
            pass
        
        # Default fallback
        return 'pure_ice'


class MenuController:
    """Main controller for the menu system."""
    
    def __init__(self):
        self.main_menu = MainMenu()
        self.should_continue = True
    
    def run(self) -> None:
        """Main menu loop."""
        while self.should_continue:
            self.main_menu.display()
            choice = self.main_menu.get_choice()
            
            if choice == "1":
                self._handle_dataset_menu('MCD43A3')
            elif choice == "2":
                self._handle_dataset_menu('MOD10A1')
            elif choice == "3":
                self._handle_comparison_menu()
            elif choice == "4":
                print("\n👋 Au revoir!")
                self.should_continue = False
    
    def _handle_dataset_menu(self, dataset_name: str) -> None:
        """Handle dataset-specific menu interactions."""
        dataset_menu = DatasetMenu(dataset_name)
        
        while True:
            dataset_menu.display()
            choice = dataset_menu.get_choice()
            
            if dataset_menu.is_return_choice(choice):
                break
            
            # Execute the chosen analysis
            self._execute_dataset_analysis(dataset_name, choice)
            
            # Ask if user wants to continue with this dataset
            if not self._ask_continue(f"Autre analyse pour {dataset_name}"):
                break
    
    def _handle_comparison_menu(self) -> None:
        """Handle comparison menu interactions."""
        comparison_menu = ComparisonMenu()
        
        while True:
            comparison_menu.display()
            choice = comparison_menu.get_choice()
            
            if choice == "5":  # Return to main menu
                break
            
            # Execute the chosen comparison
            self._execute_comparison_analysis(choice)
            
            # Ask if user wants to continue with comparisons
            if not self._ask_continue("Autre analyse comparative"):
                break
    
    def _execute_dataset_analysis(self, dataset_name: str, choice: str) -> None:
        """Execute dataset analysis based on choice."""
        from scripts.analysis_functions import run_dataset_analysis, run_custom_analysis
        
        try:
            if choice == "1":
                print(f"\n🔍 Analyse complète du dataset {dataset_name}...")
                run_dataset_analysis(dataset_name)
            elif choice == "2":
                print(f"\n📈 Analyse des tendances pour {dataset_name}...")
                run_custom_analysis(dataset_name, 2)
            elif choice == "3":
                print(f"\n🎨 Génération des visualisations pour {dataset_name}...")
                run_custom_analysis(dataset_name, 3)
            elif choice == "4":
                print(f"\n🔍 Analyse pixels/QA pour {dataset_name}...")
                run_custom_analysis(dataset_name, 4)
            elif choice == "5":
                print(f"\n📅 Graphiques quotidiens pour {dataset_name}...")
                run_custom_analysis(dataset_name, 5)
            elif choice == "6" and dataset_name == 'MOD10A1':
                print(f"\n🔍 Comparaison entre fractions MOD10A1...")
                from scripts.analysis_functions import run_mod10a1_fraction_comparison
                run_mod10a1_fraction_comparison()
            elif choice == "7" and dataset_name == 'MOD10A1':
                print(f"\n🏔️ Analyse fraction × élévation (Williamson & Menounos 2021)...")
                from scripts.analysis_functions import run_elevation_analysis_menu
                run_elevation_analysis_menu()
        except Exception as e:
            print(f"\n❌ Erreur lors de l'analyse {dataset_name}: {e}")
    
    def _execute_comparison_analysis(self, choice: str) -> None:
        """Execute comparison analysis based on choice."""
        from scripts.analysis_functions import (
            run_comparison_analysis, run_correlation_analysis, 
            run_comparative_visualizations, run_daily_melt_season_comparison
        )
        
        try:
            if choice == "1":
                print("\n🔄 Comparaison complète MCD43A3 vs MOD10A1...")
                run_comparison_analysis()
            elif choice == "2":
                print("\n📊 Analyse de corrélation entre produits...")
                run_correlation_analysis()
            elif choice == "3":
                print("\n📈 Génération des visualisations comparatives...")
                run_comparative_visualizations()
            elif choice == "4":
                print("\n📅 Graphiques quotidiens par saison de fonte...")
                fraction_selector = FractionSelector()
                fraction_selector.display()
                fraction_choice = fraction_selector.get_fraction_choice()
                run_daily_melt_season_comparison(fraction_choice)
        except Exception as e:
            print(f"\n❌ Erreur lors de la comparaison: {e}")
    
    def _ask_continue(self, prompt: str) -> bool:
        """Ask user if they want to continue."""
        print("\n" + "=" * 50)
        try:
            cont = input(f"➤ {prompt}? (o/n): ").strip().lower()
            return cont in ['o', 'oui', 'y', 'yes']
        except (KeyboardInterrupt, Exception):
            return False