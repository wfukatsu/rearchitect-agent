#!/usr/bin/env python3
"""
MMI Calculator (Tool 3)
========================
Metrics Analyzer (Tool 1) と Architecture Analyzer (Tool 2) の結果を統合し、
Dr. Carola Lilienthal の MMI スコアリングテーブルに基づいてスコアを算出する。

Usage:
    python mmi_calculator.py --metrics metrics_result.json --architecture architecture_result.json [--reviewer reviewer_input.json] [--output-dir .]

Output:
    mmi_scores.json  - 全基準のスコアと最終MMI
    mmi_report.md    - Markdownレポート
"""

import json
import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Any, Optional


# ===========================================================================
# MMI Scoring Thresholds (from Dr. Carola Lilienthal's table)
# ===========================================================================
# Each entry: (criterion_id, direction, thresholds[0..10])
# direction: "asc" = higher value -> higher score, "desc" = lower value -> higher score

SCORING_TABLE = {
    # --- 1. Modularity (45%) ---
    # 1.1 Domain and technical modularization (25%)
    "1.1.1": {"direction": "asc",  "thresholds": [54, 54, 58, 62, 66, 70, 74, 78, 82, 86, 90]},
    "1.1.2": {"direction": "asc",  "thresholds": [75, 75, 77.5, 80, 82.5, 85, 87.5, 90, 92.5, 95, 97.5]},
    "1.1.3": {"direction": "desc", "thresholds": [7.5, 7.5, 5, 3.5, 2.5, 2, 1.5, 1.1, 0.85, 0.65, 0.5]},
    "1.1.4": {"direction": "desc", "thresholds": [16.5, 16.5, 11, 7.5, 5, 3.5, 2.5, 2, 1.5, 1.1, 0.85]},
    "1.1.5": {"direction": "reviewer", "thresholds": None},  # No=0, partial=5, Yes=10
    "1.1.6": {"direction": "reviewer", "thresholds": None},

    # 1.2 Internal Interfaces (10%)
    "1.2.1": {"direction": "desc", "thresholds": [6.5, 6.5, 4, 2.5, 1.5, 1, 0.65, 0.4, 0.25, 0.15, 0.1]},
    "1.2.2": {"direction": "reviewer", "thresholds": None},

    # 1.3 Proportions (10%)
    "1.3.1": {"direction": "desc", "thresholds": [23, 23, 18, 13.5, 10.5, 8, 6, 4.75, 3.5, 2.75, 2]},
    "1.3.2": {"direction": "desc", "thresholds": [23, 23, 18, 13.5, 10.5, 8, 6, 4.75, 3.5, 2.75, 2]},
    "1.3.3": {"direction": "desc", "thresholds": [23, 23, 18, 13.5, 10.5, 8, 6, 4.75, 3.5, 2.75, 2]},
    "1.3.4": {"direction": "desc", "thresholds": [3.6, 3.6, 2.6, 1.9, 1.4, 1, 0.75, 0.5, 0.4, 0.3, 0.2]},

    # --- 2. Hierarchy (30%) ---
    # 2.1 Technical and domain layering (15%)
    "2.1.1": {"direction": "desc", "thresholds": [6.5, 6.5, 4, 2.5, 1.5, 1, 0.65, 0.4, 0.25, 0.15, 0.1]},
    "2.1.2": {"direction": "desc", "thresholds": [14, 14, 9.6, 6.5, 4.5, 3.2, 2.25, 1.5, 1.1, 0.75, 0.5]},

    # 2.2 Class and package cycles (15%)
    "2.2.1": {"direction": "desc", "thresholds": [25, 25, 22.5, 20, 17.5, 15, 12.5, 10, 7.5, 5, 2.5]},
    "2.2.2": {"direction": "desc", "thresholds": [50, 50, 45, 40, 35, 30, 25, 20, 15, 10, 5]},
    "2.2.3": {"direction": "desc", "thresholds": [106, 106, 82, 62, 48, 37, 29, 22, 17, 13, 10]},
    "2.2.4": {"direction": "desc", "thresholds": [37, 37, 30, 24, 19, 15, 12, 10, 8, 6, 5]},

    # --- 3. Pattern Consistency (25%) ---
    "3.1":   {"direction": "asc",  "thresholds": [54.5, 54.5, 59, 63.5, 68, 72.5, 77, 81.5, 86, 90.5, 95]},
    "3.2":   {"direction": "desc", "thresholds": [7.5, 7.5, 5, 3.5, 2.5, 2, 1.5, 1.1, 0.85, 0.65, 0.5]},
    "3.3":   {"direction": "reviewer", "thresholds": None},
    "3.4":   {"direction": "reviewer", "thresholds": None},
}

