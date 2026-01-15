# thekeystone.ai — Sitemap UX/Functional Audit Plan (Playwright)

Last updated: 2026-01-15

Goal: spin up `thekeystone.ai` locally and use Playwright to crawl every URL in `/sitemap.xml`, flagging broken pages, runtime errors, and obvious UX regressions, and capturing screenshots for review.

Tracking rule: update this file as each checkpoint completes.

## Scope

In scope:
- Crawl all sitemap URLs returned by the local server’s `/sitemap.xml`.
- For each URL: ensure HTTP 2xx/3xx, no Next.js `not-found`, no page crash, and no console/page errors.
- Capture screenshots (at least desktop; optionally mobile/tablet if useful).

Out of scope (unless explicitly requested):
- Auth-only routes, admin/portal flows, and any content not present in `/sitemap.xml`.
- Dynamic sitemap entries that require real Supabase credentials (we’ll still validate the sitemap endpoint and the static route set).

## Checkpoints

- [x] Checkpoint 1 — Prep + constraints
  - Testing target: `../thekeystone.ai` (sibling repo).
  - Coverage choice: **full local** sitemap coverage via local Supabase.
    - Local Supabase started and seeded so `/sitemap.xml` includes dynamic demo/industry/role/scenario entries.

- [x] Checkpoint 2 — Add/enable a sitemap crawl test
  - Add a Playwright test that:
    - Fetches `/sitemap.xml`
    - Extracts `<loc>` URLs
    - Visits each path on the local server
    - Records failures + console/page errors
    - Writes screenshots to Playwright artifacts
  - Implemented: `../thekeystone.ai/tests/e2e/sitemap.spec.ts`

- [x] Checkpoint 3 — Run the crawl + collect results
  - Run the sitemap test (ideally Chromium first; expand to other projects if needed).
  - Save the output report location (Playwright HTML report + artifacts directory).
  - Crawl output (latest run):
    - Report: `../thekeystone.ai/test-results/artifacts/sitemap-Sitemap-crawl-shou-eee3a-utes-without-runtime-errors-chromium/sitemap-audit/report.json`
    - Screenshots: same `sitemap-audit/` folder (one per route)
    - See Checkpoint 4 for findings and Checkpoint 5 for the final green run summary.

- [x] Checkpoint 4 — Summarise findings
  - Summarise any failures (route, status, error, screenshot).
  - Current failures to resolve before this checkpoint can close:
    - Hydration mismatch console errors for `NonceStyle` (`nonce=""` vs `nonce="..."`)
    - Analytics endpoint rate limiting during crawl (`/api/analytics` → `429`)
  - Fixes applied (in `../thekeystone.ai`):
    - `src/shared/components/security/NonceStyle.tsx`: add `suppressHydrationWarning` to avoid browser-hidden nonce hydration errors.
    - `src/app/api/analytics/route.ts`: short-circuit when analytics disabled/test mode to avoid rate limiting during crawls.
    - `tests/e2e/sitemap.spec.ts`: isolate each route in its own page + capture subresource HTTP failures.
    - `tests/e2e/sitemap.spec.ts`: increase per-route navigation timeout to 90s to avoid cold-compile timeouts (for example `/security`).

- [x] Checkpoint 5 — Fix + re-run to green
  - Fix the underlying runtime/console issues so the crawl reports `failures=0`.
  - Re-run the crawl and attach the new report path + summary here.
  - Latest crawl output:
    - Report: `../thekeystone.ai/test-results/artifacts/sitemap-Sitemap-crawl-shou-eee3a-utes-without-runtime-errors-chromium/sitemap-audit/report.json`
    - Generated at (UTC): `2026-01-15T23:37:45.833Z`
    - Summary: `routes=99`, `failures=0`, `warnings=0`, `cspReportOnly=0`
    - Notes:
      - `/investors` is a restricted/noindex route and is excluded from `sitemap.xml`.
      - Crawl-time UX warnings were addressed (visible `<h1>` during loading states where applicable; CSP noise made test-friendly without weakening production CSP).
      - Formatting baseline applied so `npm run format:check` now passes for `src/` (Prettier).
      - Playwright web server output now suppresses benign dev-server `ECONNRESET` abort noise for cleaner crawl logs.
      - Playwright web server output now also suppresses the Browserslist old-data notice and the Tailwind module-type warning.

## Commands (reference)

From `../thekeystone.ai`:
- Install Playwright browsers (only if needed): `npm run test:e2e:install`
- Run just the sitemap crawl: `npx playwright test tests/e2e/sitemap.spec.ts --project=chromium`
- View report: `npm run test:e2e:report`
