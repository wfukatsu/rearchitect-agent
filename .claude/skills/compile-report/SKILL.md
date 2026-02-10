---
name: compile-report
description: レポートコンパイルエージェント - 分析結果のMarkdownファイルを統合HTMLレポートに変換。/compile-report [出力パス] で呼び出し。
user_invocable: true
---

# Report Compiler Agent

分析結果のMarkdownファイルを統合HTMLレポートに変換するエージェントです。

## 概要

このエージェントは以下の機能を提供します：

1. **Markdownの自動検出・統合** - 各ディレクトリ内のすべてのMarkdownファイルを動的に検出し統合
2. **設定ファイルの表示** - YAML/JSON/Properties/TOML等の設定ファイルをシンタックスハイライト付きで表示
3. **Mermaid図のレンダリング** - Mermaid図をインライン埋め込み
4. **GraphDB可視化** - D3.jsインタラクティブグラフを埋め込み（事前に`/visualize-graph`で生成）
5. **目次生成** - 自動的にサイドバー目次を生成
6. **スタイリング** - プロフェッショナルなスタイルを適用（ライト/ダークテーマ）
7. **レスポンシブ** - モバイル/印刷対応
8. **重複除去** - ファイル名の命名規則が異なる重複ファイルを自動的に除去
9. **HTML検証・自動修正** - 生成されたHTMLの各セクションが正しく表示されるか検証し、問題があれば修正
10. **XSSサニタイゼーション** - 危険なHTMLタグ（`<script>`, `<img onerror>`等）を自動的にエスケープしてXSS攻撃を防止

## 出力形式の選択

レポートは2つの形式で生成できます：

| 形式 | 推奨用途 | 利点 | 欠点 |
|------|---------|------|------|
| **HTML** | 単一ファイル配布、ローカル閲覧 | 単一ファイル、依存関係なし、検索機能あり | ページ分割なし、大きいファイル |
| **Nextra** | Webホスティング、大規模レポート | ページ分割、高速ナビゲーション、モダンUI | Node.js必要、ビルド時間長い |

**選択ガイド**:
- メール添付や単一ファイル配布 → **HTML**
- Webサイトとして公開 → **Nextra**
- 100ページ以下のレポート → **HTML**
- 100ページ以上のレポート → **Nextra**

## 前提条件

### HTML形式
- Python 3.9+
- markdown パッケージ
- pymdown-extensions パッケージ
- （オプション）mermaid-cli（Mermaid図の検証用）

### Nextra形式
- Node.js 16.x以上
- npm 8.x以上
- Python 3.9+（変換スクリプト用）

## 実行プロンプト

あなたはレポートをコンパイルする専門家エージェントです。以下の手順でレポートを生成してください。

---

# 方式A: HTML形式（単一ファイル）

### Step 1: 環境確認

```bash
# 必要なパッケージの確認
source .venv/bin/activate
pip install markdown pymdown-extensions
```

### Step 2: Mermaid図の検証（推奨）

レポート生成前にMermaid図の構文エラーをチェックします。

```bash
# mmdc がインストールされている場合
/fix-mermaid ./reports
```

**注意: Mermaidの予約語問題**

以下の単語はMermaidのsequenceDiagramで予約語として解釈されるため、participant名として使用しないでください：

| 予約語 | 代替案 |
|-------|-------|
| `BOX` | `BoxAPI`, `BoxPlatform`, `BoxWebhook` |
| `box` | 同上 |

**例:**
```mermaid
# NG
participant BOX as BOX Platform

# OK
participant BoxPlatform as BOX Platform
```

### Step 3: GraphDB可視化の準備

ナレッジグラフのインタラクティブビューアを含める場合、事前に可視化ファイルを生成します。

```bash
# GraphDBが構築済みの場合
/visualize-graph ./reports/graph

# GraphDBが未構築の場合は先に構築
/build-graph ./path/to/source
/visualize-graph ./reports/graph
```

**生成されるファイル:**
```
reports/graph/
├── visualizations/
│   ├── graph.html          # D3.jsインタラクティブグラフ（これが必要）
│   ├── graph-mermaid.md    # Mermaid形式
│   └── graph-dot.dot       # DOT形式
└── data/
    ├── nodes.csv
    └── edges.csv
```

**重要**: `reports/graph/visualizations/graph.html`が存在する場合、自動的にインタラクティブグラフがレポートに埋め込まれます。

### Step 4: レポートコンパイルスクリプトの実行

