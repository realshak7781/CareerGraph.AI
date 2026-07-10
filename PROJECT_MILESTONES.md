# CareerGraph.AI — Project Progress & Milestones History

CareerGraph.AI is an agentic GraphRAG career discovery platform that integrates personal professional networks, resume embeddings, live job postings, and graph visualization. By combining **FastAPI**, **Celery**, **Redis**, **Neo4j**, **LangGraph**, **Playwright**, and **Next.js with Sigma.js**, the platform maps career networks and automatically generates targeted outreach pathways.

---

## 1. Where We Started (Project Inception)

The project began with a blueprint to solve a major problem in job searching: **the disconnect between job application fit (resume matching) and networking access (LinkedIn connection chains).** 

The initial goals were structured into two distinct execution phases:

### Phase 1: Asynchronous Ingestion & Infrastructure Setup
* **FastAPI Backend & Task Queue:** Build a robust, containerized backend capable of delegating heavy file parsing and ingestion tasks to Celery workers with a Redis message broker.
* **Transient & Privacy-Safe Processing:** Extract and parse incoming LinkedIn archives (`Connections.csv` and `Positions.csv`) and resumes (`resume.pdf`) entirely in memory without writing personal data (PII) to system logs or persistent disk storage.
* **Neo4j Graph Database & Vector Search:** Set up the Neo4j schema `(User)-[:CONNECTED_TO]->(Person)-[:WORKS_AT]->(Company)` and initialize vector indices to handle high-dimensional embeddings for semantic resume matching.
* **Ingestion Task Pipeline:** Create a seamless background data ingestion task queue matching the "Extract -> Embed -> Load" pipeline.

### Phase 2: Intelligent Discovery & Synthesis
* **LangGraph Orchestrator:** Coordinate multi-agent execution using a state machine that locks discovery agents from running until database ingestion and index building are completely finished.
* **Playwright Scraper Agent:** Scrape active job portals using stealth browser automation to retrieve relevant postings.
* **Matchmaker Agent:** Perform high-performance hybrid queries combining graph traversal (finding 1st/2nd degree network paths) and vector similarity (calculating job-to-resume fit scores).
* **Synthesizer Agent & Interactive UI:** Convert enriched job matches into flat Graphology-compliant JSON nodes/edges, and feed them into a Next.js front-end containing an interactive Sigma.js WebGL canvas graph visualizer.

---

## 2. Key Milestones Achieved

Every core feature in the design specification is **fully completed and verified** (T01 through T11):

| ID | Task | Status | Achievement Details |
| :--- | :--- | :--- | :--- |
| **T01** | Initialize FastAPI & Celery/Redis worker pool | **Done** | Complete setup of backend microservices running Celery worker task queues. |
| **T02** | Implement in-memory ZIP parser for LinkedIn exports | **Done** | Parsed `Connections.csv` and `Positions.csv` in-memory. Zero disk persistence for PII. |
| **T03** | Implement PDF text extraction | **Done** | Configured PyPDF text extraction from resumes to build user profile embeddings. |
| **T04** | Initialize Neo4j Schema | **Done** | Built graph schema mapping users, connections, companies, and relationship chains. |
| **T05** | Configure Neo4j Vector Indexes | **Done** | Configured high-dimensional cosine similarity indexes for resume & profile vectors. |
| **T06** | Build Ingestion Task Queue | **Done** | Created end-to-end task queue populating local Neo4j graphs via background workers. |
| **T07** | LangGraph State Machine Orchestrator | **Done** | Built orchestrator that locks Phase 2 discovery until database ingestion is complete. |
| **T08** | Playwright Scraper Agent | **Done** | Integrated Playwright with stealth settings to scrape targeted job portal listings. |
| **T09** | Matchmaker Agent (Hybrid Cypher) | **Done** | Written a unified Cypher query combining vector similarity and path traversal in a single DB trip. |
| **T10** | Graphology JSON Synthesis | **Done** | Structured output data strictly matching the Graphology contract with AI outreach directives. |
| **T11** | Next.js & Sigma.js WebGL UI | **Done** | Rendered interactive dark-themed graph, custom event hooks, side drawer, and edge cards. |

---

## 3. Notable Engineering Triumphs & Fixes

During the development cycle, several complex, platform-specific bugs and performance bottlenecks were encountered and successfully resolved:

1. **Sigma.js WebGL Shader Integration (Sigma v3):**
   * *Problem:* A black screen error appeared: `Sigma: could not find a suitable program for node type "User"!` because Sigma reserved `node.type` and `edge.type` for rendering programs.
   * *Resolution:* Modified the ingestion flow on the client side (`page.tsx`) to destructure the original `type` out of the Graphology payload and remap them to custom attributes (`entityType` and `edgeType`), ensuring standard renderers were used.
2. **Windows event-loop compatibility with Playwright subprocesses:**
   * *Problem:* Playwright threw `NotImplementedError` when executing from within FastAPI/Uvicorn on Windows due to the default `SelectorEventLoop`.
   * *Resolution:* Explicitly injected `asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())` before Uvicorn loop initialization.
3. **Uvicorn CLI execution order bypass:**
   * *Problem:* Running the app via `uvicorn main:app` set up Uvicorn's internal event-loop before the proactor event loop policy in `main.py` took effect, reviving the error.
   * *Resolution:* Created a Python execution block (`if __name__ == "__main__": uvicorn.run(...)`) ensuring the ProactorEventLoop policy is registered before Uvicorn starts.

---

## 4. Latest Milestone Achieved: End-to-End Pipeline Verification

The latest and final milestone is the **fully functioning end-to-end user pipeline**:

1. **User Upload Experience:** A dark-themed drag-and-drop landing screen where the user uploads `LinkedinData.zip` and `resume.pdf`.
2. **Server-Sent Events (SSE) Progress Bar:** As files upload, the UI receives real-time progress events from FastAPI tracking stages (Upload -> Parse Resume -> Extract Contacts -> GraphRAG Synthesis -> Write to Neo4j -> Generate Graph Layout -> Ready).
3. **Interactive Graph Visualization:** Once the backend synthesis is complete, the modal dismisses to show the interactive Sigma.js WebGL canvas:
   * **Custom Layouts:** Rendered using the ForceAtlas2 layout algorithm.
   * **Node Color-coding & Scaling:** The user node is highlighted, jobs are teal, companies purple, and network leads blue, with sizes dynamically scaled by their degree.
   * **Hover Highlights:** Hovering on a node dims all unrelated items and showcases neighbors.
   * **Outreach Message Popups:** Clicking on network paths displays AI-generated outreach templates optimized to connect with people working at the target job company.
   * **Detail Panel Side Drawer:** Clicking a node pulls in metadata, match scores, description, and action directives.
