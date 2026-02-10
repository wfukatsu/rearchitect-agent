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
        if re.match(r'^\|[\s\-:]+\|$', line):
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
    lines = content.split('\n')

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # セクションヘッダーを検出
        if line.startswith('#'):
            # # や ## 等のレベルを取り除いてセクション名を取得
            current_section = re.sub(r'^#+\s*', '', line).strip()
            i += 1
            continue

        # テーブルの開始を検出（|で始まる行）
        if line.startswith('|'):
            table_lines = []
            # テーブル行を収集
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_lines.append(lines[i])
                i += 1

            # テーブルをパース
            if len(table_lines) >= 2:  # ヘッダー + セパレータ以上
                table_content = '\n'.join(table_lines)
                parsed = parse_markdown_table(table_content)
                if parsed:
                    if current_section not in tables:
                        tables[current_section] = []
                    tables[current_section].extend(parsed)
            continue

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
            # 用語テーブル - 複数のカラム形式に対応
            # 形式1: 用語（日本語）、用語（英語）
            # 形式2: 用語、英語、定義、コード内の表現
            name = (row.get('英語', '') or
                    row.get('用語（英語）', '') or
                    row.get('コード上の表現', '') or
                    row.get('コード内の表現', ''))
            name_ja = (row.get('用語', '') or
                       row.get('用語（日本語）', ''))
            definition = (row.get('定義', '') or
                          row.get('説明', ''))

            if name and name_ja:
                # ** マーカーを除去
                name_ja = name_ja.replace('**', '').strip()
                term = {
                    'name': name,
                    'name_ja': name_ja,
                    'definition': definition,
                    'domain': section_name
                }
                terms.append(term)
                continue

            # 略語テーブル
            if '略語' in row:
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
            # エンティティマッピングテーブル
            # 形式1: 概念カテゴリ、コード上の実装
            # 形式2: ドメイン概念、クラス、テーブル
            # 形式3: ユースケース、Controller、Service
            entity_name = (row.get('クラス', '') or
                           row.get('コード上の実装', '') or
                           row.get('Controller', '') or
                           row.get('Service', ''))
            entity_name = entity_name.replace('`', '').strip()

            # 空や "-" をスキップ
            if not entity_name or entity_name == '-':
                continue

            domain_concept = (row.get('ドメイン概念', '') or
                              row.get('用語', '') or
                              row.get('ユースケース', ''))
            domain_concept = domain_concept.replace('`', '').replace('**', '').strip()

            entity_type = (row.get('概念カテゴリ', '') or
                           row.get('実装パターン', '') or
                           row.get('関係', '') or
                           'Entity')

            # クラス名を抽出（メソッド呼び出しの場合）
            if '.' in entity_name and '(' in entity_name:
                entity_name = entity_name.split('.')[0]

            entities.append({
                'name': entity_name,
                'file_path': entity_name + '.java' if not entity_name.endswith('.java') else entity_name,
                'type': entity_type,
                'line_number': 0
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
            if domain_concept:
                has_term.append({
                    'entity': entity_name,
                    'term': domain_concept
                })

    # 重複を除去
    seen_entities = set()
    unique_entities = []
    for e in entities:
        if e['name'] not in seen_entities:
            seen_entities.add(e['name'])
            unique_entities.append(e)

    # ドメインをリストに変換
    domain_list = [{'name': d, 'type': 'BusinessDomain', 'description': ''} for d in domains]

    return unique_entities, domain_list, belongs_to, has_term


def parse_actors_roles(file_path: Path) -> tuple:
    """actors_roles_permissions.md をパース"""
    content = file_path.read_text(encoding='utf-8')
    tables = extract_tables_from_markdown(content)

    actors = []
    roles = []
    has_role = []
    seen_actors = set()
    seen_roles = set()

    for section_name, rows in tables.items():
        for row in rows:
            # アクター詳細テーブル（role値を持つ）
            if 'role値' in row:
                actor_name = row.get('アクター', '').replace('**', '').strip()
                if actor_name and actor_name not in seen_actors:
                    actors.append({
                        'name': actor_name,
                        'type': 'Human',
                        'description': row.get('説明', '') + ' - ' + row.get('主な責務', '')
                    })
                    seen_actors.add(actor_name)
                    # アクターはロールでもある
                    roles.append({
                        'name': actor_name,
                        'permissions': row.get('主な責務', '')
                    })
                    seen_roles.add(actor_name)
                    has_role.append({
                        'actor': actor_name,
                        'role': actor_name
                    })

            # 外部アクターテーブル
            elif 'インタラクション' in row:
                actor_name = row.get('アクター', '').replace('**', '').strip()
                if actor_name and actor_name not in seen_actors:
                    actors.append({
                        'name': actor_name,
                        'type': 'System',
                        'description': row.get('説明', '')
                    })
                    seen_actors.add(actor_name)

            # 一般的なアクターテーブル
            elif 'アクター' in row and row.get('アクター'):
                actor_name = row.get('アクター', '').replace('**', '').strip()
                if actor_name and actor_name not in seen_actors:
                    actors.append({
                        'name': actor_name,
                        'type': 'Human' if '外部' not in section_name else 'System',
                        'description': row.get('説明', row.get('主な操作', ''))
                    })
                    seen_actors.add(actor_name)

            # ロールテーブル
            if 'ロール' in row and row.get('ロール'):
                role_name = row.get('ロール', '').replace('**', '').strip()
                if role_name and role_name not in seen_roles:
                    roles.append({
                        'name': role_name,
                        'permissions': row.get('権限セット', row.get('説明', ''))
                    })
                    seen_roles.add(role_name)

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

    # ヘルパー関数：複数のファイル名パターンを試す
    def find_file(patterns: list) -> Path:
        """複数のファイル名パターンから存在するファイルを探す"""
        for pattern in patterns:
            file_path = input_dir / pattern
            if file_path.exists():
                return file_path
        return None

    # ユビキタス言語 (kebab-case と snake_case の両方をサポート)
    ubiquitous_file = find_file(['ubiquitous-language.md', 'ubiquitous_language.md'])
    if ubiquitous_file:
        print(f"Parsing: {ubiquitous_file}")
        terms, synonyms = parse_ubiquitous_language(ubiquitous_file)
        save_csv(terms, output_dir / 'terms.csv', ['name', 'name_ja', 'definition', 'domain'])
    else:
        print(f"Warning: ubiquitous-language.md or ubiquitous_language.md not found")

    # ドメイン-コード対応
    mapping_file = find_file(['domain-code-mapping.md', 'domain_code_mapping.md'])
    if mapping_file:
        print(f"Parsing: {mapping_file}")
        entities, domains, belongs_to, has_term = parse_domain_code_mapping(mapping_file)
        save_csv(entities, output_dir / 'entities.csv', ['name', 'file_path', 'type', 'line_number'])
        save_csv(domains, output_dir / 'domains.csv', ['name', 'type', 'description'])
        save_csv(belongs_to, output_dir / 'belongs_to.csv', ['entity', 'domain'])
        save_csv(has_term, output_dir / 'has_term.csv', ['entity', 'term'])
    else:
        print(f"Warning: domain-code-mapping.md or domain_code_mapping.md not found")

    # アクター・ロール
    actors_file = find_file(['actors-roles-permissions.md', 'actors_roles_permissions.md'])
    if actors_file:
        print(f"Parsing: {actors_file}")
        actors, roles, has_role = parse_actors_roles(actors_file)
        save_csv(actors, output_dir / 'actors.csv', ['name', 'type', 'description'])
        save_csv(roles, output_dir / 'roles.csv', ['name', 'permissions'])
        save_csv(has_role, output_dir / 'has_role.csv', ['actor', 'role'])
    else:
        print(f"Warning: actors-roles-permissions.md or actors_roles_permissions.md not found")

    print("\nParsing complete!")
    print(f"Output directory: {output_dir}")


if __name__ == "__main__":
    main()
