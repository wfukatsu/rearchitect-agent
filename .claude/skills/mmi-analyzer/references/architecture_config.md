# アーキテクチャ設定ガイド

Architecture Analyzer (Tool 2) はターゲットアーキテクチャの定義を `architecture.json` で受け取る。
設定なしでもデフォルトのクリーンアーキテクチャ構造で解析するが、
プロジェクト固有のアーキテクチャを正確に評価するには設定ファイルの作成を推奨する。

## 設定ファイル構造

```json
{
  "layers": ["presentation", "application", "domain", "infrastructure"],
  "layer_direction": "top_to_bottom",
  "domain_modules": ["order", "inventory", "customer", "payment"],
  "layer_keywords": {
    "api": "presentation",
    "views": "presentation",
    "services": "application",
    "domain": "domain",
    "models": "domain",
    "repositories": "infrastructure",
    "db": "infrastructure"
  },
  "pattern_keywords": {
    "Controller": "presentation",
    "Service": "application",
    "Repository": "infrastructure",
    "Entity": "domain",
    "UseCase": "application"
  }
}
```

## 各フィールドの説明

### layers
技術レイヤーの一覧。上位から下位の順に記述する。
デフォルト: `["presentation", "application", "domain", "infrastructure"]`

一般的なパターン:
- **クリーンアーキテクチャ**: `["presentation", "application", "domain", "infrastructure"]`
- **レイヤードアーキテクチャ**: `["ui", "service", "business", "data"]`
- **ヘキサゴナル**: `["adapters", "ports", "application", "domain"]`

### layer_direction
レイヤー間の許容される依存方向。`top_to_bottom` = 上位→下位のみ許容。

### domain_modules
ドメインモジュール（Bounded Context）の名称リスト。
空の場合、トップレベルディレクトリ名をドメインモジュールとして扱う。

### layer_keywords
ディレクトリ名→レイヤーのマッピング。プロジェクト固有のディレクトリ構造に合わせてカスタマイズする。

### pattern_keywords
クラス名に含まれるキーワード→パターンレイヤーのマッピング。
クラス名のサフィックス（例: `OrderService` → `Service` → `application`）で分類する。

## プロジェクト構造の例

### DDD + Clean Architecture

```
my_project/
├── order/                    # domain_module: order
│   ├── api/                  # layer: presentation
│   │   ├── controllers.py
│   │   └── serializers.py
│   ├── application/          # layer: application
│   │   ├── services.py
│   │   └── use_cases.py
│   ├── domain/               # layer: domain
│   │   ├── entities.py
│   │   └── value_objects.py
│   └── infrastructure/       # layer: infrastructure
│       ├── repositories.py
│       └── adapters.py
├── customer/                 # domain_module: customer
│   └── ...
└── shared/                   # 共有ユーティリティ
```

対応する設定:
```json
{
  "layers": ["api", "application", "domain", "infrastructure"],
  "domain_modules": ["order", "customer"],
  "layer_keywords": {
    "api": "presentation",
    "controllers": "presentation",
    "application": "application",
    "services": "application",
    "domain": "domain",
    "entities": "domain",
    "infrastructure": "infrastructure",
    "repositories": "infrastructure"
  }
}
```

### FastAPI プロジェクト

```
app/
├── routers/                  # presentation
├── schemas/                  # presentation
├── services/                 # application
├── models/                   # domain
├── repositories/             # infrastructure
└── database/                 # infrastructure
```

### Django プロジェクト

```
myproject/
├── orders/                   # domain_module
│   ├── views.py              # presentation
│   ├── serializers.py        # presentation
│   ├── services.py           # application
│   ├── models.py             # domain
│   └── repositories.py       # infrastructure
└── customers/                # domain_module
    └── ...
```
