#!/usr/bin/env python3
"""
MMI Metrics Analyzer (Tool 1)
=============================
Pythonプロジェクトのコードメトリクスを自動計測し、MMI基準のうち
1.3（プロポーション）と 2.2（循環依存）に必要なデータを生成する。

Usage:
    python metrics_analyzer.py /path/to/project [--output metrics_result.json]

Requirements:
    pip install radon networkx --break-system-packages
"""

import ast
import json
import os
import sys
import argparse
from pathlib import Path
from collections import defaultdict
from typing import Any

try:
    from radon.complexity import cc_visit
    from radon.raw import analyze as raw_analyze
    HAS_RADON = True
except ImportError:
    HAS_RADON = False

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
LARGE_CLASS_THRESHOLD = 300      # LOC
LARGE_METHOD_THRESHOLD = 50      # LOC
LARGE_PACKAGE_THRESHOLD = 30     # classes
HIGH_COMPLEXITY_THRESHOLD = 10   # cyclomatic complexity


def find_python_files(project_path: str) -> list[Path]:
    """プロジェクト内のPythonファイルを収集する（__pycache__, .venv等を除外）"""
    excluded = {
        "__pycache__", ".venv", "venv", ".env", "env",
        "node_modules", ".git", ".tox", ".mypy_cache",
        ".pytest_cache", "dist", "build", "egg-info",
    }
    files = []
    for root, dirs, filenames in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in excluded and not d.endswith(".egg-info")]
        for f in filenames:
            if f.endswith(".py"):
                files.append(Path(root) / f)
    return files


def get_package_name(filepath: Path, project_root: Path) -> str:
    """ファイルパスからパッケージ名（ディレクトリ）を取得する"""
    try:
        rel = filepath.parent.relative_to(project_root)
        parts = rel.parts
        return ".".join(parts) if parts else "(root)"
    except ValueError:
        return "(unknown)"


def get_module_name(filepath: Path, project_root: Path) -> str:
    """ファイルパスからモジュール名を取得する"""
    try:
        rel = filepath.relative_to(project_root)
        return str(rel.with_suffix("")).replace(os.sep, ".")
    except ValueError:
        return str(filepath)


# ---------------------------------------------------------------------------
# AST-based analysis
# ---------------------------------------------------------------------------
def analyze_file_ast(filepath: Path) -> dict[str, Any]:
    """AST解析でクラス・関数のサイズと構造を分析する"""
    try:
        source = filepath.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(filepath))
    except (SyntaxError, UnicodeDecodeError):
        return {"error": str(filepath), "classes": [], "functions": [], "loc": 0}

    lines = source.splitlines()
    total_loc = len([l for l in lines if l.strip() and not l.strip().startswith("#")])

    classes = []
    functions = []
    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            end = getattr(node, "end_lineno", node.lineno)
            class_loc = end - node.lineno + 1
            methods = [n for n in ast.walk(node) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
            classes.append({
                "name": node.name,
                "loc": class_loc,
                "method_count": len(methods),
                "lineno": node.lineno,
            })
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # トップレベル関数のみ（クラスメソッドも含む）
            end = getattr(node, "end_lineno", node.lineno)
            func_loc = end - node.lineno + 1
            functions.append({
                "name": node.name,
                "loc": func_loc,
                "lineno": node.lineno,
            })
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module.split(".")[0])

    return {
        "classes": classes,
        "functions": functions,
        "imports": list(set(imports)),
        "loc": total_loc,
    }


# ---------------------------------------------------------------------------
# Cyclomatic Complexity (radon)
# ---------------------------------------------------------------------------
def analyze_complexity(filepath: Path) -> list[dict]:
    """radon を使って循環的複雑度を計測する"""
    if not HAS_RADON:
        return []
    try:
        source = filepath.read_text(encoding="utf-8", errors="replace")
        results = cc_visit(source)
        return [
            {
                "name": r.name,
                "complexity": r.complexity,
                "classname": getattr(r, "classname", None),
                "lineno": r.lineno,
            }
            for r in results
        ]
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Import graph & cycle detection
# ---------------------------------------------------------------------------
def build_import_graph(
    files: list[Path], project_root: Path
) -> tuple[dict, dict]:
    """プロジェクト内のimportを解析し、モジュール間・パッケージ間の依存グラフを構築する"""
    module_imports = {}  # module -> [imported_modules]
    all_modules = set()

    for fp in files:
        mod = get_module_name(fp, project_root)
        all_modules.add(mod)
        try:
            source = fp.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source, filename=str(fp))
        except (SyntaxError, UnicodeDecodeError):
            module_imports[mod] = []
            continue

        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
        module_imports[mod] = list(imports)

    return module_imports, all_modules


