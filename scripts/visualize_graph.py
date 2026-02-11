#!/usr/bin/env python3
"""
GraphDB可視化スクリプト

RyuGraphデータベースの内容をMermaid/DOT/HTML形式で可視化します。

使用方法:
    python3 visualize_graph.py --db-path ./knowledge.ryugraph --output-dir ./visualizations

前提条件:
    pip install ryugraph pandas
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

try:
    import pandas as pd
except ImportError:
    print("Error: pandas is not installed. Run: pip install pandas")
    sys.exit(1)


ALL_CSV_FILES = [
    # Nodes
    'terms.csv', 'domains.csv', 'entities.csv', 'methods.csv', 'files.csv',
    'actors.csv', 'roles.csv', 'business_processes.csv', 'activities.csv',
    'system_processes.csv',
    # Relationships
    'belongs_to.csv', 'defined_in.csv', 'method_defined_in.csv',
    'references.csv', 'calls.csv', 'implements.csv',
    'has_term.csv', 'method_has_term.csv', 'has_role.csv',
    'has_activity.csv', 'next_activity.csv', 'performs.csv',
    'triggers.csv', 'invokes.csv', 'participates_in.csv',
    'compensates.csv',
]


def load_csv_data(data_dir: str) -> dict:
    """CSVファイルからデータを読み込む"""
    data_path = Path(data_dir)
    data = {}

    for csv_file in ALL_CSV_FILES:
        csv_path = data_path / csv_file
        key = csv_file.replace('.csv', '')
        if csv_path.exists():
            df = pd.read_csv(csv_path)
            data[key] = df
            print(f"  Loaded: {csv_file} ({len(df)} rows)")
        else:
            data[key] = pd.DataFrame()

    return data


def safe_id(name: str) -> str:
    """Mermaid/DOT用の安全なID文字列に変換"""
    return name.replace(" ", "_").replace("-", "_").replace(".", "_").replace("/", "_")


def quote_ja(text: str) -> str:
    """日本語テキストをダブルクオートで囲む"""
    return f'"{text}"'


# ==============================================================================
# Mermaid: 全体グラフ
# ==============================================================================

def generate_mermaid_full(data: dict, output_path: str, layout: str = "LR"):
    """全体構造のMermaidグラフを生成"""
    domains = data.get('domains', pd.DataFrame())
    entities = data.get('entities', pd.DataFrame())
    belongs_to = data.get('belongs_to', pd.DataFrame())
    references = data.get('references', pd.DataFrame())
    implements_df = data.get('implements', pd.DataFrame())

    # ドメイン→エンティティのマッピング
    domain_entities = defaultdict(list)
    for _, row in belongs_to.iterrows():
        domain_entities[row['domain']].append(row['entity'])

    lines = [f"graph {layout}"]

    # ドメインサブグラフ
    for _, domain in domains.iterrows():
        dname = domain['name']
        dtype = domain.get('type', 'Unknown')
        sid = safe_id(dname)
        lines.append(f'    subgraph {sid}["{dname}<br/>{dtype}"]')
        for ent in domain_entities.get(dname, []):
            eid = safe_id(ent)
            etype = ""
            if not entities.empty:
                match = entities[entities['name'] == ent]
                if not match.empty:
                    etype = match.iloc[0].get('type', '')
            label = f"{ent}" + (f"<br/>({etype})" if etype else "")
            lines.append(f'        {eid}["{label}"]')
        lines.append('    end')
        lines.append('')

    # エンティティ参照
    for _, row in references.iterrows():
        src = safe_id(row['source'])
        tgt = safe_id(row['target'])
        lines.append(f'    {src} -->|"references"| {tgt}')

    # implements
    for _, row in implements_df.iterrows():
        child = safe_id(row['child'])
        parent = safe_id(row['parent'])
        lines.append(f'    {child} -.->|"implements"| {parent}')

    # スタイリング
    lines.append('')
    lines.append('    classDef aggRoot fill:#e74c3c,stroke:#c0392b,color:white')
    lines.append('    classDef entity fill:#3498db,stroke:#2980b9,color:white')
    lines.append('    classDef vo fill:#2ecc71,stroke:#27ae60,color:white')
    lines.append('    classDef repo fill:#9b59b6,stroke:#8e44ad,color:white')
    lines.append('    classDef service fill:#f39c12,stroke:#e67e22,color:white')
    lines.append('    classDef controller fill:#1abc9c,stroke:#16a085,color:white')
    lines.append('    classDef infra fill:#95a5a6,stroke:#7f8c8d,color:white')

    if not entities.empty:
        type_class_map = {
            'AggregateRoot': 'aggRoot', 'Entity': 'entity', 'ValueObject': 'vo',
            'RepositoryInterface': 'repo', 'DomainService': 'service',
            'ApplicationService': 'service', 'Controller': 'controller',
            'RepositoryImplementation': 'infra',
        }
        for _, ent in entities.iterrows():
            etype = ent.get('type', '')
            cls = type_class_map.get(etype)
            if cls:
                lines.append(f'    class {safe_id(ent["name"])} {cls}')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"  Generated: {output_path}")


# ==============================================================================
# Mermaid: ドメイン別
# ==============================================================================

def generate_mermaid_domain(data: dict, output_dir: Path):
    """ドメイン別のMermaidグラフを生成"""
    domains = data.get('domains', pd.DataFrame())
    entities = data.get('entities', pd.DataFrame())
    belongs_to = data.get('belongs_to', pd.DataFrame())
    has_term = data.get('has_term', pd.DataFrame())
    terms = data.get('terms', pd.DataFrame())
    references = data.get('references', pd.DataFrame())

    for _, domain in domains.iterrows():
        dname = domain['name']
        desc = domain.get('description', '')

        # このドメインのエンティティ
        domain_ents = set(belongs_to[belongs_to['domain'] == dname]['entity'].tolist()) if not belongs_to.empty else set()
        if not domain_ents:
            continue

        lines = [f'graph TB']
        lines.append(f'    subgraph domain["{dname}<br/>{desc}"]')

        for ent in domain_ents:
            eid = safe_id(ent)
            etype = ""
            if not entities.empty:
                match = entities[entities['name'] == ent]
                if not match.empty:
                    etype = match.iloc[0].get('type', '')
            lines.append(f'        {eid}["{ent}<br/>({etype})"]')

        lines.append('    end')
        lines.append('')

        # エンティティ間参照（ドメイン内）
        for _, row in references.iterrows():
            if row['source'] in domain_ents or row['target'] in domain_ents:
                src = safe_id(row['source'])
                tgt = safe_id(row['target'])
                lines.append(f'    {src} -->|"references"| {tgt}')

        # 関連する用語
        domain_terms = set()
        for ent in domain_ents:
            ent_terms = has_term[has_term['entity'] == ent]['term'].tolist() if not has_term.empty else []
            domain_terms.update(ent_terms)

        if domain_terms:
            lines.append('')
            lines.append(f'    subgraph terms["{dname} - ユビキタス言語"]')
            for t in list(domain_terms)[:15]:
                tid = safe_id(f"term_{t}")
                name_ja = ""
                if not terms.empty:
                    match = terms[terms['name'] == t]
                    if not match.empty:
                        name_ja = match.iloc[0].get('name_ja', '')
                label = f"{t}" + (f"<br/>({name_ja})" if name_ja else "")
                lines.append(f'        {tid}["{label}"]')
            lines.append('    end')

            # 用語-エンティティ関連
            for ent in domain_ents:
                ent_terms = has_term[has_term['entity'] == ent]['term'].tolist() if not has_term.empty else []
                for t in ent_terms:
                    if t in domain_terms:
                        lines.append(f'    {safe_id(ent)} -.->|"has_term"| {safe_id(f"term_{t}")}')

        lines.append('')
        lines.append('    classDef aggRoot fill:#e74c3c,stroke:#c0392b,color:white')
        lines.append('    classDef entity fill:#3498db,stroke:#2980b9,color:white')
        lines.append('    classDef term fill:#2ecc71,stroke:#27ae60,color:white')

        for ent in domain_ents:
            if not entities.empty:
                match = entities[entities['name'] == ent]
                if not match.empty and match.iloc[0].get('type', '') == 'AggregateRoot':
                    lines.append(f'    class {safe_id(ent)} aggRoot')
                else:
                    lines.append(f'    class {safe_id(ent)} entity')

        for t in domain_terms:
            lines.append(f'    class {safe_id(f"term_{t}")} term')

        fname = f"domain-{safe_id(dname).lower()}.mmd"
        with open(output_dir / fname, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        print(f"  Generated: {output_dir / fname}")


# ==============================================================================
# Mermaid: ビジネスプロセスフロー
# ==============================================================================

def generate_process_flows(data: dict, output_dir: Path):
    """ビジネスプロセスのフローチャートを生成"""
    bp = data.get('business_processes', pd.DataFrame())
    activities = data.get('activities', pd.DataFrame())
    has_activity = data.get('has_activity', pd.DataFrame())
    next_activity_df = data.get('next_activity', pd.DataFrame())
    performs = data.get('performs', pd.DataFrame())
    triggers = data.get('triggers', pd.DataFrame())

    proc_dir = output_dir / "processes"
    proc_dir.mkdir(parents=True, exist_ok=True)

    if bp.empty:
        return

    for _, proc in bp.iterrows():
        pname = proc['name']
        pname_ja = proc.get('name_ja', pname)
        pdesc = proc.get('description', '')

        # このプロセスのアクティビティ
        proc_acts = has_activity[has_activity['process'] == pname]['activity'].tolist() if not has_activity.empty else []
        if not proc_acts:
            continue

        lines = ['flowchart TD']
        lines.append(f'    subgraph proc["{pname_ja}"]')

        # アクティビティノード
        for act_name in proc_acts:
            aid = safe_id(act_name)
            act_ja = act_name
            is_decision = False
            if not activities.empty:
                match = activities[activities['name'] == act_name]
                if not match.empty:
                    act_ja = match.iloc[0].get('name_ja', act_name)
                    is_decision = str(match.iloc[0].get('is_decision', 'false')).lower() == 'true'
            if is_decision:
                lines.append(f'        {aid}{{{{{quote_ja(act_ja)}}}}}')
            else:
                lines.append(f'        {aid}[{quote_ja(act_ja)}]')

        lines.append('    end')

        # アクティビティ遷移
        for _, row in next_activity_df.iterrows():
            if row['from_activity'] in proc_acts:
                fid = safe_id(row['from_activity'])
                tid = safe_id(row['to_activity'])
                cond = row.get('condition', '')
                if pd.notna(cond) and str(cond).strip():
                    lines.append(f'    {fid} -->|{quote_ja(str(cond))}| {tid}')
                else:
                    lines.append(f'    {fid} --> {tid}')

        # アクター
        actors_set = set()
        for act_name in proc_acts:
            act_actors = performs[performs['activity'] == act_name]['actor'].tolist() if not performs.empty else []
            actors_set.update(act_actors)

        for actor in actors_set:
            actor_id = safe_id(f"actor_{actor}")
            lines.append(f'    {actor_id}(("{actor}"))')
            # アクターが実行するアクティビティへのリンク
            actor_acts = performs[performs['actor'] == actor]['activity'].tolist() if not performs.empty else []
            for act_name in actor_acts:
                if act_name in proc_acts:
                    lines.append(f'    {actor_id} -.->|"performs"| {safe_id(act_name)}')

        # システムプロセストリガー
        for act_name in proc_acts:
            triggered = triggers[triggers['activity'] == act_name] if not triggers.empty else pd.DataFrame()
            for _, tr in triggered.iterrows():
                sp_name = tr['system_process']
                sp_id = safe_id(f"sp_{sp_name}")
                event = tr.get('event_name', '')
                lines.append(f'    {sp_id}[/"{sp_name}"/]')
                label = f'"{event}"' if pd.notna(event) and str(event).strip() else '"triggers"'
                lines.append(f'    {safe_id(act_name)} ==>|{label}| {sp_id}')

        lines.append('')
        lines.append('    classDef decision fill:#f39c12,stroke:#e67e22,color:white')
        lines.append('    classDef actor fill:#9b59b6,stroke:#8e44ad,color:white')
        lines.append('    classDef sysProc fill:#1abc9c,stroke:#16a085,color:white')

        # Apply styles
        for act_name in proc_acts:
            if not activities.empty:
                match = activities[activities['name'] == act_name]
                if not match.empty and str(match.iloc[0].get('is_decision', 'false')).lower() == 'true':
                    lines.append(f'    class {safe_id(act_name)} decision')
        for actor in actors_set:
            lines.append(f'    class {safe_id(f"actor_{actor}")} actor')

        fname = f"{safe_id(pname).lower()}-flow.mmd"
        with open(proc_dir / fname, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        print(f"  Generated: {proc_dir / fname}")

    # ビジネスプロセス一覧図
    lines = ['graph LR']
    for _, proc in bp.iterrows():
        pname = proc['name']
        pname_ja = proc.get('name_ja', pname)
        pdomain = proc.get('domain', '')
        pid = safe_id(pname)
        lines.append(f'    {pid}["{pname_ja}<br/>({pdomain})"]')

    # プロセス間の共有エンティティを通じた関連
    participates = data.get('participates_in', pd.DataFrame())
    if not participates.empty:
        proc_entities = defaultdict(set)
        for _, row in participates.iterrows():
            proc_entities[row['process']].add(row['entity'])
        procs = list(proc_entities.keys())
        for i in range(len(procs)):
            for j in range(i+1, len(procs)):
                shared = proc_entities[procs[i]] & proc_entities[procs[j]]
                if shared:
                    lines.append(f'    {safe_id(procs[i])} <-->|"{", ".join(shared)}"| {safe_id(procs[j])}')

    with open(proc_dir / "business-processes.mmd", 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"  Generated: {proc_dir / 'business-processes.mmd'}")


# ==============================================================================
# Mermaid: システムプロセス（Saga）シーケンス図
# ==============================================================================

def generate_system_process_diagrams(data: dict, output_dir: Path):
    """システムプロセスのシーケンス図を生成"""
    sp = data.get('system_processes', pd.DataFrame())
    sp_invokes = data.get('invokes', pd.DataFrame())
    triggers = data.get('triggers', pd.DataFrame())

    proc_dir = output_dir / "processes"
    proc_dir.mkdir(parents=True, exist_ok=True)

    if sp.empty:
        return

    lines = ['sequenceDiagram']

    # パーティシパント
    for _, proc in sp.iterrows():
        pname = proc['name']
        ptype = proc.get('type', 'sync')
        lines.append(f'    participant {safe_id(pname)} as "{pname}<br/>({ptype})"')

    lines.append('')

    # トリガーとメソッド呼び出し
    for _, proc in sp.iterrows():
        pname = proc['name']
        pid = safe_id(pname)

        # トリガーアクティビティ
        triggered_by = triggers[triggers['system_process'] == pname] if not triggers.empty else pd.DataFrame()
        for _, tr in triggered_by.iterrows():
            event = tr.get('event_name', 'trigger')
            lines.append(f'    Note over {pid}: "{event}"')

        # 呼び出すメソッド
        invoked = sp_invokes[sp_invokes['source'] == pname] if not sp_invokes.empty else pd.DataFrame()
        # 他のシステムプロセスへの連携があれば矢印
        for _, inv in invoked.iterrows():
            method = inv['method']
            # メソッドのクラス名を抽出
            class_name = method.split('.')[0] if '.' in method else method
            lines.append(f'    {pid} ->> {pid}: "{method}"')

    with open(proc_dir / "system-processes.mmd", 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"  Generated: {proc_dir / 'system-processes.mmd'}")


# ==============================================================================
# Mermaid: アクター-アクティビティマップ
# ==============================================================================

def generate_actor_maps(data: dict, output_dir: Path):
    """アクター-アクティビティマップを生成"""
    actors = data.get('actors', pd.DataFrame())
    roles = data.get('roles', pd.DataFrame())
    has_role = data.get('has_role', pd.DataFrame())
    performs = data.get('performs', pd.DataFrame())
    activities = data.get('activities', pd.DataFrame())

    actor_dir = output_dir / "actors"
    actor_dir.mkdir(parents=True, exist_ok=True)

    if actors.empty:
        return

    # アクター-アクティビティマップ（Mermaid）
    lines = ['graph TB']

    for _, actor in actors.iterrows():
        aname = actor['name']
        atype = actor.get('type', 'Unknown')
        aid = safe_id(f"actor_{aname}")
        lines.append(f'    {aid}(("{aname}<br/>({atype})"))')

        # ロール
        actor_roles = has_role[has_role['actor'] == aname]['role'].tolist() if not has_role.empty else []
        for role in actor_roles:
            rid = safe_id(f"role_{role}")
            lines.append(f'    {rid}[/"{role}"/]')
            lines.append(f'    {aid} --> {rid}')

        # 実行するアクティビティ
        actor_acts = performs[performs['actor'] == aname]['activity'].tolist() if not performs.empty else []
        for act in actor_acts:
            act_id = safe_id(f"act_{act}")
            act_ja = act
            if not activities.empty:
                match = activities[activities['name'] == act]
                if not match.empty:
                    act_ja = match.iloc[0].get('name_ja', act)
            lines.append(f'    {act_id}["{act_ja}"]')
            lines.append(f'    {aid} -.->|"performs"| {act_id}')

    lines.append('')
    lines.append('    classDef actor fill:#9b59b6,stroke:#8e44ad,color:white')
    lines.append('    classDef role fill:#e67e22,stroke:#d35400,color:white')
    lines.append('    classDef activity fill:#3498db,stroke:#2980b9,color:white')

    for _, actor in actors.iterrows():
        lines.append(f'    class {safe_id(f"actor_{actor["name"]}")} actor')
    for _, row in has_role.iterrows():
        lines.append(f'    class {safe_id(f"role_{row["role"]}")} role')
    if not performs.empty:
        for act in performs['activity'].unique():
            lines.append(f'    class {safe_id(f"act_{act}")} activity')

    with open(actor_dir / "actor-activity-map.mmd", 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"  Generated: {actor_dir / 'actor-activity-map.mmd'}")

    # ロール-プロセスマトリクス（Markdown）
    bp = data.get('business_processes', pd.DataFrame())
    has_activity = data.get('has_activity', pd.DataFrame())

    md_lines = [
        "# ロール-プロセスマトリクス",
        "",
        f"**生成日時**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
    ]

    if not bp.empty and not performs.empty:
        procs = bp['name'].tolist()
        actor_names = actors['name'].tolist()

        # ヘッダー
        header = "| アクター |"
        sep = "|--------|"
        for p in procs:
            pja = bp[bp['name'] == p].iloc[0].get('name_ja', p) if not bp.empty else p
            header += f" {pja} |"
            sep += "------|"
        md_lines.append(header)
        md_lines.append(sep)

        for aname in actor_names:
            actor_acts = set(performs[performs['actor'] == aname]['activity'].tolist())
            row = f"| {aname} |"
            for p in procs:
                proc_acts = set(has_activity[has_activity['process'] == p]['activity'].tolist()) if not has_activity.empty else set()
                shared = actor_acts & proc_acts
                row += f" {'Yes (' + str(len(shared)) + ')' if shared else '-'} |"
            md_lines.append(row)

    with open(actor_dir / "role-process-matrix.md", 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_lines))
    print(f"  Generated: {actor_dir / 'role-process-matrix.md'}")


# ==============================================================================
# Mermaid: メソッド呼び出しグラフ
# ==============================================================================

def generate_call_graph(data: dict, output_path: str):
    """メソッド呼び出しグラフのMermaid図を生成"""
    calls = data.get('calls', pd.DataFrame())
    methods = data.get('methods', pd.DataFrame())

    if calls.empty:
        return

    lines = ['graph LR']

    # クラスごとにグループ化
    class_methods = defaultdict(set)
    all_methods_in_calls = set()

    for _, row in calls.iterrows():
        caller = row['caller']
        callee = row['callee']
        all_methods_in_calls.add(caller)
        all_methods_in_calls.add(callee)
        caller_class = caller.split('.')[0] if '.' in caller else caller
        callee_class = callee.split('.')[0] if '.' in callee else callee
        class_methods[caller_class].add(caller)
        class_methods[callee_class].add(callee)

    for cls, meths in class_methods.items():
        cid = safe_id(cls)
        lines.append(f'    subgraph {cid}["{cls}"]')
        for m in meths:
            mid = safe_id(m)
            method_name = m.split('.')[-1] if '.' in m else m
            lines.append(f'        {mid}["{method_name}"]')
        lines.append('    end')
        lines.append('')

    for _, row in calls.iterrows():
        caller_id = safe_id(row['caller'])
        callee_id = safe_id(row['callee'])
        lines.append(f'    {caller_id} --> {callee_id}')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"  Generated: {output_path}")


# ==============================================================================
# DOT形式
# ==============================================================================

def generate_dot(data: dict, output_path: str, domain_filter: str = None):
    """DOT形式のグラフを生成"""
    domains = data.get('domains', pd.DataFrame())
    entities = data.get('entities', pd.DataFrame())
    belongs_to = data.get('belongs_to', pd.DataFrame())
    references = data.get('references', pd.DataFrame())
    implements_df = data.get('implements', pd.DataFrame())
    terms = data.get('terms', pd.DataFrame())
    has_term = data.get('has_term', pd.DataFrame())

    if domain_filter:
        domains = domains[domains['name'] == domain_filter]
        if not belongs_to.empty:
            belongs_to = belongs_to[belongs_to['domain'] == domain_filter]

    domain_entities = defaultdict(list)
    for _, row in belongs_to.iterrows():
        domain_entities[row['domain']].append(row['entity'])

    colors = {
        'Core': 'lightcoral',
        'Supporting': 'lightblue',
        'Integration': 'lightgreen',
        'Generic': 'lightyellow',
    }

    type_shapes = {
        'AggregateRoot': 'doubleoctagon',
        'Entity': 'box',
        'ValueObject': 'ellipse',
        'RepositoryInterface': 'component',
        'DomainService': 'hexagon',
        'ApplicationService': 'hexagon',
        'Controller': 'parallelogram',
        'RepositoryImplementation': 'cylinder',
    }

    lines = ["digraph G {", "    rankdir=LR;", "    node [fontname=\"Helvetica\"];", ""]

    for _, domain in domains.iterrows():
        dname = domain['name']
        dtype = domain.get('type', 'Unknown')
        color = colors.get(dtype, 'lightyellow')

        lines.append(f"    subgraph cluster_{safe_id(dname)} {{")
        lines.append(f'        label="{dname} ({dtype})";')
        lines.append(f"        style=filled;")
        lines.append(f"        fillcolor={color};")
        lines.append("")

        for ent in domain_entities.get(dname, []):
            etype = ""
            if not entities.empty:
                match = entities[entities['name'] == ent]
                if not match.empty:
                    etype = match.iloc[0].get('type', '')
            shape = type_shapes.get(etype, 'box')
            lines.append(f'        {safe_id(ent)} [label="{ent}\\n({etype})" shape={shape}];')

        lines.append("    }")
        lines.append("")

    # References
    if not references.empty:
        lines.append("    // References")
        for _, row in references.iterrows():
            src = safe_id(row['source'])
            tgt = safe_id(row['target'])
            lines.append(f'    {src} -> {tgt} [label="references" style=solid];')

    # Implements
    if not implements_df.empty:
        lines.append("    // Implements")
        for _, row in implements_df.iterrows():
            child = safe_id(row['child'])
            parent = safe_id(row['parent'])
            lines.append(f'    {child} -> {parent} [label="implements" style=dashed];')

    lines.append("}")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"  Generated: {output_path}")


# ==============================================================================
# インタラクティブHTML（D3.js）
# ==============================================================================

def generate_html(data: dict, output_path: str, domain_filter: str = None):
    """インタラクティブHTML（D3.js）を生成"""
    domains = data.get('domains', pd.DataFrame())
    entities = data.get('entities', pd.DataFrame())
    belongs_to = data.get('belongs_to', pd.DataFrame())
    references = data.get('references', pd.DataFrame())
    implements_df = data.get('implements', pd.DataFrame())
    terms = data.get('terms', pd.DataFrame())
    has_term = data.get('has_term', pd.DataFrame())
    actors = data.get('actors', pd.DataFrame())
    methods = data.get('methods', pd.DataFrame())
    calls = data.get('calls', pd.DataFrame())
    bp = data.get('business_processes', pd.DataFrame())
    activities = data.get('activities', pd.DataFrame())
    sp = data.get('system_processes', pd.DataFrame())

    if domain_filter:
        domains = domains[domains['name'] == domain_filter]
        if not belongs_to.empty:
            belongs_to = belongs_to[belongs_to['domain'] == domain_filter]

    nodes = []
    links = []
    node_ids = {}
    node_idx = 0

    def add_node(name, ntype, group="", extra=None):
        nonlocal node_idx
        if name in node_ids:
            return node_ids[name]
        nid = node_idx
        node_ids[name] = nid
        node_idx += 1
        node = {"id": nid, "name": name, "type": ntype, "group": group}
        if extra:
            node.update(extra)
        nodes.append(node)
        return nid

    def add_link(source_name, target_name, rel_type):
        src = node_ids.get(source_name)
        tgt = node_ids.get(target_name)
        if src is not None and tgt is not None:
            links.append({"source": src, "target": tgt, "type": rel_type})

    # ドメインノード
    for _, row in domains.iterrows():
        add_node(row['name'], "Domain", row.get('type', 'Unknown'))

    # エンティティノード
    domain_ents = set(belongs_to['entity'].tolist()) if not belongs_to.empty else set()
    for _, row in entities.iterrows():
        if domain_filter and row['name'] not in domain_ents:
            continue
        add_node(row['name'], "Entity", row.get('type', 'class'))

    # 用語ノード（上位20件のみ）
    for _, row in terms.head(20).iterrows():
        name_ja = row.get('name_ja', '')
        add_node(row['name'], "Term", row.get('domain', ''),
                 {"name_ja": name_ja})

    # アクターノード
    for _, row in actors.iterrows():
        add_node(row['name'], "Actor", row.get('type', 'Unknown'))

    # ビジネスプロセスノード
    for _, row in bp.iterrows():
        add_node(row['name'], "BusinessProcess", row.get('domain', ''),
                 {"name_ja": row.get('name_ja', '')})

    # システムプロセスノード
    for _, row in sp.iterrows():
        add_node(row['name'], "SystemProcess", row.get('type', 'sync'))

    # BELONGS_TO
    for _, row in belongs_to.iterrows():
        add_link(row['entity'], row['domain'], "BELONGS_TO")

    # REFERENCES
    for _, row in references.iterrows():
        add_link(row['source'], row['target'], "REFERENCES")

    # IMPLEMENTS
    for _, row in implements_df.iterrows():
        add_link(row['child'], row['parent'], "IMPLEMENTS")

    # HAS_TERM (subset)
    for _, row in has_term.head(30).iterrows():
        add_link(row['entity'], row['term'], "HAS_TERM")

    # PARTICIPATES_IN
    participates = data.get('participates_in', pd.DataFrame())
    for _, row in participates.iterrows():
        add_link(row['entity'], row['process'], "PARTICIPATES_IN")

    html_content = f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="utf-8">
    <title>Knowledge Graph - SampleCode</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #0a0a1a; overflow: hidden; }}
        #graph {{ width: 100vw; height: 100vh; }}
        .link {{ stroke-opacity: 0.4; }}
        .link:hover {{ stroke-opacity: 1; stroke-width: 3px !important; }}
        .node text {{ font-size: 11px; fill: #e0e0e0; pointer-events: none; }}
        .node:hover circle, .node:hover rect {{ filter: brightness(1.4); }}
        #controls {{
            position: fixed; top: 12px; left: 12px; background: rgba(20,20,40,0.95);
            padding: 16px; border-radius: 10px; z-index: 100; color: #ccc;
            border: 1px solid rgba(255,255,255,0.1); min-width: 260px;
        }}
        #controls h3 {{ color: #fff; margin-bottom: 10px; font-size: 14px; }}
        #search {{
            width: 100%; padding: 8px 12px; border: 1px solid #444; border-radius: 6px;
            background: #1a1a2e; color: #fff; font-size: 13px; margin-bottom: 8px;
        }}
        #search::placeholder {{ color: #666; }}
        #stats {{ font-size: 11px; color: #888; margin-bottom: 8px; }}
        .legend {{ display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }}
        .legend-item {{
            display: flex; align-items: center; gap: 4px; font-size: 10px;
            padding: 2px 8px; border-radius: 10px; background: rgba(255,255,255,0.05);
        }}
        .legend-dot {{ width: 10px; height: 10px; border-radius: 50%; }}
        .tooltip {{
            position: absolute; background: rgba(0,0,0,0.9); color: #fff;
            padding: 10px 14px; border-radius: 8px; font-size: 12px;
            pointer-events: none; max-width: 300px; border: 1px solid rgba(255,255,255,0.15);
        }}
        #filter-buttons {{ margin-top: 8px; display: flex; flex-wrap: wrap; gap: 4px; }}
        .filter-btn {{
            font-size: 10px; padding: 3px 8px; border: 1px solid #555; border-radius: 4px;
            background: transparent; color: #aaa; cursor: pointer;
        }}
        .filter-btn.active {{ background: #3498db; color: #fff; border-color: #3498db; }}
    </style>
</head>
<body>
    <div id="controls">
        <h3>Knowledge Graph Explorer</h3>
        <input type="text" id="search" placeholder="Search nodes...">
        <div id="stats"></div>
        <div id="filter-buttons"></div>
        <div class="legend" id="legend"></div>
    </div>
    <div id="graph"></div>
    <script>
        const rawData = {json.dumps({"nodes": nodes, "links": links}, ensure_ascii=False)};

        const typeColors = {{
            "Domain": "#e74c3c",
            "Entity": "#3498db",
            "Term": "#2ecc71",
            "Actor": "#9b59b6",
            "BusinessProcess": "#f39c12",
            "SystemProcess": "#1abc9c",
            "Method": "#e67e22"
        }};

        const typeSizes = {{
            "Domain": 18,
            "Entity": 12,
            "Term": 8,
            "Actor": 14,
            "BusinessProcess": 16,
            "SystemProcess": 12,
            "Method": 6
        }};

        const linkColors = {{
            "BELONGS_TO": "#e74c3c",
            "REFERENCES": "#3498db",
            "IMPLEMENTS": "#9b59b6",
            "HAS_TERM": "#2ecc71",
            "PARTICIPATES_IN": "#f39c12",
            "CALLS": "#e67e22"
        }};

        const width = window.innerWidth;
        const height = window.innerHeight;

        const svg = d3.select("#graph").append("svg")
            .attr("width", width).attr("height", height);
        const g = svg.append("g");

        svg.call(d3.zoom().scaleExtent([0.05, 5])
            .on("zoom", (e) => g.attr("transform", e.transform)));

        const simulation = d3.forceSimulation(rawData.nodes)
            .force("link", d3.forceLink(rawData.links).id(d => d.id).distance(80))
            .force("charge", d3.forceManyBody().strength(-200))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collision", d3.forceCollide().radius(d => (typeSizes[d.type] || 10) + 5));

        const link = g.append("g").selectAll("line").data(rawData.links).join("line")
            .attr("class", "link")
            .attr("stroke", d => linkColors[d.type] || "#555")
            .attr("stroke-width", 1.2);

        const node = g.append("g").selectAll("g").data(rawData.nodes).join("g")
            .attr("class", "node")
            .call(d3.drag()
                .on("start", (e) => {{ if (!e.active) simulation.alphaTarget(0.3).restart(); e.subject.fx = e.subject.x; e.subject.fy = e.subject.y; }})
                .on("drag", (e) => {{ e.subject.fx = e.x; e.subject.fy = e.y; }})
                .on("end", (e) => {{ if (!e.active) simulation.alphaTarget(0); e.subject.fx = null; e.subject.fy = null; }}));

        node.append("circle")
            .attr("r", d => typeSizes[d.type] || 10)
            .attr("fill", d => typeColors[d.type] || "#666")
            .attr("stroke", "rgba(255,255,255,0.2)")
            .attr("stroke-width", 1.5);

        node.append("text").attr("dx", d => (typeSizes[d.type] || 10) + 4).attr("dy", 4)
            .text(d => d.name.length > 25 ? d.name.substring(0, 25) + "..." : d.name);

        const tooltip = d3.select("body").append("div").attr("class", "tooltip").style("opacity", 0);

        node.on("mouseover", (e, d) => {{
            tooltip.transition().duration(150).style("opacity", 1);
            let html = `<strong>${{d.name}}</strong><br/>Type: ${{d.type}}<br/>Group: ${{d.group}}`;
            if (d.name_ja) html += `<br/>日本語: ${{d.name_ja}}`;
            tooltip.html(html).style("left", (e.pageX + 12) + "px").style("top", (e.pageY - 12) + "px");
        }}).on("mouseout", () => tooltip.transition().duration(300).style("opacity", 0));

        simulation.on("tick", () => {{
            link.attr("x1", d => d.source.x).attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
            node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
        }});

        // Search
        d3.select("#search").on("input", function() {{
            const q = this.value.toLowerCase();
            if (!q) {{ node.style("opacity", 1); link.style("opacity", 0.4); return; }}
            const matched = new Set();
            rawData.nodes.forEach(n => {{ if (n.name.toLowerCase().includes(q) || (n.name_ja && n.name_ja.includes(q))) matched.add(n.id); }});
            node.style("opacity", d => matched.has(d.id) ? 1 : 0.1);
            link.style("opacity", d => (matched.has(d.source.id) || matched.has(d.target.id)) ? 0.6 : 0.05);
        }});

        // Filter buttons
        const types = [...new Set(rawData.nodes.map(n => n.type))];
        const activeFilters = new Set(types);
        const btnContainer = d3.select("#filter-buttons");
        types.forEach(t => {{
            btnContainer.append("button").attr("class", "filter-btn active")
                .style("border-color", typeColors[t] || "#555")
                .text(t + " (" + rawData.nodes.filter(n => n.type === t).length + ")")
                .on("click", function() {{
                    if (activeFilters.has(t)) activeFilters.delete(t); else activeFilters.add(t);
                    d3.select(this).classed("active", activeFilters.has(t));
                    node.style("display", d => activeFilters.has(d.type) ? null : "none");
                    link.style("display", d => {{
                        const sn = rawData.nodes[typeof d.source === 'object' ? d.source.id : d.source];
                        const tn = rawData.nodes[typeof d.target === 'object' ? d.target.id : d.target];
                        return (sn && activeFilters.has(sn.type) && tn && activeFilters.has(tn.type)) ? null : "none";
                    }});
                }});
        }});

        // Legend
        const legend = d3.select("#legend");
        Object.entries(typeColors).forEach(([t, c]) => {{
            const item = legend.append("div").attr("class", "legend-item");
            item.append("div").attr("class", "legend-dot").style("background", c);
            item.append("span").text(t);
        }});

        d3.select("#stats").html(`Nodes: ${{rawData.nodes.length}} | Links: ${{rawData.links.length}}`);
    </script>
</body>
</html>'''

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"  Generated: {output_path}")


# ==============================================================================
# サマリー
# ==============================================================================

def generate_summary(data: dict, output_path: str, output_dir: Path):
    """可視化サマリーを生成"""
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # ファイル一覧を収集
    files_generated = []
    for root, dirs, files in os.walk(output_dir):
        for f in sorted(files):
            rel = os.path.relpath(os.path.join(root, f), output_dir)
            files_generated.append(rel)

    lines = [
        "---",
        "title: GraphDB可視化サマリー",
        'phase: "Phase 12: Visualization"',
        "skill: visualize-graph",
        f"generated_at: {now}",
        "---",
        "",
        "# GraphDB可視化サマリー",
        "",
        f"**生成日時**: {now}",
        "",
        "## 統計情報",
        "",
        "| 項目 | 件数 |",
        "|------|------|",
    ]

    stats = [
        ("ドメイン", 'domains'), ("エンティティ", 'entities'), ("メソッド", 'methods'),
        ("ファイル", 'files'), ("用語", 'terms'), ("アクター", 'actors'),
        ("ロール", 'roles'), ("ビジネスプロセス", 'business_processes'),
        ("アクティビティ", 'activities'), ("システムプロセス", 'system_processes'),
    ]

    total_nodes = 0
    for label, key in stats:
        df = data.get(key, pd.DataFrame())
        count = len(df)
        total_nodes += count
        lines.append(f"| {label} | {count} |")
    lines.append(f"| **ノード合計** | **{total_nodes}** |")

    rel_stats = [
        ("BELONGS_TO", 'belongs_to'), ("DEFINED_IN", 'defined_in'),
        ("METHOD_DEFINED_IN", 'method_defined_in'), ("REFERENCES", 'references'),
        ("CALLS", 'calls'), ("IMPLEMENTS", 'implements'),
        ("HAS_TERM", 'has_term'), ("METHOD_HAS_TERM", 'method_has_term'),
        ("HAS_ROLE", 'has_role'), ("HAS_ACTIVITY", 'has_activity'),
        ("NEXT_ACTIVITY", 'next_activity'), ("PERFORMS", 'performs'),
        ("TRIGGERS", 'triggers'), ("INVOKES", 'invokes'),
        ("PARTICIPATES_IN", 'participates_in'), ("COMPENSATES", 'compensates'),
    ]

    lines.extend(["", "| リレーション | 件数 |", "|-------------|------|"])
    total_rels = 0
    for label, key in rel_stats:
        df = data.get(key, pd.DataFrame())
        count = len(df)
        total_rels += count
        if count > 0:
            lines.append(f"| {label} | {count} |")
    lines.append(f"| **リレーション合計** | **{total_rels}** |")

    lines.extend([
        "",
        "## 生成ファイル一覧",
        "",
        "| ファイル | 形式 | 用途 |",
        "|---------|------|------|",
    ])

    format_map = {
        '.mmd': ('Mermaid', 'ドキュメント埋め込み'),
        '.dot': ('DOT', 'Graphviz変換'),
        '.html': ('HTML', 'インタラクティブビュー'),
        '.md': ('Markdown', 'ドキュメント'),
        '.png': ('PNG', '画像'),
        '.svg': ('SVG', 'ベクター画像'),
    }

    for f in files_generated:
        ext = Path(f).suffix
        fmt, purpose = format_map.get(ext, ('Other', '-'))
        lines.append(f"| {f} | {fmt} | {purpose} |")

    lines.extend([
        "",
        "## 使用方法",
        "",
        "### HTMLインタラクティブビュー",
        "```bash",
        "open reports/graph/visualizations/graph.html  # macOS",
        "```",
        "",
        "### Mermaid → PNG変換",
        "```bash",
        "mmdc -i reports/graph/visualizations/graph.mmd -o reports/graph/visualizations/graph.png",
        "```",
        "",
        "### DOT → PNG変換（Graphviz）",
        "```bash",
        "dot -Tpng reports/graph/visualizations/graph.dot -o reports/graph/visualizations/graph-dot.png",
        "```",
        "",
    ])

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"  Generated: {output_path}")


# ==============================================================================
# Main
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description="Visualize GraphDB")
    parser.add_argument("--db-path", default="./knowledge.ryugraph",
                        help="Path to RyuGraph database")
    parser.add_argument("--data-dir", default="./reports/graph/data",
                        help="Path to CSV data directory")
    parser.add_argument("--output-dir", default="./reports/graph/visualizations",
                        help="Output directory for visualizations")
    parser.add_argument("--format", choices=["mermaid", "dot", "html", "all", "flowchart", "sequence"],
                        default="all", help="Output format")
    parser.add_argument("--domain", help="Filter by domain")
    parser.add_argument("--node-type", help="Filter by node type")
    parser.add_argument("--layout", choices=["LR", "TB", "RL", "BT"],
                        default="LR", help="Graph layout direction")
    args = parser.parse_args()

    print("=== GraphDB Visualization ===")
    print(f"Data directory: {args.data_dir}")
    print(f"Output directory: {args.output_dir}")
    print()

    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print("Loading data...")
    data = load_csv_data(args.data_dir)
    print()

    print("Generating visualizations...")

    if args.format in ["mermaid", "all"]:
        generate_mermaid_full(data, output_path / "graph.mmd", layout=args.layout)
        generate_mermaid_domain(data, output_path)
        generate_call_graph(data, output_path / "call-graph.mmd")

    if args.format in ["dot", "all"]:
        generate_dot(data, output_path / "graph.dot", domain_filter=args.domain)

    if args.format in ["html", "all"]:
        generate_html(data, output_path / "graph.html", domain_filter=args.domain)

    if args.format in ["flowchart", "all"]:
        generate_process_flows(data, output_path)
        generate_system_process_diagrams(data, output_path)

    if args.format in ["sequence", "all"]:
        generate_system_process_diagrams(data, output_path)

    # Actor maps (always when "all")
    if args.format == "all":
        generate_actor_maps(data, output_path)

    generate_summary(data, output_path / "summary.md", output_path)

    print()
    print("=== Visualization Complete ===")
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()
