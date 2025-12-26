#!/usr/bin/env python3
"""
GraphDB構築スクリプト

ユビキタス言語とコード解析結果からRyuGraphデータベースを構築します。

使用方法:
    python build_graph.py --data-dir ./data --db-path ./knowledge.ryugraph

前提条件:
    pip install ryugraph pandas
"""

import argparse
import os
import sys
from pathlib import Path
from datetime import datetime

try:
    import ryugraph
except ImportError:
    print("Error: ryugraph is not installed. Run: pip install ryugraph")
    sys.exit(1)

try:
    import pandas as pd
except ImportError:
    print("Error: pandas is not installed. Run: pip install pandas")
    sys.exit(1)


# グラフスキーマ定義
SCHEMA = """
-- ノードテーブル
CREATE NODE TABLE IF NOT EXISTS UbiquitousTerm(
    name STRING PRIMARY KEY,
    name_ja STRING,
    definition STRING,
    domain STRING
);

CREATE NODE TABLE IF NOT EXISTS Domain(
    name STRING PRIMARY KEY,
    type STRING,
    description STRING
);

CREATE NODE TABLE IF NOT EXISTS Entity(
    name STRING PRIMARY KEY,
    file_path STRING,
    type STRING,
    line_number INT64
);

CREATE NODE TABLE IF NOT EXISTS Method(
    name STRING PRIMARY KEY,
    signature STRING,
    file_path STRING,
    line_number INT64
);

CREATE NODE TABLE IF NOT EXISTS File(
    path STRING PRIMARY KEY,
    language STRING,
    module STRING
);

CREATE NODE TABLE IF NOT EXISTS Actor(
    name STRING PRIMARY KEY,
    type STRING,
    description STRING
);

CREATE NODE TABLE IF NOT EXISTS Role(
    name STRING PRIMARY KEY,
    permissions STRING
);

-- リレーションテーブル
CREATE REL TABLE IF NOT EXISTS BELONGS_TO(FROM Entity TO Domain);
CREATE REL TABLE IF NOT EXISTS DEFINED_IN(FROM Entity TO File);
CREATE REL TABLE IF NOT EXISTS METHOD_DEFINED_IN(FROM Method TO File);
CREATE REL TABLE IF NOT EXISTS REFERENCES(FROM Entity TO Entity);
CREATE REL TABLE IF NOT EXISTS CALLS(FROM Method TO Method);
CREATE REL TABLE IF NOT EXISTS IMPLEMENTS(FROM Entity TO Entity);
CREATE REL TABLE IF NOT EXISTS HAS_TERM(FROM Entity TO UbiquitousTerm);
CREATE REL TABLE IF NOT EXISTS METHOD_HAS_TERM(FROM Method TO UbiquitousTerm);
CREATE REL TABLE IF NOT EXISTS HAS_ROLE(FROM Actor TO Role);
"""


def create_database(db_path: str) -> tuple:
    """データベースを作成または開く"""
    # 既存のDBがあれば削除（再構築）
    db_dir = Path(db_path)
    if db_dir.exists():
        import shutil
        shutil.rmtree(db_dir)

    db = ryugraph.Database(db_path)
    conn = ryugraph.Connection(db)
    return db, conn


def create_schema(conn) -> None:
    """グラフスキーマを作成"""
    for statement in SCHEMA.strip().split(';'):
        statement = statement.strip()
        if statement and not statement.startswith('--'):
            try:
                conn.execute(statement)
            except Exception as e:
                print(f"Warning: Schema creation issue: {e}")


def load_csv_if_exists(data_dir: Path, filename: str) -> pd.DataFrame:
    """CSVファイルが存在すれば読み込む"""
    filepath = data_dir / filename
    if filepath.exists():
        return pd.read_csv(filepath)
    return pd.DataFrame()


