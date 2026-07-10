# CareerGraph - Project Todo List

| ID | Task | Status | Verification Method |
| :--- | :--- | :--- | :--- |
| **Phase 1: Asynchronous Ingestion & Setup** | | | |
| T01 | Initialize FastAPI application and Celery worker pool with Redis broker. | Done | `celery -A worker ping` responds successfully. |
| T02 | Implement in-memory ZIP parser for `LinkedinData.zip` (`Connections.csv`, `Positions.csv`). | Done | Unit tests confirming transient extraction without writing to disk. |
| T03 | Implement PDF text extraction for `resume.pdf`. | Done | Test script outputs correct plain text string from a sample PDF. |
| T04 | Initialize Neo4j schema `(User)-[:CONNECTED_TO]->(Person)-[:WORKS_AT]->(Company)`. | Done | Verify schema via Neo4j browser/Cypher. |
| T05 | Configure Neo4j Vector Index for resume and profile text embeddings. | Done | `db.index.vector.queryNodes()` returns expected dimensions. |
| T06 | Build ingestion task queue logic (Extract -> Embed -> Load to Neo4j). | Done | E2E task execution populates local Neo4j instance successfully. |
| **Phase 2: Intelligent Discovery & Synthesis** | | | |
| T07 | Configure LangGraph state machine orchestrator (blocks until Phase 1 signals complete). | Done | LangGraph state visually confirms Phase 1 wait state before proceeding. |
| T08 | Implement Scraper Agent using Playwright (stealth configurations active). | Done | Scraper successfully retrieves 5 job postings from target portal without blocks. |
| T09 | Implement Matchmaker Agent hybrid Cypher query (Vector similarity + Graph traversal). | Done | Query executes in a single trip and returns both job fit and 1st/2nd degree paths. |
| T10 | Generate Synthesis JSON output (Graphology-compliant nodes/edges). | Done | FastAPI endpoint output strictly matches the Graphology JSON contract. |
| T11 | Implement Next.js frontend with Sigma WebGL Canvas, side drawer, and edge card. | Done | UI renders canvas cleanly, handles hover dimming, and correctly triggers drawer and floating edge cards. |
| **Phase 3: Code Craftsmanship & Mastery** | | | |
| T12 | Perform comprehensive codebase audit and generate step-by-step curriculum in `learning.md`. | Done | `learning.md` is present in the workspace root and contains complete educational modules. |
| **Pre-Flight Sweep** | | | |
| T13 | Perform aggressive security sweep and generate root `.gitignore`. | Done | Root `.gitignore` created; PII/secrets checklist provided. |


