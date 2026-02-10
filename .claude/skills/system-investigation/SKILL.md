---
name: system-investigation
description: システム調査エージェント - コードベースの構造・技術スタック・問題点・DDD適合性を調査。/system-investigation [対象パス] で呼び出し。
user_invocable: true
---

# System Investigation Agent

対象システムの現行調査を実施し、リファクタリング計画の基礎情報を収集するエージェントです。

## 概要

このエージェントは以下を実行します：

1. **技術スタック調査** - 使用言語、フレームワーク、ライブラリの特定
2. **構造分析** - ディレクトリ構成、モジュール構造、依存関係の把握
3. **問題点特定** - 技術的負債、アンチパターン、セキュリティリスクの検出
4. **DDD適合性評価** - ドメイン駆動設計への移行可能性を評価

## ユーザー入力確認（必須）

**重要**: このスキルを実行する前に、必ず以下の項目をユーザーに確認してください。

### 1. 調査対象フォルダの確認

引数で対象パスが指定されていない場合は、AskUserQuestionツールで質問してください：

```json
{
  "questions": [{
    "question": "調査対象のフォルダパスを指定してください",
    "header": "対象フォルダ",
    "options": [
      {"label": "カレントディレクトリ", "description": "現在のディレクトリ全体を調査"},
      {"label": "src/", "description": "srcディレクトリを調査"},
      {"label": "パス指定", "description": "カスタムパスを入力"}
    ],
    "multiSelect": false
  }]
}
```

### 2. 出力先ディレクトリの確認

デフォルト出力先: `./reports/`（カレントディレクトリ配下）

```json
{
  "questions": [{
    "question": "レポートの出力先ディレクトリを確認してください",
    "header": "出力先",
    "options": [
      {"label": "./reports/ (推奨)", "description": "カレントディレクトリ配下のreportsフォルダ"},
      {"label": "カスタムパス", "description": "別のパスを指定"}
    ],
    "multiSelect": false
  }]
}
```

## 前提条件

- 対象システムのソースコードにアクセス可能であること
- Serena MCPが利用可能（推奨）

## 出力先

結果は `reports/before/{project}/` に出力します。
中間状態は `work/{project}/investigation/` に記録します。
**重要**: 各ステップ完了時に即座にファイルを出力してください。

```
reports/before/{project}/
├── technology-stack.md       # Step 1完了時
├── codebase-structure.md     # Step 2完了時
├── issues-and-debt.md        # Step 3完了時
└── ddd-readiness.md          # Step 4完了時

work/{project}/investigation/
├── file-inventory.md         # ファイル一覧
├── dependency-analysis.md    # 依存関係分析
└── investigation-progress.md # 進捗状況
```

## サブエージェント活用

大規模コードベースの場合、Task toolのExploreエージェントを並列起動してコンテキストを保護しつつ効率的に調査できます。
詳細は `.claude/skills/common/sub-agent-patterns.md` の「Pattern 1: コードベース探索エージェント」を参照。

## 実行プロンプト

あなたはレガシーシステム調査の専門家エージェントです。以下の手順でシステム調査を実行してください。

### Step 0: プロジェクト名の特定

対象パスからプロジェクト名を特定します：
- ディレクトリ名またはpackage.json/pom.xml等から取得
- 出力ディレクトリを作成: `reports/before/{project}/`, `work/{project}/investigation/`

### Step 1: 技術スタック調査

Serenaツールまたはファイル探索で以下を特定：

```
調査対象:
├── 言語・バージョン (package.json, pom.xml, build.gradle, requirements.txt等)
├── フレームワーク (Spring, Express, React, Vue等)
├── データベース (設定ファイル、マイグレーション、ORM設定)
├── 外部サービス (API呼び出し、SDK使用)
├── ビルドツール (Maven, Gradle, npm, webpack等)
└── テストフレームワーク (JUnit, Jest, pytest等)
```

**Serena使用例:**
```
mcp__serena__list_dir: relative_path=".", recursive=false
mcp__serena__find_file: file_mask="package.json", relative_path="."
mcp__serena__find_file: file_mask="pom.xml", relative_path="."
```

