# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Project Overview

Legacy system analysis and microservices refactoring agent system for Claude Code. Analyzes existing codebases and generates comprehensive refactoring plans following DDD and microservices architecture principles.

## Core Architecture

This is a **skill-based agent system** (37 skills) with three execution layers:

1. **Orchestration Skills** - Full workflow automation (`workflow`, `full-pipeline`, `refactor-system`)
2. **Phase-specific Skills** - Individual analysis/design phases (investigation → analysis → evaluation → design → implementation → code generation)
3. **Utility Skills** - Supporting tools (graph operations, report compilation, Mermaid rendering)

### Execution Model

```
User Input → Skill Invocation → Agent Execution → Output Generation
    ↓              ↓                    ↓                ↓
Source Path   /skill-name     Task/Explore agents   reports/*/
```

**Key Principles:**
- Each skill is self-contained with its own SKILL.md instruction file
- Skills produce structured Markdown outputs in `reports/` directory
- Intermediate state stored in `work/{project}/` (not committed to git)
- Knowledge graph built from analysis results stored in `knowledge.ryugraph`

## Common Commands

### Skill Invocation Pattern

All skills are invoked using the `Skill` tool:
```
Skill(skill="skill-name", args="./path/to/source")
```

Claude Code provides aliases for common skills as `/skill-name` commands.

### Full Workflow Execution

```bash
# Interactive workflow selection (recommended for flexible execution)
/workflow ./path/to/source

# Complete pipeline (investigation → design → code generation)
/full-pipeline ./path/to/source

# Refactoring analysis only (no code generation)
/refactor-system ./path/to/source
```

### Individual Phase Execution

```bash
# Phase 0: System Investigation
/system-investigation ./src

# Phase 0.5: Security Analysis (optional)
/security-analysis ./src            # OWASP Top 10 + zero trust readiness
/access-control-analysis ./src      # Zero trust access control analysis

# Phase 1: Analysis
/analyze-system ./src          # Extract ubiquitous language, actors, domain mapping

# Phase 1.5: Data Model Analysis (optional)
/data-model-analysis ./src     # Entity, relationship, domain rule extraction
/db-design-analysis ./src      # Table definitions, indexes, constraints
/er-diagram-analysis ./src     # Generate current ER diagrams

# Phase 2: Evaluation
/evaluate-mmi ./src            # Modularity Maturity Index evaluation (manual 4-axis)
/mmi-analyzer ./src            # MMI automated analysis with Python scripts (Lilienthal 3-axis)
/ddd-evaluation ./src          # DDD principles evaluation
/integrate-evaluations ./src   # Merge MMI + DDD results into unified improvement plan

# Phase 3-5: Design
/ddd-redesign ./src           # Bounded contexts, aggregates, value objects
/map-domains ./src            # Domain classification, context mapping
/design-microservices ./src   # Target architecture, transformation plan
/select-scalardb-edition          # ScalarDBエディション選定（対話形式）
/design-scalardb-app-patterns ./src  # ドメインタイプ別設計パターン
/design-scalardb ./src            # ScalarDB schema & transaction design
/design-scalardb-analytics ./src  # ScalarDB Analytics (Apache Spark) design
/review-scalardb --mode=design    # ScalarDB設計レビュー
/design-api ./src             # REST/GraphQL/gRPC/AsyncAPI specs

# Phase 6-8: Implementation & Code Generation
/design-implementation ./src   # Detailed implementation specs for AI coding agents
/generate-test-specs ./src     # BDD scenarios, unit/integration test specs
/generate-scalardb-code ./src  # Generate ScalarDB/Spring Boot code
/review-scalardb --mode=code      # ScalarDBコードレビュー

# Phase 8.7: Infrastructure
/design-infrastructure         # Kubernetes & IaC (Terraform/Helm/Kustomize/OpenShift)

# Phase 9-10: Documentation & Estimation
/create-domain-story --domain=Order       # Domain storytelling (interactive)
/estimate-cost ./reports                  # Infrastructure & license cost estimation
/scalardb-sizing-estimator                # ScalarDB Cluster sizing & cost estimation (interactive)
```

### Knowledge Graph Operations

```bash
/build-graph ./src             # Build graph from analysis results
/query-graph "Show me all entities related to Order"  # Natural language query
/visualize-graph ./reports/graph/visualizations        # Visualize graph
```

### Utility Commands

```bash
/compile-report                # Compile Markdown reports to HTML
/render-mermaid ./reports/     # Render all Mermaid diagrams to PNG/SVG
/fix-mermaid ./reports/        # Fix Mermaid syntax errors
/init-output ./reports         # Initialize output directory structure

# Nextra static site generation
python scripts/compile_report.py --input-dir ./reports --format nextra
```

## Development Setup

### Python Dependencies (for graph & report tools)

