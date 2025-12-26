#!/usr/bin/env python3
"""
GraphDB探索スクリプト

RyuGraphデータベースに対してCypherクエリを実行します。

使用方法:
    python query_graph.py --db-path ./knowledge.ryugraph --query "MATCH (n) RETURN n LIMIT 10"
    python query_graph.py --db-path ./knowledge.ryugraph --interactive

前提条件:
    pip install ryugraph pandas
"""

import argparse
import sys
import json
from pathlib import Path

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


# よく使うクエリテンプレート
QUERY_TEMPLATES = {
    "all_nodes": "MATCH (n) RETURN labels(n) AS type, count(*) AS count",
    "all_rels": "MATCH ()-[r]->() RETURN type(r) AS type, count(*) AS count",
    "terms": "MATCH (t:UbiquitousTerm) RETURN t.name, t.name_ja, t.definition LIMIT 20",
    "entities": "MATCH (e:Entity) RETURN e.name, e.type, e.file_path LIMIT 20",
    "domains": "MATCH (d:Domain) RETURN d.name, d.type, d.description",
    "actors": "MATCH (a:Actor) RETURN a.name, a.type, a.description",
    "term_entities": """
        MATCH (e:Entity)-[:HAS_TERM]->(t:UbiquitousTerm)
        RETURN t.name_ja AS term, collect(e.name) AS entities
    """,
    "entity_dependencies": """
        MATCH (e:Entity)-[:REFERENCES]->(target:Entity)
        RETURN e.name AS source, collect(target.name) AS dependencies
    """,
    "method_calls": """
        MATCH (m:Method)-[:CALLS]->(target:Method)
        RETURN m.name AS caller, collect(target.name) AS callees
        LIMIT 20
    """,
    "most_referenced": """
        MATCH (e:Entity)<-[:REFERENCES]-(other)
        RETURN e.name, e.file_path, count(other) AS references
        ORDER BY references DESC
        LIMIT 10
    """,
    "circular_deps": """
        MATCH (a:Entity)-[:REFERENCES]->(b:Entity)-[:REFERENCES]->(a)
        RETURN a.name AS entity1, b.name AS entity2
    """,
}


def open_database(db_path: str):
    """データベースを開く"""
    db_dir = Path(db_path)
    if not db_dir.exists():
        print(f"Error: Database does not exist: {db_path}")
        print("Run /build-graph first to create the database.")
        sys.exit(1)

    db = ryugraph.Database(db_path)
    conn = ryugraph.Connection(db)
    return db, conn


def execute_query(conn, query: str, output_format: str = 'table') -> str:
    """クエリを実行して結果を返す"""
    try:
        result = conn.execute(query)

        if output_format == 'json':
            rows = []
            for row in result:
                rows.append(dict(zip(result.get_column_names(), row)))
            return json.dumps(rows, indent=2, ensure_ascii=False)

        elif output_format == 'table':
            df = result.get_as_df()
            if df.empty:
                return "No results found."
            return df.to_markdown(index=False)

        elif output_format == 'csv':
            df = result.get_as_df()
            return df.to_csv(index=False)

        else:
            # raw形式
            lines = []
            for row in result:
                lines.append(str(row))
            return '\n'.join(lines) if lines else "No results found."

    except Exception as e:
        return f"Query error: {e}"


def show_schema(conn) -> str:
    """スキーマ情報を表示"""
    output = []
    output.append("## Node Tables\n")

    # ノード数をカウント
    node_types = ['UbiquitousTerm', 'Domain', 'Entity', 'Method', 'File', 'Actor', 'Role']
    for node_type in node_types:
        try:
            result = conn.execute(f"MATCH (n:{node_type}) RETURN count(*) AS count")
            for row in result:
                count = row[0]
                output.append(f"- {node_type}: {count} nodes")
        except:
            pass

    output.append("\n## Relationship Tables\n")

    rel_types = ['BELONGS_TO', 'DEFINED_IN', 'METHOD_DEFINED_IN', 'REFERENCES',
                 'CALLS', 'IMPLEMENTS', 'HAS_TERM', 'METHOD_HAS_TERM', 'HAS_ROLE']
    for rel_type in rel_types:
        try:
            result = conn.execute(f"MATCH ()-[r:{rel_type}]->() RETURN count(*) AS count")
            for row in result:
                count = row[0]
                output.append(f"- {rel_type}: {count} relationships")
        except:
            pass

    return '\n'.join(output)


def interactive_mode(conn):
    """対話モードで実行"""
    print("RyuGraph Interactive Query Mode")
    print("=" * 40)
    print("Commands:")
    print("  :schema     - Show database schema")
    print("  :templates  - Show query templates")
    print("  :t <name>   - Execute template query")
    print("  :format <f> - Set output format (table, json, csv, raw)")
    print("  :quit       - Exit")
    print("=" * 40)
    print()

    output_format = 'table'

    while True:
        try:
            query = input("cypher> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not query:
            continue

        if query == ':quit' or query == ':q':
            print("Goodbye!")
            break

        elif query == ':schema':
            print(show_schema(conn))

        elif query == ':templates':
            print("\nAvailable templates:")
            for name, q in QUERY_TEMPLATES.items():
                print(f"  {name}: {q.strip()[:60]}...")
            print()

        elif query.startswith(':t '):
            template_name = query[3:].strip()
            if template_name in QUERY_TEMPLATES:
                print(f"\nExecuting template: {template_name}")
                print(f"Query: {QUERY_TEMPLATES[template_name].strip()}")
                print()
                result = execute_query(conn, QUERY_TEMPLATES[template_name], output_format)
                print(result)
            else:
                print(f"Unknown template: {template_name}")

        elif query.startswith(':format '):
            output_format = query[8:].strip()
            print(f"Output format set to: {output_format}")

        else:
            result = execute_query(conn, query, output_format)
            print(result)

        print()


def main():
    parser = argparse.ArgumentParser(description='Query RyuGraph database')
    parser.add_argument('--db-path', required=True, help='Path to the RyuGraph database')
    parser.add_argument('--query', '-q', help='Cypher query to execute')
    parser.add_argument('--template', '-t', help='Use a predefined query template')
    parser.add_argument('--format', '-f', choices=['table', 'json', 'csv', 'raw'],
                        default='table', help='Output format')
    parser.add_argument('--interactive', '-i', action='store_true',
                        help='Run in interactive mode')
    parser.add_argument('--schema', '-s', action='store_true',
                        help='Show database schema')
    args = parser.parse_args()

    db, conn = open_database(args.db_path)

    if args.schema:
        print(show_schema(conn))

    elif args.interactive:
        interactive_mode(conn)

    elif args.template:
        if args.template in QUERY_TEMPLATES:
            result = execute_query(conn, QUERY_TEMPLATES[args.template], args.format)
            print(result)
        else:
            print(f"Unknown template: {args.template}")
            print("Available templates:", ', '.join(QUERY_TEMPLATES.keys()))
            sys.exit(1)

    elif args.query:
        result = execute_query(conn, args.query, args.format)
        print(result)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
