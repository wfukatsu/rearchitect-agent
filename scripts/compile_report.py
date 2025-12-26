#!/usr/bin/env python3
"""
レポートコンパイルスクリプト

分析結果のMarkdownファイルを統合HTMLレポートに変換します。

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


# セクション定義
SECTIONS = [
    {
        "id": "summary",
        "title": "エグゼクティブサマリー",
        "dir": "00_summary",
        "files": ["executive-summary.md"]
    },
    {
        "id": "analysis",
        "title": "システム分析",
        "dir": "01_analysis",
        "files": ["system-overview.md", "ubiquitous-language.md", "actors-roles-permissions.md", "domain-code-mapping.md"]
    },
    {
        "id": "evaluation",
        "title": "MMI評価",
        "dir": "02_evaluation",
        "files": ["mmi-overview.md", "mmi-by-module.md", "mmi-improvement-plan.md"]
    },
    {
        "id": "design",
        "title": "設計",
        "dir": "03_design",
        "files": [
            "domain-analysis.md", "context-map.md", "system-mapping.md",
            "target_architecture.md", "transformation_plan.md", "operations_plan.md",
            "scalardb_architecture.md", "scalardb_schema.md", "scalardb_transaction.md", "scalardb_migration.md"
        ]
    },
    {
        "id": "stories",
        "title": "ドメインストーリー",
        "dir": "04_stories",
        "files": ["domain-stories.md"]
    },
    {
        "id": "graph",
        "title": "ナレッジグラフ",
        "dir": "graph",
        "files": ["schema.md", "statistics.md"]
    }
]


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
        file_id = file.replace('.md', '').replace('_', '-')
        file_title = file.replace('.md', '').replace('_', ' ').replace('-', ' ').title()
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
        TocExtension(permalink=True)
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

        # 目次エントリ
        toc_html.append(generate_toc_entry(section_id, section_title, section["files"]))

        # セクションコンテンツ
        content_html.append(f'<section id="{section_id}">')
        content_html.append(f'<h1>{section_title}</h1>')

        for file_name in section["files"]:
            file_path = section_dir / file_name
            if not file_path.exists():
                continue

            file_id = file_name.replace('.md', '').replace('_', '-')
            content = read_markdown_file(file_path)

            # Mermaidブロックを変換
            content = convert_mermaid_blocks(content)

            # MarkdownをHTMLに変換
            md.reset()
            html_content = md.convert(content)

            content_html.append(f'<article id="{section_id}-{file_id}">')
            content_html.append(html_content)
            content_html.append('</article>')

        # グラフセクションの場合、インタラクティブビューアを追加
        if section_id == "graph":
            graph_html_path = section_dir / "visualizations" / "graph.html"
            graph_data = extract_graph_data(graph_html_path)
            if graph_data:
                print(f"  Adding: Interactive graph viewer")
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


def main():
    parser = argparse.ArgumentParser(description="Compile Markdown reports to HTML")
    parser.add_argument("--input-dir", default="./reports",
                        help="Input directory containing markdown files")
    parser.add_argument("--output", default="./reports/00_summary/full-report.html",
                        help="Output HTML file")
    parser.add_argument("--title", default="リファクタリング分析レポート",
                        help="Report title")
    parser.add_argument("--theme", choices=["light", "dark"], default="light",
                        help="Color theme")
    args = parser.parse_args()

    compile_report(args.input_dir, args.output, args.title, args.theme)


if __name__ == "__main__":
    main()
