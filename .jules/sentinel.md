## 2026-01-27 - Unprotected Administrative Routes
**Vulnerability:** Sensitive moderation endpoints (`/moderation`, `/moderation/.../resolve`) were exposed publicly without authentication in `app.py`.
**Learning:** Redundant route definitions in `app.py` bypassed security controls implemented in Blueprints (`routes/admin.py`). Code duplication led to a "shadow" API that was insecure.
**Prevention:** Centralize route definitions. Ensure all routes, especially sensitive ones, are defined within Blueprints with appropriate `url_prefix` and decorators. Audit `app.py` to ensure it only contains app initialization and truly global/public routes.