```bash
source .venv/bin/activate && python scripts/compile_report.py \
  --input-dir ./reports \
  --output ./reports/00_summary/full-report.html \
  --title "リファクタリング分析レポート"
```

**自動的に実行される処理:**
- Markdownファイルの検出・統合
- Mermaid図のレンダリング
- 設定ファイルのシンタックスハイライト
- GraphDB可視化の埋め込み
- **XSSサニタイゼーション** - 危険なHTMLタグを自動エスケープ
- HTML検証

### Step 5: 出力形式

#### 統合HTMLレポート

```html
<!DOCTYPE html>
<html>
<head>
    <title>リファクタリング分析レポート</title>
    <script src="mermaid.min.js"></script>
    <script src="d3.v7.min.js"></script>
    <style>/* プロフェッショナルスタイル */</style>
</head>
<body>
    <nav class="sidebar"><!-- サイドバー目次 --></nav>
    <main class="main-content">
        <section id="summary"><!-- エグゼクティブサマリー --></section>
        <section id="analysis"><!-- 分析結果 --></section>
        <section id="evaluation"><!-- MMI評価 --></section>
        <section id="design"><!-- 設計書 --></section>
        <section id="stories"><!-- ドメインストーリー --></section>
        <section id="graph">
            <!-- ナレッジグラフ -->
            <!-- D3.jsインタラクティブビューア -->
        </section>
    </main>
</body>
</html>
```

### Step 6: コマンドオプション

| オプション | 説明 | デフォルト |
|-----------|------|----------|
| `--input-dir` | 入力ディレクトリ | ./reports |
| `--output` | 出力HTMLファイル（`--format html`時） | ./reports/00_summary/full-report.html |
| `--title` | レポートタイトル | リファクタリング分析レポート |
| `--theme` | テーマ (light/dark)（`--format html`時） | light |
| `--format` | 出力形式 (html/nextra) | html |
| `--nextra-output` | Nextraサイト出力先（`--format nextra`時） | ./reports/nextra-site |
| `--no-verify` | HTML検証をスキップ（`--format html`時） | false（検証はデフォルト有効） |

### Step 7: HTML検証と修正

レポート生成後、各セクションが正しく表示されるかを検証します。

**検証項目:**
1. **セクションの存在確認** - 各セクションIDが存在するか
2. **コンテンツの存在確認** - 各セクションに内容が含まれているか
3. **Mermaid図のレンダリング** - Mermaid図が正しく埋め込まれているか
4. **GraphDBビューアの動作確認** - graph.htmlからデータが正しく抽出されているか
5. **設定ファイルの表示** - YAML/JSON等がシンタックスハイライト付きで表示されるか
6. **リンクの整合性** - 目次のリンクが正しいセクションを指しているか
7. **XSSサニタイゼーション** - 危険なHTMLタグが適切にエスケープされているか

**自動修正される問題:**
- 空のセクション → スキップまたは「コンテンツなし」表示
- 破損したMermaidブロック → エラーメッセージを表示
- 不正なJSON → パース失敗時はそのまま表示

**検証の実行:**
```bash
# スクリプト実行時に自動で検証（デフォルト）
python scripts/compile_report.py --input-dir ./reports --output ./reports/00_summary/full-report.html

# 検証をスキップ
python scripts/compile_report.py --input-dir ./reports --output ./reports/00_summary/full-report.html --no-verify
```

**検証結果の出力例:**
```
=== HTML Verification ===
✓ Section 'summary' - 2 articles
✓ Section 'analysis' - 5 articles
✓ Section 'evaluation' - 9 articles
✓ Section 'design' - 12 articles (3 config files)
✓ Section 'graph' - 2 articles + interactive viewer
⚠ Section 'stories' - Empty (no content found)
✓ Mermaid diagrams: 15 found
✓ Navigation links: 31 valid

=== Verification Complete ===
Warnings: 1
Errors: 0
```

---

# 方式B: Nextra形式（静的サイト）

Nextra形式は、Next.js + Nextra 2.xを使用した静的サイト生成です。

## 概要

- **出力**: 44ページの静的サイト（23MB、`out/`ディレクトリ）
- **ビルド時間**: 約30-40秒
- **特徴**: ページ分割、高速ナビゲーション、検索機能、レスポンシブUI

## Step 1: 環境確認

```bash
# Node.jsバージョン確認
node --version  # 16.x以上

# Python環境
source .venv/bin/activate
```

## Step 2: Markdownから.mdxへの変換

```bash
python scripts/convert_to_nextra.py \
  --input ./reports \
  --output ./reports/nextra-site
```