def detect_cycles(module_imports: dict, all_modules: set, project_root: str) -> dict:
    """networkx で循環依存を検出する"""
    if not HAS_NETWORKX:
        return {"error": "networkx not installed", "class_cycles": [], "package_cycles": []}

    # モジュール（クラス）レベルのグラフ
    g_module = nx.DiGraph()
    for mod in all_modules:
        g_module.add_node(mod)
    for mod, imports in module_imports.items():
        for imp in imports:
            # プロジェクト内のモジュールのみ
            matching = [m for m in all_modules if m == imp or m.startswith(imp + ".") or imp.startswith(m + ".")]
            for target in matching:
                if target != mod:
                    g_module.add_edge(mod, target)

    module_cycles_raw = list(nx.simple_cycles(g_module))
    # 大きすぎるサイクルは集約
    module_cycles = [c for c in module_cycles_raw if len(c) <= 500]
    modules_in_cycles = set()
    for c in module_cycles:
        modules_in_cycles.update(c)

    # パッケージレベルのグラフ
    g_package = nx.DiGraph()
    pkg_edges = set()
    for mod, imports in module_imports.items():
        src_pkg = mod.rsplit(".", 1)[0] if "." in mod else "(root)"
        for imp in imports:
            matching = [m for m in all_modules if m == imp or m.startswith(imp + ".")]
            for target in matching:
                tgt_pkg = target.rsplit(".", 1)[0] if "." in target else "(root)"
                if src_pkg != tgt_pkg:
                    pkg_edges.add((src_pkg, tgt_pkg))

    for src, tgt in pkg_edges:
        g_package.add_edge(src, tgt)

    package_cycles_raw = list(nx.simple_cycles(g_package))
    package_cycles = [c for c in package_cycles_raw if len(c) <= 200]
    packages_in_cycles = set()
    for c in package_cycles:
        packages_in_cycles.update(c)

    return {
        "total_modules": len(all_modules),
        "modules_in_cycles": len(modules_in_cycles),
        "modules_in_cycles_pct": round(len(modules_in_cycles) / max(len(all_modules), 1) * 100, 2),
        "module_cycle_count": len(module_cycles),
        "max_module_cycle_size": max((len(c) for c in module_cycles), default=0),
        "avg_module_cycle_size": round(
            sum(len(c) for c in module_cycles) / max(len(module_cycles), 1), 1
        ),
        "total_packages": g_package.number_of_nodes(),
        "packages_in_cycles": len(packages_in_cycles),
        "packages_in_cycles_pct": round(
            len(packages_in_cycles) / max(g_package.number_of_nodes(), 1) * 100, 2
        ),
        "package_cycle_count": len(package_cycles),
        "max_package_cycle_size": max((len(c) for c in package_cycles), default=0),
        "avg_package_cycle_size": round(
            sum(len(c) for c in package_cycles) / max(len(package_cycles), 1), 1
        ),
        "sample_module_cycles": [c[:10] for c in sorted(module_cycles, key=len, reverse=True)[:5]],
        "sample_package_cycles": [c[:10] for c in sorted(package_cycles, key=len, reverse=True)[:5]],
    }


# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------
def analyze_project(project_path: str) -> dict:
    """プロジェクト全体を解析してメトリクスを収集する"""
    root = Path(project_path).resolve()
    files = find_python_files(str(root))

    if not files:
        return {"error": f"No Python files found in {project_path}"}

    # --- Per-file analysis ---
    all_classes = []
    all_functions = []
    all_complexities = []
    package_stats = defaultdict(lambda: {"loc": 0, "classes": 0, "files": 0})
    total_loc = 0

    for fp in files:
        ast_result = analyze_file_ast(fp)
        pkg = get_package_name(fp, root)

        total_loc += ast_result["loc"]
        package_stats[pkg]["loc"] += ast_result["loc"]
        package_stats[pkg]["files"] += 1

        for cls in ast_result["classes"]:
            cls["file"] = str(fp.relative_to(root))
            cls["package"] = pkg
            all_classes.append(cls)
            package_stats[pkg]["classes"] += 1

        for func in ast_result["functions"]:
            func["file"] = str(fp.relative_to(root))
            all_functions.append(func)

        complexity = analyze_complexity(fp)
        for c in complexity:
            c["file"] = str(fp.relative_to(root))
        all_complexities.extend(complexity)

    # --- Proportions (MMI 1.3) ---
    total_class_loc = sum(c["loc"] for c in all_classes)
    large_classes = [c for c in all_classes if c["loc"] >= LARGE_CLASS_THRESHOLD]
    large_class_loc = sum(c["loc"] for c in large_classes)
    large_class_pct = round(large_class_loc / max(total_loc, 1) * 100, 2)

    large_methods = [f for f in all_functions if f["loc"] >= LARGE_METHOD_THRESHOLD]
    large_method_loc = sum(f["loc"] for f in large_methods)
    large_method_pct = round(large_method_loc / max(total_loc, 1) * 100, 2)

    large_packages = [
        p for p, s in package_stats.items()
        if s["classes"] >= LARGE_PACKAGE_THRESHOLD
    ]
    total_classes = len(all_classes)
    classes_in_large_pkgs = sum(
        package_stats[p]["classes"] for p in large_packages
    )
    large_package_pct = round(classes_in_large_pkgs / max(total_classes, 1) * 100, 2)

    high_complexity_methods = [c for c in all_complexities if c["complexity"] >= HIGH_COMPLEXITY_THRESHOLD]
    total_methods_measured = len(all_complexities)
    high_complexity_pct = round(
        len(high_complexity_methods) / max(total_methods_measured, 1) * 100, 2
    )

    # --- Package size ratios (MMI 1.1.3, 1.1.4) ---
    pkg_locs = [s["loc"] for s in package_stats.values() if s["loc"] > 0]
    if len(pkg_locs) >= 2:
        pkg_size_ratio = round((max(pkg_locs) / max(min(pkg_locs), 1)) / len(pkg_locs), 2)
    else:
        pkg_size_ratio = 0

    # --- Cycle detection (MMI 2.2) ---
    module_imports, all_modules = build_import_graph(files, root)
    cycles = detect_cycles(module_imports, all_modules, str(root))

    # --- Compile results ---
    result = {
        "project_path": str(root),
        "summary": {
            "total_files": len(files),
            "total_loc": total_loc,
            "total_classes": total_classes,
            "total_functions": len(all_functions),
            "total_packages": len(package_stats),
        },
        "proportions": {
            "large_class_pct": large_class_pct,
            "large_class_count": len(large_classes),
            "large_class_threshold_loc": LARGE_CLASS_THRESHOLD,
            "large_method_pct": large_method_pct,
            "large_method_count": len(large_methods),
            "large_method_threshold_loc": LARGE_METHOD_THRESHOLD,
            "large_package_pct": large_package_pct,
            "large_package_count": len(large_packages),
            "large_package_threshold_classes": LARGE_PACKAGE_THRESHOLD,
            "high_complexity_pct": high_complexity_pct,
            "high_complexity_count": len(high_complexity_methods),
            "high_complexity_threshold": HIGH_COMPLEXITY_THRESHOLD,
            "total_methods_measured": total_methods_measured,
        },
        "size_ratios": {
            "package_size_ratio": pkg_size_ratio,
            "package_loc_max": max(pkg_locs) if pkg_locs else 0,
            "package_loc_min": min(pkg_locs) if pkg_locs else 0,
            "package_count": len(pkg_locs),
        },
        "cycles": cycles,
        "top_large_classes": sorted(large_classes, key=lambda c: c["loc"], reverse=True)[:10],
        "top_complex_methods": sorted(
            high_complexity_methods, key=lambda c: c["complexity"], reverse=True
        )[:10],
        "package_details": {
            pkg: {
                "loc": stats["loc"],
                "classes": stats["classes"],
                "files": stats["files"],
            }
            for pkg, stats in sorted(package_stats.items(), key=lambda x: x[1]["loc"], reverse=True)
        },
    }

    return result


def main():
    parser = argparse.ArgumentParser(description="MMI Metrics Analyzer (Tool 1)")
    parser.add_argument("project_path", help="Path to the Python project root")
    parser.add_argument("--output", "-o", default="metrics_result.json", help="Output JSON file")
    args = parser.parse_args()

    if not os.path.isdir(args.project_path):
        print(f"Error: {args.project_path} is not a valid directory", file=sys.stderr)
        sys.exit(1)

    print(f"Analyzing project: {args.project_path}")
    result = analyze_project(args.project_path)

    output_path = Path(args.output)
    output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Results written to: {output_path}")

    # Summary
    s = result.get("summary", {})
    p = result.get("proportions", {})
    c = result.get("cycles", {})
    print(f"\n=== Summary ===")
    print(f"  Files: {s.get('total_files', 0)}, LOC: {s.get('total_loc', 0)}")
    print(f"  Classes: {s.get('total_classes', 0)}, Functions: {s.get('total_functions', 0)}")
    print(f"  Large classes: {p.get('large_class_pct', 0)}%, Large methods: {p.get('large_method_pct', 0)}%")
    print(f"  High complexity: {p.get('high_complexity_pct', 0)}%")
    print(f"  Modules in cycles: {c.get('modules_in_cycles_pct', 'N/A')}%")
    print(f"  Packages in cycles: {c.get('packages_in_cycles_pct', 'N/A')}%")


if __name__ == "__main__":
    main()
