#!/usr/bin/env python
"""Detailed Phase 2 analysis - find exact methods lacking type hints."""

import re
import sys
from pathlib import Path

def analyze_service(filepath):
    """Analyze service file and return methods without return type hints."""
    
    content = filepath.read_text(encoding='utf-8')
    
    # Find all method definitions
    method_pattern = r'def (\w+)\s*\(([^)]*)\)([^:]*)'
    matches = list(re.finditer(method_pattern, content))
    
    methods_without_return = []
    
    for match in matches:
        method_name = match.group(1)
        params = match.group(2)
        rest = match.group(3)  # This includes the -> annotation if present
        
        # Skip private/magic methods and __init__
        if method_name.startswith('_'):
            continue
        
        # Check if has return type annotation
        has_return_type = '->' in rest
        
        if not has_return_type:
            methods_without_return.append(method_name)
    
    return methods_without_return


def main():
    """Find all methods without return type hints."""
    
    services_dir = Path(__file__).parent / 'app' / 'services'
    
    print("\n" + "="*70)
    print("PHASE 2 - DETAILED ANALYSIS: Methods without Return Type Hints")
    print("="*70 + "\n")
    
    total_without_types = 0
    
    services = sorted([
        f for f in services_dir.glob('*.py')
        if f.name not in ('__init__.py',)
    ])
    
    for service_file in services:
        methods = analyze_service(service_file)
        
        if methods:
            print(f"📄 {service_file.name}:")
            for method in methods:
                print(f"   - {method}()")
                total_without_types += 1
            print()
    
    print("="*70)
    print(f"Total methods without return types: {total_without_types}")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