**自動実行される処理**:
1. Markdownファイルの検出
2. **MDXエスケープ処理** - JSX構文と衝突するパターンを自動エスケープ
3. `_meta.json`の生成（ナビゲーション構造）
4. `.mdx`ファイルの出力

**MDXエスケープルール（自動適用）**:

| パターン | 変換 | 理由 |
|---------|------|------|
| `Array<String>` | `Array&lt;String&gt;` | JSX汎用型syntax |
| `<500ms` | `&lt;500ms` | JSX開始タグとして解釈される |
| `{id}`, `{token}` | `\{id\}`, `\{token\}` | JSX式として解釈される |
| `test<>.txt` | `test&lt;&gt;.txt` | 空フラグメント |
| `<img src=x>` | `&lt;img src=x&gt;` | XSSテスト用HTMLタグ |

**注意**: コードブロック内（```...```）はエスケープされません。

## Step 3: npm依存関係のインストール

```bash
cd reports/nextra-site
npm install
```

**初回のみ実行**。依存関係:
- next ^13.5.0
- nextra ^2.13.4
- nextra-theme-docs ^2.13.4
- react, react-dom

## Step 4: ビルド実行

```bash
cd reports/nextra-site
npx next build
```

**出力**: `out/` ディレクトリに静的サイトが生成されます。

## Step 5: プレビュー

```bash
# ローカルサーバーで確認（開発モード）
cd reports/nextra-site
npx next dev

# ブラウザで開く
open http://localhost:3000

# 本番ビルド後のプレビュー
npx serve out/
```

## Step 6: 出力構造

```
reports/nextra-site/
├── pages/                  # MDXソースファイル
│   ├── index.mdx          # トップページ
│   ├── _meta.json         # ナビゲーション定義
│   ├── 00_summary/        # エグゼクティブサマリー（3ページ）
│   ├── 01_analysis/       # システム分析（4ページ）
│   ├── 02_evaluation/     # 品質評価（8ページ）
│   ├── 03_design/         # アーキテクチャ設計（9ページ）
│   ├── 04_stories/        # ドメインストーリー（1ページ）
│   ├── 06_implementation/ # 実装仕様（2ページ）
│   ├── 07_test-specs/     # テスト仕様（11ページ）
│   └── graph/             # ナレッジグラフ（3ページ）
├── out/                   # 静的サイト（next build後）
│   ├── index.html
│   ├── _next/            # JSバンドル
│   ├── 00_summary/
│   ├── 01_analysis/
│   └── ...
├── package.json
├── next.config.js
└── theme.config.tsx
```

## Nextra提供機能

### ビルトイン機能
- **検索機能**: サイドバー検索（全ページ対象）
- **ナビゲーション**: サイドバー + パンくず + 前/次ページ移動
- **テーマ切り替え**: ライト/ダークモード
- **レスポンシブ**: モバイル対応（ハンバーガーメニュー）
- **シンタックスハイライト**: コードブロック
- **コピーボタン**: コードブロックに自動追加

### Mermaid図の表示
Nextra 2.xはMermaidをネイティブサポートしていないため、カスタムコンポーネントが必要です：

```mdx
import Mermaid from '@/components/Mermaid'

<Mermaid chart={`
graph TD
  A[Start] --> B[End]
`} />
```

**TODO**: Mermaidコンポーネントの実装（次のステップ）

### GraphDB可視化の表示
同様にカスタムコンポーネントが必要です：

```mdx
import GraphViewer from '@/components/GraphViewer'

<GraphViewer dataPath="/data/graph.json" />
```

**TODO**: GraphViewerコンポーネントの実装（次のステップ）

## トラブルシューティング

### MDXパースエラー

**エラー例**:
```
Expected a closing tag for `<String>`
```

**原因**: MDXは`<>`や`{}`をJSX構文として解釈します。

**対応**: `convert_to_nextra.py`が自動エスケープします。エラーが出る場合:

1. 最新の変換スクリプトを使用しているか確認
2. 手動でエスケープ:
   ```bash
   # 問題箇所を特定
   npx next build  # エラーメッセージでファイル名と行番号を確認

   # 該当MDXファイルを編集
   # Array<String> → Array&lt;String&gt;
   # {id} → \{id\}
   ```

### ビルド時間が長い

**対応**:
- キャッシュ削除: `rm -rf .next/`
- 増分ビルド: `npx next build` は変更ファイルのみ再ビルド

### npm installエラー

