#!/usr/bin/env python3
"""
MMI Architecture Analyzer (Tool 2)
===================================
Pythonプロジェクトのアーキテクチャ構造を解析し、MMI基準のうち
1.1（モジュール化）、1.2（インターフェース）、2.1（レイヤー違反）、
3.1-3.2（パターン一貫性）に必要なデータを生成する。

Usage:
    python architecture_analyzer.py /path/to/project [--config architecture.json] [--output architecture_result.json]

Config (architecture.json) example:
    {
        "layers": ["presentation", "application", "domain", "infrastructure"],
        "layer_direction": "top_to_bottom",
        "domain_modules": ["order", "inventory", "customer", "payment"],
        "pattern_keywords": {
            "Controller": "presentation",
            "Service": "application",
            "Repository": "infrastructure",
            "Entity": "domain",
            "Model": "domain",
            "DTO": "application",
            "UseCase": "application",
            "Handler": "application",
            "Factory": "domain",
            "ValueObject": "domain",
            "Gateway": "infrastructure",
            "Adapter": "infrastructure",
            "Port": "domain",
            "Router": "presentation",
            "View": "presentation",
            "Serializer": "presentation"
        }
    }
"""

import ast
import json
import os
import re
import sys
import argparse
from pathlib import Path
from collections import defaultdict
from typing import Any, Optional

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False


# ---------------------------------------------------------------------------
# Default configuration
# ---------------------------------------------------------------------------
DEFAULT_LAYERS = ["presentation", "application", "domain", "infrastructure"]

DEFAULT_PATTERN_KEYWORDS = {
    # Class name suffix/contains -> pattern layer
    "Controller": "presentation",
    "View": "presentation",
    "Router": "presentation",
    "Serializer": "presentation",
    "Handler": "application",
    "Service": "application",
    "UseCase": "application",
    "Interactor": "application",
    "DTO": "application",
    "Command": "application",
    "Query": "application",
    "Entity": "domain",
    "Model": "domain",
    "ValueObject": "domain",
    "DomainEvent": "domain",
    "Factory": "domain",
    "Aggregate": "domain",
    "Port": "domain",
    "Repository": "infrastructure",
    "Gateway": "infrastructure",
    "Adapter": "infrastructure",
    "Client": "infrastructure",
    "Mapper": "infrastructure",
}

DEFAULT_LAYER_KEYWORDS = {
    # Directory name patterns -> layer
    "api": "presentation",
    "views": "presentation",
    "controllers": "presentation",
    "routes": "presentation",
    "routers": "presentation",
    "endpoints": "presentation",
    "schemas": "presentation",
    "services": "application",
    "usecases": "application",
    "use_cases": "application",
    "application": "application",
    "handlers": "application",
    "commands": "application",
    "queries": "application",
    "domain": "domain",
    "models": "domain",
    "entities": "domain",
    "core": "domain",
    "repositories": "infrastructure",
    "infrastructure": "infrastructure",
    "adapters": "infrastructure",
    "gateways": "infrastructure",
    "db": "infrastructure",
    "database": "infrastructure",
    "persistence": "infrastructure",
    "external": "infrastructure",
}


def find_python_files(project_path: str) -> list[Path]:
    """プロジェクト内のPythonファイルを収集する"""
    excluded = {
        "__pycache__", ".venv", "venv", ".env", "env",
        "node_modules", ".git", ".tox", ".mypy_cache",
        ".pytest_cache", "dist", "build", "egg-info",
        "tests", "test", "migrations",
    }
    files = []
    for root, dirs, filenames in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in excluded and not d.endswith(".egg-info")]
        for f in filenames:
            if f.endswith(".py") and not f.startswith("test_"):
                files.append(Path(root) / f)
    return files


def load_config(config_path: Optional[str]) -> dict:
    """設定ファイルを読み込む。なければデフォルトを使用する。"""
    if config_path and os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        config.setdefault("layers", DEFAULT_LAYERS)
        config.setdefault("pattern_keywords", DEFAULT_PATTERN_KEYWORDS)
        config.setdefault("layer_keywords", DEFAULT_LAYER_KEYWORDS)
        config.setdefault("domain_modules", [])
        return config
    return {
        "layers": DEFAULT_LAYERS,
        "pattern_keywords": DEFAULT_PATTERN_KEYWORDS,
        "layer_keywords": DEFAULT_LAYER_KEYWORDS,
        "domain_modules": [],
    }