# Category structure with weights
CATEGORIES = {
    "1_modularity": {
        "name": "Modularity",
        "name_ja": "モジュール性",
        "weight": 0.45,
        "subcategories": {
            "1.1": {
                "name": "Domain & Technical Modularization",
                "name_ja": "ドメイン・技術的モジュール化",
                "weight_within": 25 / 45,
                "criteria": ["1.1.1", "1.1.2", "1.1.3", "1.1.4", "1.1.5", "1.1.6"],
            },
            "1.2": {
                "name": "Internal Interfaces",
                "name_ja": "内部インターフェース",
                "weight_within": 10 / 45,
                "criteria": ["1.2.1", "1.2.2"],
            },
            "1.3": {
                "name": "Proportions",
                "name_ja": "プロポーション（均衡性）",
                "weight_within": 10 / 45,
                "criteria": ["1.3.1", "1.3.2", "1.3.3", "1.3.4"],
            },
        },
    },
    "2_hierarchy": {
        "name": "Hierarchy",
        "name_ja": "階層性",
        "weight": 0.30,
        "subcategories": {
            "2.1": {
                "name": "Technical & Domain Layering",
                "name_ja": "技術・ドメインレイヤリング",
                "weight_within": 15 / 30,
                "criteria": ["2.1.1", "2.1.2"],
            },
            "2.2": {
                "name": "Class & Package Cycles",
                "name_ja": "クラス・パッケージ循環",
                "weight_within": 15 / 30,
                "criteria": ["2.2.1", "2.2.2", "2.2.3", "2.2.4"],
            },
        },
    },
    "3_pattern": {
        "name": "Pattern Consistency",
        "name_ja": "パターン一貫性",
        "weight": 0.25,
        "subcategories": {
            "3": {
                "name": "Pattern Consistency",
                "name_ja": "パターン一貫性",
                "weight_within": 1.0,
                "criteria": ["3.1", "3.2", "3.3", "3.4"],
            },
        },
    },
}

CRITERIA_LABELS = {
    "1.1.1": "ドメインモジュールへのソースコード割当率 (%)",
    "1.1.2": "技術レイヤーへのソースコード割当率 (%)",
    "1.1.3": "ドメインモジュールのサイズ比 (LoC max/min)/数",
    "1.1.4": "技術レイヤーのサイズ比 (LoC max/min)/数",
    "1.1.5": "責務の明確さ (Reviewer)",
    "1.1.6": "マッピングの適切さ (Reviewer)",
    "1.2.1": "インターフェース違反率 (%)",
    "1.2.2": "インターフェースマッピング (Reviewer)",
    "1.3.1": "大クラスのコード率 (%)",
    "1.3.2": "大メソッドのコード率 (%)",
    "1.3.3": "大パッケージのクラス率 (%)",
    "1.3.4": "高複雑度メソッド率 (%)",
    "2.1.1": "技術レイヤー違反率 (%)",
    "2.1.2": "ドメインレイヤー違反率 (%)",
    "2.2.1": "循環に含まれるクラスの割合 (%)",
    "2.2.2": "循環に含まれるパッケージの割合 (%)",
    "2.2.3": "循環あたりのクラス数",
    "2.2.4": "循環あたりのパッケージ数",
    "3.1":   "パターンへのソースコード割当率 (%)",
    "3.2":   "パターン間循環違反率 (%)",
    "3.3":   "パターンの明示的マッピング (Reviewer)",
    "3.4":   "ドメイン/技術コード分離 (Reviewer)",
}


