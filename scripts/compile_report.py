#!/usr/bin/env python3
"""
レポートコンパイルスクリプト

分析結果のMarkdownファイルを統合HTMLレポートに変換します。

主な機能:
    - Markdownファイルの自動検出・統合
    - Mermaid図のレンダリング
    - 設定ファイルのシンタックスハイライト
    - GraphDB可視化の埋め込み
    - XSSサニタイゼーション（危険なHTMLタグの自動エスケープ）
    - HTML検証

使用方法:
    python compile_report.py --input-dir ./reports --output ./report.html

前提条件:
    pip install markdown pymdown-extensions
"""

import argparse
import os
import re
import json
from pathlib import Path
from datetime import datetime

try:
    import markdown
    from markdown.extensions.toc import TocExtension
except ImportError:
    print("Error: markdown is not installed. Run: pip install markdown pymdown-extensions")
    import sys
    sys.exit(1)


def custom_slugify(value, separator):
    """
    カスタムslugify関数。
    TocExtensionのデフォルトslugifyと完全に一致するように、
    特殊文字を一貫して処理する。

    変換ルール:
    - 小文字に変換
    - & を "and" に変換せず削除
    - 連続するハイフンを1つに統合
    - 前後の空白・ハイフンを削除
    """
    import unicodedata

    # Unicode正規化
    value = unicodedata.normalize('NFKD', value)

    # &記号とその前後の空白を削除
    value = re.sub(r'\s*&\s*', ' ', value)

    # 小文字化
    value = value.lower()

    # 英数字とハイフン以外を空白に変換
    value = re.sub(r'[^\w\s-]', '', value)

    # 空白をseparatorに変換
    value = re.sub(r'[-\s]+', separator, value)

    # 前後のseparatorを削除
    value = value.strip(separator)

    return value


def normalize_file_id(file_name: str) -> str:
    """
    ファイル名からIDを正規化する。

    TOCのリンクとarticleのIDで一貫したIDを生成するために使用。

    変換ルール:
    - '/' を '-' に変換（サブディレクトリ対応）
    - 拡張子を除去（.md, .yaml, .yml, .json, .properties, .toml, .xml, .feature等）
    - '_' を '-' に変換
    - '.' を '-' に変換（拡張子除去後の残りのドット）

    例:
    - "api-specifications/openapi.yaml" → "api-specifications-openapi"
    - "project_metadata.json" → "project-metadata"
    - "config/app.properties" → "config-app"
    """
    # 拡張子のリスト（除去対象）
    extensions_to_remove = [
        '.md', '.yaml', '.yml', '.json', '.properties',
        '.toml', '.xml', '.feature', '.graphql', '.gql',
        '.proto', '.tf', '.hcl', '.env'
    ]

    result = file_name

    # 拡張子を除去
    for ext in extensions_to_remove:
        if result.endswith(ext):
            result = result[:-len(ext)]
            break

    # パス区切り、アンダースコア、ドットをハイフンに変換
    result = result.replace('/', '-').replace('_', '-').replace('.', '-')

    return result


def sanitize_html_content(html_content: str) -> str:
    """
    HTMLコンテンツ内の危険なタグをエスケープする。

    テーブルやパラグラフ内に含まれる<script>、<img>等の危険なタグを
    HTMLエンティティに変換してXSS攻撃を防ぐ。

    ただし、以下は保持:
    - <code>ブロック（既にエスケープ済み）
    - <div class="mermaid">（Mermaid図）
    - その他の安全なマークアップ（<table>, <p>, <h1-6>, <ul>, <li>等）
    """
    import html

    # 危険なタグのパターン
    dangerous_patterns = [
        (r'<script[^>]*>.*?</script>', lambda m: html.escape(m.group(0))),  # <script>タグ
        (r'<script[^>]*>', lambda m: html.escape(m.group(0))),  # 閉じられていない<script>
        (r'<img[^>]*onerror[^>]*>', lambda m: html.escape(m.group(0))),  # onerror付き<img>
        (r'<iframe[^>]*>.*?</iframe>', lambda m: html.escape(m.group(0))),  # <iframe>タグ
        (r'<embed[^>]*>', lambda m: html.escape(m.group(0))),  # <embed>タグ
        (r'<object[^>]*>.*?</object>', lambda m: html.escape(m.group(0))),  # <object>タグ
    ]

    result = html_content
    for pattern, replacer in dangerous_patterns:
        result = re.sub(pattern, replacer, result, flags=re.IGNORECASE | re.DOTALL)

    return result


