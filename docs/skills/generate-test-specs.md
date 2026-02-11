# /generate-test-specs — テスト仕様生成

**カテゴリ**: Code Generation & Test（コード生成・テスト） | **Phase 7**

AIエージェントがテストコードを実装可能なBDDシナリオ・ユニットテスト・統合テスト仕様を生成します。

## 使用方法

```bash
/generate-test-specs ./path/to/source
```

## 前提条件

### 必須（`/design-implementation` の出力）
- `reports/06_implementation/domain-services-spec.md`
- `reports/06_implementation/repository-interfaces-spec.md`

### 推奨
- `reports/06_implementation/value-objects-spec.md`
- `reports/06_implementation/exception-mapping-spec.md`
- `reports/06_implementation/saga-orchestration-spec.md`
- `reports/03_design/api-design-overview.md`

## 実行ステップ

1. **前提条件の検証** — 実装仕様ファイルの存在確認
2. **BDDシナリオ生成** — Gherkin形式のビジネス要件ベースシナリオ
3. **ユニットテスト仕様生成** — クラス・メソッド単位のテストケース（JUnit/Jest形式）
4. **統合テスト仕様生成** — サービス間連携テスト（Testcontainers使用）
5. **エッジケース・エラーケース** — 境界値テスト、異常系テスト
6. **パフォーマンステスト仕様** — 負荷テスト、応答時間テスト

## 出力ファイル

| ファイル | 内容 |
|---------|------|
| `reports/07_test-specs/bdd-scenarios.md` | BDDシナリオ（Gherkin形式） |
| `reports/07_test-specs/unit-test-specs.md` | ユニットテスト仕様 |
| `reports/07_test-specs/integration-test-specs.md` | 統合テスト仕様 |
| `reports/07_test-specs/edge-case-specs.md` | エッジケース・エラーケース仕様 |
| `reports/07_test-specs/performance-test-specs.md` | パフォーマンステスト仕様 |

## 関連スキル

- 前提: [/design-implementation](design-implementation.md)
- 次のフェーズ: [/generate-scalardb-code](generate-scalardb-code.md)