**このステップ完了時に出力**: `reports/before/{project}/technology-stack.md`

### Step 2: 構造分析

コードベースの構造を分析：

```
分析項目:
├── ディレクトリ構成
│   ├── src/, lib/, app/ 等の主要ディレクトリ
│   ├── 設定ファイルの配置
│   └── テストコードの配置
├── モジュール/パッケージ構成
│   ├── 主要モジュールの特定
│   ├── 公開インターフェース
│   └── 内部実装
├── 依存関係
│   ├── モジュール間依存
│   ├── 循環依存の検出
│   └── 外部依存の整理
└── エントリポイント
    ├── メイン関数/クラス
    ├── APIエンドポイント
    └── イベントハンドラ
```

**Serena使用例:**
```
mcp__serena__get_symbols_overview: relative_path="src/main.ts", depth=1
mcp__serena__find_symbol: name_path_pattern="Controller", substring_matching=true
mcp__serena__find_referencing_symbols: name_path="UserService", relative_path="src/services/user.ts"
```

**このステップ完了時に出力**:
- `reports/before/{project}/codebase-structure.md`
- `work/{project}/investigation/file-inventory.md`
- `work/{project}/investigation/dependency-analysis.md`

### Step 3: 問題点特定

技術的負債とリスクを特定：

```
検出対象:
├── コード品質
│   ├── 巨大クラス/関数 (500行以上)
│   ├── 複雑な条件分岐 (深いネスト)
│   ├── 重複コード
│   └── 命名の一貫性欠如
├── アーキテクチャ
│   ├── 循環依存
│   ├── God Object / God Class
│   ├── レイヤー違反
│   └── 密結合
├── セキュリティ
│   ├── ハードコードされた認証情報
│   ├── SQLインジェクションリスク
│   ├── 入力検証の欠如
│   └── 古い依存パッケージ
└── 保守性
    ├── ドキュメント不足
    ├── テストカバレッジ
    ├── エラーハンドリング
    └── ログ/監視
```

**Serena使用例:**
```
mcp__serena__search_for_pattern: substring_pattern="password.*=.*['\"]", restrict_search_to_code_files=true
mcp__serena__search_for_pattern: substring_pattern="TODO|FIXME|HACK", restrict_search_to_code_files=true
```

**このステップ完了時に出力**: `reports/before/{project}/issues-and-debt.md`

### Step 4: DDD適合性評価

ドメイン駆動設計への移行可能性を評価：

```
評価項目:
├── ドメイン層の存在
│   ├── ドメインモデル (Entity, Value Object)
│   ├── ドメインサービス
│   └── ドメインイベント
├── 境界の明確さ
│   ├── モジュール境界
│   ├── コンテキスト候補
│   └── 共有カーネル候補
├── ユビキタス言語の痕跡
│   ├── ビジネス用語の使用
│   ├── 命名の一貫性
│   └── コメント/ドキュメント
└── 移行難易度
    ├── 密結合度
    ├── データベース依存
    └── 外部システム連携
```

**評価スコア:**
- **High (80-100)**: DDD適合済み、微調整のみ必要
- **Medium (50-79)**: 部分的にDDD、段階的移行が可能
- **Low (20-49)**: DDDの痕跡あり、大幅なリファクタリング必要
- **Very Low (0-19)**: DDD未適用、根本的な再設計が必要

**このステップ完了時に出力**: `reports/before/{project}/ddd-readiness.md`

### Step 5: 調査レポートの統合

全調査結果をサマリーとしてまとめる：

**このステップ完了時に出力**: `reports/before/{project}/investigation-summary.md`

### Step 6: Mermaid図の検証

出力したファイルのMermaid図を検証し、エラーがあれば修正：

```bash
/fix-mermaid ./reports/before/{project}
```

## 出力フォーマット

### technology-stack.md