# ---------------------------------------------------------------------------
# Layer classification
# ---------------------------------------------------------------------------
def classify_file_to_layer(
    filepath: Path, project_root: Path, config: dict
) -> Optional[str]:
    """ファイルを技術レイヤーに分類する（ディレクトリ名ベース）"""
    try:
        rel = filepath.relative_to(project_root)
    except ValueError:
        return None

    parts = [p.lower() for p in rel.parts[:-1]]  # ディレクトリ部分のみ
    layer_keywords = config.get("layer_keywords", DEFAULT_LAYER_KEYWORDS)

    for part in parts:
        if part in layer_keywords:
            return layer_keywords[part]
    return None


def classify_file_to_domain(
    filepath: Path, project_root: Path, config: dict
) -> Optional[str]:
    """ファイルをドメインモジュールに分類する"""
    try:
        rel = filepath.relative_to(project_root)
    except ValueError:
        return None

    parts = [p.lower() for p in rel.parts[:-1]]
    domain_modules = [m.lower() for m in config.get("domain_modules", [])]

    if domain_modules:
        for part in parts:
            if part in domain_modules:
                return part
    else:
        # ドメインモジュール未定義の場合、トップレベルディレクトリを使用
        if len(rel.parts) > 1:
            return rel.parts[0].lower()
    return None


# ---------------------------------------------------------------------------
# Pattern classification
# ---------------------------------------------------------------------------
def classify_classes_to_patterns(
    filepath: Path, config: dict
) -> list[dict]:
    """ファイル内のクラスをパターンに分類する"""
    try:
        source = filepath.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(filepath))
    except (SyntaxError, UnicodeDecodeError):
        return []

    pattern_keywords = config.get("pattern_keywords", DEFAULT_PATTERN_KEYWORDS)
    results = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            end = getattr(node, "end_lineno", node.lineno)
            loc = end - node.lineno + 1
            pattern = None

            # クラス名からパターンを推定
            for keyword, layer in pattern_keywords.items():
                if keyword.lower() in node.name.lower():
                    pattern = keyword
                    break

            # デコレータからも推定
            if not pattern:
                for decorator in node.decorator_list:
                    dec_name = ""
                    if isinstance(decorator, ast.Name):
                        dec_name = decorator.id
                    elif isinstance(decorator, ast.Attribute):
                        dec_name = decorator.attr
                    for keyword in pattern_keywords:
                        if keyword.lower() in dec_name.lower():
                            pattern = keyword
                            break

            # 継承元からも推定
            if not pattern:
                for base in node.bases:
                    base_name = ""
                    if isinstance(base, ast.Name):
                        base_name = base.id
                    elif isinstance(base, ast.Attribute):
                        base_name = base.attr
                    for keyword in pattern_keywords:
                        if keyword.lower() in base_name.lower():
                            pattern = keyword
                            break

            results.append({
                "name": node.name,
                "pattern": pattern,
                "pattern_layer": pattern_keywords.get(pattern) if pattern else None,
                "loc": loc,
                "lineno": node.lineno,
            })

    return results


# ---------------------------------------------------------------------------
# Import dependency analysis
# ---------------------------------------------------------------------------
def extract_imports(filepath: Path, project_root: Path) -> list[str]:
    """ファイルのimportを解析する"""
    try:
        source = filepath.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(filepath))
    except (SyntaxError, UnicodeDecodeError):
        return []

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
    return imports


def get_module_name(filepath: Path, project_root: Path) -> str:
    """ファイルパスからモジュール名を取得する"""
    try:
        rel = filepath.relative_to(project_root)
        return str(rel.with_suffix("")).replace(os.sep, ".")
    except ValueError:
        return str(filepath)


