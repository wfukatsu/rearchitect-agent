# /init-output — 出力ディレクトリ初期化

**カテゴリ**: Utility（ユーティリティ）

リファクタリング分析を開始する前に、`reports/` 配下の出力ディレクトリ構造を自動作成します。

## 使用方法

```bash
/init-output ./reports
```

## 前提条件

なし（スタンドアロンで実行可能）

## 動作

実行すると以下のディレクトリ構造を作成します:

```
reports/
├── before/{project}/        # Phase 0: 調査
├── 00_summary/             # エグゼクティブサマリー
├── 01_analysis/            # Phase 1: 分析
├── 02_evaluation/          # Phase 2: 評価
├── 03_design/              # Phase 3-5: 設計
│   └── api-specifications/ # API仕様書
├── 04_stories/             # ドメインストーリー
├── 05_estimate/            # コスト見積もり
├── 06_implementation/      # 実装仕様
├── 07_test-specs/          # テスト仕様
├── 08_infrastructure/      # インフラ構成
├── graph/                  # ナレッジグラフ
│   ├── data/               # CSVデータ
│   └── visualizations/     # 可視化出力
└── sizing-estimates/       # サイジング見積もり
```

## ユーザー確認

実行前にデフォルト出力先（`./reports/`）をユーザーに確認します。カスタムパスを指定することも可能です。

## 関連スキル

- 通常は `/full-pipeline` や `/workflow` が自動的にこのスキルを呼び出します
- 個別フェーズ実行時に手動で呼び出すこともできます
