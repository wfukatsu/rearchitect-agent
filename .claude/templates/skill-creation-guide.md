# スキル作成ガイド

新しいスキルを追加する際の手順とベストプラクティスです。

## ファイル構成

新しいスキルを追加する際は、以下のファイルを作成します：

```
.claude/
└── skills/
    └── {skill-name}/
        └── SKILL.md          # スキル定義（実行手順）
```

スキルは `user_invocable: true` を設定することで、直接 `/{skill-name}` として呼び出し可能になります。

## SKILL.md テンプレート

```markdown
---
name: {skill-name}
description: {簡潔な説明} - {詳細説明}。/{skill-name} [引数] で呼び出し。
user_invocable: true
---

# {スキル名} Agent

{スキルの概要説明}

## 目的

このエージェントは以下を実行します：

1. **{機能1}** - {説明}
2. **{機能2}** - {説明}
3. **{機能3}** - {説明}

## 前提条件

- {前提条件1}
- {前提条件2}
- 以下の中間ファイルが存在すること：
  - `{path/to/file.md}`

## 出力先ディレクトリ

結果は `reports/{XX}_{category}/` に出力します。
**重要**: 各ステップ完了時に即座にファイルを出力してください。

\`\`\`
reports/{XX}_{category}/
├── {output-file-1}.md    # Step N完了時
└── {output-file-2}.md    # Step M完了時
\`\`\`

## 実行プロンプト

あなたは{専門分野}の専門家エージェントです。以下の手順で{タスク}を実行してください。

### Step 1: {ステップ名}

{ステップの説明}

\`\`\`bash
# コマンド例
\`\`\`

**エラーハンドリング:**
- {条件} の場合 → {対応}

**このステップ完了時に出力**: `reports/{XX}_{category}/{file}.md`

### Step 2: {ステップ名}

{以下同様...}

### Step N: Mermaid図の検証

出力したファイルのMermaid図を検証し、エラーがあれば修正：

\`\`\`bash
/fix-mermaid ./reports/{XX}_{category}
\`\`\`

## 出力フォーマット

### {output-file}.md

{出力ファイルの形式説明}

## ツール活用ガイドライン

### 優先順位

1. **Serenaツール** - シンボリック解析に最適
2. **Glob/Grep** - パターンマッチング
3. **Read** - 詳細確認

## エラーハンドリング

- {エラー条件1} → {対応}
- {エラー条件2} → {対応}

## 関連スキル

| スキル | 用途 |
|-------|-----|
| `/{related-skill}` | {用途説明} |
```

## 命名規則

### ファイル名
- **kebab-case**を使用: `domain-analysis.md`, `target-architecture.md`
- **snake_case禁止**: ~~`domain_analysis.md`~~

### スキル名
- **kebab-case**を使用: `design-microservices`, `build-graph`
- 動詞-名詞の形式を推奨: `analyze-system`, `estimate-cost`

### 出力ディレクトリ
- 番号プレフィックス: `00_summary`, `01_analysis`, `02_evaluation`
- アンダースコア区切り: `{XX}_{category}`

## チェックリスト

新しいスキルを追加する前に確認：

- [ ] SKILL.mdのYAMLフロントマターが正しい形式
- [ ] `user_invocable: true` が設定されている（ユーザー呼び出し可能な場合）
- [ ] 出力ファイル名がkebab-case
- [ ] エラーハンドリングが記載されている
- [ ] Mermaid検証ステップが含まれている（図を出力する場合）
- [ ] 関連スキルとの依存関係が明記されている
- [ ] CLAUDE.mdのQuick Startセクションに追加（主要スキルの場合）

## 依存関係の管理

### 前提条件の記載例

```markdown
## 前提条件

以下の中間ファイルが存在すること：
- `01_analysis/ubiquitous-language.md` ← /analyze-system で生成
- `03_design/target-architecture.md` ← /design-microservices で生成
```

### 実行順序の制約

スキルは以下の実行順序に従う必要があります：

```
/analyze-system → /evaluate-mmi → /map-domains → /design-microservices → ...
```

依存関係を無視した実行は、前提条件エラーとして処理します。

## テスト方法

1. SampleCodeディレクトリで実行テスト
2. 出力ファイルの形式確認
3. Mermaid図のレンダリング確認
4. 依存スキルとの連携確認
