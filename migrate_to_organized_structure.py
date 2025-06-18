#!/usr/bin/env python3
"""
Migration Script for Saskatchewan Glacier Albedo Analysis Results
================================================================

This script migrates existing outputs and results to the new organized
directory structure by MODIS product type and data category.

Usage:
    python migrate_to_organized_structure.py [--dry-run] [--verbose]

Options:
    --dry-run   Show what would be moved without actually moving files
    --verbose   Show detailed migration steps
"""

import os
import shutil
import glob
import argparse
from pathlib import Path
from datetime import datetime

# Migration mapping rules
MIGRATION_RULES = {
    # Excel and text reports -> MCD43A3_albedo/reports
    '**/*saskatchewan*albedo*.xlsx': 'results/MCD43A3_albedo/reports/',
    '**/*saskatchewan*albedo*.txt': 'results/MCD43A3_albedo/reports/',
    '**/*albedo*analysis*.xlsx': 'results/MCD43A3_albedo/reports/',
    '**/*albedo*statistical*.txt': 'results/MCD43A3_albedo/reports/',
    
    # CSV summary files -> MCD43A3_albedo/reports  
    '**/*saskatchewan*summary*.csv': 'results/MCD43A3_albedo/reports/',
    '**/*albedo*summary*.csv': 'results/MCD43A3_albedo/reports/',
    
    # Raw albedo CSV data -> MCD43A3_albedo/raw_data
    '**/daily_albedo*.csv': 'results/MCD43A3_albedo/raw_data/',
    '**/*albedo*mann_kendall*.csv': 'results/MCD43A3_albedo/processed_data/',
    
    # PNG figures and plots -> MCD43A3_albedo/figures
    '**/*trend*.png': 'results/MCD43A3_albedo/figures/',
    '**/*albedo*.png': 'results/MCD43A3_albedo/figures/',
    '**/*seasonal*.png': 'results/MCD43A3_albedo/figures/',
    '**/*correlation*.png': 'results/MCD43A3_albedo/figures/',
    '**/*dashboard*.png': 'results/MCD43A3_albedo/figures/',
    '**/*timeseries*.png': 'results/MCD43A3_albedo/figures/',
    
    # MODIS data downloads -> appropriate raw_data directories
    '**/*MCD43A3*.tif': 'results/MCD43A3_albedo/raw_data/',
    '**/*MCD43A3*.hdf': 'results/MCD43A3_albedo/raw_data/',
    '**/*MOD10A1*.tif': 'results/MOD10A1_snow_cover/raw_data/',
    '**/*MOD10A1*.hdf': 'results/MOD10A1_snow_cover/raw_data/',
    '**/*MYD10A1*.tif': 'results/MYD10A1_aqua_snow/raw_data/',
    '**/*MYD10A1*.hdf': 'results/MYD10A1_aqua_snow/raw_data/',
    
    # Google Earth Engine exports -> appropriate directories
    'exports/**/*.csv': 'results/MCD43A3_albedo/raw_data/',
    'GEE_exports/**/*.csv': 'results/MCD43A3_albedo/raw_data/',
    'exports/**/*.tif': 'results/MCD43A3_albedo/raw_data/',
    'GEE_exports/**/*.tif': 'results/MCD43A3_albedo/raw_data/',
    
    # Analysis output directories
    'analysis_output/**/*': 'results/MCD43A3_albedo/',
    'analysis_results/**/*': 'results/MCD43A3_albedo/',
    
    # Log files -> metadata/processing_logs
    '**/*.log': 'results/metadata/processing_logs/',
}

def find_files_to_migrate(base_path, dry_run=False, verbose=False):
    """
    Find all files that need to be migrated based on the rules
    
    Args:
        base_path (str): Base directory to search
        dry_run (bool): If True, don't actually move files
        verbose (bool): Show detailed output
        
    Returns:
        list: List of (source, destination) tuples
    """
    migrations = []
    base_path = Path(base_path)
    
    for pattern, dest_dir in MIGRATION_RULES.items():
        if verbose:
            print(f"🔍 Searching for pattern: {pattern}")
            
        # Use glob to find matching files
        matches = list(base_path.glob(pattern))
        
        for match in matches:
            # Skip files already in results directory
            if 'results/' in str(match):
                continue
                
            # Create full destination path
            dest_path = base_path / dest_dir / match.name
            
            # Avoid duplicates and handle conflicts
            if dest_path.exists():
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                name_parts = dest_path.stem, timestamp, dest_path.suffix
                dest_path = dest_path.parent / f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
            
            migrations.append((match, dest_path))
            
            if verbose:
                print(f"  📁 {match} -> {dest_path}")
    
    return migrations