def score_criterion(criterion_id: str, value: float) -> int:
    """閾値テーブルに基づいて0〜10のスコアを返す"""
    entry = SCORING_TABLE.get(criterion_id)
    if not entry or entry["direction"] == "reviewer":
        return int(value)  # レビュアー入力はそのまま

    thresholds = entry["thresholds"]
    direction = entry["direction"]

    if direction == "asc":
        # 値が大きいほどスコアが高い
        score = 0
        for i in range(11):
            if value > thresholds[i]:
                score = i
            else:
                break
        # Check if value exceeds highest threshold
        if value > thresholds[10]:
            score = 10
        return score
    elif direction == "desc":
        # 値が小さいほどスコアが高い
        score = 0
        for i in range(11):
            if value < thresholds[i]:
                score = i
            else:
                break
        if value < thresholds[10]:
            score = 10
        return score

    return 0


def extract_values(
    metrics: dict, architecture: dict, reviewer: dict
) -> dict[str, float]:
    """メトリクスとアーキテクチャ結果から各基準の値を抽出する"""
    values = {}

    # --- From architecture_result.json ---
    dl = architecture.get("domain_and_layers", {})
    lv = architecture.get("layer_violations", {})
    intf = architecture.get("interfaces", {})
    pc = architecture.get("pattern_consistency", {})

    values["1.1.1"] = dl.get("domain_allocation_pct", 0)
    values["1.1.2"] = dl.get("layer_allocation_pct", 0)
    values["1.1.3"] = dl.get("domain_size_ratio", 0)
    values["1.1.4"] = dl.get("layer_size_ratio", 0)
    values["1.2.1"] = intf.get("interface_violation_pct", 0)

    # --- From metrics_result.json ---
    prop = metrics.get("proportions", {})
    cycles = metrics.get("cycles", {})
    sr = metrics.get("size_ratios", {})

    values["1.3.1"] = prop.get("large_class_pct", 0)
    values["1.3.2"] = prop.get("large_method_pct", 0)
    values["1.3.3"] = prop.get("large_package_pct", 0)
    values["1.3.4"] = prop.get("high_complexity_pct", 0)

    values["2.1.1"] = lv.get("violation_pct", 0)
    values["2.1.2"] = lv.get("violation_pct", 0)  # Use same for domain layer approx

    values["2.2.1"] = cycles.get("modules_in_cycles_pct", 0)
    values["2.2.2"] = cycles.get("packages_in_cycles_pct", 0)
    values["2.2.3"] = cycles.get("max_module_cycle_size", 0)
    values["2.2.4"] = cycles.get("max_package_cycle_size", 0)

    values["3.1"] = pc.get("pattern_allocation_pct", 0)
    values["3.2"] = pc.get("pattern_violation_pct", 0)

    # --- Reviewer inputs (default=5 "partial") ---
    values["1.1.5"] = reviewer.get("1.1.5_clear_responsibilities", 5)
    values["1.1.6"] = reviewer.get("1.1.6_mapping_quality", 5)
    values["1.2.2"] = reviewer.get("1.2.2_interface_mapping", 5)
    values["3.3"] = reviewer.get("3.3_explicit_pattern_mapping", 5)
    values["3.4"] = reviewer.get("3.4_domain_technical_separation", 5)

    return values


