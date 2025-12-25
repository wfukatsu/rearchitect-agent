---
description: GraphDB探索エージェント - RyuGraphデータベースを自然言語またはCypherで探索し、関連コードや仕様を返却。
argument-hint: [クエリ]
---

# GraphDB探索エージェント

RyuGraphに構築されたナレッジグラフを探索し、ユビキタス言語に基づいて関連するコードや仕様を返却するエージェントです。

## クエリモード

### 自然言語モード
```
/query-graph 「注文」に関連するクラスを教えて
/query-graph 認証フローに関わるメソッドは？
```

### Cypherモード
```
/query-graph MATCH (e:Entity)-[:HAS_TERM]->(t:UbiquitousTerm {name_ja: '注文'}) RETURN e
```

## 出力

- 実行されたCypherクエリ
- 検索結果（テーブル形式）
- 関連ソースコード
- 関連用語定義

詳細は `.claude/skills/query-graph/SKILL.md` を参照してください。
