#!/usr/bin/env python3
"""
Markdown → Nextra変換スクリプト

既存のreports/ディレクトリのMarkdownファイルをNextra形式に変換します。

使用方法:
    python scripts/convert_to_nextra.py --input reports --output reports/nextra-site

機能:
    - Markdownファイルの自動検出
    - _meta.json自動生成
    - フロントマター追加
    - 設定ファイル（YAML/JSON等）のMDX変換
    - GraphDBデータのコピー
"""

import argparse
import json
import shutil
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List


# セクション定義（既存のcompile_report.pyから）
SECTION_DEFINITIONS = {
    "00_summary": {
        "title": "Executive Summary",
        "priority": ["executive-summary.md", "conversation-summary.md"],
        "subdirs": []
    },
    "01_analysis": {
        "title": "System Analysis",
        "priority": [
            "ubiquitous-language.md",
            "actors-roles-permissions.md",
            "domain-code-mapping.md"
        ],
        "subdirs": []
    },
    "02_evaluation": {
        "title": "Quality Evaluation",
        "priority": [
            "mmi-overview.md",
            "ddd-evaluation-report.md",
            "integrated-evaluation.md",
            "unified-improvement-plan.md"
        ],
        "subdirs": []
    },
    "03_design": {
        "title": "Architecture Design",
        "priority": [
            "ddd-redesign.md",
            "microservices-architecture.md",
            "api-design-overview.md",
            "api-gateway-design.md",
            "api-security-design.md",
            "scalardb-architecture.md"
        ],
        "subdirs": ["api-specifications", "config"]
    },
    "04_stories": {
        "title": "Domain Stories",
        "priority": ["domain-stories.md"],
        "subdirs": []
    },
    "05_estimate": {
        "title": "Cost Estimates",
        "priority": [],
        "subdirs": []
    },
    "06_implementation": {
        "title": "Implementation Specs",
        "priority": ["implementation-specs.md"],
        "subdirs": []
    },
    "07_test-specs": {
        "title": "Test Specifications",
        "priority": [
            "unit-test-specs.md",
            "integration-test-specs.md",
            "performance-test-specs.md"
        ],
        "subdirs": ["bdd-scenarios"]
    },
    "graph": {
        "title": "Knowledge Graph",
        "priority": ["statistics.md"],
        "subdirs": ["visualizations"]
    }
}

# 設定ファイル拡張子
CONFIG_EXTENSIONS = [".yaml", ".yml", ".json", ".properties", ".toml", ".xml", ".feature", ".graphql", ".gql", ".proto"]


def normalize_file_id(file_name: str) -> str:
    """ファイル名をIDに正規化"""
    extensions_to_remove = ['.md', '.yaml', '.yml', '.json', '.properties', '.toml', '.xml', '.feature', '.graphql', '.gql', '.proto']

    result = file_name
    for ext in extensions_to_remove:
        if result.endswith(ext):
            result = result[:-len(ext)]
            break

    result = result.replace('/', '-').replace('_', '-').replace('.', '-')
    return result


def discover_files(section_dir: Path, priority_files: List[str], include_subdirs: List[str]) -> List[str]:
    """ディレクトリ内のファイルを検出"""
    found_files = []
    seen_basenames = set()

    extensions = [".md"] + CONFIG_EXTENSIONS

    # サブディレクトリを解決
    actual_subdirs = []
    if include_subdirs:
        for subdir in include_subdirs:
            if subdir == "*":
                if section_dir.exists():
                    for d in section_dir.iterdir():
                        if d.is_dir():
                            actual_subdirs.append(d.name)
            else:
                actual_subdirs.append(subdir)

    def get_dedup_basename(fname: str) -> str:
        if '/' in fname:
            fname = fname.split('/')[-1]
        return normalize_file_id(fname)

    # 優先ファイルを追加
    for file_name in priority_files:
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


