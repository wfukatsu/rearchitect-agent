# Sub-Agent Patterns

スキル実行時にTask toolで活用するサブエージェントの標準パターン。
メインコンテキストの肥大化を防ぎ、並列処理で効率化する。

## Pattern 1: コードベース探索エージェント

コードベースを直接スキャンするスキルで使用。メインエージェントのコンテキストを保護しながら、大規模コードベースの情報を収集する。

### 対象スキル

system-investigation, analyze-system, evaluate-mmi, ddd-evaluation

### 使用方法

```
Task(
  subagent_type="Explore",
  prompt="対象ディレクトリ {target_path} のコードベースを探索し、以下を調査してください:
    1. [調査項目1]
    2. [調査項目2]
    結果をJSON形式でまとめてください。",
  description="コードベース探索"
)
```

### 並列探索パターン

複数の観点を同時に調査する場合、独立したExploreエージェントを並列起動:

```
# 並列で3つのExploreエージェントを起動（1つのメッセージで複数Task呼び出し）
Task(subagent_type="Explore", prompt="パッケージ構造と依存関係を調査...", description="構造調査")
Task(subagent_type="Explore", prompt="ドメイン用語とビジネスロジックを抽出...", description="ドメイン用語抽出")
Task(subagent_type="Explore", prompt="外部連携とAPI定義を調査...", description="外部連携調査")
```

### ベストプラクティス

- **スコープを絞る**: 1エージェントにつき1つの明確な調査目的
- **結果フォーマットを指定**: JSON/Markdown等、メインエージェントが処理しやすい形式を指定
- **ファイル数が多い場合はサンプリング指示**: 「主要なファイルを最大20件調査」等


## Pattern 2: 前フェーズ出力読み込みエージェント

前フェーズの出力ファイルを読み込んで要約し、メインエージェントに必要な情報のみを渡す。

### 対象スキル

integrate-evaluations, ddd-redesign, map-domains, design-microservices, design-api, design-scalardb, design-scalardb-analytics, design-implementation, generate-test-specs, generate-scalardb-code, estimate-cost

### 使用方法

```
Task(
  subagent_type="Explore",
  prompt="以下のファイルを読み込み、{current_skill}に必要な情報を抽出・要約してください:

    必須ファイル:
    - reports/02_evaluation/mmi-overview.md
    - reports/02_evaluation/ddd-strategic-evaluation.md

    推奨ファイル（存在すれば読み込み）:
    - reports/01_analysis/ubiquitous-language.md

    抽出する情報:
    1. モジュール一覧とMMIスコア
    2. 境界コンテキスト候補
    3. 主要な改善提案

    結果をMarkdown形式でまとめてください。
    ファイルが存在しない場合は、そのファイル名を「未検出」として報告してください。",
  description="前フェーズ出力の読み込み"
)
```

### 前提条件チェックとの組み合わせ

Step 0（前提条件検証）で存在確認と読み込みを同時に行う:

```
Task(
  subagent_type="Explore",
  prompt="以下のファイルの存在を確認し、存在するファイルの内容を要約してください:

    [必須] reports/03_design/bounded-contexts-redesign.md
    [必須] reports/03_design/aggregate-redesign.md
    [推奨] reports/02_evaluation/mmi-overview.md

    結果フォーマット:
    - ファイルパス: 存在(found)/未検出(not_found)
    - 要約: (存在する場合のみ)

    必須ファイルが未検出の場合は明確に警告してください。",
  description="前提条件チェック"
)
```

### ベストプラクティス

- **要約を求める**: 全文をメインコンテキストに送らず、必要情報のみ抽出
- **存在確認を含める**: ファイルの有無で分岐処理に活用
- **抽出項目を明示**: 「何を抽出するか」を具体的に指定
