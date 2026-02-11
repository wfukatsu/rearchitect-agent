# /refactor-system — 統合リファクタリング分析・設計

**カテゴリ**: Orchestration（統括）

既存システムをマイクロサービスアーキテクチャにリファクタリングするための統合分析・設計を実行します。`/full-pipeline` と異なり、コード生成（Phase 8）を含まない分析・設計に特化したオーケストレーターです。

## 使用方法

```bash
/refactor-system ./path/to/source
/refactor-system ./src --analyze-only
/refactor-system ./src --skip-mmi
/refactor-system ./src --domain=Order
/refactor-system ./src --output=./reports/
```

## 概要

以下のプロセスを順次実行します：

1. **システム分析** — コードと設計書の解析
2. **MMI評価** — モジュール成熟度評価
3. **DDD評価** — ドメイン駆動設計の適合度評価
4. **ドメインマッピング** — ビジネスドメインとコードの紐付け
5. **マイクロサービス設計** — ターゲットアーキテクチャの策定
6. **ScalarDB設計** — 分散トランザクション・データアーキテクチャ
7. **ドメインストーリー** — 各ドメインのユースケース整理

## 前提条件

- 対象ディレクトリにソースコードまたは設計書が存在すること

## オプション

| フラグ | 説明 |
|--------|------|
| `--analyze-only` | 分析のみ実行（設計書生成なし） |
| `--skip-mmi` | MMI評価をスキップ |
| `--domain=Name` | 特定ドメインのみ対象 |
| `--output=PATH` | 出力先ディレクトリ指定（デフォルト: `./reports/`） |

## 実行ステップ

1. **入力確認** — 対象フォルダパス、出力先ディレクトリをユーザーに確認
2. **Phase 0**: システム調査（`/system-investigation`）
3. **Phase 1**: システム分析（`/analyze-system`）
4. **Phase 2a/2b**: MMI/DDD評価（並行実行）
5. **Phase 2.5**: 評価統合（`/integrate-evaluations`）
6. **Phase 3**: DDD再設計（`/ddd-redesign`）
7. **Phase 4**: マイクロサービス設計（`/design-microservices`）
8. **Phase 4.7〜5.9**: ScalarDB選定・設計・レビュー
9. **Phase 5.95**: API設計（`/design-api`）
10. **Phase 6**: 実装仕様（`/design-implementation`）
11. **Phase 7**: テスト仕様（`/generate-test-specs`）
12. **Phase 8.7**: インフラ設計（`/design-infrastructure`）
13. **Phase 9**: コスト見積もり（`/estimate-cost`）
14. **Phase 10**: ドメインストーリー（`/create-domain-story`）
15. **Phase 11**: グラフ構築（`/build-graph`）
16. **Phase 12**: Mermaid検証（`/fix-mermaid`）
17. **Phase 13**: エグゼクティブサマリー

## 出力ファイル

`reports/` 配下に各フェーズの成果物が生成されます。`generated/` 配下のコード生成は含まれません。

## `/full-pipeline` との違い

| 観点 | `/refactor-system` | `/full-pipeline` |
|------|-------------------|-----------------|
| コード生成 | なし | あり（Phase 8） |
| 主な用途 | 分析・設計レビュー | 完全な実行 |
| 対話的入力 | 対象パス・出力先を確認 | 対象パス・出力先を確認 |

## 関連スキル

- [/full-pipeline](full-pipeline.md) — コード生成を含む完全パイプライン
- [/workflow](workflow.md) — 対話的なフェーズ選択