def calculate_mmi(values: dict[str, float]) -> dict:
    """MMIスコアを算出する"""
    scores = {}
    for cid, val in values.items():
        scores[cid] = score_criterion(cid, val)

    # Category scores
    category_scores = {}
    for cat_key, cat in CATEGORIES.items():
        subcat_scores = []
        for subcat_key, subcat in cat["subcategories"].items():
            criteria = subcat["criteria"]
            s = [scores[c] for c in criteria if c in scores]
            avg = sum(s) / max(len(s), 1)
            subcat_scores.append({
                "id": subcat_key,
                "name": subcat["name"],
                "name_ja": subcat["name_ja"],
                "avg_score": round(avg, 2),
                "weight_within": subcat["weight_within"],
                "weighted_score": round(avg * subcat["weight_within"], 2),
                "criteria_scores": {c: scores[c] for c in criteria},
            })

        cat_score = sum(s["weighted_score"] for s in subcat_scores)
        category_scores[cat_key] = {
            "name": cat["name"],
            "name_ja": cat["name_ja"],
            "weight": cat["weight"],
            "score": round(cat_score, 2),
            "weighted_score": round(cat_score * cat["weight"], 2),
            "subcategories": subcat_scores,
        }

    mmi = sum(c["weighted_score"] for c in category_scores.values())

    return {
        "mmi": round(mmi, 2),
        "categories": category_scores,
        "all_scores": scores,
        "all_values": {k: round(v, 2) for k, v in values.items()},
    }


def interpret_mmi(mmi: float) -> dict:
    """MMIスコアの解釈"""
    if mmi >= 8:
        return {
            "level": "Good",
            "level_ja": "良好",
            "color": "🟢",
            "description": "技術的負債が少ない。低コスト・安定保守の領域。",
            "recommendation": "現状維持。定期的なアーキテクチャレビューを継続。",
        }
    elif mmi >= 4:
        return {
            "level": "Warning",
            "level_ja": "要改善",
            "color": "🟡",
            "description": "技術的負債がかなり蓄積。リファクタリングが必要。",
            "recommendation": "段階的にリファクタリングを計画・実施。置換よりリファクタリングが経済的。",
        }
    else:
        return {
            "level": "Critical",
            "level_ja": "危険",
            "color": "🔴",
            "description": "保守・拡張に多大な労力。高コスト・不安定。",
            "recommendation": "リファクタリング vs システム置換の判断が必要。ROI分析を推奨。",
        }


