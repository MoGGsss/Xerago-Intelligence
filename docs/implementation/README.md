# MVP Implementation Planning

Staff-level implementation plan for the Xerago Intelligence Engine MVP.

**North star pipeline:**

```
Article → Summary → Why It Matters → Strategic Score → MySQL → REST API → (post-MVP) Next.js
```

| Document | Contents |
|----------|----------|
| [project-structure.md](project-structure.md) | Final repository layout and module ownership |
| [service-boundaries.md](service-boundaries.md) | Processes, contracts, queues, failure modes |
| [mvp-implementation-order.md](mvp-implementation-order.md) | Sprint-by-sprint build sequence |
| [../../db/schema/001_initial.sql](../../db/schema/001_initial.sql) | MySQL 8.0+ DDL (MVP) |

**Constraints:** local-first, FreshRSS ingestion, **Python** processing (Celery), local/company LLM, **MySQL**, FastAPI (read-only). **Integration target:** Next.js + React + TypeScript (company platform, post-MVP).

**Out of scope for this plan:** application Python/TS source code (implemented incrementally per `mvp-implementation-order.md`).