# ---------------------------------------------------------------------------
# Layer violation detection
# ---------------------------------------------------------------------------
def detect_layer_violations(
    files: list[Path],
    project_root: Path,
    config: dict,
) -> dict:
    """レイヤー間の依存方向を分析し、違反（逆方向参照）を検出する"""
    layers = config["layers"]
    layer_order = {layer: idx for idx, layer in enumerate(layers)}  # 上位=小, 下位=大

    file_layers = {}
    for fp in files:
        layer = classify_file_to_layer(fp, project_root, config)
        if layer:
            file_layers[get_module_name(fp, project_root)] = layer

    violations = []
    total_cross_layer_deps = 0
    all_modules = set(get_module_name(fp, project_root) for fp in files)

    for fp in files:
        src_mod = get_module_name(fp, project_root)
        src_layer = file_layers.get(src_mod)
        if not src_layer:
            continue

        imports = extract_imports(fp, project_root)
        for imp in imports:
            # プロジェクト内のモジュールにマッチするものを探す
            for tgt_mod in all_modules:
                if tgt_mod == imp or tgt_mod.startswith(imp + ".") or imp.startswith(tgt_mod + "."):
                    tgt_layer = file_layers.get(tgt_mod)
                    if tgt_layer and tgt_layer != src_layer:
                        total_cross_layer_deps += 1
                        src_order = layer_order.get(src_layer, -1)
                        tgt_order = layer_order.get(tgt_layer, -1)
                        if src_order > tgt_order:
                            # 下位レイヤーから上位レイヤーへの参照 = 違反
                            violations.append({
                                "source_module": src_mod,
                                "source_layer": src_layer,
                                "target_module": tgt_mod,
                                "target_layer": tgt_layer,
                                "type": "upward_reference",
                            })
                    break

    violation_pct = round(
        len(violations) / max(total_cross_layer_deps, 1) * 100, 2
    )

    return {
        "total_cross_layer_deps": total_cross_layer_deps,
        "violation_count": len(violations),
        "violation_pct": violation_pct,
        "violations": violations[:50],  # 最大50件
    }


# ---------------------------------------------------------------------------
# Interface analysis
# ---------------------------------------------------------------------------
def analyze_interfaces(
    files: list[Path], project_root: Path, config: dict
) -> dict:
    """モジュールのインターフェース違反を分析する（__init__.py, ABC の使用状況）"""
    packages = defaultdict(lambda: {"has_init": False, "has_abc": False, "files": 0, "public_imports": 0})

    for fp in files:
        try:
            rel = fp.relative_to(project_root)
        except ValueError:
            continue

        pkg = str(rel.parent).replace(os.sep, ".")
        packages[pkg]["files"] += 1

        if fp.name == "__init__.py":
            packages[pkg]["has_init"] = True
            try:
                source = fp.read_text(encoding="utf-8", errors="replace")
                # __all__ の定義チェック
                if "__all__" in source:
                    packages[pkg]["public_imports"] += 1
            except Exception:
                pass

        # ABC使用のチェック
        try:
            source = fp.read_text(encoding="utf-8", errors="replace")
            if "ABC" in source or "abstractmethod" in source or "Protocol" in source:
                packages[pkg]["has_abc"] = True
        except Exception:
            pass

    total_pkgs = len(packages)
    pkgs_without_interface = sum(
        1 for p in packages.values()
        if p["files"] > 1 and not p["has_init"] and not p["has_abc"]
    )
    multi_file_pkgs = sum(1 for p in packages.values() if p["files"] > 1)
    violation_pct = round(
        pkgs_without_interface / max(multi_file_pkgs, 1) * 100, 2
    )

    return {
        "total_packages": total_pkgs,
        "multi_file_packages": multi_file_pkgs,
        "packages_without_interface": pkgs_without_interface,
        "interface_violation_pct": violation_pct,
        "package_details": {
            pkg: stats for pkg, stats in sorted(
                packages.items(), key=lambda x: x[1]["files"], reverse=True
            )[:20]
        },
    }


