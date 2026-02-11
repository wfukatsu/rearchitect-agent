# /query-graph — ナレッジグラフ探索

**カテゴリ**: Knowledge Graph（ナレッジグラフ） | **Phase 11.5**

RyuGraphデータベースを自然言語またはCypherで探索し、関連するコードや仕様書を返却します。

## 使用方法

```bash
# 自然言語クエリ
/query-graph "Orderエンティティに関連するすべての要素を表示"

# Cypherクエリ
/query-graph "MATCH (n:Entity)-[r]->(m) WHERE n.name = 'Order' RETURN n, r, m"
```

## 前提条件

- `/build-graph` が実行済みで `knowledge.ryugraph` が存在すること
- Python 3.9+ と `ryugraph` パッケージ

## クエリモード

### 1. 自然言語モード

日本語で質問すると、内部でCypherクエリに変換して実行します。

**例:**
- 「注文に関連するすべてのエンティティを見せて」
- 「Customer と Order の関係は？」
- 「最も多くの依存関係を持つモジュールは？」

### 2. Cypherモード

直接Cypher構文でグラフを探索します。

**例:**
```cypher
MATCH (n:BoundedContext)-[:CONTAINS]->(e:Entity)
RETURN n.name, collect(e.name)
```

## 出力

クエリ結果は構造化された形式で返却されます:
- ノード情報（名前、タイプ、プロパティ）
- リレーションシップ情報
- 関連するソースコードの場所
- 関連する仕様書の参照

## 関連スキル

- 前提: [/build-graph](build-graph.md)
- 補完: [/visualize-graph](visualize-graph.md)