def apply_escape_rules(line: str) -> str:
    """MDXエスケープルールを適用（単一行）"""
    # Type A: 汎用型syntax (Array<String>, Map<K,V>, etc.)
    line = re.sub(r'Array<([A-Za-z]+)>', r'Array&lt;\1&gt;', line)
    line = re.sub(r'Map<([A-Za-z]+),\s*([A-Za-z]+)>', r'Map&lt;\1, \2&gt;', line)
    line = re.sub(r'Optional<([A-Za-z]+)>', r'Optional&lt;\1&gt;', line)
    line = re.sub(r'List<([A-Za-z]+)>', r'List&lt;\1&gt;', line)
    line = re.sub(r'Set<([A-Za-z]+)>', r'Set&lt;\1&gt;', line)

    # Type B: 比較演算子+数値 (<500ms, <1 min, etc.)
    # スペースありなしの両方に対応
    line = re.sub(r'<(\d+)\s*(ms|s|min|minute|minutes|hour|hours|%)', r'&lt;\1 \2', line)

    # Type B-2: RPO/RTO パターン (<1 hour など、括弧内も含む)
    line = re.sub(r'\(<(\d+)', r'(&lt;\1', line)

    # Type C: 特殊ファイル名・XSSテスト
    line = re.sub(r'"([^"]*)<>([^"]*)"', r'"\1&lt;&gt;\2"', line)
    line = re.sub(r'<img\s+src=([^\s>]+)([^>]*)>', r'&lt;img src=\1\2&gt;', line)

    # Type D: API変数参照 ({id}, {token}, etc.)
    api_vars = ['id', 'token', 'key', 'name', 'type', 'value', 'orderId', 'userId',
                'fileId', 'auditSetId', 'folderId', 'groupId', 'itemId']
    for var in api_vars:
        line = re.sub(rf'\{{{var}\}}', rf'\\{{{var}}}', line)

    # Type E: JavaScript式 ({{ new Date() }})
    line = re.sub(r'\{\{\s*new\s+Date\(\)[^}]*\}\}', datetime.now().strftime('%Y-%m-%d'), line)

    return line


def escape_mdx_content(content: str) -> str:
    """コードブロック外のMDX問題パターンをエスケープし、Mermaidブロックを変換する"""
    lines = content.split("\n")
    result = []
    in_code_block = False
    in_mermaid_block = False
    mermaid_content = []
    has_mermaid = False

    for line in lines:
        # コードブロック境界を検出
        if line.strip().startswith("```"):
            if in_mermaid_block:
                # Mermaidブロック終了 - コンポーネントに変換
                in_mermaid_block = False
                in_code_block = False
                has_mermaid = True
                mermaid_chart = "\n".join(mermaid_content)
                # Mermaidコンポーネントとして出力
                result.append("")
                result.append("<Mermaid chart={`")
                result.append(mermaid_chart)
                result.append("`} />")
                result.append("")
                mermaid_content = []
                continue
            elif line.strip().startswith("```mermaid"):
                # Mermaidブロック開始
                in_mermaid_block = True
                in_code_block = True
                continue
            else:
                # 通常のコードブロック
                in_code_block = not in_code_block
                result.append(line)
                continue

        # Mermaidブロック内
        if in_mermaid_block:
            mermaid_content.append(line)
            continue

        # コードブロック外でのみエスケープルールを適用
        if not in_code_block:
            line = apply_escape_rules(line)

        result.append(line)

    content_with_mermaid = "\n".join(result)

    # Mermaidを使用している場合、インポート文を追加
    if has_mermaid:
        content_with_mermaid = "import Mermaid from '@/components/Mermaid'\n\n" + content_with_mermaid

    return content_with_mermaid


def add_frontmatter(content: str, title: str, description: str = "") -> str:
    """フロントマターを追加"""
    # 既にフロントマターがある場合はスキップ
    if content.startswith('---'):
        return content

    frontmatter = f"""---
title: {title}
description: {description or title}
---

"""
    return frontmatter + content


