# /fix-mermaid — Mermaid修正

**カテゴリ**: Utility（ユーティリティ）

Mermaid図のシンタックスエラーを検出し、自動修正します。

## 使用方法

```bash
/fix-mermaid ./reports/
```

## 前提条件

- Mermaid図（` ```mermaid ` ブロック）を含むMarkdownファイルが存在すること

## よくあるエラーと修正

### 1. 日本語テキストの問題
スペースや特殊文字を含む日本語テキストはダブルクオートで囲む必要があります。

```mermaid
%% NG
A[監査セット 作成] --> B[ユーザー認証]

%% OK
A["監査セット作成"] --> B["ユーザー認証"]
```

### 2. サブグラフ名のクオート漏れ

```mermaid
%% NG
subgraph Phase 1 分析

%% OK
subgraph "Phase 1 分析"
```

### 3. HTMLタグのクオート漏れ

```mermaid
%% NG
A[複数行<br/>テキスト]

%% OK
A["複数行<br/>テキスト"]
```

### 4. エッジラベルの特殊文字

```mermaid
%% NG
A -->|Customer-Supplier| B

%% OK
A -->|"Customer-Supplier"| B
```

### 5. 数字始まりのノードID

```mermaid
%% NG
1[First] --> 2[Second]

%% OK
node1["First"] --> node2["Second"]
```

## 検証項目

- [ ] 日本語テキストがダブルクオートで囲まれている
- [ ] サブグラフ名がクオートで囲まれている
- [ ] HTMLタグを含むノードがクオートで囲まれている
- [ ] エッジラベルの特殊文字がクオートで囲まれている
- [ ] ノードIDが英字で始まっている
- [ ] classDiagramのメソッド名が英語

## 関連スキル

- 補完: [/render-mermaid](render-mermaid.md)（修正後のレンダリング）
- パイプラインでは各フェーズの最終ステップとして自動実行されます