**エラー**: `ERESOLVE unable to resolve dependency tree`

**対応**:
```bash
# 強制インストール
npm install --legacy-peer-deps

# またはpackage-lock.jsonを削除
rm package-lock.json
npm install
```

## HTML vs Nextra 比較表

| 観点 | HTML | Nextra |
|------|------|--------|
| **ファイルサイズ** | 1.3MB（単一） | 23MB（ディレクトリ） |
| **ビルド時間** | ~10秒 | ~35秒 |
| **ページ分割** | ❌ 単一ファイル | ✅ 44ページ |
| **検索機能** | ✅ Lunr.js | ✅ ビルトイン |
| **ナビゲーション** | サイドバーのみ | パンくず + 前/次移動 |
| **モバイル対応** | ⚠️ 重い | ✅ 最適化済み |
| **配布方法** | 単一ファイル添付 | ディレクトリまたはホスティング |
| **依存関係** | Python | Node.js + npm |
| **カスタマイズ** | CSSのみ | Reactコンポーネント |

## 詳細調査レポート

Nextra移行の技術詳細、MDXパターン問題の完全な分析、既知の制限については以下を参照:

📖 **`docs/nextra-investigation.md`** - Nextra移行調査レポート

---

## 機能詳細

### Markdownファイルの自動検出

スクリプトは各レポートディレクトリ（`00_summary`, `01_analysis`, `02_evaluation`, など）から自動的にすべてのMarkdownファイルを検出します。

**動作:**
1. 優先ファイルリストに従って順序を決定
2. ディレクトリ内の他のMarkdownファイルを自動検出
3. 重複ファイルを自動除去
4. サブディレクトリ（`visualizations/`など）も検索対象

**対応するファイル構造:**
```
reports/
├── 00_summary/          # エグゼクティブサマリー
├── 01_analysis/         # システム分析（全ファイル自動検出）
├── 02_evaluation/       # MMI評価
├── 03_design/           # 設計（API、ScalarDB含む全ファイル）
│   └── api-specifications/  # OpenAPI/AsyncAPI仕様（YAML/JSON）
├── 04_stories/          # ドメインストーリー（個別ストーリー含む）
├── 05_estimate/         # コスト試算
└── graph/               # ナレッジグラフ（サブディレクトリ含む）
```

### 設定ファイルの表示

Markdown以外の設定ファイルも自動的に検出し、シンタックスハイライト付きで表示します。

**対応するファイル形式:**

| 拡張子 | 形式 | 表示方法 |
|-------|------|---------|
| `.yaml`, `.yml` | YAML | コードブロック（yaml） |
| `.json` | JSON | フォーマット済みコードブロック（json） |
| `.properties` | Properties | コードブロック（properties） |
| `.toml` | TOML | コードブロック（toml） |
| `.xml` | XML | コードブロック（xml） |
| `.env`, `.env.example` | 環境変数 | コードブロック（bash） |
| `.feature` | Gherkin | コードブロック（gherkin） |
| `.graphql`, `.gql` | GraphQL | コードブロック（graphql） |
| `.proto` | Protocol Buffers | コードブロック（protobuf） |
| `.tf`, `.hcl` | Terraform/HCL | コードブロック（hcl） |

**例: OpenAPI仕様の表示**

`reports/03_design/api-specifications/openapi.yaml`が存在する場合：

```html
<h2>Openapi</h2>
<pre><code class="language-yaml">
openapi: 3.0.0
info:
  title: Order Service API
  version: 1.0.0
paths:
  /orders:
    get:
      summary: List orders
      ...
</code></pre>
```

**自動検出されるディレクトリ:**
- `api-specifications/` - API仕様書（OpenAPI, AsyncAPI, GraphQL, gRPC）
- `config/` - 設定ファイル
- `k8s/` - Kubernetesマニフェスト
- `schemas/` - スキーマ定義（JSON Schema, Protocol Buffers等）
- `bdd-scenarios/` - BDDシナリオ（Gherkin .featureファイル）
- `visualizations/` - 可視化ファイル

### GraphDB可視化の統合

`reports/graph/visualizations/graph.html`が存在する場合、自動的にインタラクティブグラフをレポートに埋め込みます。

**機能:**
- ノードのドラッグ移動
- マウスホイールでズーム
- ノードホバーで詳細表示（名前、タイプ、グループ）
- ノード検索
- 凡例表示（Domain/Entity/Term）

**前提:**
- `/build-graph` でGraphDBが構築済み
- `/visualize-graph` で可視化ファイルが生成済み

