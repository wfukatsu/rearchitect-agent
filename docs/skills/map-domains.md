# /map-domains — ドメインマッピング

**カテゴリ**: Design（設計） | **Phase 3（簡易版）**

ビジネスドメインの分類と境界づけられたコンテキスト、コンテキストマップを作成します。

## 使用方法

```bash
/map-domains ./path/to/source
```

> **注意**: 統合パイプライン（`/full-pipeline`, `/refactor-system`）では `/ddd-redesign` がドメインマッピング機能を包含するため、本スキルは単独実行時に使用します。

## 前提条件

### 必須（`/analyze-system` の出力）
- `reports/01_analysis/ubiquitous-language.md`
- `reports/01_analysis/actors-roles-permissions.md`
- `reports/01_analysis/domain-code-mapping.md`
- `reports/01_analysis/system-overview.md`

## ドメイン分類フレームワーク

### ビジネス構造軸（Domain Type）

| タイプ | 特徴 | 例 |
|-------|------|-----|
| **Pipeline** | 順序的なデータ/処理フロー | 注文処理、ワークフロー |
| **Blackboard** | 共有データへの協調的アクセス | 在庫管理、予約システム |
| **Dialogue** | 双方向のインタラクション | チャット、通知システム |

### マイクロサービス境界軸（Service Category）

| カテゴリ | 責務 | 特徴 |
|---------|------|------|
| **Process** | ビジネスプロセスの実行 | ステートフル、サガ管理 |
| **Master** | マスタデータの管理 | CRUD中心、データ整合性 |
| **Integration** | 外部システム連携 | アダプタ、変換処理 |
| **Supporting** | 横断的機能の提供 | 認証、ログ、通知 |

## 実行ステップ

1. **入力ファイル確認** — 前提条件ファイルの存在確認
2. **ドメイン境界の特定** — 用語・責務・ライフサイクルの違いから境界を識別
3. **ドメインタイプの判定** — ビジネス構造軸での分類
4. **サービスカテゴリの判定** — マイクロサービス境界軸での分類
5. **境界づけられたコンテキストの定義** → `domain-analysis.md`
6. **コンテキストマップの作成** → `context-map.md`, `system-mapping.md`
7. **Mermaid図の検証**

## 出力ファイル

| ファイル | 内容 |
|---------|------|
| `reports/03_design/domain-analysis.md` | ドメイン一覧、分類、コンテキスト定義 |
| `reports/03_design/context-map.md` | コンテキストマップ（Mermaid図含む） |
| `reports/03_design/system-mapping.md` | 現行システム→ドメインマッピング |

## 関連スキル

- 前提: [/analyze-system](analyze-system.md)
- 上位互換: [/ddd-redesign](ddd-redesign.md)（完全なDDD再設計）
- 次のフェーズ: [/design-microservices](design-microservices.md)
