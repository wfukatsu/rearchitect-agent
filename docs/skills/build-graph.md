# /build-graph — ナレッジグラフ構築

**カテゴリ**: Knowledge Graph（ナレッジグラフ） | **Phase 11**

ユビキタス言語とコード解析結果からRyuGraphデータベースにナレッジグラフを構築します。

## 使用方法

```bash
/build-graph ./path/to/source
```

## 前提条件

### 環境
- Python 3.9+
- `ryugraph` パッケージ（`pip install ryugraph`）

### 推奨（`/analyze-system` の出力）
- `reports/01_analysis/ubiquitous-language.md`
- `reports/01_analysis/domain-code-mapping.md`
- `reports/01_analysis/actors-roles-permissions.md`
- `reports/01_analysis/system-overview.md`

## ノードタイプ（10種類）

| タイプ | 説明 |
|--------|------|
| `DomainConcept` | ユビキタス言語の用語 |
| `Entity` | エンティティ |
| `ValueObject` | 値オブジェクト |
| `Aggregate` | 集約 |
| `BoundedContext` | 境界コンテキスト |
| `Actor` | アクター/ロール |
| `UseCase` | ユースケース |
| `Module` | コードモジュール |
| `Class` | クラス |
| `Package` | パッケージ |

## リレーションシップタイプ（17種類）

`BELONGS_TO`, `CONTAINS`, `DEPENDS_ON`, `IMPLEMENTS`, `REFERENCES`, `HAS_ROLE`, `PERFORMS`, `MAPS_TO` 等

## 実行ステップ

1. **分析結果の収集** — `/analyze-system` の出力を読み込み
2. **コード解析** — Serenaツールでソースコードの構造を解析
3. **CSVデータ生成** — ノードとリレーションシップのCSVデータを生成
4. **グラフ構築** — RyuGraphにデータを登録
5. **メタデータ保存** — スキーマ情報と統計を保存

## 出力ファイル

| ファイル | 内容 |
|---------|------|
| `knowledge.ryugraph` | RyuGraphデータベースファイル |
| `reports/graph/data/nodes.csv` | ノードデータ |
| `reports/graph/data/edges.csv` | リレーションシップデータ |
| `reports/graph/data/graph-metadata.json` | グラフメタデータ |

## 関連スキル

- 前提: [/analyze-system](analyze-system.md)
- 次のステップ: [/query-graph](query-graph.md), [/visualize-graph](visualize-graph.md)