# ---------------------------------------------------------------------------
# Domain module analysis
# ---------------------------------------------------------------------------
def analyze_domain_modules(
    files: list[Path], project_root: Path, config: dict
) -> dict:
    """ドメインモジュールの構造を分析する"""
    domain_stats = defaultdict(lambda: {"loc": 0, "files": 0, "classes": 0})
    unclassified_loc = 0
    total_loc = 0

    for fp in files:
        try:
            source = fp.read_text(encoding="utf-8", errors="replace")
            lines = source.splitlines()
            loc = len([l for l in lines if l.strip() and not l.strip().startswith("#")])
        except Exception:
            loc = 0

        total_loc += loc
        domain = classify_file_to_domain(fp, project_root, config)

        if domain:
            domain_stats[domain]["loc"] += loc
            domain_stats[domain]["files"] += 1
        else:
            unclassified_loc += loc

    # レイヤー別集計
    layer_stats = defaultdict(lambda: {"loc": 0, "files": 0})
    for fp in files:
        try:
            source = fp.read_text(encoding="utf-8", errors="replace")
            lines = source.splitlines()
            loc = len([l for l in lines if l.strip() and not l.strip().startswith("#")])
        except Exception:
            loc = 0

        layer = classify_file_to_layer(fp, project_root, config)
        if layer:
            layer_stats[layer]["loc"] += loc
            layer_stats[layer]["files"] += 1

    # Allocation percentages
    domain_allocated_loc = sum(s["loc"] for s in domain_stats.values())
    domain_allocation_pct = round(domain_allocated_loc / max(total_loc, 1) * 100, 2)

    layer_allocated_loc = sum(s["loc"] for s in layer_stats.values())
    layer_allocation_pct = round(layer_allocated_loc / max(total_loc, 1) * 100, 2)

    # Size ratios
    domain_locs = [s["loc"] for s in domain_stats.values() if s["loc"] > 0]
    if len(domain_locs) >= 2:
        domain_size_ratio = round(
            (max(domain_locs) / max(min(domain_locs), 1)) / len(domain_locs), 2
        )
    else:
        domain_size_ratio = 0

    layer_locs = [s["loc"] for s in layer_stats.values() if s["loc"] > 0]
    if len(layer_locs) >= 2:
        layer_size_ratio = round(
            (max(layer_locs) / max(min(layer_locs), 1)) / len(layer_locs), 2
        )
    else:
        layer_size_ratio = 0

    return {
        "total_loc": total_loc,
        "domain_allocation_pct": domain_allocation_pct,
        "layer_allocation_pct": layer_allocation_pct,
        "domain_size_ratio": domain_size_ratio,
        "layer_size_ratio": layer_size_ratio,
        "domain_modules": {
            d: dict(s) for d, s in sorted(
                domain_stats.items(), key=lambda x: x[1]["loc"], reverse=True
            )
        },
        "layer_modules": {
            l: dict(s) for l, s in sorted(
                layer_stats.items(), key=lambda x: x[1]["loc"], reverse=True
            )
        },
    }


