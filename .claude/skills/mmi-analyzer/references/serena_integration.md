# Serena MCP 連携ガイド

Serena MCP の LSP（Language Server Protocol）機能を活用することで、MMI解析の精度を大幅に向上させることができる。

## Serena で強化される解析

### 1. 依存関係の精密検出

Python の `import` 文だけでは検出できない依存関係を、Serena の参照解析で補完する。

**活用するSerenaツール:**
- `find_references` — シンボルの全参照箇所を検出
- `go_to_definition` — 依存先の特定

**補完される MMI 基準:**
- 1.2.1 インターフェース違反率
- 2.1.1/2.1.2 レイヤー違反

**使い方:**
```
Serena を使って、<クラス名> の全参照箇所を検索してください。
→ find_references で参照元を特定
→ 参照元のレイヤーとクラスのレイヤーを比較
→ 逆方向参照があればレイヤー違反として記録
```

### 2. 型階層と継承関係

`type_hierarchy` で継承ツリーを完全に把握し、パターン分類の精度を向上させる。

**活用するSerenaツール:**
- `type_hierarchy` — 継承階層の取得
- `document_symbols` — ファイル内のシンボル一覧

**補完される MMI 基準:**
- 3.1 パターンへのソースコード割当率
- 3.3 パターンの明示的マッピング

**使い方:**
```
Serena で Repository パターンを実装しているクラスを探してください。
→ workspace_symbols で "Repository" を含むシンボルを検索
→ type_hierarchy で AbstractRepository の子クラスを列挙
→ パターン分類に反映
```

### 3. 循環依存の精密検出

`call_hierarchy` で実際の呼び出し関係を追跡し、import 解析だけでは見えない循環を検出する。

**活用するSerenaツール:**
- `call_hierarchy` — 呼び出し元/呼び出し先の追跡

**補完される MMI 基準:**
- 2.2.1/2.2.2 循環に含まれるクラス/パッケージの割合
- 2.2.3/2.2.4 循環あたりのクラス/パッケージ数

### 4. モジュール構造の把握

`workspace_symbols` でプロジェクト全体のシンボル構造を把握し、モジュール分割の質を評価する。

**活用するSerenaツール:**
- `workspace_symbols` — プロジェクト全体のシンボル検索
- `document_symbols` — ファイル内のシンボル一覧

**補完される MMI 基準:**
- 1.1.1 ドメインモジュールへのソースコード割当率
- 1.1.5 責務の明確さ（シンボル名の分析で補助）

## ワークフロー例

### 基本ワークフロー（Serena なし）

```
1. python metrics_analyzer.py /path/to/project
2. python architecture_analyzer.py /path/to/project --config architecture.json
3. python mmi_calculator.py --metrics metrics_result.json --architecture architecture_result.json
```

### 強化ワークフロー（Serena あり）

```
1. Serena でプロジェクトをオンボード
2. workspace_symbols でプロジェクト構造を把握
3. python metrics_analyzer.py /path/to/project
4. python architecture_analyzer.py /path/to/project --config architecture.json
5. Serena の find_references/call_hierarchy で
   - レイヤー違反の追加検出
   - 循環依存の精密検出
   - パターン分類の補完
6. 追加情報を reviewer_input.json に反映
7. python mmi_calculator.py --metrics ... --architecture ... --reviewer reviewer_input.json
```

## Serena プロジェクト設定例

```yaml
# .serena/project.yml
name: my-project
languages:
  - python
read_only: true   # 解析のみ、コード変更なし
ignored_dirs:
  - __pycache__
  - .venv
  - node_modules
  - .git
```