def create_backup(base_path, verbose=False):
    """
    Create a backup of the current state before migration
    
    Args:
        base_path (str): Base directory
        verbose (bool): Show detailed output
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = Path(base_path) / f"backup_pre_migration_{timestamp}"
    
    if verbose:
        print(f"💾 Creating backup at: {backup_dir}")
    
    # Backup important directories if they exist
    dirs_to_backup = ['exports', 'GEE_exports', 'analysis_output', 'analysis_results']
    
    for dir_name in dirs_to_backup:
        source_dir = Path(base_path) / dir_name
        if source_dir.exists():
            dest_dir = backup_dir / dir_name
            shutil.copytree(source_dir, dest_dir)
            if verbose:
                print(f"  ✅ Backed up: {source_dir}")
    
    # Backup individual files
    for pattern in ['*.png', '*.csv', '*.xlsx', '*.txt']:
        matches = list(Path(base_path).glob(pattern))
        if matches:
            files_backup = backup_dir / 'individual_files'
            files_backup.mkdir(parents=True, exist_ok=True)
            
            for match in matches:
                shutil.copy2(match, files_backup / match.name)
                if verbose:
                    print(f"  ✅ Backed up file: {match}")
    
    return backup_dir

def perform_migration(migrations, dry_run=False, verbose=False):
    """
    Perform the actual file migrations
    
    Args:
        migrations (list): List of (source, destination) tuples
        dry_run (bool): If True, don't actually move files
        verbose (bool): Show detailed output
    """
    if not migrations:
        print("📝 No files found to migrate.")
        return
    
    print(f"📦 Found {len(migrations)} files to migrate")
    
    for source, dest in migrations:
        # Ensure destination directory exists
        dest.parent.mkdir(parents=True, exist_ok=True)
        
        if dry_run:
            print(f"[DRY RUN] Would move: {source} -> {dest}")
        else:
            try:
                shutil.move(str(source), str(dest))
                if verbose:
                    print(f"✅ Moved: {source} -> {dest}")
            except Exception as e:
                print(f"❌ Error moving {source}: {e}")

def save_migration_log(migrations, base_path, dry_run=False):
    """
    Save a log of the migration for reference
    
    Args:
        migrations (list): List of (source, destination) tuples
        base_path (str): Base directory
        dry_run (bool): Whether this was a dry run
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_filename = f"migration_log_{timestamp}.txt"
    log_path = Path(base_path) / 'results' / 'metadata' / 'processing_logs' / log_filename
    
    # Ensure log directory exists
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write("Saskatchewan Glacier Albedo Analysis - Migration Log\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Migration Date: {datetime.now().isoformat()}\n")
        f.write(f"Mode: {'DRY RUN' if dry_run else 'ACTUAL MIGRATION'}\n")
        f.write(f"Files Processed: {len(migrations)}\n\n")
        
        f.write("Migration Details:\n")
        f.write("-" * 30 + "\n")
        
        for source, dest in migrations:
            f.write(f"{source} -> {dest}\n")
        
        f.write("\n" + "=" * 60 + "\n")
        f.write("Migration completed by migrate_to_organized_structure.py\n")
    
    print(f"📄 Migration log saved: {log_path}")

def main():
    """Main migration function"""
    parser = argparse.ArgumentParser(
        description="Migrate Saskatchewan glacier analysis outputs to organized structure"
    )
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be moved without actually moving files')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Show detailed migration steps')
    parser.add_argument('--base-path', default='.',
                       help='Base path of the project (default: current directory)')
    
    args = parser.parse_args()
    
    print("🔄 Saskatchewan Glacier Albedo Analysis - Structure Migration")
    print("=" * 65)
    
    base_path = Path(args.base_path).resolve()
    print(f"📍 Base path: {base_path}")
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be moved")
    
    # Find files to migrate
    print("\n1. Scanning for files to migrate...")
    migrations = find_files_to_migrate(base_path, args.dry_run, args.verbose)
    
    if not args.dry_run and migrations:
        # Create backup before migration
        print("\n2. Creating backup...")
        backup_dir = create_backup(base_path, args.verbose)
        print(f"✅ Backup created at: {backup_dir}")
    
    # Perform migration
    print("\n3. Performing migration...")
    perform_migration(migrations, args.dry_run, args.verbose)
    
    # Save migration log
    print("\n4. Saving migration log...")
    save_migration_log(migrations, base_path, args.dry_run)
    
    print("\n✅ Migration completed!")
    
    if args.dry_run:
        print("\n💡 Run without --dry-run to perform actual migration")
    else:
        print("\n📁 New structure:")
        print("   results/")
        print("   ├── MCD43A3_albedo/     (BRDF-Albedo data)")
        print("   ├── MOD10A1_snow_cover/ (Snow cover data)")
        print("   ├── MYD10A1_aqua_snow/  (Aqua snow data)")
        print("   ├── combined_analysis/   (Multi-product analysis)")
        print("   └── metadata/           (Logs and documentation)")

if __name__ == "__main__":
    main()