```bash
pip install ryugraph pandas markdown pymdown-extensions radon networkx

# Or use venv
python3 -m venv .venv
source .venv/bin/activate
pip install ryugraph pandas markdown pymdown-extensions radon networkx
```

### Node.js (for Mermaid rendering & Nextra reports)

```bash
npm install -g @mermaid-js/mermaid-cli
mmdc --version
```

### Serena MCP Configuration

The project uses Serena MCP for symbolic code analysis. Configuration is in `.serena/project.yml`:
- **Language servers**: Java (primary target language for analysis)
- **Encoding**: UTF-8
- **Gitignore**: Enabled (respects .gitignore for file operations)

## Output Structure

```
reports/
├── before/{project}/        # Phase 0/0.5: Investigation & security analysis
├── 00_summary/             # Executive summary & HTML report
├── 01_analysis/            # Phase 1/1.5: System & data model analysis
├── 02_evaluation/          # Phase 2: MMI & DDD evaluation
├── 03_design/              # Phase 3-5: Architecture & data design
├── 04_stories/             # Domain stories
├── 05_estimate/            # Cost estimation
├── 06_implementation/      # Phase 6: Implementation specifications
├── 07_test-specs/          # Phase 7: Test specifications
├── 08_infrastructure/      # Phase 8.7: Infrastructure architecture docs
├── graph/                  # Knowledge graph data
└── sizing-estimates/       # ScalarDB sizing estimation

generated/{service}/         # Phase 8: Generated Spring Boot code
generated/infrastructure/    # Phase 8.7: IaC & K8s manifests
work/{project}/             # Intermediate state (git-ignored)
workspace/                  # Alternative working directory (git-ignored)
knowledge.ryugraph          # RyuGraph database file
```

## Architecture Patterns

### DDD Concepts Used

- **Strategic Design**: Bounded Contexts, Context Mapping, Ubiquitous Language
- **Tactical Design**: Entities, Value Objects, Aggregates, Repositories, Domain Services
- **Layered Architecture**: Domain → Application → Infrastructure → Presentation

### ScalarDB Integration

Skills support 3 ScalarDB editions (OSS / Enterprise Standard / Enterprise Premium):
- **Consensus Commit**: Single-storage ACID transactions
- **Two-Phase Commit**: Cross-service distributed transactions
- **Multi-Storage**: PostgreSQL + DynamoDB + other heterogeneous backends
- **Repository Pattern**: Domain-driven repository interfaces with ScalarDB implementations
- **Edition-Aware Design**: `/select-scalardb-edition` for edition selection, edition-specific code generation

See `.claude/rules/scalardb-coding-patterns.md` and `.claude/rules/scalardb-edition-profiles.md` for detailed patterns.

## Skill Reference (37 skills)

All skills are user-invocable via `/skill-name` slash commands. Each skill is defined in `.claude/skills/{skill-name}/SKILL.md`.

### Orchestration (3)
| Skill | Description |
|-------|-------------|
| `/workflow` | インタラクティブワークフロー選択 |
| `/full-pipeline` | 全フェーズ一括実行 |
| `/refactor-system` | 統合リファクタリング分析・設計 |

### Investigation & Analysis (7)
| Skill | Description |
|-------|-------------|
| `/system-investigation` | コードベースの構造・技術スタック・問題点を調査 |
| `/analyze-system` | ユビキタス言語、アクター、ドメイン-コード対応表を抽出 |
| `/security-analysis` | セキュリティ分析（OWASP Top 10、ゼロトラスト準備度） |
| `/access-control-analysis` | アクセス制御分析（ゼロトラストモデル） |
| `/data-model-analysis` | データモデル分析（エンティティ、リレーションシップ、ドメインルール） |
| `/db-design-analysis` | DB設計分析（テーブル定義、インデックス、正規化） |
| `/er-diagram-analysis` | ER図分析（現行ER図の生成・可視化） |

### Evaluation (4)
| Skill | Description |
|-------|-------------|
| `/evaluate-mmi` | MMI 4軸モジュール成熟度評価（手動定性評価） |
| `/mmi-analyzer` | MMI自動定量評価（Lilienthal 3軸、Pythonスクリプト） |
| `/ddd-evaluation` | DDD戦略的・戦術的設計評価 |
| `/integrate-evaluations` | MMI+DDD統合改善計画 |