def import_nodes(conn, data_dir: Path) -> dict:
    """ノードデータをインポート"""
    stats = {}

    # UbiquitousTerm
    terms_df = load_csv_if_exists(data_dir, 'terms.csv')
    if not terms_df.empty:
        for _, row in terms_df.iterrows():
            try:
                conn.execute(
                    "CREATE (t:UbiquitousTerm {name: $name, name_ja: $name_ja, definition: $definition, domain: $domain})",
                    {
                        "name": str(row.get('name', '')),
                        "name_ja": str(row.get('name_ja', '')),
                        "definition": str(row.get('definition', '')),
                        "domain": str(row.get('domain', ''))
                    }
                )
            except Exception as e:
                print(f"Warning: Failed to insert term {row.get('name')}: {e}")
        stats['UbiquitousTerm'] = len(terms_df)

    # Domain
    domains_df = load_csv_if_exists(data_dir, 'domains.csv')
    if not domains_df.empty:
        for _, row in domains_df.iterrows():
            try:
                conn.execute(
                    "CREATE (d:Domain {name: $name, type: $type, description: $description})",
                    {
                        "name": str(row.get('name', '')),
                        "type": str(row.get('type', '')),
                        "description": str(row.get('description', ''))
                    }
                )
            except Exception as e:
                print(f"Warning: Failed to insert domain {row.get('name')}: {e}")
        stats['Domain'] = len(domains_df)

    # Entity
    entities_df = load_csv_if_exists(data_dir, 'entities.csv')
    if not entities_df.empty:
        for _, row in entities_df.iterrows():
            try:
                conn.execute(
                    "CREATE (e:Entity {name: $name, file_path: $file_path, type: $type, line_number: $line_number})",
                    {
                        "name": str(row.get('name', '')),
                        "file_path": str(row.get('file_path', '')),
                        "type": str(row.get('type', '')),
                        "line_number": int(row.get('line_number', 0))
                    }
                )
            except Exception as e:
                print(f"Warning: Failed to insert entity {row.get('name')}: {e}")
        stats['Entity'] = len(entities_df)

    # Method
    methods_df = load_csv_if_exists(data_dir, 'methods.csv')
    if not methods_df.empty:
        for _, row in methods_df.iterrows():
            try:
                conn.execute(
                    "CREATE (m:Method {name: $name, signature: $signature, file_path: $file_path, line_number: $line_number})",
                    {
                        "name": str(row.get('name', '')),
                        "signature": str(row.get('signature', '')),
                        "file_path": str(row.get('file_path', '')),
                        "line_number": int(row.get('line_number', 0))
                    }
                )
            except Exception as e:
                print(f"Warning: Failed to insert method {row.get('name')}: {e}")
        stats['Method'] = len(methods_df)

    # File
    files_df = load_csv_if_exists(data_dir, 'files.csv')
    if not files_df.empty:
        for _, row in files_df.iterrows():
            try:
                conn.execute(
                    "CREATE (f:File {path: $path, language: $language, module: $module})",
                    {
                        "path": str(row.get('path', '')),
                        "language": str(row.get('language', '')),
                        "module": str(row.get('module', ''))
                    }
                )
            except Exception as e:
                print(f"Warning: Failed to insert file {row.get('path')}: {e}")
        stats['File'] = len(files_df)

    # Actor
    actors_df = load_csv_if_exists(data_dir, 'actors.csv')
    if not actors_df.empty:
        for _, row in actors_df.iterrows():
            try:
                conn.execute(
                    "CREATE (a:Actor {name: $name, type: $type, description: $description})",
                    {
                        "name": str(row.get('name', '')),
                        "type": str(row.get('type', '')),
                        "description": str(row.get('description', ''))
                    }
                )
            except Exception as e:
                print(f"Warning: Failed to insert actor {row.get('name')}: {e}")
        stats['Actor'] = len(actors_df)

    # Role
    roles_df = load_csv_if_exists(data_dir, 'roles.csv')
    if not roles_df.empty:
        for _, row in roles_df.iterrows():
            try:
                conn.execute(
                    "CREATE (r:Role {name: $name, permissions: $permissions})",
                    {
                        "name": str(row.get('name', '')),
                        "permissions": str(row.get('permissions', ''))
                    }
                )
            except Exception as e:
                print(f"Warning: Failed to insert role {row.get('name')}: {e}")
        stats['Role'] = len(roles_df)

    return stats


