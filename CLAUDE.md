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
- Each skill is self-contained with its own SKILL.md instruction file in `.claude/skills/{skill-name}/`
- Skills produce structured Markdown outputs in `reports/` directory
- Intermediate state stored in `work/{project}/` (not committed to git)
- Knowledge graph built from analysis results stored in `knowledge.ryugraph`
- Skills use sub-agents (Task tool) following patterns in `.claude/skills/common/sub-agent-patterns.md`
- Pipeline execution state tracked via `.claude/skills/common/progress-registry.md` (33 phases with dependency graph)

## Common Commands

### Skill Invocation

All skills are invoked as `/skill-name` slash commands (via the Skill tool):
```
/skill-name ./path/to/source
```

### Orchestration (Start Here)

```bash
/workflow ./path/to/source          # Interactive workflow selection (recommended)
/full-pipeline ./path/to/source     # All phases: investigation → design → code generation
/refactor-system ./path/to/source   # Refactoring analysis only (no code generation)
```

### Pipeline Phase Order

The pipeline executes in this order. Each phase can also be run individually:

| Phase | Skills | Output |
|-------|--------|--------|
| 0: Investigation | `/system-investigation` | `reports/before/{project}/` |
| 0.5: Security (optional) | `/security-analysis`, `/access-control-analysis` | `reports/before/{project}/` |
| 1: Analysis | `/analyze-system` | `reports/01_analysis/` |
| 1.5: Data Model (optional) | `/data-model-analysis`, `/db-design-analysis`, `/er-diagram-analysis` | `reports/01_analysis/` |
| 2: Evaluation | `/evaluate-mmi`, `/mmi-analyzer`, `/ddd-evaluation`, `/integrate-evaluations` | `reports/02_evaluation/` |
| 3-5: Design | `/ddd-redesign`, `/map-domains`, `/design-microservices`, `/select-scalardb-edition`, `/design-scalardb`, `/design-scalardb-app-patterns`, `/design-scalardb-analytics`, `/review-scalardb --mode=design`, `/design-api`, `/design-infrastructure` | `reports/03_design/` |
| 6-7: Implementation | `/design-implementation`, `/generate-test-specs` | `reports/06_implementation/`, `reports/07_test-specs/` |
| 8: Code Generation | `/generate-scalardb-code`, `/review-scalardb --mode=code` | `generated/{service}/` |
| 8.7: Infrastructure | `/design-infrastructure` | `generated/infrastructure/` |
| 9-10: Docs & Estimation | `/create-domain-story --domain=Order`, `/estimate-cost`, `/scalardb-sizing-estimator` | `reports/04_stories/`, `reports/05_estimate/` |

### Knowledge Graph

```bash
/build-graph ./src             # Build graph from analysis results
/query-graph "Show me all entities related to Order"
/visualize-graph ./reports/graph/visualizations
```

### Utilities

```bash
/compile-report                # Compile Markdown reports to HTML
/render-mermaid ./reports/     # Render Mermaid diagrams to PNG/SVG
/fix-mermaid ./reports/        # Fix Mermaid syntax errors
/init-output ./reports         # Initialize output directory structure
python scripts/compile_report.py --input-dir ./reports --format nextra  # Nextra static site
```

## Development Setup

### Python Dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Node.js (for Mermaid rendering)

```bash
npm install -g @mermaid-js/mermaid-cli
```

### Serena MCP

Configuration in `.serena/project.yml`: Java language server, UTF-8 encoding, gitignore-aware.

## Tool Selection Priority

When skills analyze target codebases:

1. **Serena MCP** (primary) - Symbol-level analysis, AST operations, code navigation
2. **Glob/Grep** - Pattern matching, file discovery
3. **Read** - Direct file content access
4. **Task tool with Explore agent** - Open-ended codebase exploration

## Output Structure

```
reports/                    # Analysis & design documents (git-ignored)
├── before/{project}/       # Phase 0/0.5: Investigation & security
├── 00_summary/             # Executive summary & HTML report
├── 01_analysis/            # Phase 1/1.5: System & data model analysis
├── 02_evaluation/          # Phase 2: MMI & DDD evaluation
├── 03_design/              # Phase 3-5: Architecture & data design
├── 04_stories/             # Domain stories
├── 05_estimate/            # Cost estimation
├── 06_implementation/      # Phase 6: Implementation specifications
├── 07_test-specs/          # Phase 7: Test specifications
├── 08_infrastructure/      # Phase 8.7: Infrastructure docs
├── graph/                  # Knowledge graph data
└── sizing-estimates/       # ScalarDB sizing

generated/{service}/        # Generated Spring Boot code (git-ignored)
generated/infrastructure/   # IaC & K8s manifests (git-ignored)
work/{project}/             # Intermediate state (git-ignored)
```

Output conventions (naming, frontmatter, immediate-output rule): `.claude/rules/output-conventions.md`

## Key References

| Path | Purpose |
|------|---------|
| `.claude/skills/*/SKILL.md` | Skill definitions (37 skills) |
| `.claude/skills/common/progress-registry.md` | Pipeline phase tracking (33 phases, dependencies, resume support) |
| `.claude/skills/common/sub-agent-patterns.md` | Task tool usage patterns (8 categories, subagent type guidance) |
| `.claude/rules/evaluation-frameworks.md` | MMI (2 variants) and DDD evaluation frameworks with scoring formulas |
| `.claude/rules/scalardb-coding-patterns.md` | ScalarDB Java patterns (entities, VOs, repositories, transactions) |
| `.claude/rules/scalardb-edition-profiles.md` | ScalarDB 3-edition comparison (OSS / Standard / Premium) |
| `.claude/rules/spring-boot-integration.md` | Spring Boot + ScalarDB integration |
| `.claude/rules/mermaid-best-practices.md` | Mermaid diagram rules (required for 15+ skills that output diagrams) |
| `.claude/templates/` | Output templates, error handling patterns, skill creation guide |
| `scripts/*.py` | Python utilities (graph build/query/visualize, report compile, Nextra convert) |
| `.claude/skills/mmi-analyzer/scripts/*.py` | MMI automated analysis scripts |

## ScalarDB Integration

Skills support 3 ScalarDB editions (OSS / Enterprise Standard / Enterprise Premium). Use `/select-scalardb-edition` for interactive edition selection. Edition config is stored in `work/{project}/scalardb-edition-config.md` and consumed by downstream design/code-gen skills.

See `.claude/rules/scalardb-edition-profiles.md` for edition comparison and `.claude/rules/scalardb-coding-patterns.md` for implementation patterns.

## Modifying Skills

### Edit an existing skill
1. Edit `.claude/skills/{skill-name}/SKILL.md`
2. Test with a sample project: `/skill-name ./SampleCode/project`
3. Commit only the SKILL.md changes (output files are git-ignored)

### Create a new skill
1. See `.claude/templates/skill-creation-guide.md` for the template
2. Create `.claude/skills/{new-skill}/SKILL.md`
3. Register in progress-registry if it's a pipeline phase

### Key conventions for skill development
- Skills use Task tool sub-agents following `.claude/skills/common/sub-agent-patterns.md`
- Mermaid diagrams must follow `.claude/rules/mermaid-best-practices.md` (Japanese text in double quotes, subgraph names quoted, node IDs alphanumeric only)
- Output files immediately after each step (not batched at end) for interrupt resilience
- Include YAML frontmatter in output files (title, phase, skill, generated_at, input_files)

## Git Workflow

Generated outputs are NOT committed:
- `reports/`, `work/`, `workspace/`, `generated/`, `knowledge.ryugraph`, `SampleCode/` - All git-ignored

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