### Design (12)
| Skill | Description |
|-------|-------------|
| `/ddd-redesign` | DDD原則に基づくシステム再設計 |
| `/map-domains` | ドメイン分類・コンテキストマップ作成 |
| `/design-microservices` | ターゲットアーキテクチャ策定 |
| `/select-scalardb-edition` | ScalarDBエディション選定（対話形式） |
| `/design-scalardb` | エディション設定に基づくScalarDBデータアーキテクチャ |
| `/design-scalardb-app-patterns` | ドメインタイプ別アプリケーション設計パターン |
| `/design-scalardb-analytics` | ScalarDB Analytics分析基盤設計 |
| `/review-scalardb` | ScalarDB設計・コードレビュー |
| `/design-api` | REST/GraphQL/gRPC/AsyncAPI仕様書 |
| `/design-implementation` | AI向け詳細実装仕様生成 |
| `/design-infrastructure` | Kubernetes・IaC構成生成（Terraform/Helm/Kustomize/OpenShift） |
| `/create-domain-story` | ドメインストーリー作成（対話形式） |

### Code Generation & Test (2)
| Skill | Description |
|-------|-------------|
| `/generate-test-specs` | BDD/ユニット/統合テスト仕様生成 |
| `/generate-scalardb-code` | ScalarDB/Spring Bootコード自動生成 |

### Estimation (2)
| Skill | Description |
|-------|-------------|
| `/estimate-cost` | インフラ・ライセンスコスト見積もり |
| `/scalardb-sizing-estimator` | ScalarDBサイジング・コスト見積もり（対話形式） |

### Knowledge Graph (3)
| Skill | Description |
|-------|-------------|
| `/build-graph` | RyuGraphデータベース構築 |
| `/query-graph` | 自然言語/Cypherでグラフ探索 |
| `/visualize-graph` | Mermaid/DOT/HTML形式で可視化 |

### Utility (4)
| Skill | Description |
|-------|-------------|
| `/init-output` | 出力ディレクトリ構造作成 |
| `/compile-report` | Markdown→HTML統合レポート |
| `/render-mermaid` | Mermaid図→PNG/SVG変換 |
| `/fix-mermaid` | Mermaidシンタックスエラー修正 |

## Key Metrics

### MMI (Modularity Maturity Index) — 2 variants

**Variant A: 4-axis evaluation** (`/evaluate-mmi`) — Manual qualitative assessment

Axes: Cohesion (30%), Coupling (30%), Independence (20%), Reusability (20%)

**Score**: `(0.3×Cohesion + 0.3×Coupling + 0.2×Independence + 0.2×Reusability) / 5 × 100`

Levels: 80-100 High | 60-80 Medium | 40-60 Low-medium | 0-40 Immature

**Variant B: Lilienthal 3-axis evaluation** (`/mmi-analyzer`) — Automated quantitative analysis (Python projects)

Axes: Modularity (45%), Hierarchy (30%), Pattern Consistency (25%)

**Score**: `Modularity×0.45 + Hierarchy×0.30 + Pattern×0.25` (0-10 scale)

Levels: 8-10 Good | 4-8 Warning | 0-4 Critical

## Tool Selection Priority

1. **Serena MCP** (primary) - Symbol-level analysis, AST operations, code navigation
2. **Glob/Grep** - Pattern matching, file discovery
3. **Read** - Direct file content access
4. **Task tool with Explore agent** - Open-ended codebase exploration

## File Locations Reference

| Path | Purpose |
|------|---------|
| `.claude/skills/*/SKILL.md` | Skill definitions (37 skills) |
| `.claude/skills/common/progress-registry.md` | Pipeline phase tracking (27 phases, dependencies, resume support) |
| `.claude/skills/common/sub-agent-patterns.md` | Task tool usage patterns (8 categories, subagent type guidance) |
| `.claude/rules/*.md` | Coding patterns (ScalarDB, Spring Boot) |
| `.claude/templates/*.md` | Output templates, error handling patterns |
| `scripts/*.py` | Python utilities for graph/report operations |
| `.claude/skills/mmi-analyzer/scripts/*.py` | MMI automated analysis scripts (metrics, architecture, calculator) |
| `reports/` | Generated analysis & design documents |
| `generated/` | Generated Spring Boot source code |
| `work/` | Intermediate state (not committed) |
| `workspace/` | Alternative working directory (not committed) |
| `.serena/` | Serena MCP configuration & memories |

## Git Workflow

Generated outputs should NOT be committed:
- `reports/`, `work/`, `workspace/`, `generated/`, `knowledge.ryugraph` - All git-ignored

When modifying skills:
1. Edit `.claude/skills/{skill-name}/SKILL.md`
2. Test the skill with a sample project
3. Commit only the skill definition changes

## Working with Large Codebases

- Use `--domain=Order,Customer` to limit analysis scope
- Intermediate state in `work/` allows resuming interrupted pipelines
- Knowledge graph enables incremental analysis (build once, query repeatedly)

## Error Recovery

```bash
cat work/{project}/{phase}/_state.md      # Check intermediate state
/full-pipeline ./src --resume-from=phase-{N}  # Resume from last successful phase
/{phase-skill-name} ./src                  # Re-run specific phase
```

---

**Coding Patterns**: `.claude/rules/scalardb-coding-patterns.md`