# ---------------------------------------------------------------------------
# Pattern consistency analysis
# ---------------------------------------------------------------------------
def analyze_pattern_consistency(
    files: list[Path], project_root: Path, config: dict
) -> dict:
    """パターン一貫性を分析する"""
    all_classes = []
    total_loc = 0

    for fp in files:
        classes = classify_classes_to_patterns(fp, config)
        for cls in classes:
            cls["file"] = str(fp.relative_to(project_root))
            all_classes.append(cls)
            total_loc += cls["loc"]

    classified = [c for c in all_classes if c["pattern"] is not None]
    classified_loc = sum(c["loc"] for c in classified)
    pattern_allocation_pct = round(classified_loc / max(total_loc, 1) * 100, 2)

    # Pattern distribution
    pattern_dist = defaultdict(lambda: {"count": 0, "loc": 0})
    for c in classified:
        p = c["pattern"]
        pattern_dist[p]["count"] += 1
        pattern_dist[p]["loc"] += c["loc"]

    # Pattern layer cycle detection
    pattern_layer_deps = set()
    layers = config["layers"]
    layer_order = {layer: idx for idx, layer in enumerate(layers)}

    pattern_violations = 0
    total_pattern_deps = 0

    for fp in files:
        classes = classify_classes_to_patterns(fp, config)
        src_layers = set(c["pattern_layer"] for c in classes if c["pattern_layer"])
        imports = extract_imports(fp, project_root)

        for imp_file in files:
            imp_mod = get_module_name(imp_file, project_root)
            if any(imp_mod.startswith(imp) or imp.startswith(imp_mod) for imp in imports):
                tgt_classes = classify_classes_to_patterns(imp_file, config)
                tgt_layers = set(c["pattern_layer"] for c in tgt_classes if c["pattern_layer"])
                for sl in src_layers:
                    for tl in tgt_layers:
                        if sl != tl:
                            total_pattern_deps += 1
                            s_ord = layer_order.get(sl, -1)
                            t_ord = layer_order.get(tl, -1)
                            if s_ord > t_ord:
                                pattern_violations += 1

    pattern_violation_pct = round(
        pattern_violations / max(total_pattern_deps, 1) * 100, 2
    )

    return {
        "total_classes": len(all_classes),
        "classified_classes": len(classified),
        "unclassified_classes": len(all_classes) - len(classified),
        "pattern_allocation_pct": pattern_allocation_pct,
        "pattern_violation_pct": pattern_violation_pct,
        "total_pattern_deps": total_pattern_deps,
        "pattern_violations": pattern_violations,
        "pattern_distribution": {
            p: dict(s) for p, s in sorted(
                pattern_dist.items(), key=lambda x: x[1]["loc"], reverse=True
            )
        },
        "unclassified_samples": [
            {"name": c["name"], "file": c["file"]}
            for c in all_classes if c["pattern"] is None
        ][:20],
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def analyze_architecture(project_path: str, config_path: Optional[str] = None) -> dict:
    """アーキテクチャ全体を分析する"""
    root = Path(project_path).resolve()
    config = load_config(config_path)
    files = find_python_files(str(root))

    if not files:
        return {"error": f"No Python files found in {project_path}"}

    domain = analyze_domain_modules(files, root, config)
    interfaces = analyze_interfaces(files, root, config)
    layer_violations = detect_layer_violations(files, root, config)
    patterns = analyze_pattern_consistency(files, root, config)

    return {
        "project_path": str(root),
        "config_used": {
            "layers": config["layers"],
            "domain_modules": config.get("domain_modules", []),
            "config_file": config_path or "(default)",
        },
        "domain_and_layers": domain,
        "interfaces": interfaces,
        "layer_violations": layer_violations,
        "pattern_consistency": patterns,
    }


def main():
    parser = argparse.ArgumentParser(description="MMI Architecture Analyzer (Tool 2)")
    parser.add_argument("project_path", help="Path to the Python project root")
    parser.add_argument("--config", "-c", default=None, help="Architecture config JSON")
    parser.add_argument("--output", "-o", default="architecture_result.json", help="Output JSON file")
    args = parser.parse_args()

    if not os.path.isdir(args.project_path):
        print(f"Error: {args.project_path} is not a valid directory", file=sys.stderr)
        sys.exit(1)

    print(f"Analyzing architecture: {args.project_path}")
    result = analyze_architecture(args.project_path, args.config)

    output_path = Path(args.output)
    output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Results written to: {output_path}")

    d = result.get("domain_and_layers", {})
    lv = result.get("layer_violations", {})
    p = result.get("pattern_consistency", {})
    i = result.get("interfaces", {})

    print(f"\n=== Architecture Summary ===")
    print(f"  Domain allocation: {d.get('domain_allocation_pct', 0)}%")
    print(f"  Layer allocation: {d.get('layer_allocation_pct', 0)}%")
    print(f"  Layer violations: {lv.get('violation_pct', 0)}% ({lv.get('violation_count', 0)} violations)")
    print(f"  Interface violations: {i.get('interface_violation_pct', 0)}%")
    print(f"  Pattern allocation: {p.get('pattern_allocation_pct', 0)}%")
    print(f"  Pattern violations: {p.get('pattern_violation_pct', 0)}%")


if __name__ == "__main__":
    main()