def convert_markdown_to_mdx(input_path: Path, output_path: Path, title: str):
    """MarkdownをMDXに変換"""
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # MDXエスケープ処理（コードブロック外のみ）
    content = escape_mdx_content(content)

    # フロントマター追加
    content = add_frontmatter(content, title)

    # MDX import statements を追加（必要に応じて）
    # 例: GraphViewer, ConfigFileなど

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)


def convert_config_file_to_mdx(input_path: Path, output_path: Path, title: str):
    """設定ファイルをMDXに変換（ConfigFileコンポーネント使用）"""
    ext = input_path.suffix.lower()

    # 言語マッピング
    lang_map = {
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.json': 'json',
        '.properties': 'properties',
        '.toml': 'toml',
        '.xml': 'xml',
        '.feature': 'gherkin',
        '.graphql': 'graphql',
        '.gql': 'graphql',
        '.proto': 'protobuf'
    }

    language = lang_map.get(ext, 'text')

    # ファイル内容を読み込み
    with open(input_path, 'r', encoding='utf-8') as f:
        file_content = f.read()

    # エスケープ処理（バッククォートとバックスラッシュ）
    file_content = file_content.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')

    # MDX content
    mdx_content = f"""---
title: {title}
---

import ConfigFile from '@/components/ConfigFile'

# {title}

<ConfigFile
  content={{`{file_content}`}}
  language="{language}"
  filename="{input_path.name}"
/>
"""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(mdx_content)


def generate_meta_json(section_id: str, files: List[str], section_def: Dict) -> Dict:
    """_meta.jsonを生成"""
    meta = {}

    for file_name in files:
        # ファイルIDを生成
        file_id = normalize_file_id(file_name)

        # タイトルを生成（ファイル名から）
        if '/' in file_name:
            # サブディレクトリ内のファイル
            parts = file_name.split('/')
            title = parts[-1].replace('-', ' ').replace('_', ' ').title()
            for ext in CONFIG_EXTENSIONS + ['.md']:
                title = title.replace(ext.title(), '')
        else:
            title = file_name.replace('-', ' ').replace('_', ' ').title()
            for ext in CONFIG_EXTENSIONS + ['.md']:
                title = title.replace(ext.title(), '')

        meta[file_id] = title

    return meta


def copy_graph_data(input_dir: Path, nextra_dir: Path):
    """GraphDBデータをコピー"""
    graph_dir = input_dir / "graph"
    if not graph_dir.exists():
        return

    # visualizations/graph.html からデータを抽出してJSONに変換
    graph_html = graph_dir / "visualizations" / "graph.html"
    if graph_html.exists():
        with open(graph_html, 'r', encoding='utf-8') as f:
            content = f.read()

        # JavaScriptのdataオブジェクトを抽出
        match = re.search(r'const data = ({.*?});', content, re.DOTALL)
        if match:
            data_json = match.group(1)

            # public/data/graph.json に保存
            output_path = nextra_dir / "public" / "data" / "graph.json"
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(data_json)

            print(f"  ✓ Graph data extracted to public/data/graph.json")

    # statistics.md などのMarkdownファイルをコピー
    stats_md = graph_dir / "statistics.md"
    if stats_md.exists():
        output_path = nextra_dir / "pages" / "graph" / "statistics.mdx"
        convert_markdown_to_mdx(stats_md, output_path, "Graph Statistics")
        print(f"  ✓ Converted graph/statistics.md")

    # インタラクティブビューアのページを作成
    viewer_mdx = nextra_dir / "pages" / "graph" / "interactive-viewer.mdx"
    viewer_content = """---
title: Interactive Graph Viewer
---

import GraphViewer from '@/components/GraphViewer'

# Interactive Knowledge Graph

Explore the system's knowledge graph with an interactive D3.js visualization.

**Features:**
- Drag nodes to rearrange
- Scroll to zoom
- Hover over nodes for details
- Search for specific nodes

<GraphViewer dataPath="/data/graph.json" />

## Legend

- **Domain** - Business domain
- **Entity** - Domain entity
- **Term** - Ubiquitous language term
- **ValueObject** - Value object
- **Aggregate** - Aggregate root
"""

    viewer_mdx.parent.mkdir(parents=True, exist_ok=True)
    with open(viewer_mdx, 'w', encoding='utf-8') as f:
        f.write(viewer_content)

    print(f"  ✓ Created interactive graph viewer page")


