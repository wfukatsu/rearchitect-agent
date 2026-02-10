---
name: init-output
description: 出力ディレクトリ初期化 - リファクタリング分析用の出力ディレクトリ構造を作成。/init-output [出力パス] で呼び出し。
user_invocable: true
---

# Output Directory Initializer

出力ディレクトリを初期化し、必要なフォルダ構造を作成するユーティリティスキルです。

## 概要

リファクタリング分析を開始する前に、`reports/` 配下の出力ディレクトリ構造を自動作成します。各フェーズの分析・設計スキルが出力するファイルの格納先を事前に準備します。

## 前提条件

なし（スタンドアロンで実行可能）

## 使用方法

リファクタリング分析を開始する前に、このスキルを実行して出力ディレクトリを準備します。

## ユーザー入力確認（必須）

**重要**: このスキルを実行する前に、必ず出力先ディレクトリをユーザーに確認してください。

デフォルト出力先: `./reports/`（カレントディレクトリ配下）

AskUserQuestionツールで確認：
```json
{
  "questions": [{
    "question": "出力ディレクトリを確認してください。デフォルト: ./reports/（カレントディレクトリ配下）",
    "header": "出力先",
    "options": [
      {"label": "./reports/ (推奨)", "description": "カレントディレクトリ配下のreportsフォルダ"},
      {"label": "カスタムパス", "description": "別のパスを指定"}
    ],
    "multiSelect": false
  }]
}
```

## 実行コマンド

```bash
# デフォルトの出力先（./reports/、カレントディレクトリ配下）
/init-output

# カスタム出力先
/init-output ./custom-output
```

## 作成されるディレクトリ構造

```
reports/
├── 00_summary/
├── 01_analysis/
├── 02_evaluation/
├── 03_design/
├── 04_stories/
├── 05_estimate/
├── 06_implementation/
├── 07_test-specs/
├── graph/
│   ├── data/
│   └── visualizations/
└── sizing-estimates/
```

## 初期化スクリプト

以下のBashコマンドを実行して出力ディレクトリを作成します：

```bash
#!/bin/bash

OUTPUT_DIR="${1:-reports}"

mkdir -p "${OUTPUT_DIR}/00_summary"
mkdir -p "${OUTPUT_DIR}/01_analysis"
mkdir -p "${OUTPUT_DIR}/02_evaluation"
mkdir -p "${OUTPUT_DIR}/03_design"
mkdir -p "${OUTPUT_DIR}/04_stories"
mkdir -p "${OUTPUT_DIR}/05_estimate"
mkdir -p "${OUTPUT_DIR}/06_implementation"
mkdir -p "${OUTPUT_DIR}/07_test-specs"
mkdir -p "${OUTPUT_DIR}/graph/data"
mkdir -p "${OUTPUT_DIR}/graph/visualizations"
mkdir -p "${OUTPUT_DIR}/sizing-estimates"

# メタデータファイルの初期化
cat > "${OUTPUT_DIR}/00_summary/project_metadata.json" << 'EOF'
{
    "project": {
        "name": "",
        "version": "1.0.0",
        "created_at": "",
        "updated_at": ""
    },
    "source": {
        "path": "",
        "type": "",
        "languages": [],
        "frameworks": []
    },
    "analysis": {
        "status": "not_started",
        "modules_count": 0,
        "domains_count": 0,
        "average_mmi": 0
    },
    "agents": {
        "system_analyzer": { "status": "pending" },
        "mmi_evaluator": { "status": "pending" },
        "domain_mapper": { "status": "pending" },
        "microservice_architect": { "status": "pending" },
        "domain_storyteller": { "status": "pending" }
    }
}
EOF

echo "Output directory initialized: ${OUTPUT_DIR}"
```

## 既存ディレクトリの扱い

- 既存のディレクトリがある場合は上書きしません
- `--force` オプションで強制的に再作成できます

```bash
/init-output --force
```

## プロンプト

あなたは出力ディレクトリを初期化するユーティリティエージェントです。

以下の手順で実行してください：

1. 出力先ディレクトリパスを確認
2. 既存ディレクトリの有無を確認
3. ディレクトリ構造を作成
4. メタデータファイルを初期化
5. 完了メッセージを表示

```
# Bashツールで実行
Bash: mkdir -p reports/{00_summary,01_analysis,02_evaluation,03_design,04_stories,05_estimate,06_implementation,07_test-specs,graph/data,graph/visualizations,sizing-estimates}
```

## 注意事項

- 書き込み権限がない場合はエラーになります
- 大文字小文字は区別されます
- 相対パスと絶対パスの両方が使用可能です
