#!/usr/bin/env python3
"""
GraphDB可視化スクリプト

RyuGraphデータベースの内容をMermaid/DOT/HTML形式で可視化します。

使用方法:
    python visualize_graph.py --db-path ./knowledge.ryugraph --output-dir ./visualizations

前提条件:
    pip install ryugraph pandas
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

try:
    import pandas as pd
except ImportError:
    print("Error: pandas is not installed. Run: pip install pandas")
    sys.exit(1)


def load_csv_data(data_dir: str) -> dict:
    """CSVファイルからデータを読み込む"""
    data_path = Path(data_dir)
    data = {}

    csv_files = [
        'terms.csv', 'domains.csv', 'entities.csv', 'actors.csv', 'roles.csv',
        'belongs_to.csv', 'has_term.csv', 'has_role.csv', 'references.csv'
    ]

    for csv_file in csv_files:
        csv_path = data_path / csv_file
        if csv_path.exists():
            df = pd.read_csv(csv_path)
            data[csv_file.replace('.csv', '')] = df
            print(f"  Loaded: {csv_file} ({len(df)} rows)")
        else:
            print(f"  Not found: {csv_file}")
            data[csv_file.replace('.csv', '')] = pd.DataFrame()

    return data


def generate_mermaid(data: dict, output_path: str, domain_filter: str = None,
                     node_type_filter: str = None, layout: str = "LR"):
    """Mermaid形式のグラフを生成"""

    lines = [f"graph {layout}"]

    # ドメイン別にエンティティをグループ化
    domains = data.get('domains', pd.DataFrame())
    entities = data.get('entities', pd.DataFrame())
    belongs_to = data.get('belongs_to', pd.DataFrame())
    references = data.get('references', pd.DataFrame())

    if domains.empty or entities.empty:
        lines.append("    NoData[No data available]")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        return

    # ドメインフィルタ
    if domain_filter:
        domains = domains[domains['name'] == domain_filter]
        belongs_to = belongs_to[belongs_to['domain'] == domain_filter]

    # ドメイン別にサブグラフを作成
    domain_entities = defaultdict(list)
    for _, row in belongs_to.iterrows():
        domain_entities[row['domain']].append(row['entity'])

    for _, domain in domains.iterrows():
        domain_name = domain['name']
        domain_type = domain.get('type', 'Unknown')
        lines.append(f"    subgraph {domain_name}[\"{domain_name} ({domain_type})\"]")

        entities_in_domain = domain_entities.get(domain_name, [])
        for entity_name in entities_in_domain[:20]:  # 最大20エンティティ
            # ノードタイプフィルタ
            if node_type_filter:
                entity_row = entities[entities['name'] == entity_name]
                if not entity_row.empty and entity_row.iloc[0].get('type', '') != node_type_filter:
                    continue
            safe_name = entity_name.replace(" ", "_")
            lines.append(f"        {safe_name}[{entity_name}]")

        lines.append("    end")

    # リレーションを追加
    if not references.empty:
        lines.append("")
        lines.append("    %% References")
        for _, row in references.head(50).iterrows():  # 最大50リレーション
            from_entity = row['from_entity'].replace(" ", "_")
            to_entity = row['to_entity'].replace(" ", "_")
            rel_type = row.get('relation_type', 'references')
            lines.append(f"    {from_entity} -->|{rel_type}| {to_entity}")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"  Generated: {output_path}")


def generate_dot(data: dict, output_path: str, domain_filter: str = None):
    """DOT形式（Graphviz）のグラフを生成"""

    lines = [
        "digraph KnowledgeGraph {",
        "    rankdir=LR;",
        "    node [shape=box, style=filled, fillcolor=lightblue];",
        "    edge [color=gray];",
        ""
    ]

    domains = data.get('domains', pd.DataFrame())
    entities = data.get('entities', pd.DataFrame())
    belongs_to = data.get('belongs_to', pd.DataFrame())
    references = data.get('references', pd.DataFrame())

    # ドメインフィルタ
    if domain_filter:
        domains = domains[domains['name'] == domain_filter]
        belongs_to = belongs_to[belongs_to['domain'] == domain_filter]

    # ドメイン別にクラスタを作成
    domain_entities = defaultdict(list)
    for _, row in belongs_to.iterrows():
        domain_entities[row['domain']].append(row['entity'])

    # 色マップ
    colors = {
        'Core': 'lightcoral',
        'Supporting': 'lightblue',
        'Integration': 'lightgreen'
    }

    for _, domain in domains.iterrows():
        domain_name = domain['name']
        domain_type = domain.get('type', 'Unknown')
        color = colors.get(domain_type, 'lightyellow')

        lines.append(f"    subgraph cluster_{domain_name} {{")
        lines.append(f"        label=\"{domain_name}\";")
        lines.append(f"        style=filled;")
        lines.append(f"        fillcolor={color};")

        entities_in_domain = domain_entities.get(domain_name, [])
        for entity_name in entities_in_domain[:20]:
            safe_name = entity_name.replace(" ", "_").replace("-", "_")
            lines.append(f"        {safe_name} [label=\"{entity_name}\"];")

        lines.append("    }")
        lines.append("")

    # リレーションを追加
    if not references.empty:
        lines.append("    // References")
        for _, row in references.head(50).iterrows():
            from_entity = row['from_entity'].replace(" ", "_").replace("-", "_")
            to_entity = row['to_entity'].replace(" ", "_").replace("-", "_")
            rel_type = row.get('relation_type', 'references')
            lines.append(f"    {from_entity} -> {to_entity} [label=\"{rel_type}\"];")

    lines.append("}")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"  Generated: {output_path}")


def generate_html(data: dict, output_path: str, domain_filter: str = None):
    """インタラクティブHTML（D3.js）を生成"""

    domains = data.get('domains', pd.DataFrame())
    entities = data.get('entities', pd.DataFrame())
    belongs_to = data.get('belongs_to', pd.DataFrame())
    references = data.get('references', pd.DataFrame())
    terms = data.get('terms', pd.DataFrame())

    # ノードとリンクのデータを構築
    nodes = []
    links = []
    node_ids = {}

    # ドメインノード
    for idx, row in domains.iterrows():
        node_id = f"domain_{row['name']}"
        node_ids[row['name']] = node_id
        nodes.append({
            "id": node_id,
            "name": row['name'],
            "type": "Domain",
            "group": row.get('type', 'Unknown')
        })

    # エンティティノード
    for idx, row in entities.iterrows():
        node_id = f"entity_{row['name']}"
        node_ids[row['name']] = node_id
        nodes.append({
            "id": node_id,
            "name": row['name'],
            "type": "Entity",
            "group": row.get('type', 'class')
        })

    # 用語ノード
    for idx, row in terms.iterrows():
        node_id = f"term_{row['name']}"
        node_ids[row['name']] = node_id
        nodes.append({
            "id": node_id,
            "name": f"{row['name']} ({row.get('name_ja', '')})",
            "type": "Term",
            "group": row.get('domain', 'Unknown')
        })

    # BELONGS_TO リンク
    for _, row in belongs_to.iterrows():
        source = node_ids.get(row['entity'])
        target = node_ids.get(row['domain'])
        if source and target:
            links.append({
                "source": source,
                "target": target,
                "type": "BELONGS_TO"
            })

    # REFERENCES リンク
    for _, row in references.iterrows():
        source = node_ids.get(row['from_entity'])
        target = node_ids.get(row['to_entity'])
        if source and target:
            links.append({
                "source": source,
                "target": target,
                "type": row.get('relation_type', 'references')
            })

    # HTMLテンプレート
    html_template = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Knowledge Graph Visualization</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background: #1a1a2e;
        }
        #graph {
            width: 100vw;
            height: 100vh;
        }
        .node {
            cursor: pointer;
        }
        .node text {
            font-size: 10px;
            fill: white;
        }
        .link {
            stroke: #666;
            stroke-opacity: 0.6;
        }
        .tooltip {
            position: absolute;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 10px;
            border-radius: 5px;
            font-size: 12px;
            pointer-events: none;
        }
        #controls {
            position: fixed;
            top: 10px;
            left: 10px;
            background: rgba(255,255,255,0.9);
            padding: 10px;
            border-radius: 5px;
            z-index: 100;
        }
        #search {
            width: 200px;
            padding: 5px;
            margin-bottom: 10px;
        }
        #stats {
            font-size: 12px;
            color: #666;
        }
    </style>
</head>
<body>
    <div id="controls">
        <input type="text" id="search" placeholder="Search nodes...">
        <div id="stats"></div>
    </div>
    <div id="graph"></div>
    <script>
        const data = ''' + json.dumps({"nodes": nodes, "links": links}) + ''';

        const width = window.innerWidth;
        const height = window.innerHeight;

        const svg = d3.select("#graph")
            .append("svg")
            .attr("width", width)
            .attr("height", height);

        const g = svg.append("g");

        // Zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on("zoom", (event) => g.attr("transform", event.transform));
        svg.call(zoom);

        // Color scale
        const color = d3.scaleOrdinal()
            .domain(["Domain", "Entity", "Term"])
            .range(["#e74c3c", "#3498db", "#2ecc71"]);

        // Force simulation
        const simulation = d3.forceSimulation(data.nodes)
            .force("link", d3.forceLink(data.links).id(d => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collision", d3.forceCollide().radius(30));

        // Links
        const link = g.append("g")
            .selectAll("line")
            .data(data.links)
            .join("line")
            .attr("class", "link")
            .attr("stroke-width", 1);

        // Nodes
        const node = g.append("g")
            .selectAll("g")
            .data(data.nodes)
            .join("g")
            .attr("class", "node")
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));

        node.append("circle")
            .attr("r", d => d.type === "Domain" ? 15 : 10)
            .attr("fill", d => color(d.type));

        node.append("text")
            .attr("dx", 12)
            .attr("dy", 4)
            .text(d => d.name.substring(0, 20));

        // Tooltip
        const tooltip = d3.select("body")
            .append("div")
            .attr("class", "tooltip")
            .style("opacity", 0);

        node.on("mouseover", (event, d) => {
            tooltip.transition().duration(200).style("opacity", 1);
            tooltip.html(`<strong>${d.name}</strong><br/>Type: ${d.type}<br/>Group: ${d.group}`)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 10) + "px");
        }).on("mouseout", () => {
            tooltip.transition().duration(500).style("opacity", 0);
        });

        simulation.on("tick", () => {
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);

            node.attr("transform", d => `translate(${d.x},${d.y})`);
        });

        function dragstarted(event) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            event.subject.fx = event.subject.x;
            event.subject.fy = event.subject.y;
        }

        function dragged(event) {
            event.subject.fx = event.x;
            event.subject.fy = event.y;
        }

        function dragended(event) {
            if (!event.active) simulation.alphaTarget(0);
            event.subject.fx = null;
            event.subject.fy = null;
        }

        // Search
        d3.select("#search").on("input", function() {
            const query = this.value.toLowerCase();
            node.style("opacity", d =>
                d.name.toLowerCase().includes(query) ? 1 : 0.2);
            link.style("opacity", 0.2);
        });

        // Stats
        d3.select("#stats").html(
            `Nodes: ${data.nodes.length} | Links: ${data.links.length}`
        );
    </script>
</body>
</html>'''

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_template)

    print(f"  Generated: {output_path}")


def generate_summary(data: dict, output_path: str):
    """可視化サマリーを生成"""

    domains = data.get('domains', pd.DataFrame())
    entities = data.get('entities', pd.DataFrame())
    terms = data.get('terms', pd.DataFrame())
    references = data.get('references', pd.DataFrame())

    lines = [
        "# GraphDB可視化サマリー",
        "",
        f"**生成日時**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 統計情報",
        "",
        "| 項目 | 件数 |",
        "|------|------|",
        f"| ドメイン | {len(domains)} |",
        f"| エンティティ | {len(entities)} |",
        f"| 用語 | {len(terms)} |",
        f"| リレーション | {len(references)} |",
        "",
        "## 生成ファイル",
        "",
        "| ファイル | 形式 | 用途 |",
        "|---------|------|------|",
        "| graph.mmd | Mermaid | ドキュメント埋め込み |",
        "| graph.dot | DOT | Graphviz変換 |",
        "| graph.html | HTML | インタラクティブビュー |",
        "",
        "## 使用方法",
        "",
        "### Mermaid → PNG変換",
        "```bash",
        "mmdc -i graph.mmd -o graph.png",
        "```",
        "",
        "### DOT → PNG変換",
        "```bash",
        "dot -Tpng graph.dot -o graph-dot.png",
        "```",
        "",
        "### HTMLビュー",
        "```bash",
        "open graph.html  # macOS",
        "xdg-open graph.html  # Linux",
        "```",
        ""
    ]

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"  Generated: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Visualize GraphDB")
    parser.add_argument("--db-path", default="./knowledge.ryugraph",
                        help="Path to RyuGraph database")
    parser.add_argument("--data-dir", default="./reports/graph/data",
                        help="Path to CSV data directory")
    parser.add_argument("--output-dir", default="./reports/graph/visualizations",
                        help="Output directory for visualizations")
    parser.add_argument("--format", choices=["mermaid", "dot", "html", "all"],
                        default="all", help="Output format")
    parser.add_argument("--domain", help="Filter by domain")
    parser.add_argument("--node-type", help="Filter by node type")
    parser.add_argument("--layout", choices=["LR", "TB", "RL", "BT"],
                        default="LR", help="Graph layout direction")
    args = parser.parse_args()

    print("=== GraphDB Visualization ===")
    print(f"Data directory: {args.data_dir}")
    print(f"Output directory: {args.output_dir}")
    print()

    # 出力ディレクトリを作成
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # データを読み込み
    print("Loading data...")
    data = load_csv_data(args.data_dir)
    print()

    # 可視化を生成
    print("Generating visualizations...")

    if args.format in ["mermaid", "all"]:
        generate_mermaid(data, output_path / "graph.mmd",
                        domain_filter=args.domain,
                        node_type_filter=args.node_type,
                        layout=args.layout)

    if args.format in ["dot", "all"]:
        generate_dot(data, output_path / "graph.dot",
                    domain_filter=args.domain)

    if args.format in ["html", "all"]:
        generate_html(data, output_path / "graph.html",
                     domain_filter=args.domain)

    generate_summary(data, output_path / "summary.md")

    print()
    print("=== Visualization Complete ===")
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()
