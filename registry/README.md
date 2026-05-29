# Registry

Machine-readable configuration for the Xerago Intelligence Engine.

| File | Schema | Documentation |
|------|--------|---------------|
| [`sources.yaml`](sources.yaml) | [`schemas/sources.schema.json`](schemas/sources.schema.json) | [`docs/sources.md`](../docs/sources.md) |
| [`repos.yaml`](repos.yaml) | [`schemas/repos.schema.json`](schemas/repos.schema.json) | [`docs/repository_tracking_strategy.md`](../docs/repository_tracking_strategy.md) |

## Validation

Validate YAML against JSON Schema using any compatible tool, for example:

```bash
# npx (Node.js)
npx ajv-cli validate -s registry/schemas/sources.schema.json -d registry/sources.yaml --spec=draft2020
npx ajv-cli validate -s registry/schemas/repos.schema.json -d registry/repos.yaml --spec=draft2020
```

```bash
# check-jsonschema (Python)
check-jsonschema --schemafile registry/schemas/sources.schema.json registry/sources.yaml
check-jsonschema --schemafile registry/schemas/repos.schema.json registry/repos.yaml
```

## Conventions

- **IDs:** `source_id` and entity `slug` use kebab-case; `repo_id` uses lowercase `org/repo`.
- **Cadence:** ISO 8601 durations (`PT4H`) or `cron:` expressions.
- **Trust:** T3 sources cannot originate standalone strategic signals.
- **OSS:** Version ledger prevents re-surfacing the same release (see `repos.yaml` tier policies).
- **Database:** MySQL 8.0+ — see `db/schema/001_initial.sql`.

## Governance

Changes require registry commit alongside updates to the corresponding `docs/*.md` file.
