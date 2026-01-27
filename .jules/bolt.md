## 2024-05-22 - Flask Context Processor N+1
**Learning:** Context processors run on every template render. Doing DB queries there without caching guarantees N+1 issues (1 query per page load). In this codebase, `inject_site_settings` was the culprit.
**Action:** Always check context processors for DB queries and cache them if the data is static/low-churn.