def generate_report(result: dict, metrics: dict, architecture: dict) -> str:
    """Markdownレポートを生成する"""
    mmi = result["mmi"]
    interp = interpret_mmi(mmi)
    cats = result["categories"]
    values = result["all_values"]
    scores = result["all_scores"]

    project = metrics.get("project_path", architecture.get("project_path", "Unknown"))
    summary = metrics.get("summary", {})

    lines = []
    lines.append(f"# MMI Analysis Report")
    lines.append(f"")
    lines.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**Project:** `{project}`")
    lines.append(f"")
    lines.append(f"---")
    lines.append(f"")
    lines.append(f"## Overall MMI Score: {mmi:.1f} / 10 {interp['color']}")
    lines.append(f"")
    lines.append(f"**評価:** {interp['level_ja']} ({interp['level']})")
    lines.append(f"")
    lines.append(f"{interp['description']}")
    lines.append(f"")
    lines.append(f"**推奨アクション:** {interp['recommendation']}")
    lines.append(f"")
    lines.append(f"---")
    lines.append(f"")

    # Project summary
    lines.append(f"## プロジェクト概要")
    lines.append(f"")
    lines.append(f"| 項目 | 値 |")
    lines.append(f"|------|-----|")
    lines.append(f"| ファイル数 | {summary.get('total_files', 'N/A')} |")
    lines.append(f"| 総LOC | {summary.get('total_loc', 'N/A'):,} |")
    lines.append(f"| クラス数 | {summary.get('total_classes', 'N/A')} |")
    lines.append(f"| 関数数 | {summary.get('total_functions', 'N/A')} |")
    lines.append(f"| パッケージ数 | {summary.get('total_packages', 'N/A')} |")
    lines.append(f"")

    # Category breakdown
    lines.append(f"## カテゴリ別スコア")
    lines.append(f"")
    lines.append(f"| カテゴリ | 重み | スコア | 加重スコア |")
    lines.append(f"|---------|------|--------|----------|")
    for cat_key, cat in cats.items():
        lines.append(
            f"| {cat['name_ja']} ({cat['name']}) | {cat['weight']*100:.0f}% "
            f"| {cat['score']:.1f}/10 | {cat['weighted_score']:.2f} |"
        )
    lines.append(f"| **合計 (MMI)** | **100%** | | **{mmi:.2f}** |")
    lines.append(f"")

    # Detailed scores
    lines.append(f"## 基準別詳細スコア")
    lines.append(f"")

    for cat_key, cat in cats.items():
        lines.append(f"### {cat['name_ja']} ({cat['name']}) — {cat['weight']*100:.0f}%")
        lines.append(f"")
        lines.append(f"| 基準 | 説明 | 測定値 | スコア |")
        lines.append(f"|------|------|--------|--------|")
        for subcat in cat["subcategories"]:
            for cid, s in subcat["criteria_scores"].items():
                label = CRITERIA_LABELS.get(cid, cid)
                val = values.get(cid, "N/A")
                score_bar = "█" * s + "░" * (10 - s)
                lines.append(f"| {cid} | {label} | {val} | {s}/10 `{score_bar}` |")
        lines.append(f"")

    # Improvement suggestions
    lines.append(f"## 改善提案")
    lines.append(f"")

    low_scores = sorted(
        [(cid, s) for cid, s in scores.items() if s <= 4],
        key=lambda x: x[1]
    )

    if low_scores:
        lines.append(f"以下の基準はスコアが低く（4以下）、優先的な改善が推奨される:")
        lines.append(f"")
        for cid, s in low_scores:
            label = CRITERIA_LABELS.get(cid, cid)
            val = values.get(cid, "N/A")
            lines.append(f"- **{cid}** {label}: スコア {s}/10（測定値: {val}）")
        lines.append(f"")
    else:
        lines.append(f"全基準でスコア5以上。大きな問題は検出されなかった。")
        lines.append(f"")

    # Footer
    lines.append(f"---")
    lines.append(f"")
    lines.append(f"*Generated by MMI Analyzer Skill — based on Dr. Carola Lilienthal's Modularity Maturity Index*")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="MMI Calculator (Tool 3)")
    parser.add_argument("--metrics", "-m", required=True, help="Path to metrics_result.json")
    parser.add_argument("--architecture", "-a", required=True, help="Path to architecture_result.json")
    parser.add_argument("--reviewer", "-r", default=None, help="Path to reviewer_input.json")
    parser.add_argument("--output-dir", "-d", default=".", help="Output directory")
    args = parser.parse_args()

    # Load inputs
    with open(args.metrics, "r", encoding="utf-8") as f:
        metrics = json.load(f)
    with open(args.architecture, "r", encoding="utf-8") as f:
        architecture = json.load(f)

    reviewer = {}
    if args.reviewer and os.path.exists(args.reviewer):
        with open(args.reviewer, "r", encoding="utf-8") as f:
            reviewer = json.load(f)

    # Calculate
    values = extract_values(metrics, architecture, reviewer)
    result = calculate_mmi(values)
    interp = interpret_mmi(result["mmi"])

    # Output
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    scores_path = out_dir / "mmi_scores.json"
    scores_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    report = generate_report(result, metrics, architecture)
    report_path = out_dir / "mmi_report.md"
    report_path.write_text(report, encoding="utf-8")

    print(f"\n{'='*50}")
    print(f"  MMI Score: {result['mmi']:.1f} / 10  {interp['color']}  {interp['level_ja']}")
    print(f"{'='*50}")
    print(f"  Modularity:          {result['categories']['1_modularity']['score']:.1f}/10 (×45%)")
    print(f"  Hierarchy:           {result['categories']['2_hierarchy']['score']:.1f}/10 (×30%)")
    print(f"  Pattern Consistency: {result['categories']['3_pattern']['score']:.1f}/10 (×25%)")
    print(f"{'='*50}")
    print(f"  Scores: {scores_path}")
    print(f"  Report: {report_path}")


if __name__ == "__main__":
    main()
