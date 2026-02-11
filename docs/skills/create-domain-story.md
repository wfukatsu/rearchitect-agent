# /create-domain-story — ドメインストーリーテリング

**カテゴリ**: Design（設計） | **Phase 10**

ドメインストーリーテリング手法を用いて、各ドメインのビジネスプロセスを物語形式で整理・可視化します。

## 使用方法

```bash
/create-domain-story --domain=Order
```

## ストーリー要素

| 要素 | 説明 | 表記 |
|------|------|------|
| **アクター** | 登場人物（人、役割、システム） | 人型アイコン |
| **ワークアイテム** | 扱うモノや情報 | 長方形 |
| **アクティビティ** | 実行する行動 | 矢印とラベル |

## 前提条件

### 推奨
- `reports/03_design/bounded-contexts-redesign.md`（`/ddd-redesign`）
- `reports/01_analysis/ubiquitous-language.md`（`/analyze-system`）
- `reports/01_analysis/actors-roles-permissions.md`（`/analyze-system`）

## 実行モード

### インタラクティブモード（推奨）

ユーザーとの対話を通じて7段階のファシリテーションプロセスでストーリーを引き出します:

1. **Stage 1: 舞台設定** — ストーリーのスコープ決定
2. **Stage 2: アクター登場** — 登場人物の特定
3. **Stage 3: ワークアイテム** — 扱うモノ・情報の特定
4. **Stage 4: ストーリー展開** — メインフローの記述
5. **Stage 5: 例外シナリオ** — 異常系・代替フローの記述
6. **Stage 6: 技術的背景** — システム制約・技術要素の記述
7. **Stage 7: まとめ** — ストーリーの検証と文書化

### 自動生成モード

既存の分析結果からストーリーを自動生成します。精度は低下しますが、大量のドメインを効率的に処理できます。

## 出力ファイル

| ファイル | 内容 |
|---------|------|
| `reports/04_stories/domain-story-{domain}.md` | ドメインストーリー（アクター、ワークアイテム、フロー、Mermaid図） |

## 関連スキル

- 前提: [/ddd-redesign](ddd-redesign.md), [/analyze-system](analyze-system.md)
