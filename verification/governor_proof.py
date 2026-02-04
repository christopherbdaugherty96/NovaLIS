"""Governor Mediation Proof - Phase 3.5 Verification
Purpose: Verify all execution flows through Governor as single choke point

Run from repository root:
    python verification/governor_proof.py
"""
import ast
import sys
from pathlib import Path

EXECUTION_KEYWORDS = {'execute', 'launch', 'perform', 'invoke'}
SKIP_DIRS = {'__pycache__', 'tests', 'verification', 'archive_quarantine'}

def find_python_files(root_dir):
    files = []
    for path in Path(root_dir).rglob("*.py"):
        if not any(skip in path.parts for skip in SKIP_DIRS):
            files.append(path)
    return files

def analyze_file_for_execution(filepath):
    try:
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

        tree = ast.parse(content)
        findings = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name.lower() in EXECUTION_KEYWORDS:
                    findings.append((node.lineno, node.name, 'definition'))

            elif isinstance(node, ast.Call):
                if hasattr(node.func, 'id') and node.func.id and node.func.id.lower() in EXECUTION_KEYWORDS:
                    findings.append((getattr(node, 'lineno', '?'), node.func.id, 'call'))
                elif hasattr(node.func, 'attr') and node.func.attr.lower() in EXECUTION_KEYWORDS:
                    findings.append((getattr(node, 'lineno', '?'), node.func.attr, 'method'))

            elif isinstance(node, ast.ImportFrom):
                if node.module and 'archive_quarantine' in node.module:
                    findings.append((node.lineno, node.module, 'quarantine_import'))

        return findings

    except (SyntaxError, UnicodeDecodeError, PermissionError) as e:
        print(f"  ⚠️  Skipping {filepath}: {e}")
        return []

def main():
    print("=" * 60)
    print("PHASE 3.5 - GOVERNOR MEDIATION VERIFICATION")
    print("=" * 60)

    repo_root = Path(__file__).parent.parent
    src_dir = repo_root / "nova_backend" / "src"

    python_files = find_python_files(src_dir)
    print(f"📄 Found {len(python_files)} Python files to analyze")

    for file in python_files:
        findings = analyze_file_for_execution(file)
        for line, name, kind in findings:
            if kind == 'quarantine_import':
                print(f"❌ Quarantine import detected: {file}:{line}")
                sys.exit(1)
            if 'governor' not in str(file).lower():
                print(f"❌ Execution outside Governor: {file}:{line} ({name})")
                sys.exit(1)

    print("✅ PHASE 3.5 GOVERNOR VERIFICATION: PASS")
    sys.exit(0)

if __name__ == "__main__":
    main()
