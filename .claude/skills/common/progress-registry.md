# Progress Registry Specification

リファクタリングパイプラインの進捗を追跡するためのレジストリ仕様です。

## レジストリファイル

進捗は `work/{project}/pipeline-progress.json` に記録されます。

## スキーマ

```json
{
  "$schema": "progress-registry-v1",
  "project_name": "sample-project",
  "target_path": "./SampleCode/sample-project",
  "created_at": "2025-01-20T10:00:00Z",
  "updated_at": "2025-01-20T12:30:00Z",
  "phases": {
    "system-investigation": {
      "status": "completed",
      "started_at": "2025-01-20T10:00:00Z",
      "completed_at": "2025-01-20T10:30:00Z",
      "outputs": [
        "reports/before/sample-project/technology-stack.md",
        "reports/before/sample-project/codebase-structure.md",
        "reports/before/sample-project/issues-and-debt.md",
        "reports/before/sample-project/ddd-readiness.md",
        "reports/before/sample-project/investigation-summary.md"
      ]
    },
    "analyze-system": {
      "status": "completed",
      "started_at": "2025-01-20T10:30:00Z",
      "completed_at": "2025-01-20T11:00:00Z",
      "outputs": [
        "reports/01_analysis/system-overview.md",
        "reports/01_analysis/ubiquitous-language.md",
        "reports/01_analysis/actors-roles-permissions.md",
        "reports/01_analysis/domain-code-mapping.md"
      ]
    },
    "evaluate-mmi": {
      "status": "completed",
      "started_at": "2025-01-20T11:00:00Z",
      "completed_at": "2025-01-20T11:20:00Z",
      "outputs": [
        "reports/02_evaluation/mmi-overview.md",
        "reports/02_evaluation/mmi-by-module.md",
        "reports/02_evaluation/mmi-improvement-plan.md"
      ]
    },
    "ddd-evaluation": {
      "status": "in_progress",
      "started_at": "2025-01-20T11:20:00Z",
      "completed_at": null,
      "outputs": []
    },
    "integrate-evaluations": {
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "outputs": []
    },
    "ddd-redesign": {
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "outputs": []
    },
    "design-microservices": {
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "outputs": []
    },
    "design-api": {
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "outputs": []
    },
    "design-scalardb": {
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "outputs": []
    },
    "create-domain-story": {
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "outputs": []
    },
    "estimate-cost": {
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "outputs": []
    },
    "build-graph": {
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "outputs": []
    }
  },
  "errors": [],
  "warnings": []
}
```

## ステータス値

| ステータス | 説明 |
|-----------|------|
| `pending` | 未開始 |
| `in_progress` | 実行中 |
| `completed` | 完了 |
| `failed` | 失敗 |
| `skipped` | スキップ |

## フェーズ依存関係

```
system-investigation (optional)
       ↓
analyze-system
       ↓
    ┌──┴──┐
    ↓     ↓
evaluate-mmi  ddd-evaluation
    ↓     ↓
    └──┬──┘
       ↓
integrate-evaluations
       ↓
ddd-redesign
       ↓
design-microservices
       ↓
    ┌──┴──┐
    ↓     ↓
design-api  design-scalardb
    ↓     ↓
    └──┬──┘
       ↓
estimate-cost
       ↓
create-domain-story (optional)

Parallel: build-graph (can run after analyze-system)
```

## 使用方法

### 進捗の更新

各スキルは実行開始時と完了時に進捗を更新します：

```python
# 開始時
progress["phases"]["ddd-evaluation"]["status"] = "in_progress"
progress["phases"]["ddd-evaluation"]["started_at"] = datetime.now().isoformat()

# 完了時
progress["phases"]["ddd-evaluation"]["status"] = "completed"
progress["phases"]["ddd-evaluation"]["completed_at"] = datetime.now().isoformat()
progress["phases"]["ddd-evaluation"]["outputs"] = [
    "reports/02_evaluation/ddd-strategic-evaluation.md",
    "reports/02_evaluation/ddd-tactical-evaluation.md",
    "reports/02_evaluation/ddd-pattern-analysis.md",
    "reports/02_evaluation/ddd-improvement-plan.md"
]
```

### 前提条件チェック

スキルは実行前に依存フェーズの完了を確認：

```python
def check_prerequisites(progress, required_phases):
    for phase in required_phases:
        if progress["phases"][phase]["status"] != "completed":
            return False, f"Phase '{phase}' must be completed first"
    return True, None
```

### オーケストレーターでの使用

`/refactor-system` オーケストレーターは進捗レジストリを参照して：
1. どのフェーズから再開するか判断
2. 並列実行可能なフェーズを特定
3. 全体の進捗状況をレポート