### Mermaid図のレンダリング

Markdownファイル内の```mermaid```ブロックを自動的に`<div class="mermaid">`に変換し、Mermaid.jsでレンダリングします。

**対応図:**
- flowchart / graph
- sequenceDiagram
- classDiagram
- stateDiagram
- erDiagram
- gantt
- xychart-beta

**非対応:**
- radarChart（xychart-betaで代替）

### XSSサニタイゼーション

セキュリティテストケース等で危険なHTMLタグが含まれるMarkdownファイルを処理する際、自動的にXSS対策を行います。

**エスケープ対象のタグ:**
- `<script>...</script>` - JavaScriptコード実行
- `<img onerror="...">` - エラーハンドラによるコード実行
- `<iframe>...</iframe>` - 外部コンテンツ埋め込み
- `<embed>` - 外部リソース埋め込み
- `<object>...</object>` - 外部オブジェクト埋め込み

**処理例:**

入力（Markdownテーブル内）:
```markdown
| File name with script | "<script>alert('XSS')</script>.pdf" | Rejected by validation |
```

出力（HTMLテーブル内）:
```html
<td>"&lt;script&gt;alert('XSS')&lt;/script&gt;.pdf"</td>
```

**動作:**
1. MarkdownをHTMLに変換
2. 危険なHTMLタグを検出（正規表現）
3. `html.escape()`でHTMLエンティティに変換
4. 安全なHTMLとして出力

**注意事項:**
- Mermaid図内の`<div class="mermaid">`、コードブロック内の`<code>`等、正当なHTMLタグはエスケープされません
- セキュリティテストケースの内容が安全にテキストとして表示されます
- ブラウザでXSSエラーが発生することなくHTMLを開けます

## 出力ファイル

```
reports/
└── 00_summary/
    └── full-report.html   # 統合HTMLレポート (約450KB)
```

## 使用例

### 例1: HTML形式で基本コンパイル

```bash
# コマンド形式
/compile-report

# または直接実行
source .venv/bin/activate && python scripts/compile_report.py \
  --input-dir ./reports \
  --output ./reports/00_summary/full-report.html
```

### 例2: Nextra形式で静的サイト生成

```bash
# Step 1: 変換
python scripts/convert_to_nextra.py --input ./reports --output ./reports/nextra-site

# Step 2: ビルド
cd reports/nextra-site
npm install  # 初回のみ
npx next build

# Step 3: 確認
npx serve out/
```

### 例3: HTMLをカスタムタイトルとダークテーマで生成

```bash
source .venv/bin/activate && python scripts/compile_report.py \
  --input-dir ./reports \
  --output ./reports/00_summary/full-report.html \
  --title "My Project Report" \
  --theme dark
```

### 例4: ブラウザで開く

```bash
# HTML
open reports/00_summary/full-report.html

# Nextra（ローカル開発サーバー）
cd reports/nextra-site && npx next dev
# → http://localhost:3000 を開く

# Nextra（ビルド済みサイト）
cd reports/nextra-site && npx serve out/
# → http://localhost:3000 を開く
```

## トラブルシューティング

### Mermaid図が表示されない

1. ブラウザのコンソールでエラーを確認
2. `/fix-mermaid`で構文エラーをチェック
3. 予約語（BOX等）を使用していないか確認

### GraphDBビューアが表示されない

1. `reports/graph/visualizations/graph.html`の存在を確認
2. `/visualize-graph`を実行してファイルを生成

### 日本語が文字化けする

1. HTMLファイルがUTF-8で保存されているか確認
2. ブラウザのエンコーディング設定を確認

### XSSエラーが表示される

HTMLを開いた際にXSSエラーが表示される場合：

1. **原因**: セキュリティテストケース等に含まれる`<script>`タグがエスケープされていない
2. **対応**: スクリプトが最新版（XSSサニタイゼーション対応）であることを確認
3. **確認方法**:
   ```bash
   # sanitize_html_content関数が存在するか確認
   grep -n "def sanitize_html_content" scripts/compile_report.py
   ```
4. **修正後**: レポートを再コンパイル
   ```bash
   source .venv/bin/activate && python scripts/compile_report.py \
     --input-dir ./reports \
     --output ./reports/00_summary/full-report.html
   ```

## 関連スキル

- `/render-mermaid` - Mermaid図を画像に変換
- `/fix-mermaid` - Mermaid図のシンタックスエラーを修正
- `/visualize-graph` - GraphDBを可視化
- `/build-graph` - GraphDBを構築
