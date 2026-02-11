# /security-analysis — セキュリティ分析

**カテゴリ**: Investigation（調査） | **Phase 0.5a**

OWASP Top 10 への対応状況とゼロトラストアーキテクチャへの移行準備度を評価します。

## 使用方法

```bash
/security-analysis ./path/to/source
```

## 前提条件

- **推奨**: `reports/before/{project}/technology-stack.md`（`/system-investigation` の出力）
- **推奨**: `reports/01_analysis/actors-roles-permissions.md`（`/analyze-system` の出力）

前提ファイルがなくてもコードから直接分析可能です。

## 実行ステップ

1. **プロジェクト名の特定**
2. **認証・認可メカニズムの分析** — 使用フレームワーク、認証方式の特定
3. **OWASP Top 10対応状況の評価** — A01〜A10 の各カテゴリで対応状況を判定
4. **データ保護の分析** — 暗号化、個人情報保護、通信セキュリティ
5. **ゼロトラスト準備度の評価** — ゼロトラスト原則への適合度スコアリング
6. **レポートの作成** → `security-analysis.md`
7. **Mermaid図の検証**

## 出力ファイル

| ファイル | 内容 |
|---------|------|
| `reports/before/{project}/security-analysis.md` | セキュリティ分析レポート（OWASP評価、ゼロトラスト準備度、改善ロードマップ） |

## 関連スキル

- 前提: [/system-investigation](system-investigation.md)
- 関連: [/access-control-analysis](access-control-analysis.md)
