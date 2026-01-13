# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Claude Code agent system for analyzing legacy systems and planning microservices refactoring. The main orchestrator (`/refactor-system`) coordinates specialized sub-agents through a defined pipeline, producing comprehensive analysis reports and a knowledge graph database.

## Quick Start

```bash
# Full refactoring analysis (runs all 9 phases in sequence)
/refactor-system ./path/to/source

# Individual skills (can be run standalone after /analyze-system)
/analyze-system ./path/to/source      # Phase 1: System analysis, ubiquitous language
/evaluate-mmi ./path/to/source        # Phase 2: MMI evaluation (requires Phase 1)
/map-domains ./path/to/source         # Phase 3: Domain mapping, bounded contexts
/design-microservices ./path/to/source # Phase 4: Target architecture
/design-api ./path/to/source          # Phase 4.5: API design (REST/GraphQL/gRPC/AsyncAPI)
/design-scalardb ./path/to/source     # Phase 5: ScalarDB data architecture
/design-scalardb-analytics ./path/to/source # Phase 5.5: HTAP design (optional)
/create-domain-story --domain=Order   # Phase 6: Domain storytelling (interactive)
/estimate-cost ./reports              # Phase 7: Cost estimation

# ScalarDB infrastructure sizing (standalone)
/scalardb-sizing-estimator            # Interactive sizing & cost estimation for ScalarDB Cluster

# Knowledge graph (parallel with main pipeline)
/build-graph ./path/to/source         # Build RyuGraph from analysis
/query-graph "注文に関連するクラス"     # Query via natural language or Cypher
/visualize-graph ./reports/graph      # Generate Mermaid/DOT/HTML visualizations

# Utilities
/compile-report                       # Compile Markdown reports to HTML
/render-mermaid ./reports             # Convert Mermaid diagrams to PNG/SVG
/fix-mermaid ./reports                # Fix Mermaid syntax errors
```

### Command Options

```bash
/refactor-system ./src --output=./custom-output/  # Custom output directory
/refactor-system ./src --domain=Order,Customer    # Analyze specific domains only
/refactor-system ./src --analyze-only             # Analysis only (no design docs)
/refactor-system ./src --skip-mmi                 # Skip MMI evaluation
/refactor-system ./src --skip-stories             # Skip domain storytelling
```

## Python Utilities

```bash
# Setup
pip install ryugraph pandas markdown pymdown-extensions

# Manual graph building pipeline
python scripts/parse_analysis.py --input-dir ./reports/01_analysis --output-dir ./reports/graph/data
python scripts/build_graph.py --data-dir ./reports/graph/data --db-path ./knowledge.ryugraph
python scripts/query_graph.py --db-path ./knowledge.ryugraph --interactive
python scripts/visualize_graph.py --data-dir ./reports/graph/data --output-dir ./reports/graph/visualizations
python scripts/compile_report.py --input-dir ./reports --output ./reports/00_summary/full-report.html
```

## Architecture

### Execution Pipeline

```
/refactor-system (orchestrator)
    ├── Phase 1: /analyze-system      → reports/01_analysis/
    ├── Phase 2: /evaluate-mmi        → reports/02_evaluation/
    ├── Phase 3: /map-domains         → reports/03_design/
    ├── Phase 4: /design-microservices → reports/03_design/
    ├── Phase 4.5: /design-api        → reports/03_design/ (API specs, Gateway, Security)
    ├── Phase 5: /design-scalardb     → reports/03_design/
    ├── Phase 5.5: /design-scalardb-analytics (if analytics required)
    ├── Phase 6: /create-domain-story → reports/04_stories/
    ├── Phase 7: /estimate-cost       → reports/05_estimate/
    └── Phase 8: Executive Summary    → reports/00_summary/

Parallel: /build-graph → knowledge.ryugraph/ + reports/graph/

Standalone: /scalardb-sizing-estimator (interactive Pod/node/DB sizing + cost)
```

### Skill System

