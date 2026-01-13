---
name: estimate-cost-cmd
description: コスト見積もりエージェント - クラウドインフラ、ScalarDB、その他ライセンスの見積もりを作成。
user_invocable: true
---

# Cost Estimation Agent Command

このコマンドは、設計ドキュメントに基づいてインフラ費用とライセンス費用を見積もります。

## 使用方法

```bash
/estimate-cost [対象パス]

# 例
/estimate-cost ./reports
```

## 実行手順

1. `/.claude/skills/estimate-cost/SKILL.md` を読み込んで指示に従ってください
2. `reports/03_design/` の設計ドキュメントを参照
3. クラウドプロバイダーをユーザーに確認
4. 見積もりを作成し `reports/05_estimate/` に出力

## 出力ファイル

```
reports/05_estimate/
├── cost-summary.md           # コストサマリー
├── infrastructure-detail.md  # インフラ詳細見積もり
├── license-requirements.md   # ライセンス要件・問い合わせ情報
└── cost-assumptions.md       # 見積もり前提条件
```

ARGUMENTS: $ARGUMENTS
