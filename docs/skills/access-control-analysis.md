# /access-control-analysis — アクセス制御分析

**カテゴリ**: Investigation（調査） | **Phase 0.5b**

ゼロトラストモデルに基づくアクセス制御の現状分析と、マイクロサービス移行時の認証・認可アーキテクチャ設計の基礎情報を提供します。

## 使用方法

```bash
/access-control-analysis ./path/to/source
```

## 前提条件

- **推奨**: `reports/01_analysis/actors-roles-permissions.md`（`/analyze-system` の出力）
- **推奨**: `reports/before/{project}/security-analysis.md`（`/security-analysis` の出力）

前提ファイルがなくてもコードから直接分析可能です。

## 実行ステップ

1. **プロジェクト名の特定**
2. **アクセス制御メカニズムの特定** — Spring Security、フィルター、アノテーション等
3. **アクセス制御マトリクスの構築** — リソース×ロール×アクションの対応表
4. **認証・認可フローの可視化** — Mermaid シーケンス図で認証フローを表現
5. **ゼロトラスト準備度の評価** — マイクロサービス向けの認可モデル評価
6. **レポートの作成** → `access-control-analysis.md`
7. **Mermaid図の検証**

## 出力ファイル

| ファイル | 内容 |
|---------|------|
| `reports/before/{project}/access-control-analysis.md` | アクセス制御分析（マトリクス、認証フロー図、ゼロトラスト準備度、改善ロードマップ） |

## 関連スキル

- 前提: [/system-investigation](system-investigation.md), [/analyze-system](analyze-system.md)
- 関連: [/security-analysis](security-analysis.md)