def convert_reports_to_nextra(input_dir: str, nextra_dir: str):
    """reportsディレクトリをNextra形式に変換"""
    input_path = Path(input_dir)
    nextra_path = Path(nextra_dir)

    print(f"Converting reports from {input_dir} to {nextra_dir}")

    # Root _meta.json
    root_meta = {}
    root_meta["index"] = {
        "title": "Overview",
        "type": "page"
    }

    # 各セクションを処理
    for section_id, section_def in SECTION_DEFINITIONS.items():
        section_dir = input_path / section_id
        if not section_dir.exists():
            print(f"  ⚠ Section {section_id} not found, skipping")
            continue

        print(f"  Processing {section_id}...")

        # ファイルを検出
        files = discover_files(
            section_dir,
            section_def["priority"],
            section_def.get("subdirs", [])
        )

        if not files:
            print(f"    No files found in {section_id}")
            continue

        # Root _meta.jsonに追加
        root_meta[section_id] = section_def["title"]

        # セクション用ディレクトリ作成
        section_output_dir = nextra_path / "pages" / section_id
        section_output_dir.mkdir(parents=True, exist_ok=True)

        # セクション _meta.json生成
        section_meta = generate_meta_json(section_id, files, section_def)

        # ファイルを変換
        for file_name in files:
            input_file = section_dir / file_name
            file_id = normalize_file_id(file_name)
            output_file = section_output_dir / f"{file_id}.mdx"

            # ファイルタイトル
            title = section_meta.get(file_id, file_name)

            # 拡張子で処理を分岐
            if input_file.suffix == '.md':
                convert_markdown_to_mdx(input_file, output_file, title)
            elif input_file.suffix in CONFIG_EXTENSIONS:
                convert_config_file_to_mdx(input_file, output_file, title)

            print(f"    ✓ Converted {file_name}")

        # _meta.json保存
        meta_path = section_output_dir / "_meta.json"
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(section_meta, f, indent=2)

        print(f"    ✓ Generated _meta.json for {section_id}")

    # Root _meta.json保存
    root_meta_path = nextra_path / "pages" / "_meta.json"
    with open(root_meta_path, 'w', encoding='utf-8') as f:
        json.dump(root_meta, f, indent=2)

    print(f"  ✓ Generated root _meta.json")

    # GraphDBデータをコピー
    copy_graph_data(input_path, nextra_path)

    # コンポーネントをコピー
    copy_components(nextra_path)

    print(f"\n✅ Conversion complete!")


def copy_components(nextra_dir: Path):
    """コンポーネントテンプレートをコピー"""
    template_dir = Path(__file__).parent.parent / ".claude" / "templates" / "nextra"

    if not template_dir.exists():
        print(f"  ⚠ Component templates not found at {template_dir}")
        return

    components_dir = nextra_dir / "components"
    components_dir.mkdir(parents=True, exist_ok=True)

    for template_file in template_dir.glob("*.tsx"):
        output_file = components_dir / template_file.name
        shutil.copy(template_file, output_file)
        print(f"  ✓ Copied component: {template_file.name}")


def main():
    parser = argparse.ArgumentParser(description="Convert Markdown reports to Nextra format")
    parser.add_argument(
        "--input",
        type=str,
        default="reports",
        help="Input reports directory (default: reports)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="reports/nextra-site",
        help="Output Nextra directory (default: reports/nextra-site)"
    )

    args = parser.parse_args()

    convert_reports_to_nextra(args.input, args.output)


if __name__ == "__main__":
    main()