def extract_graph_data(graph_html_path: Path) -> dict:
    """graph.htmlからD3.jsデータを抽出"""
    if not graph_html_path.exists():
        return None

    with open(graph_html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # JavaScriptのdataオブジェクトを抽出
    import re
    match = re.search(r'const data = ({.*?});', content, re.DOTALL)
    if match:
        return match.group(1)
    return None


def generate_graph_section(graph_data: str) -> str:
    """インタラクティブグラフセクションを生成"""
    if not graph_data:
        return ""

    return f'''
<article id="graph-interactive">
<h2>インタラクティブグラフビューア</h2>
<p>ノードをドラッグして移動、マウスホイールでズーム、ノードにホバーで詳細表示できます。</p>
<div id="graph-container" style="width: 100%; height: 600px; border: 1px solid var(--border-color); border-radius: 8px; overflow: hidden; background: #1a1a2e;">
    <div id="graph-controls" style="position: absolute; padding: 10px; background: rgba(255,255,255,0.9); border-radius: 5px; margin: 10px; z-index: 100;">
        <input type="text" id="graph-search" placeholder="ノードを検索..." style="width: 180px; padding: 5px;">
        <div id="graph-stats" style="font-size: 12px; color: #666; margin-top: 5px;"></div>
    </div>
    <svg id="graph-svg"></svg>
</div>
<div id="graph-legend" style="margin-top: 15px; display: flex; gap: 20px; flex-wrap: wrap;">
    <span><span style="display: inline-block; width: 12px; height: 12px; background: #e74c3c; border-radius: 50%; margin-right: 5px;"></span>Domain</span>
    <span><span style="display: inline-block; width: 12px; height: 12px; background: #3498db; border-radius: 50%; margin-right: 5px;"></span>Entity</span>
    <span><span style="display: inline-block; width: 12px; height: 12px; background: #2ecc71; border-radius: 50%; margin-right: 5px;"></span>Term</span>
</div>
</article>
<script>
(function() {{
    const data = {graph_data};

    const container = document.getElementById('graph-container');
    const width = container.clientWidth;
    const height = 600;

    const svg = d3.select("#graph-svg")
        .attr("width", width)
        .attr("height", height);

    const g = svg.append("g");

    // Zoom
    const zoom = d3.zoom()
        .scaleExtent([0.1, 4])
        .on("zoom", (event) => g.attr("transform", event.transform));
    svg.call(zoom);

    // Colors
    const color = d3.scaleOrdinal()
        .domain(["Domain", "Entity", "Term"])
        .range(["#e74c3c", "#3498db", "#2ecc71"]);

    // Simulation
    const simulation = d3.forceSimulation(data.nodes)
        .force("link", d3.forceLink(data.links).id(d => d.id).distance(80))
        .force("charge", d3.forceManyBody().strength(-200))
        .force("center", d3.forceCenter(width / 2, height / 2))
        .force("collision", d3.forceCollide().radius(25));

    // Links
    const link = g.append("g")
        .selectAll("line")
        .data(data.links)
        .join("line")
        .attr("stroke", "#666")
        .attr("stroke-opacity", 0.6)
        .attr("stroke-width", 1);

    // Nodes
    const node = g.append("g")
        .selectAll("g")
        .data(data.nodes)
        .join("g")
        .attr("cursor", "pointer")
        .call(d3.drag()
            .on("start", (event, d) => {{
                if (!event.active) simulation.alphaTarget(0.3).restart();
                d.fx = d.x; d.fy = d.y;
            }})
            .on("drag", (event, d) => {{ d.fx = event.x; d.fy = event.y; }})
            .on("end", (event, d) => {{
                if (!event.active) simulation.alphaTarget(0);
                d.fx = null; d.fy = null;
            }}));

    node.append("circle")
        .attr("r", d => d.type === "Domain" ? 15 : 8)
        .attr("fill", d => color(d.type));

    node.append("text")
        .text(d => d.name.length > 15 ? d.name.substring(0, 15) + "..." : d.name)
        .attr("x", 12)
        .attr("y", 4)
        .attr("font-size", "10px")
        .attr("fill", "white");

    // Tooltip
    const tooltip = d3.select("body").append("div")
        .style("position", "absolute")
        .style("background", "rgba(0,0,0,0.8)")
        .style("color", "white")
        .style("padding", "10px")
        .style("border-radius", "5px")
        .style("font-size", "12px")
        .style("pointer-events", "none")
        .style("opacity", 0);

    node.on("mouseover", (event, d) => {{
        tooltip.style("opacity", 1)
            .html(`<strong>${{d.name}}</strong><br/>Type: ${{d.type}}<br/>Group: ${{d.group || 'N/A'}}`)
            .style("left", (event.pageX + 10) + "px")
            .style("top", (event.pageY - 10) + "px");
    }}).on("mouseout", () => {{ tooltip.style("opacity", 0); }});

    simulation.on("tick", () => {{
        link.attr("x1", d => d.source.x).attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
        node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
    }});

    // Stats
    document.getElementById("graph-stats").innerHTML =
        `Nodes: ${{data.nodes.length}} | Links: ${{data.links.length}}`;

    // Search
    document.getElementById("graph-search").addEventListener("input", (e) => {{
        const query = e.target.value.toLowerCase();
        node.style("opacity", d =>
            query === "" || d.name.toLowerCase().includes(query) ? 1 : 0.2);
    }});
}})();
</script>
'''


# セクション定義（ディレクトリと優先ファイル順序）
SECTIONS = [
    {
        "id": "summary",
        "title": "エグゼクティブサマリー",
        "dir": "00_summary",
        "priority_files": ["executive-summary.md"],
        "auto_discover": True
    },
    {
        "id": "before",
        "title": "現行システム調査",
        "dir": "before",
        "priority_files": [
            "technology-stack.md",
            "codebase-structure.md",
            "issues-and-debt.md",
            "ddd-readiness.md"
        ],
        "auto_discover": True,
        "include_subdirs": ["*"]  # プロジェクト名のサブディレクトリを検索
    },
    {
        "id": "analysis",
        "title": "システム分析",
        "dir": "01_analysis",
        "priority_files": [
            "system-overview.md",
            "architecture-diagram.md",
            "ubiquitous-language.md",
            "domain-entities.md",
            "actors-roles-permissions.md",
            "domain-code-mapping.md",
            "api-endpoints.md"
        ],
        "auto_discover": True
    },
    {
        "id": "evaluation",
        "title": "評価（MMI・DDD）",
        "dir": "02_evaluation",
        "priority_files": [
            "mmi-overview.md",
            "mmi-by-module.md",
            "mmi-improvement-plan.md",
            "ddd-strategic-evaluation.md",
            "ddd-tactical-evaluation.md",
            "ddd-improvement-plan.md",
            "integrated-evaluation.md",
            "priority-matrix.md",
            "unified-improvement-plan.md"
        ],
        "auto_discover": True
    },
    {
        "id": "design",
        "title": "設計",
        "dir": "03_design",
        "priority_files": [
            # 境界コンテキスト・集約
            "bounded-contexts-redesign.md",
            "context-map-redesign.md",
            "aggregate-redesign.md",
            "domain-events-redesign.md",
            "domain-services-redesign.md",
            # ターゲットアーキテクチャ
            "target-architecture.md",
            "migration-plan.md",
            "operations-plan.md",
            # API設計
            "api-design-overview.md",
            "api-gateway-design.md",
            "api-security-design.md",
            # ScalarDB設計
            "scalardb-design.md",
            "scalardb-architecture.md",
            "scalardb-schema-design.md",
            "scalardb-transaction-design.md"
        ],
        "auto_discover": True,
        "include_subdirs": ["api-specifications", "config", "k8s", "schemas"],
        "include_extensions": [".yaml", ".yml", ".json", ".properties", ".toml", ".xml", ".graphql", ".proto"]
    },
    {
        "id": "implementation",
        "title": "実装仕様",
        "dir": "06_implementation",
        "priority_files": [
            "domain-services-spec.md",
            "repository-interfaces-spec.md",
            "value-objects-spec.md",
            "exception-mapping.md",
            "saga-orchestration-spec.md",
            "implementation-checklist.md",
            "api-gateway-implementation-spec.md"
        ],
        "auto_discover": True,
        "include_subdirs": ["config", "schemas"],
        "include_extensions": [".yaml", ".yml", ".json", ".properties"]
    },
    {
        "id": "test-specs",
        "title": "テスト仕様",
        "dir": "07_test-specs",
        "priority_files": [
            "unit-test-specs.md",
            "integration-test-specs.md",
            "edge-case-specs.md",
            "performance-test-specs.md",
            "test-data-requirements.md"
        ],
        "auto_discover": True,
        "include_subdirs": ["bdd-scenarios"],
        "include_extensions": [".feature", ".yaml", ".json"]
    },
    {
        "id": "stories",
        "title": "ドメインストーリー",
        "dir": "04_stories",
        "priority_files": [
            "domain-stories.md",
            "file-management-story.md",
            "audit-compliance-story.md",
            "collaboration-story.md"
        ],
        "auto_discover": True
    },
    {
        "id": "estimate",
        "title": "コスト試算",
        "dir": "05_estimate",
        "priority_files": ["cost-summary.md", "infrastructure-detail.md", "license-requirements.md", "cost-assumptions.md"],
        "auto_discover": True
    },
    {
        "id": "graph",
        "title": "ナレッジグラフ",
        "dir": "graph",
        "priority_files": ["schema.md", "statistics.md"],
        "auto_discover": True,
        "include_subdirs": ["visualizations", "data"],
        "include_extensions": [".yaml", ".yml", ".json"]
    }
]


def discover_markdown_files(section_dir: Path, priority_files: list, include_subdirs: list = None, include_extensions: list = None) -> list:
    """ディレクトリ内のMarkdownファイルを検出し、優先順位順に返す"""
    found_files = []
    seen_basenames = set()

    # 対象拡張子（デフォルトで設定ファイルも含む）
    DEFAULT_CONFIG_EXTENSIONS = [".yaml", ".yml", ".json", ".properties", ".toml", ".xml", ".feature"]
    extensions = [".md"]
    if include_extensions:
        extensions.extend(include_extensions)
    else:
        # include_extensionsが指定されていない場合でも、設定ファイルは自動検出
        extensions.extend(DEFAULT_CONFIG_EXTENSIONS)

    # サブディレクトリを解決（"*"の場合は全サブディレクトリ）
    actual_subdirs = []
    if include_subdirs:
        for subdir in include_subdirs:
            if subdir == "*":
                # 全サブディレクトリを検索
                if section_dir.exists():
                    for d in section_dir.iterdir():
                        if d.is_dir():
                            actual_subdirs.append(d.name)
            else:
                actual_subdirs.append(subdir)

    # 重複チェック用のベース名を取得（ファイル名のみ、パスなし）
    def get_dedup_basename(fname: str) -> str:
        """重複チェック用のベース名を取得（ファイル名のみ）"""
        # パスがある場合はファイル名のみを取得
        if '/' in fname:
            fname = fname.split('/')[-1]
        return normalize_file_id(fname)

    # 優先ファイルを最初に追加（メインディレクトリとサブディレクトリから）
    for file_name in priority_files:
        # メインディレクトリから検索
        file_path = section_dir / file_name
        if file_path.exists():
            basename = get_dedup_basename(file_name)
            if basename not in seen_basenames:
                found_files.append(file_name)
                seen_basenames.add(basename)
        else:
            # サブディレクトリから検索
            for subdir in actual_subdirs:
                subdir_path = section_dir / subdir / file_name
                if subdir_path.exists():
                    rel_path = f"{subdir}/{file_name}"
                    basename = get_dedup_basename(file_name)
                    if basename not in seen_basenames:
                        found_files.append(rel_path)
                        seen_basenames.add(basename)
                    break

    # ディレクトリ内の他のファイルを検出
    if section_dir.exists():
        for ext in extensions:
            for file in sorted(section_dir.glob(f"*{ext}")):
                file_name = file.name
                basename = get_dedup_basename(file_name)
                if basename not in seen_basenames:
                    found_files.append(file_name)
                    seen_basenames.add(basename)

    # サブディレクトリも検索
    for subdir in actual_subdirs:
        subdir_path = section_dir / subdir
        if subdir_path.exists():
            for ext in extensions:
                for file in sorted(subdir_path.glob(f"*{ext}")):
                    rel_path = f"{subdir}/{file.name}"
                    basename = get_dedup_basename(file.name)
                    if basename not in seen_basenames:
                        found_files.append(rel_path)
                        seen_basenames.add(basename)

    return found_files


def get_html_template(title: str, theme: str = "light") -> tuple:
    """HTMLテンプレートを取得"""

    dark_styles = """
        :root {
            --bg-color: #1a1a2e;
            --text-color: #e0e0e0;
            --heading-color: #ffffff;
            --link-color: #64b5f6;
            --border-color: #333;
            --code-bg: #2d2d2d;
            --table-header-bg: #333;
            --sidebar-bg: #16213e;
        }
    """ if theme == "dark" else """
        :root {
            --bg-color: #ffffff;
            --text-color: #333333;
            --heading-color: #1a1a2e;
            --link-color: #1976d2;
            --border-color: #e0e0e0;
            --code-bg: #f5f5f5;
            --table-header-bg: #f0f0f0;
            --sidebar-bg: #fafafa;
        }
    """

    header = f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script src="https://unpkg.com/lunr/lunr.js"></script>
    <style>
        {dark_styles}

        * {{
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            background-color: var(--bg-color);
            margin: 0;
            padding: 0;
            display: flex;
        }}

        /* サイドバー */
        .sidebar {{
            width: 280px;
            height: 100vh;
            position: fixed;
            left: 0;
            top: 0;
            background: var(--sidebar-bg);
            border-right: 1px solid var(--border-color);
            overflow-y: auto;
            padding: 20px;
        }}

        .sidebar h2 {{
            font-size: 1.1rem;
            margin-bottom: 15px;
            color: var(--heading-color);
        }}

        .sidebar ul {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}

        .sidebar li {{
            margin: 5px 0;
        }}

        .sidebar a {{
            color: var(--link-color);
            text-decoration: none;
            font-size: 0.9rem;
            display: block;
            padding: 5px 0;
        }}

        .sidebar a:hover {{
            text-decoration: underline;
        }}

        .sidebar .section-title {{
            font-weight: bold;
            margin-top: 15px;
            color: var(--heading-color);
        }}

        /* 検索 */
        .search-container {{
            margin-bottom: 20px;
            padding-bottom: 20px;
            border-bottom: 1px solid var(--border-color);
        }}

        .search-box {{
            width: 100%;
            padding: 10px;
            font-size: 0.9rem;
            border: 1px solid var(--border-color);
            border-radius: 5px;
            background: var(--bg-color);
            color: var(--text-color);
        }}

        .search-box:focus {{
            outline: 2px solid var(--link-color);
            outline-offset: 0;
        }}

        .search-results {{
            margin-top: 10px;
            max-height: 300px;
            overflow-y: auto;
        }}

        .search-result-item {{
            padding: 8px;
            margin: 5px 0;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.85rem;
            background: rgba(100, 181, 246, 0.1);
        }}

        .search-result-item:hover {{
            background: rgba(100, 181, 246, 0.2);
        }}

        .search-result-title {{
            font-weight: bold;
            color: var(--link-color);
            margin-bottom: 3px;
        }}

        .search-result-snippet {{
            color: var(--text-color);
            opacity: 0.8;
            font-size: 0.8rem;
        }}

        .search-highlight {{
            background-color: #ffeb3b;
            color: #000;
            padding: 2px 4px;
            border-radius: 2px;
        }}

        .search-stats {{
            font-size: 0.8rem;
            color: var(--text-color);
            opacity: 0.6;
            margin-top: 5px;
        }}

        /* メインコンテンツ */
        .main-content {{
            margin-left: 280px;
            padding: 40px 60px;
            max-width: 1200px;
            width: calc(100% - 280px);
        }}

        /* ヘッダー */
        .report-header {{
            text-align: center;
            padding: 40px 0;
            border-bottom: 2px solid var(--border-color);
            margin-bottom: 40px;
        }}

        .report-header h1 {{
            font-size: 2.5rem;
            color: var(--heading-color);
            margin-bottom: 10px;
        }}

        .report-header .meta {{
            color: var(--text-color);
            opacity: 0.7;
        }}

        /* セクション */
        section {{
            margin-bottom: 60px;
            padding-bottom: 40px;
            border-bottom: 1px solid var(--border-color);
        }}

        h1 {{
            font-size: 2rem;
            color: var(--heading-color);
            border-bottom: 2px solid var(--link-color);
            padding-bottom: 10px;
            margin-top: 40px;
        }}

        h2 {{
            font-size: 1.5rem;
            color: var(--heading-color);
            margin-top: 30px;
        }}

        h3 {{
            font-size: 1.25rem;
            color: var(--heading-color);
            margin-top: 25px;
        }}

        h4 {{
            font-size: 1.1rem;
            color: var(--heading-color);
        }}

        /* テーブル */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 0.9rem;
        }}

        th, td {{
            padding: 12px 15px;
            text-align: left;
            border: 1px solid var(--border-color);
        }}

        th {{
            background-color: var(--table-header-bg);
            font-weight: 600;
        }}

        tr:nth-child(even) {{
            background-color: rgba(0,0,0,0.02);
        }}

        /* コード */
        pre {{
            background-color: var(--code-bg);
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            font-size: 0.9rem;
        }}

        code {{
            font-family: 'Fira Code', 'Consolas', monospace;
            background-color: var(--code-bg);
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.9em;
        }}

        pre code {{
            padding: 0;
            background: none;
        }}

        /* Mermaid */
        .mermaid {{
            text-align: center;
            margin: 20px 0;
            background: white;
            padding: 20px;
            border-radius: 8px;
        }}

        /* リスト */
        ul, ol {{
            margin: 15px 0;
            padding-left: 25px;
        }}

        li {{
            margin: 8px 0;
        }}

        /* リンク */
        a {{
            color: var(--link-color);
        }}

        /* 引用 */
        blockquote {{
            border-left: 4px solid var(--link-color);
            margin: 20px 0;
            padding: 10px 20px;
            background: rgba(0,0,0,0.03);
        }}

        /* 印刷用 */
        @media print {{
            .sidebar {{
                display: none;
            }}
            .main-content {{
                margin-left: 0;
                width: 100%;
            }}
            section {{
                page-break-inside: avoid;
            }}
        }}

        /* レスポンシブ */
        @media (max-width: 768px) {{
            .sidebar {{
                display: none;
            }}
            .main-content {{
                margin-left: 0;
                width: 100%;
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <nav class="sidebar">
        <div class="search-container">
            <input type="text" id="search-box" class="search-box" placeholder="検索...">
            <div id="search-stats" class="search-stats"></div>
            <div id="search-results" class="search-results"></div>
        </div>
        <h2>目次</h2>
        <ul>
'''

    footer = '''
    <script>
        mermaid.initialize({
            startOnLoad: true,
            theme: 'default',
            securityLevel: 'loose'
        });

        // 検索機能の初期化
        (function() {
            let searchIndex;
            let documents = [];

            // ドキュメントインデックスの構築
            function buildSearchIndex() {
                const sections = document.querySelectorAll('section');

                sections.forEach((section, idx) => {
                    const id = section.id || `section-${idx}`;
                    if (!section.id) {
                        section.id = id;
                    }

                    // セクションのタイトルを取得
                    const heading = section.querySelector('h1, h2');
                    const title = heading ? heading.textContent.trim() : `Section ${idx + 1}`;

                    // セクションのテキストコンテンツを取得（コードブロックとMermaidを除外）
                    const clone = section.cloneNode(true);
                    clone.querySelectorAll('pre, .mermaid, script').forEach(el => el.remove());
                    const content = clone.textContent.trim();

                    documents.push({
                        id: id,
                        title: title,
                        content: content,
                        element: section
                    });
                });

                // Lunr.jsインデックスの構築
                searchIndex = lunr(function() {
                    this.ref('id');
                    this.field('title', { boost: 10 });
                    this.field('content');

                    // 日本語サポート（トークナイザー）
                    this.pipeline.remove(lunr.stemmer);
                    this.pipeline.remove(lunr.stopWordFilter);

                    documents.forEach(doc => {
                        this.add(doc);
                    });
                });

                console.log(`Search index built with ${documents.length} sections`);
            }

            // 検索実行
            function performSearch(query) {
                if (!query || query.length < 2) {
                    document.getElementById('search-results').innerHTML = '';
                    document.getElementById('search-stats').textContent = '';
                    return;
                }

                try {
                    const results = searchIndex.search(query + '*');  // 前方一致サポート
                    displayResults(results, query);
                } catch (e) {
                    console.error('Search error:', e);
                    document.getElementById('search-results').innerHTML = '<div style="color: red;">検索エラー</div>';
                }
            }

            // 結果表示
            function displayResults(results, query) {
                const resultsContainer = document.getElementById('search-results');
                const statsContainer = document.getElementById('search-stats');

                if (results.length === 0) {
                    statsContainer.textContent = '結果なし';
                    resultsContainer.innerHTML = '';
                    return;
                }

                statsContainer.textContent = `${results.length}件の結果`;

                const html = results.slice(0, 10).map(result => {
                    const doc = documents.find(d => d.id === result.ref);
                    if (!doc) return '';

                    // スニペット生成（マッチした部分を抽出）
                    const snippet = createSnippet(doc.content, query);

                    return `
                        <div class="search-result-item" data-section-id="${doc.id}">
                            <div class="search-result-title">${escapeHtml(doc.title)}</div>
                            <div class="search-result-snippet">${snippet}</div>
                        </div>
                    `;
                }).join('');

                resultsContainer.innerHTML = html;

                // クリックイベントの設定
                resultsContainer.querySelectorAll('.search-result-item').forEach(item => {
                    item.addEventListener('click', function() {
                        const sectionId = this.getAttribute('data-section-id');
                        const section = document.getElementById(sectionId);
                        if (section) {
                            section.scrollIntoView({ behavior: 'smooth', block: 'start' });
                            // ハイライト効果
                            section.style.backgroundColor = 'rgba(100, 181, 246, 0.2)';
                            setTimeout(() => {
                                section.style.backgroundColor = '';
                            }, 2000);
                        }
                    });
                });
            }

            // スニペット生成（マッチした部分を含む150文字）
            function createSnippet(content, query) {
                const lowerContent = content.toLowerCase();
                const lowerQuery = query.toLowerCase();
                const index = lowerContent.indexOf(lowerQuery);

                if (index === -1) {
                    return escapeHtml(content.substring(0, 150)) + '...';
                }

                const start = Math.max(0, index - 50);
                const end = Math.min(content.length, index + query.length + 100);
                let snippet = content.substring(start, end);

                if (start > 0) snippet = '...' + snippet;
                if (end < content.length) snippet = snippet + '...';

                // クエリをハイライト
                const regex = new RegExp(`(${escapeRegex(query)})`, 'gi');
                snippet = escapeHtml(snippet).replace(regex, '<span class="search-highlight">$1</span>');

                return snippet;
            }

            // HTMLエスケープ
            function escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }

            // 正規表現エスケープ
            function escapeRegex(text) {
                return text.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&');
            }

            // 初期化
            if (typeof lunr !== 'undefined') {
                buildSearchIndex();

                // 検索ボックスのイベントリスナー
                const searchBox = document.getElementById('search-box');
                let searchTimeout;
                searchBox.addEventListener('input', function(e) {
                    clearTimeout(searchTimeout);
                    searchTimeout = setTimeout(() => {
                        performSearch(e.target.value);
                    }, 300);  // 300msのデバウンス
                });

                // Enterキーで最初の結果に移動
                searchBox.addEventListener('keydown', function(e) {
                    if (e.key === 'Enter') {
                        const firstResult = document.querySelector('.search-result-item');
                        if (firstResult) {
                            firstResult.click();
                        }
                    }
                });
            } else {
                console.error('Lunr.js not loaded');
            }
        })();
    </script>
</body>
</html>
'''

    return header, footer


def read_markdown_file(file_path: Path) -> str:
    """Markdownファイルを読み込む"""
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""


def get_language_for_extension(ext: str) -> str:
    """拡張子からシンタックスハイライト用の言語名を取得"""
    EXTENSION_TO_LANGUAGE = {
        ".yaml": "yaml",
        ".yml": "yaml",
        ".json": "json",
        ".properties": "properties",
        ".toml": "toml",
        ".xml": "xml",
        ".env": "bash",
        ".sh": "bash",
        ".sql": "sql",
        ".graphql": "graphql",
        ".gql": "graphql",
        ".proto": "protobuf",
        ".gradle": "groovy",
        ".kt": "kotlin",
        ".java": "java",
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".tsx": "tsx",
        ".jsx": "jsx",
        ".css": "css",
        ".scss": "scss",
        ".html": "html",
        ".feature": "gherkin",  # BDDシナリオ
        ".tf": "hcl",  # Terraform
        ".hcl": "hcl",
    }
    return EXTENSION_TO_LANGUAGE.get(ext.lower(), "")


def read_file_as_markdown(file_path: Path) -> str:
    """ファイルを読み込み、Markdown形式で返す（YAML/JSONはコードブロックとして表示）"""
    if not file_path.exists():
        return ""

    ext = file_path.suffix.lower()
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if ext == ".md":
        return content

    # ファイル名からタイトルを生成
    title = file_path.stem.replace('-', ' ').replace('_', ' ').title()

    # JSONファイルは整形を試みる
    if ext == ".json":
        try:
            parsed = json.loads(content)
            content = json.dumps(parsed, indent=2, ensure_ascii=False)
        except json.JSONDecodeError:
            pass  # パース失敗時はそのまま表示

    # シンタックスハイライト用の言語を取得
    language = get_language_for_extension(ext)

    # ファイルパスも表示（設定ファイルの場合は参照用に便利）
    file_info = f"*File: `{file_path.name}`*\n\n" if ext not in [".md"] else ""

    return f"## {title}\n\n{file_info}```{language}\n{content}\n```"


def convert_mermaid_blocks(content: str) -> str:
    """Mermaidコードブロックをdivに変換"""
    pattern = r'```mermaid\n(.*?)```'

    def replace_mermaid(match):
        mermaid_code = match.group(1)
        return f'<div class="mermaid">\n{mermaid_code}</div>'

    return re.sub(pattern, replace_mermaid, content, flags=re.DOTALL)


def generate_toc_entry(section_id: str, section_title: str, files: list) -> str:
    """目次エントリを生成"""
    entries = [f'<li class="section-title">{section_title}</li>']
    for file in files:
        file_id = normalize_file_id(file)
        # タイトル用：拡張子除去、アンダースコアとハイフンをスペースに、Title Case
        file_title = normalize_file_id(file).replace('-', ' ').title()
        entries.append(f'<li><a href="#{section_id}-{file_id}">{file_title}</a></li>')
    return '\n'.join(entries)


def compile_report(input_dir: str, output: str, title: str, theme: str = "light"):
    """レポートをコンパイル"""

    input_path = Path(input_dir)
    output_path = Path(output)

    print(f"=== Report Compilation ===")
    print(f"Input: {input_path}")
    print(f"Output: {output_path}")
    print()

    # Markdown拡張
    md = markdown.Markdown(extensions=[
        'tables',
        'fenced_code',
        'codehilite',
        TocExtension(permalink=True, slugify=custom_slugify)
    ])

    # HTMLテンプレート取得
    header, footer = get_html_template(title, theme)

    # 目次とコンテンツを構築
    toc_html = []
    content_html = []

    # レポートヘッダー
    content_html.append(f'''
    <main class="main-content">
        <header class="report-header">
            <h1>{title}</h1>
            <p class="meta">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </header>
    ''')

    for section in SECTIONS:
        section_id = section["id"]
        section_title = section["title"]
        section_dir = input_path / section["dir"]

        if not section_dir.exists():
            print(f"  Skipping: {section['dir']} (not found)")
            continue

        print(f"  Processing: {section['dir']}")

        # ファイルを動的に検出
        include_subdirs = section.get("include_subdirs", None)
        include_extensions = section.get("include_extensions", None)
        discovered_files = discover_markdown_files(
            section_dir,
            section.get("priority_files", []),
            include_subdirs,
            include_extensions
        )

        if not discovered_files:
            print(f"    No markdown files found")
            continue

        print(f"    Found {len(discovered_files)} file(s)")

        # 目次エントリ
        toc_html.append(generate_toc_entry(section_id, section_title, discovered_files))

        # セクションコンテンツ
        content_html.append(f'<section id="{section_id}">')
        content_html.append(f'<h1>{section_title}</h1>')

        for file_name in discovered_files:
            file_path = section_dir / file_name
            if not file_path.exists():
                continue

            # ファイルIDを生成（サブディレクトリのパスも考慮）
            file_id = normalize_file_id(file_name)
            content = read_file_as_markdown(file_path)

            # Mermaidブロックを変換
            content = convert_mermaid_blocks(content)

            # MarkdownをHTMLに変換
            md.reset()
            html_content = md.convert(content)

            # 危険なHTMLタグをサニタイズ（XSS対策）
            html_content = sanitize_html_content(html_content)

            content_html.append(f'<article id="{section_id}-{file_id}">')
            content_html.append(html_content)
            content_html.append('</article>')

        # グラフセクションの場合、インタラクティブビューアを追加
        if section_id == "graph":
            graph_html_path = section_dir / "visualizations" / "graph.html"
            graph_data = extract_graph_data(graph_html_path)
            if graph_data:
                print(f"    Adding: Interactive graph viewer")
                # 目次にインタラクティブグラフを追加
                toc_html.append('<li><a href="#graph-interactive">Interactive Viewer</a></li>')
                content_html.append(generate_graph_section(graph_data))

        content_html.append('</section>')

    content_html.append('</main>')

    # HTMLを組み立て
    full_html = header + '\n'.join(toc_html) + '\n</ul>\n</nav>\n' + '\n'.join(content_html) + footer

    # 出力
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_html)

    print()
    print(f"=== Compilation Complete ===")
    print(f"Output: {output_path}")
    print(f"Size: {output_path.stat().st_size / 1024:.1f} KB")


def verify_html_report(html_path: Path) -> dict:
    """生成されたHTMLレポートを検証し、問題をレポート"""
    if not html_path.exists():
        return {"success": False, "errors": ["HTML file not found"], "warnings": [], "stats": {}}

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    errors = []
    warnings = []
    stats = {
        "sections": 0,
        "articles": 0,
        "mermaid_diagrams": 0,
        "config_files": 0,
        "nav_links": 0,
        "has_graph_viewer": False,
    }

    # セクションの検証
    section_pattern = r'<section id="([^"]+)">'
    sections = re.findall(section_pattern, content)
    stats["sections"] = len(sections)

    # 各セクション内のarticleを検証
    for section_id in sections:
        section_match = re.search(
            rf'<section id="{section_id}">(.*?)</section>',
            content,
            re.DOTALL
        )
        if section_match:
            section_content = section_match.group(1)
            articles = re.findall(r'<article id="([^"]+)">', section_content)
            stats["articles"] += len(articles)

            # 空のセクションをチェック
            if len(articles) == 0 and 'graph-interactive' not in section_content:
                warnings.append(f"Section '{section_id}' has no articles")

            # 各articleの内容をチェック
            for article_id in articles:
                article_match = re.search(
                    rf'<article id="{article_id}">(.*?)</article>',
                    section_content,
                    re.DOTALL
                )
                if article_match:
                    article_content = article_match.group(1).strip()
                    if len(article_content) < 10:  # ほぼ空のarticle
                        warnings.append(f"Article '{article_id}' appears to be empty")

    # Mermaid図の検証
    mermaid_diagrams = re.findall(r'<div class="mermaid">', content)
    stats["mermaid_diagrams"] = len(mermaid_diagrams)

    # 設定ファイル（コードブロック）の検証
    config_languages = ["yaml", "json", "properties", "toml", "xml"]
    for lang in config_languages:
        config_blocks = re.findall(rf'<code class="language-{lang}">', content)
        stats["config_files"] += len(config_blocks)

    # GraphDBビューアの検証
    if 'id="graph-interactive"' in content:
        stats["has_graph_viewer"] = True
        # D3.jsデータの存在確認
        if 'const data = {' not in content:
            errors.append("Graph viewer found but data is missing")

    # ナビゲーションリンクの検証
    nav_links = re.findall(r'<a href="#([^"]+)">', content)
    stats["nav_links"] = len(nav_links)

    # リンク先の存在確認
    for link_target in nav_links:
        if f'id="{link_target}"' not in content:
            warnings.append(f"Navigation link '#{link_target}' has no target")

    # 必須要素のチェック
    if '<nav class="sidebar">' not in content:
        errors.append("Sidebar navigation is missing")
    if '<main class="main-content">' not in content:
        errors.append("Main content area is missing")
    if 'mermaid.initialize' not in content:
        warnings.append("Mermaid initialization script is missing")

    return {
        "success": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "stats": stats
    }


def print_verification_report(result: dict):
    """検証結果をプリント"""
    print()
    print("=== HTML Verification ===")

    stats = result["stats"]

    # 統計情報
    if stats["sections"] > 0:
        print(f"✓ Sections: {stats['sections']}")
    if stats["articles"] > 0:
        print(f"✓ Articles: {stats['articles']}")
    if stats["mermaid_diagrams"] > 0:
        print(f"✓ Mermaid diagrams: {stats['mermaid_diagrams']}")
    if stats["config_files"] > 0:
        print(f"✓ Config files (syntax highlighted): {stats['config_files']}")
    if stats["has_graph_viewer"]:
        print(f"✓ Interactive graph viewer: included")
    if stats["nav_links"] > 0:
        print(f"✓ Navigation links: {stats['nav_links']}")

    # 警告
    if result["warnings"]:
        print()
        print("Warnings:")
        for warning in result["warnings"]:
            print(f"  ⚠ {warning}")

    # エラー
    if result["errors"]:
        print()
        print("Errors:")
        for error in result["errors"]:
            print(f"  ✗ {error}")

    print()
    print("=== Verification Complete ===")
    print(f"Warnings: {len(result['warnings'])}")
    print(f"Errors: {len(result['errors'])}")

    return result["success"]


def fix_html_issues(html_path: Path, result: dict) -> bool:
    """検出された問題を自動修正"""
    if not result["errors"]:
        return True

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    modified = False

    # GraphDBデータ欠損の修正
    if "Graph viewer found but data is missing" in result["errors"]:
        # 空のデータで初期化
        empty_data = '{"nodes": [], "links": []}'
        content = re.sub(
            r'const data = \{\};',
            f'const data = {empty_data};',
            content
        )
        modified = True
        print("  Fixed: Added empty graph data")

    if modified:
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True

    return False


def compile_nextra(input_dir: str, output_dir: str = None):
    """
    Nextra形式でレポートをコンパイル

    Args:
        input_dir: 入力ディレクトリ（Markdownファイル）
        output_dir: 出力ディレクトリ（デフォルト: ./reports/nextra-site）
    """
    import subprocess

    if output_dir is None:
        output_dir = os.path.join(input_dir, "nextra-site")

    # Step 1: Markdown to MDX conversion
    print("Step 1: Converting Markdown to MDX...")
    convert_script = Path(__file__).parent / "convert_to_nextra.py"

    result = subprocess.run([
        "python", str(convert_script),
        "--input", input_dir,
        "--output", output_dir
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error converting to MDX: {result.stderr}")
        return False

    print(result.stdout)

    # Step 2: npm install (if needed)
    print("\nStep 2: Checking dependencies...")
    node_modules = Path(output_dir) / "node_modules"
    if not node_modules.exists():
        print("Installing dependencies...")
        result = subprocess.run(
            ["npm", "install"],
            cwd=output_dir,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"Error installing dependencies: {result.stderr}")
            return False
        print("Dependencies installed.")
    else:
        print("Dependencies already installed.")

    # Step 3: Build Next.js site
    print("\nStep 3: Building Next.js site...")
    result = subprocess.run(
        ["npx", "next", "build"],
        cwd=output_dir,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"Error building Next.js site: {result.stderr}")
        return False

    print(result.stdout)

    # Success
    out_dir = Path(output_dir) / "out"
    print(f"\n✅ Nextra site built successfully!")
    print(f"   Output: {out_dir}")
    print(f"\nTo preview:")
    print(f"   cd {output_dir}")
    print(f"   npx serve out/")

    return True


def main():
    parser = argparse.ArgumentParser(description="Compile Markdown reports to HTML or Nextra")
    parser.add_argument("--input-dir", default="./reports",
                        help="Input directory containing markdown files")
    parser.add_argument("--output", default="./reports/00_summary/full-report.html",
                        help="Output HTML file (for --format html)")
    parser.add_argument("--title", default="リファクタリング分析レポート",
                        help="Report title")
    parser.add_argument("--theme", choices=["light", "dark"], default="light",
                        help="Color theme (for --format html)")
    parser.add_argument("--format", choices=["html", "nextra"], default="html",
                        help="Output format: html (single file) or nextra (static site)")
    parser.add_argument("--nextra-output", default=None,
                        help="Output directory for Nextra site (default: ./reports/nextra-site)")
    parser.add_argument("--no-verify", action="store_true",
                        help="Skip HTML verification (for --format html)")
    args = parser.parse_args()

    if args.format == "nextra":
        # Nextra形式でビルド
        compile_nextra(args.input_dir, args.nextra_output)
    else:
        # HTML形式でビルド（既存の機能）
        compile_report(args.input_dir, args.output, args.title, args.theme)

        # HTML検証
        if not args.no_verify:
            output_path = Path(args.output)
            result = verify_html_report(output_path)
            print_verification_report(result)

            # 問題があれば自動修正を試みる
            if result["errors"]:
                print()
                print("Attempting to fix issues...")
                if fix_html_issues(output_path, result):
                    print("Issues fixed. Re-verifying...")
                    result = verify_html_report(output_path)
                    print_verification_report(result)


if __name__ == "__main__":
    main()