```markdown
# 技術スタック調査

## 概要

| カテゴリ | 技術 | バージョン | 備考 |
|---------|------|-----------|------|
| 言語 | Java | 17 | LTS |
| フレームワーク | Spring Boot | 3.2.x | Web MVC |
| データベース | PostgreSQL | 15 | メインDB |

## 詳細

### バックエンド
...

### フロントエンド
...

### インフラ
...

## 依存パッケージ一覧

| パッケージ | バージョン | 用途 | 最新バージョン |
|-----------|-----------|------|---------------|
```

### codebase-structure.md

```markdown
# コードベース構造

## ディレクトリ構成

\`\`\`
project-root/
├── src/
│   ├── main/
│   │   ├── java/
│   │   └── resources/
│   └── test/
├── config/
└── docs/
\`\`\`

## モジュール構成

\`\`\`mermaid
graph TD
    subgraph "Application Layer"
        Controller
        Service
    end
    subgraph "Domain Layer"
        Entity
        Repository
    end
    subgraph "Infrastructure"
        Database
        External
    end
    Controller --> Service
    Service --> Entity
    Service --> Repository
    Repository --> Database
\`\`\`

## 依存関係マトリックス

| モジュール | 依存先 | 依存元 | 循環 |
|-----------|--------|--------|------|
```

### issues-and-debt.md

```markdown
# 問題点・技術的負債

## サマリー

| カテゴリ | 重大 | 高 | 中 | 低 |
|---------|-----|---|---|---|
| コード品質 | 2 | 5 | 10 | 15 |
| アーキテクチャ | 1 | 3 | 5 | 8 |
| セキュリティ | 0 | 2 | 3 | 5 |
| 保守性 | 1 | 4 | 8 | 12 |

## 重大な問題

### CRITICAL-001: [問題名]

- **カテゴリ**: セキュリティ
- **場所**: `src/auth/login.ts:45`
- **説明**: ...
- **推奨対応**: ...
- **影響範囲**: ...

## 高優先度の問題

...
```

### ddd-readiness.md

```markdown
# DDD適合性評価

## 総合スコア: 55/100 (Medium)

## 評価詳細

| 評価項目 | スコア | 重み | 加重スコア |
|---------|--------|------|-----------|
| ドメイン層の存在 | 60 | 30% | 18 |
| 境界の明確さ | 50 | 25% | 12.5 |
| ユビキタス言語 | 40 | 20% | 8 |
| 移行難易度 | 65 | 25% | 16.25 |

## ドメイン層分析

### 検出されたドメイン要素

| 要素タイプ | 数 | 例 |
|-----------|---|---|
| Entity候補 | 12 | User, Order, Product |
| Value Object候補 | 5 | Money, Address |
| Service | 8 | OrderService, PaymentService |

## 推奨アクション

1. **短期（1-2週間）**: ...
2. **中期（1-2ヶ月）**: ...
3. **長期（3ヶ月以上）**: ...
```

## ツール活用ガイドライン

### 優先順位

1. **Serenaツール** - シンボリック解析に最適
2. **Glob/Grep** - パターンマッチング
3. **Read** - 詳細確認

### Serena活用パターン

```
# ファイル構造の把握
mcp__serena__list_dir(relative_path=".", recursive=true, skip_ignored_files=true)

# シンボル概要
mcp__serena__get_symbols_overview(relative_path="src/main/java/com/example/App.java", depth=2)

# 特定パターンの検索
mcp__serena__search_for_pattern(substring_pattern="@Entity", restrict_search_to_code_files=true)

# 参照追跡
mcp__serena__find_referencing_symbols(name_path="UserRepository", relative_path="src/repositories/user.ts")
```

## エラーハンドリング

- **対象パスが存在しない場合** → エラーメッセージを表示し終了
- **言語がサポートされていない場合** → Grep/Readベースの調査にフォールバック
- **大規模コードベース（10,000ファイル以上）の場合** → サンプリング調査を提案

## 関連スキル

| スキル | 用途 |
|-------|-----|
| `/analyze-system` | 調査後のシステム分析（ユビキタス言語抽出等） |
| `/ddd-evaluation` | DDD観点での詳細評価 |
| `/evaluate-mmi` | モジュール成熟度の定量評価 |