Skills are defined in `.claude/skills/*/SKILL.md` with:
- YAML frontmatter: `name`, `description`, `user_invocable`
- Prerequisites and dependency chain
- Step-by-step execution workflow
- Output file specifications

Commands in `.claude/commands/*.md` invoke the corresponding skills.

### Output Structure

```
reports/
├── 00_summary/          # executive-summary.md, project_metadata.json, full-report.html
├── 01_analysis/         # system-overview.md, ubiquitous-language.md, actors-roles-permissions.md, domain-code-mapping.md
├── 02_evaluation/       # mmi-overview.md, mmi-by-module.md, mmi-improvement-plan.md
├── 03_design/           # domain-analysis.md, context-map.md, target-architecture.md, scalardb-*.md
│   ├── api-design-overview.md      # API設計概要
│   ├── api-gateway-design.md       # API Gateway設計
│   ├── api-security-design.md      # 認証・認可設計
│   └── api-specifications/         # OpenAPI, GraphQL, gRPC, AsyncAPI仕様書
├── 04_stories/          # [domain]-story.md
├── 05_estimate/         # cost-summary.md, infrastructure-detail.md, license-requirements.md
├── graph/data/          # CSV files for graph construction
└── 99_appendix/         # Supporting materials
```

## Tool Priority for Code Analysis

1. **Serena MCP Tools** (primary - language-aware AST analysis)
   - `mcp__serena__get_symbols_overview` - File structure and symbols
   - `mcp__serena__find_symbol` - Symbol search across codebase
   - `mcp__serena__find_referencing_symbols` - Reference tracking
   - `mcp__serena__list_dir` - Directory traversal

2. **Glob/Grep** - Pattern matching when Serena unavailable or for specific patterns
3. **Read** - Direct file content access

## Key Concepts

### MMI (Modularity Maturity Index)

4-axis evaluation with weighted scoring:

| Axis | Weight | Evaluates |
|------|--------|-----------|
| Cohesion | 30% | Single responsibility |
| Coupling | 30% | Loose coupling, no circular deps |
| Independence | 20% | Deploy independence |
| Reusability | 20% | Cross-context applicability |

Formula: `MMI = (0.3×Cohesion + 0.3×Coupling + 0.2×Independence + 0.2×Reusability) / 5 × 100`

Maturity levels: 80-100 (high), 60-80 (medium), 40-60 (low-medium), 0-40 (immature)

### Domain Classification

**Business Structure Axis:**
- Pipeline Domain - Sequential data/process flow (order processing)
- Blackboard Domain - Shared data coordination (inventory management)
- Dialogue Domain - Bidirectional interaction (chat, notifications)

**Microservice Boundary Axis:**
- Process Domain - Business process execution (stateful, saga management)
- Master Domain - Master data management (CRUD, data consistency)
- Integration Domain - External system adapters
- Supporting Domain - Cross-cutting concerns (auth, logging)

### Knowledge Graph Schema

**Node types:** `Entity`, `UbiquitousTerm`, `Actor`, `Domain`, `Activity`, `Role`, `Method`, `File`

**Key relationships:** `BELONGS_TO`, `DEFINED_IN`, `REFERENCES`, `CALLS`, `IMPLEMENTS`, `HAS_TERM`, `PERFORMS`

## Adding New Skills

1. Create `.claude/skills/{skill-name}/SKILL.md` with YAML frontmatter
2. Create `.claude/commands/{skill-name}-cmd.md` for user-facing command
3. Skills marked `user_invocable: true` can be called directly

## Documentation

- `docs/USER_GUIDE.md` - Comprehensive user guide with examples
- `docs/OUTPUT_FILES_REFERENCE.md` - Detailed explanation of all output files
- `README.md` - Project overview and setup instructions

## External References

- [ScalarDB Documentation](https://scalardb.scalar-labs.com/docs/)
- [ScalarDB Analytics](https://scalardb.scalar-labs.com/docs/latest/scalardb-analytics/)
- [RyuGraph Documentation](https://ryugraph.io/docs/)