def import_relationships(conn, data_dir: Path) -> dict:
    """リレーションデータをインポート"""
    stats = {}

    rel_mappings = [
        ('belongs_to.csv', 'BELONGS_TO', 'Entity', 'Domain', 'entity', 'domain'),
        ('defined_in.csv', 'DEFINED_IN', 'Entity', 'File', 'entity', 'file'),
        ('method_defined_in.csv', 'METHOD_DEFINED_IN', 'Method', 'File', 'method', 'file'),
        ('references.csv', 'REFERENCES', 'Entity', 'Entity', 'source', 'target'),
        ('calls.csv', 'CALLS', 'Method', 'Method', 'caller', 'callee'),
        ('implements.csv', 'IMPLEMENTS', 'Entity', 'Entity', 'child', 'parent'),
        ('has_term.csv', 'HAS_TERM', 'Entity', 'UbiquitousTerm', 'entity', 'term'),
        ('method_has_term.csv', 'METHOD_HAS_TERM', 'Method', 'UbiquitousTerm', 'method', 'term'),
        ('has_role.csv', 'HAS_ROLE', 'Actor', 'Role', 'actor', 'role'),
    ]

    for filename, rel_type, from_label, to_label, from_col, to_col in rel_mappings:
        df = load_csv_if_exists(data_dir, filename)
        if not df.empty:
            count = 0
            for _, row in df.iterrows():
                try:
                    query = f"""
                        MATCH (a:{from_label} {{name: $from_name}})
                        MATCH (b:{to_label} {{name: $to_name}})
                        CREATE (a)-[:{rel_type}]->(b)
                    """
                    # File ノードは path で検索
                    if to_label == 'File':
                        query = f"""
                            MATCH (a:{from_label} {{name: $from_name}})
                            MATCH (b:{to_label} {{path: $to_name}})
                            CREATE (a)-[:{rel_type}]->(b)
                        """

                    conn.execute(query, {
                        "from_name": str(row.get(from_col, '')),
                        "to_name": str(row.get(to_col, ''))
                    })
                    count += 1
                except Exception as e:
                    print(f"Warning: Failed to create {rel_type}: {e}")
            stats[rel_type] = count

    return stats


def generate_statistics(data_dir: Path, node_stats: dict, rel_stats: dict) -> str:
    """統計情報のMarkdownを生成"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    md = f"""# GraphDB統計情報

## 生成日時
{now}

## ノード統計

| ノードタイプ | 件数 |
|------------|------|
"""
    for node_type, count in node_stats.items():
        md += f"| {node_type} | {count} |\n"

    md += """
## リレーション統計

| リレーションタイプ | 件数 |
|------------------|------|
"""
    for rel_type, count in rel_stats.items():
        md += f"| {rel_type} | {count} |\n"

    total_nodes = sum(node_stats.values())
    total_rels = sum(rel_stats.values())

    md += f"""
## サマリー

- 総ノード数: {total_nodes}
- 総リレーション数: {total_rels}
- データディレクトリ: {data_dir}
"""

    return md


def main():
    parser = argparse.ArgumentParser(description='Build RyuGraph database from CSV data')
    parser.add_argument('--data-dir', required=True, help='Directory containing CSV files')
    parser.add_argument('--db-path', required=True, help='Path for the RyuGraph database')
    parser.add_argument('--stats-output', help='Path to output statistics markdown file')
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    db_path = args.db_path

    if not data_dir.exists():
        print(f"Error: Data directory does not exist: {data_dir}")
        sys.exit(1)

    print(f"Creating database at: {db_path}")
    db, conn = create_database(db_path)

    print("Creating schema...")
    create_schema(conn)

    print("Importing nodes...")
    node_stats = import_nodes(conn, data_dir)
    print(f"  Imported: {node_stats}")

    print("Importing relationships...")
    rel_stats = import_relationships(conn, data_dir)
    print(f"  Imported: {rel_stats}")

    # 統計情報の出力
    stats_md = generate_statistics(data_dir, node_stats, rel_stats)

    if args.stats_output:
        stats_path = Path(args.stats_output)
        stats_path.parent.mkdir(parents=True, exist_ok=True)
        stats_path.write_text(stats_md, encoding='utf-8')
        print(f"Statistics written to: {stats_path}")
    else:
        print("\n" + stats_md)

    print("\nDatabase build complete!")


if __name__ == "__main__":
    main()
