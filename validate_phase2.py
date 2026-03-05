#!/usr/bin/env python
"""Phase 2 Quality Code Validation - Type hints and docstring checker."""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent))


class CodeQualityValidator:
    """Validates type hints and docstrings in service modules."""
    
    def __init__(self, services_dir: Path):
        """Initialize validator."""
        self.services_dir = services_dir
        self.services = self._collect_services()
        
    def _collect_services(self) -> List[Path]:
        """Collect all service files."""
        return sorted([
            f for f in self.services_dir.glob('*.py')
            if f.name not in ('__init__.py', '__pycache__')
        ])
    
    def validate_all(self) -> Dict[str, Dict[str, any]]:
        """Validate all service modules."""
        
        print("\n" + "="*70)
        print("PHASE 2 - CODE QUALITY VALIDATION REPORT")
        print("="*70 + "\n")
        
        results = {}
        total_methods = 0
        documented_methods = 0
        type_hinted_methods = 0
        
        for service_file in self.services:
            print(f"📄 Analyzing: {service_file.name}")
            
            content = service_file.read_text(encoding='utf-8')
            
            # Extract class and method definitions
            methods = self._extract_methods(content)
            service_results = {
                'file': service_file.name,
                'methods_total': len(methods),
                'methods_documented': 0,
                'methods_type_hinted': 0,
                'methods': []
            }
            
            for method_name, method_code in methods:
                method_info = {
                    'name': method_name,
                    'has_docstring': self._has_docstring(method_code),
                    'has_return_type': self._has_return_type(method_code),
                    'has_parameter_types': self._has_parameter_types(method_code)
                }
                
                service_results['methods'].append(method_info)
                total_methods += 1
                
                if method_info['has_docstring']:
                    service_results['methods_documented'] += 1
                    documented_methods += 1
                    
                if method_info['has_return_type']:
                    service_results['methods_type_hinted'] += 1
                    type_hinted_methods += 1
            
            # Print service summary
            doc_pct = (service_results['methods_documented'] / len(methods) * 100) if methods else 0
            type_pct = (service_results['methods_type_hinted'] / len(methods) * 100) if methods else 0
            
            status_doc = "✅" if doc_pct == 100 else "⚠️ " if doc_pct >= 80 else "❌"
            status_type = "✅" if type_pct == 100 else "⚠️ " if type_pct >= 80 else "❌"
            
            print(f"  {status_doc} Docstrings: {service_results['methods_documented']}/{len(methods)} ({doc_pct:.0f}%)")
            print(f"  {status_type} Return Types: {service_results['methods_type_hinted']}/{len(methods)} ({type_pct:.0f}%)")
            
            results[service_file.stem] = service_results
            print()
        
        # Print overall summary
        print("="*70)
        print("OVERALL SUMMARY")
        print("="*70)
        print(f"Total methods analyzed: {total_methods}")
        print(f"Methods with docstrings: {documented_methods}/{total_methods} ({documented_methods/total_methods*100:.1f}%)")
        print(f"Methods with return types: {type_hinted_methods}/{total_methods} ({type_hinted_methods/total_methods*100:.1f}%)")
        
        # Final status
        print("\n" + "="*70)
        if documented_methods == total_methods and type_hinted_methods == total_methods:
            print("✅ PHASE 2 VALIDATION PASSED - All services meet quality standards!")
        elif documented_methods >= total_methods * 0.90:
            print("⚠️  PHASE 2 PARTIALLY COMPLETE - Most services meet quality standards")
        else:
            print("❌ PHASE 2 INCOMPLETE - There are still services that need improvement")
        print("="*70 + "\n")
        
        return results
    
    def _extract_methods(self, content: str) -> List[Tuple[str, str]]:
        """Extract method definitions from class."""
        methods = []
        
        # Find all method definitions: def method_name(
        pattern = r'def (\w+)\s*\('
        matches = re.finditer(pattern, content)
        
        method_positions = []
        for match in matches:
            method_name = match.group(1)
            if not method_name.startswith('_'):  # Skip private methods
                method_positions.append((match.start(), method_name))
        
        # Extract method code
        lines = content.split('\n')
        for i, (pos, method_name) in enumerate(method_positions):
            # Find starting line
            start_line = content[:pos].count('\n')
            
            # Find ending line (next method or end of file)
            if i + 1 < len(method_positions):
                next_pos = method_positions[i + 1][0]
                end_line = content[:next_pos].count('\n')
            else:
                end_line = len(lines)
            
            method_code = '\n'.join(lines[start_line:end_line])
            methods.append((method_name, method_code))
        
        return methods
    
    def _has_docstring(self, method_code: str) -> bool:
        """Check if method has docstring."""
        return '"""' in method_code or "'''" in method_code
    
    def _has_return_type(self, method_code: str) -> bool:
        """Check if method has return type annotation."""
        return '-> ' in method_code.split('\n')[0]  # Check first line (def statement)
    
    def _has_parameter_types(self, method_code: str) -> bool:
        """Check if method has parameter type annotations."""
        first_line = method_code.split('\n')[0]
        # Check for type annotations in parameters
        return ':' in first_line and '(' in first_line


def main():
    """Run validation."""
    services_dir = Path(__file__).parent / 'app' / 'services'
    
    if not services_dir.exists():
        print(f"❌ Services directory not found: {services_dir}")
        sys.exit(1)
    
    validator = CodeQualityValidator(services_dir)
    results = validator.validate_all()
    
    # Return success code if most services are good
    total_methods = sum(r['methods_total'] for r in results.values())
    documented = sum(r['methods_documented'] for r in results.values())
    
    if documented >= total_methods * 0.90:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
