# Error Log Template & History

*Keep logs clean, lightweight, and structured to maintain context across sessions.*

## Log Compaction Protocol
Once this file exceeds 100 lines, summarize resolved errors into a single "Resolved Issues" block and clear the detailed logs to save context window.

---

### [2026-04-30 01:08:28]
* **Attempted Action:** Run `docker-compose up -d` to start Neo4j and Redis.
* **Observed Error:** `error during connect: Get "http://%2F%2F.%2Fpipe%2FdockerDesktopLinuxEngine/v1.51/images/redis:alpine/json": open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.` (Docker daemon is not running).
* **Hypothesized Fix:** The USER needs to start Docker Desktop (or the Docker engine) locally and then re-run `docker-compose up -d`.

---

### [2026-05-12 19:45:50 & 19:50:23]
* **Attempted Action:** Render the Next.js `Sigma` graph using Graphology JSON payload containing nodes and edges with a `type` attribute.
* **Observed Error:** Black screen on the frontend with console errors: `Sigma: could not find a suitable program for node type "User"!` and `Sigma: could not find a suitable program for edge type "CONNECTED_TO"!`
* **Hypothesized Fix:** In Sigma v3, `node.type` and `edge.type` are strictly reserved for WebGL rendering programs. We must destructure `type` out of the attributes during `graph.addNode` and `graph.addEdge` and remap them to `entityType` and `edgeType` so Sigma uses the default renderers while preserving our data. (Implemented fix in `page.tsx`).

---

### [2026-05-12 20:00:55]
* **Attempted Action:** Run the FastAPI backend and query `/api/graph?user_id=sharique`.
* **Observed Error:** Neo4j connection refused (`[WinError 10061]`), followed by `400 Bad Request` from the API. Also, a deprecation warning from `google.generativeai`.
* **Hypothesized Fix:** The connection error occurred because the Docker containers for Neo4j and Redis were not running. Executed `docker-compose up -d` to start the infrastructure. The 400 Bad Request is the intentional LangGraph security lock correctly enforcing Phase 1 completion when the database is offline. The deprecation warning is non-fatal, but updating the SDK or suppressing the warning cleans up the logs.

### [2026-05-12 20:03:48]
* **Attempted Action:** Fetch `/api/graph` endpoint after starting Neo4j.
* **Observed Error:** `500 Internal Server Error` with `TypeError: No synchronous function provided to "scraper_agent". Either initialize with a synchronous function or invoke via the async API`.
* **Hypothesized Fix:** In LangGraph, because our nodes (`scraper_node`, etc.) are defined as asynchronous (`async def`), we cannot call `career_graph_orchestrator.invoke(initial_state)`. We must use the asynchronous counterpart `await career_graph_orchestrator.ainvoke(initial_state)` inside our FastAPI route. (Fixed in `main.py`).

### [2026-05-12 20:05:25]
* **Attempted Action:** Running `scraper_node` which utilizes `async_playwright()` underneath the FastAPI/Uvicorn server.
* **Observed Error:** `NotImplementedError` thrown from `asyncio.create_subprocess_exec` within `playwright\_impl\_transport.py`.
* **Hypothesized Fix:** This is a well-documented Python/Windows compatibility bug. Uvicorn on Windows can default to using `SelectorEventLoop`, which does not support asynchronous subprocesses (required by Playwright to launch Chromium). The fix is to explicitly inject `asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())` at the top of `main.py` before the FastAPI app initializes. (Implemented).

### [2026-05-12 21:54:50]
* **Attempted Action:** Running the agent pipeline again using `uvicorn main:app --reload`.
* **Observed Error:** The `NotImplementedError` returned! Playwright crashed again while creating a subprocess.
* **Hypothesized Fix:** Even though `asyncio.WindowsProactorEventLoopPolicy()` was added to `main.py`, invoking the app directly via the `uvicorn` CLI executes Uvicorn's internal event-loop setup *before* `main.py` is fully evaluated, forcing the unsupported `SelectorEventLoop` back into play. To fix this, I added an `if __name__ == "__main__":` block to `main.py`. Running the server via `python main.py` ensures the policy is firmly set before Uvicorn spins up the loop.

---

### [2026-05-31 22:10:26]
* **Attempted Action:** Generating node embeddings for LinkedIn connections during the background intake worker cycle.
* **Observed Error:** `404 models/text-embedding-004 is not found for API version v1beta, or is not supported for embedContent.`
* **Hypothesized Fix:** Replace the deprecated `text-embedding-004` model identifier string with the modern, active `gemini-embedding-001` model string across the backend service configuration.

---

### [2026-05-31 22:22:15]
* **Attempted Action:** Sequential single-item vector embedding extraction for 1,209 LinkedIn connections.
* **Observed Error:** `429 You exceeded your current quota... Quota exceeded for metric: generativelanguage.googleapis.com/embed_content_free_tier_requests, limit: 100, model: gemini-embedding-1.0`
* **Hypothesized Fix:** Refactor the ingestion loop in the Celery worker to batch connection profiles into chunks of 100, utilizing Gemini's native `batch_embed_contents` API method to execute only ~13 total network requests, and apply defensive throttling (`time.sleep(0.5)`) between batch transactions.

---

### [2026-05-31 22:24:37]
* **Attempted Action:** Running hybrid Cypher matching on scraped job listings using live vector projections.
* **Observed Error:** `Neo.ClientError.Statement.ArgumentError: Invalid input for 'vector.similarity.cosine()': Argument b is not a valid vector...` driven by an upstream Gemini 404.
* **Hypothesized Fix:** Perform a global code sweep to replace remaining instances of `text-embedding-004` with the active model configuration, and add a protective guard clause to reject empty vectors before hitting the database.

---

### [2026-05-31 22:33:10]
* **Attempted Action:** Processing full network graph generation for 1,209 connections.
* **Observed Error:** `429 Quota exceeded for metric... limit: 1000, model: gemini-embedding-1.0`
* **Hypothesized Fix:** Temporarily intercept and truncate the incoming parsed connections array to a subset of 50 profiles in the Celery worker to bypass daily cloud quota limits.

---

### [2026-05-31 22:48:22]
* **Attempted Action:** Rendering synthesized GraphRAG network on the frontend Sigma.js WebGL canvas.
* **Observed Anomaly:** The WebGL canvas only renders User, Job, and Company nodes; Contact nodes and connecting edges are absent. This is because real scraped job company names do not match connection companies in the database, resulting in empty paths. Additionally, RGBA edge color formats can fail to render in some WebGL configurations.
* **Hypothesized Fix:** Update the Matchmaker agent to generate synthetic/mock paths using real ingested connections from the database when no direct paths are found (enabling visual QA). Also, update the frontend WebGL configuration to use solid hex colors for edges to ensure visibility.

---
*(Duplicate the template above for new entries)*
