#!/usr/bin/env python3
"""
分析結果パーサー

/analyze-system の出力（Markdownファイル）をパースして、
GraphDB構築用のCSVファイルを生成します。

使用方法:
    python parse_analysis.py --input-dir ./.refactoring-output/01_analysis --output-dir ./.refactoring-output/graph/data

前提条件:
    pip install pandas
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Dict, Any

try:
    import pandas as pd
except ImportError:
    print("Error: pandas is not installed. Run: pip install pandas")
    sys.exit(1)


def parse_markdown_table(content: str) -> List[Dict[str, str]]:
    """Markdownテーブルをパースしてリストに変換"""
    lines = content.strip().split('\n')
    rows = []
    headers = []

    for i, line in enumerate(lines):
        line = line.strip()
        if not line or not line.startswith('|'):
            continue

        # セパレータ行をスキップ
        if re.match(r'^\|[\s\-:]+\|$', line.replace('|', '|')):
            continue
        if '---' in line:
            continue

        cells = [cell.strip() for cell in line.split('|')[1:-1]]

        if not headers:
            headers = cells
        else:
            if len(cells) == len(headers):
                row = dict(zip(headers, cells))
                rows.append(row)

    return rows


def extract_tables_from_markdown(content: str) -> Dict[str, List[Dict[str, str]]]:
    """Markdownファイルから複数のテーブルを抽出"""
    tables = {}
    current_section = "default"

    # セクションごとにテーブルを分割
    sections = re.split(r'^(#{1,4})\s+(.+)$', content, flags=re.MULTILINE)

    i = 0
    while i < len(sections):
        if sections[i].startswith('#'):
            # セクションヘッダー
            level = sections[i]
            name = sections[i + 1] if i + 1 < len(sections) else ""
            current_section = name.strip()
            i += 2
        else:
            # コンテンツ
            section_content = sections[i]
            # テーブルを探す
            table_pattern = r'\|[^\n]+\|\n\|[\s\-:]+\|\n(?:\|[^\n]+\|\n?)+'
            matches = re.findall(table_pattern, section_content)
            for match in matches:
                parsed = parse_markdown_table(match)
                if parsed:
                    if current_section not in tables:
                        tables[current_section] = []
                    tables[current_section].extend(parsed)
            i += 1

    return tables


def parse_ubiquitous_language(file_path: Path) -> tuple:
    """ubiquitous_language.md をパース"""
    content = file_path.read_text(encoding='utf-8')
    tables = extract_tables_from_markdown(content)

    terms = []
    synonyms = []

    for section_name, rows in tables.items():
        for row in rows:
            # 用語テーブル
            if '用語（日本語）' in row or '用語' in row.get('', ''):
                term = {
                    'name': row.get('用語（英語）', row.get('コード上の表現', '')),
                    'name_ja': row.get('用語（日本語）', row.get('用語', '')),
                    'definition': row.get('定義', row.get('説明', '')),
                    'domain': section_name
                }
                if term['name']:
                    terms.append(term)

            # 略語テーブル
            elif '略語' in row:
                term = {
                    'name': row.get('略語', ''),
                    'name_ja': row.get('正式名称', ''),
                    'definition': row.get('説明', ''),
                    'domain': 'Abbreviation'
                }
                if term['name']:
                    terms.append(term)

            # 同義語テーブル
            elif '用語A' in row:
                synonyms.append({
                    'term_a': row.get('用語A', ''),
                    'term_b': row.get('用語B', ''),
                    'preferred': row.get('推奨用語', ''),
                    'reason': row.get('理由', '')
                })

    return terms, synonyms


def parse_domain_code_mapping(file_path: Path) -> tuple:
    """domain_code_mapping.md をパース"""
    content = file_path.read_text(encoding='utf-8')
    tables = extract_tables_from_markdown(content)

    entities = []
    domains = set()
    belongs_to = []
    has_term = []

    for section_name, rows in tables.items():
        for row in rows:
            # ドメイン-コードマッピングテーブル
            if '概念カテゴリ' in row or 'コード上の実装' in row:
                entity_name = row.get('コード上の実装', '').replace('`', '').strip()
                file_path_val = row.get('ファイルパス', '')
                entity_type = row.get('概念カテゴリ', row.get('実装パターン', ''))
                term_name = row.get('設計書での名称', '')

                if entity_name:
                    entities.append({
                        'name': entity_name,
                        'file_path': file_path_val,
                        'type': entity_type,
                        'line_number': 0  # 行番号は後で補完
                    })

                    # ドメインへの所属
                    domain_name = section_name.replace('###', '').strip()
                    if domain_name and domain_name != 'default':
                        domains.add(domain_name)
                        belongs_to.append({
                            'entity': entity_name,
                            'domain': domain_name
                        })

                    # 用語との関連
                    if term_name:
                        has_term.append({
                            'entity': entity_name,
                            'term': term_name
                        })

    # ドメインをリストに変換
    domain_list = [{'name': d, 'type': 'BusinessDomain', 'description': ''} for d in domains]

    return entities, domain_list, belongs_to, has_term


def parse_actors_roles(file_path: Path) -> tuple:
    """actors_roles_permissions.md をパース"""
    content = file_path.read_text(encoding='utf-8')
    tables = extract_tables_from_markdown(content)

    actors = []
    roles = []
    has_role = []

    for section_name, rows in tables.items():
        for row in rows:
            # アクターテーブル
            if 'アクター' in row:
                actor = {
                    'name': row.get('アクター', ''),
                    'type': 'Human' if '人間' in section_name else 'System',
                    'description': row.get('説明', row.get('主な操作', ''))
                }
                if actor['name']:
                    actors.append(actor)

            # ロールテーブル
            elif 'ロール' in row:
                role = {
                    'name': row.get('ロール', ''),
                    'permissions': row.get('権限セット', row.get('説明', ''))
                }
                if role['name']:
                    roles.append(role)

                # アクターとロールの関連（権限マトリックスから推測）
                # ここは簡易的な実装

    return actors, roles, has_role


def save_csv(data: List[Dict], output_path: Path, columns: List[str] = None):
    """データをCSVとして保存"""
    if not data:
        return

    df = pd.DataFrame(data)
    if columns:
        # 指定されたカラムのみ、順序通りに出力
        existing_cols = [c for c in columns if c in df.columns]
        df = df[existing_cols]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"Saved: {output_path} ({len(df)} rows)")


def main():
    parser = argparse.ArgumentParser(description='Parse analysis results to CSV')
    parser.add_argument('--input-dir', required=True, help='Directory containing analysis markdown files')
    parser.add_argument('--output-dir', required=True, help='Directory to output CSV files')
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)

    if not input_dir.exists():
        print(f"Error: Input directory does not exist: {input_dir}")
        sys.exit(1)

    # ユビキタス言語
    ubiquitous_file = input_dir / 'ubiquitous_language.md'
    if ubiquitous_file.exists():
        print(f"Parsing: {ubiquitous_file}")
        terms, synonyms = parse_ubiquitous_language(ubiquitous_file)
        save_csv(terms, output_dir / 'terms.csv', ['name', 'name_ja', 'definition', 'domain'])
    else:
        print(f"Warning: {ubiquitous_file} not found")

    # ドメイン-コード対応
    mapping_file = input_dir / 'domain_code_mapping.md'
    if mapping_file.exists():
        print(f"Parsing: {mapping_file}")
        entities, domains, belongs_to, has_term = parse_domain_code_mapping(mapping_file)
        save_csv(entities, output_dir / 'entities.csv', ['name', 'file_path', 'type', 'line_number'])
        save_csv(domains, output_dir / 'domains.csv', ['name', 'type', 'description'])
        save_csv(belongs_to, output_dir / 'belongs_to.csv', ['entity', 'domain'])
        save_csv(has_term, output_dir / 'has_term.csv', ['entity', 'term'])
    else:
        print(f"Warning: {mapping_file} not found")

    # アクター・ロール
    actors_file = input_dir / 'actors_roles_permissions.md'
    if actors_file.exists():
        print(f"Parsing: {actors_file}")
        actors, roles, has_role = parse_actors_roles(actors_file)
        save_csv(actors, output_dir / 'actors.csv', ['name', 'type', 'description'])
        save_csv(roles, output_dir / 'roles.csv', ['name', 'permissions'])
        save_csv(has_role, output_dir / 'has_role.csv', ['actor', 'role'])
    else:
        print(f"Warning: {actors_file} not found")

    print("\nParsing complete!")
    print(f"Output directory: {output_dir}")


if __name__ == "__main__":
    main()
