#!/usr/bin/env python3
"""
ScalarDB Sizing Estimation HTML Report Generator

Usage:
    python generate_html.py --input estimate.md --output estimate.html
    python generate_html.py --json estimate.json --output estimate.html
"""

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ScalarDB Cluster サイジング見積もり</title>
    <style>
        :root {
            --primary-color: #2563eb;
            --secondary-color: #64748b;
            --success-color: #22c55e;
            --warning-color: #f59e0b;
            --danger-color: #ef4444;
            --bg-color: #f8fafc;
            --card-bg: #ffffff;
            --text-color: #1e293b;
            --border-color: #e2e8f0;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            line-height: 1.6;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }

        header {
            background: linear-gradient(135deg, var(--primary-color), #1d4ed8);
            color: white;
            padding: 2rem;
            margin-bottom: 2rem;
            border-radius: 12px;
        }

        header h1 {
            font-size: 1.75rem;
            margin-bottom: 0.5rem;
        }

        header .subtitle {
            opacity: 0.9;
            font-size: 0.95rem;
        }

        .meta-info {
            display: flex;
            gap: 2rem;
            margin-top: 1rem;
            font-size: 0.85rem;
            opacity: 0.9;
        }

        .card {
            background: var(--card-bg);
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 1.5rem;
            overflow: hidden;
        }

        .card-header {
            background: var(--bg-color);
            padding: 1rem 1.5rem;
            border-bottom: 1px solid var(--border-color);
            font-weight: 600;
            font-size: 1.1rem;
        }

        .card-body {
            padding: 1.5rem;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
        }

        th, td {
            padding: 0.75rem 1rem;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }

        th {
            background: var(--bg-color);
            font-weight: 600;
            color: var(--secondary-color);
        }

        tr:hover {
            background: var(--bg-color);
        }

        .cost-highlight {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--primary-color);
        }

        .cost-secondary {
            font-size: 1rem;
            color: var(--secondary-color);
        }

        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin-bottom: 1.5rem;
        }

        .summary-item {
            background: var(--card-bg);
            padding: 1.25rem;
            border-radius: 8px;
            border: 1px solid var(--border-color);
        }

        .summary-item .label {
            font-size: 0.85rem;
            color: var(--secondary-color);
            margin-bottom: 0.25rem;
        }

        .summary-item .value {
            font-size: 1.25rem;
            font-weight: 600;
        }

        .badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 500;
        }

        .badge-primary { background: #dbeafe; color: var(--primary-color); }
        .badge-success { background: #dcfce7; color: var(--success-color); }
        .badge-warning { background: #fef3c7; color: var(--warning-color); }
        .badge-danger { background: #fee2e2; color: var(--danger-color); }

        .architecture-diagram {
            background: #1e293b;
            color: #e2e8f0;
            padding: 1.5rem;
            border-radius: 8px;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.8rem;
            overflow-x: auto;
            white-space: pre;
        }

        .section-title {
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid var(--primary-color);
        }

        .notes {
            background: #fffbeb;
            border-left: 4px solid var(--warning-color);
            padding: 1rem;
            margin-top: 1rem;
            font-size: 0.9rem;
        }

        .footer {
            text-align: center;
            padding: 2rem;
            color: var(--secondary-color);
            font-size: 0.85rem;
        }

        @media print {
            body { background: white; }
            .container { max-width: 100%; padding: 1rem; }
            .card { break-inside: avoid; box-shadow: none; border: 1px solid var(--border-color); }
            header { print-color-adjust: exact; -webkit-print-color-adjust: exact; }
        }

        @media (max-width: 768px) {
            .container { padding: 1rem; }
            .meta-info { flex-direction: column; gap: 0.5rem; }
            table { font-size: 0.8rem; }
            th, td { padding: 0.5rem; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>ScalarDB Cluster サイジング見積もり</h1>
            <p class="subtitle">{title}</p>
            <div class="meta-info">
                <span>作成日: {date}</span>
                <span>環境: {environment}</span>
                <span>クラウド: {cloud}</span>
            </div>
        </header>

        <!-- Executive Summary -->
        <div class="card">
            <div class="card-header">エグゼクティブサマリー</div>
            <div class="card-body">
                <div class="summary-grid">
                    <div class="summary-item">
                        <div class="label">月額費用 (USD)</div>
                        <div class="value cost-highlight">${total_cost_usd:,.0f}</div>
                    </div>
                    <div class="summary-item">
                        <div class="label">月額費用 (JPY)</div>
                        <div class="value cost-highlight">¥{total_cost_jpy:,.0f}</div>
                    </div>
                    <div class="summary-item">
                        <div class="label">ScalarDB Pod数</div>
                        <div class="value">{scalardb_pods}</div>
                    </div>
                    <div class="summary-item">
                        <div class="label">Kubernetes Node数</div>
                        <div class="value">{k8s_nodes}</div>
                    </div>
                    <div class="summary-item">
                        <div class="label">想定TPS</div>
                        <div class="value">{target_tps}</div>
                    </div>
                    <div class="summary-item">
                        <div class="label">可用性目標</div>
                        <div class="value">{availability}</div>
                    </div>
                </div>
                <div class="notes">
                    <strong>為替レート:</strong> 1 USD = {exchange_rate} JPY（参考値）<br>
                    <strong>注意:</strong> ScalarDBライセンス費用は別途お問い合わせください
                </div>
            </div>
        </div>

        <!-- Architecture -->
        <div class="card">
            <div class="card-header">アーキテクチャ構成</div>
            <div class="card-body">
                <div class="architecture-diagram">{architecture_diagram}</div>
            </div>
        </div>

        <!-- Component Details -->
        <div class="card">
            <div class="card-header">コンポーネント別構成</div>
            <div class="card-body">
                <h3 class="section-title">Kubernetes クラスター</h3>
                <table>
                    <thead>
                        <tr>
                            <th>項目</th>
                            <th>構成</th>
                            <th>数量</th>
                            <th>費用 (USD/月)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {k8s_table_rows}
                    </tbody>
                </table>

                <h3 class="section-title" style="margin-top: 2rem;">ScalarDB Cluster</h3>
                <table>
                    <thead>
                        <tr>
                            <th>項目</th>
                            <th>設定値</th>
                        </tr>
                    </thead>
                    <tbody>
                        {scalardb_table_rows}
                    </tbody>
                </table>

                <h3 class="section-title" style="margin-top: 2rem;">バックエンドデータベース</h3>
                <table>
                    <thead>
                        <tr>
                            <th>項目</th>
                            <th>構成</th>
                            <th>費用 (USD/月)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {db_table_rows}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Cost Breakdown -->
        <div class="card">
            <div class="card-header">費用内訳</div>
            <div class="card-body">
                <table>
                    <thead>
                        <tr>
                            <th>コンポーネント</th>
                            <th>月額 (USD)</th>
                            <th>月額 (JPY)</th>
                            <th>備考</th>
                        </tr>
                    </thead>
                    <tbody>
                        {cost_table_rows}
                    </tbody>
                    <tfoot>
                        <tr style="font-weight: bold; background: var(--bg-color);">
                            <td>合計</td>
                            <td>${total_cost_usd:,.0f}</td>
                            <td>¥{total_cost_jpy:,.0f}</td>
                            <td></td>
                        </tr>
                    </tfoot>
                </table>
            </div>
        </div>

        <!-- Recommendations -->
        <div class="card">
            <div class="card-header">推奨事項</div>
            <div class="card-body">
                {recommendations}
            </div>
        </div>

        <footer class="footer">
            <p>Generated by ScalarDB Sizing Estimator</p>
            <p>このレポートは見積もり目的であり、実際の費用は変動する可能性があります</p>
        </footer>
    </div>
</body>
</html>
"""

def generate_html_from_json(data: dict) -> str:
    """Generate HTML from structured JSON data"""

    # Default values
    defaults = {
        'title': 'ScalarDB Cluster 構成見積もり',
        'date': datetime.now().strftime('%Y-%m-%d'),
        'environment': '本番環境',
        'cloud': 'AWS',
        'total_cost_usd': 0,
        'total_cost_jpy': 0,
        'exchange_rate': 150,
        'scalardb_pods': 5,
        'k8s_nodes': 8,
        'target_tps': '2,000',
        'availability': '99.9%',
        'architecture_diagram': '',
        'k8s_table_rows': '',
        'scalardb_table_rows': '',
        'db_table_rows': '',
        'cost_table_rows': '',
        'recommendations': ''
    }

    # Merge with provided data
    for key, value in data.items():
        if key in defaults:
            defaults[key] = value

    # Calculate JPY if not provided
    if defaults['total_cost_jpy'] == 0 and defaults['total_cost_usd'] > 0:
        defaults['total_cost_jpy'] = defaults['total_cost_usd'] * defaults['exchange_rate']

    return HTML_TEMPLATE.format(**defaults)


def parse_markdown_to_data(markdown_content: str) -> dict:
    """Parse markdown content to extract structured data"""
    data = {}

    # Extract title
    title_match = re.search(r'^#\s+(.+)$', markdown_content, re.MULTILINE)
    if title_match:
        data['title'] = title_match.group(1)

    # Extract date
    date_match = re.search(r'作成日[：:]\s*(\d{4}-\d{2}-\d{2})', markdown_content)
    if date_match:
        data['date'] = date_match.group(1)

    # Extract environment
    env_match = re.search(r'環境[：:]\s*(.+)', markdown_content)
    if env_match:
        data['environment'] = env_match.group(1).strip()

    # Extract cloud
    cloud_match = re.search(r'クラウド[：:]\s*(.+)', markdown_content)
    if cloud_match:
        data['cloud'] = cloud_match.group(1).strip()

    # Extract costs (try to find USD amounts)
    cost_match = re.search(r'\$([0-9,]+)', markdown_content)
    if cost_match:
        data['total_cost_usd'] = float(cost_match.group(1).replace(',', ''))

    return data


def main():
    parser = argparse.ArgumentParser(description='Generate HTML report from ScalarDB sizing estimate')
    parser.add_argument('--input', '-i', help='Input markdown file')
    parser.add_argument('--json', '-j', help='Input JSON file')
    parser.add_argument('--output', '-o', required=True, help='Output HTML file')

    args = parser.parse_args()

    if args.json:
        with open(args.json, 'r', encoding='utf-8') as f:
            data = json.load(f)
    elif args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        data = parse_markdown_to_data(markdown_content)
    else:
        # Use defaults
        data = {}

    html_content = generate_html_from_json(data)

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"HTML report generated: {args.output}")


if __name__ == '__main__':
    main()
