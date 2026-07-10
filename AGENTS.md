# AGENTS: Rules of Engagement & System Constraints

These rules dictate the behavioral and technical boundaries for all autonomous agents operating within the CareerGraph environment. Read before executing any structural changes.

## 1. Technical & Framework Constraints
* **Strict Sequential Execution:** The overarching LangGraph orchestrator MUST enforce a hard lock on Phase 2. Scraping and matching agents are prohibited from firing until the Celery/Redis task queue explicitly confirms the Neo4j database is fully populated and vector indexes are built.
* **Unified Queries:** Latency is the enemy. Leverage Neo4j's hybrid search to perform graph traversals and vector similarity calculations in a single database trip. Do not execute a vector search in Python and subsequently loop through graph queries.
* **Privacy by Design:** All `.zip` processing must remain entirely transient during the background task. You are strictly forbidden from writing Personally Identifiable Information (PII) to external system logs, standard output, or persistent disk storage outside the secured graph database.

## 2. Engineering Philosophy
* **First Principles Execution:** Deconstruct all architectural tasks to their fundamental logic before relying on heavy framework abstractions. Ensure the core data flow is understood at a basic level before wrapping it in LangGraph nodes.
* **Architectural Uncompromising Integrity:** Build this system like a functional masterpiece. Do not patch over logical flaws with hacky workarounds. If the schema is flawed, rebuild the schema. Every component must serve a precise, defined purpose.
* **Telegram-Optimized Output:** The final Synthesis JSON must remain clean and directly parsable for the planned Telegram integration, prioritizing cost-efficiency and direct delivery over immediate email or WhatsApp bindings.

## 3. Standard Operating Procedures
* **Reconnaissance First:** Always check existing files and project structure before creating new ones.
* **Continuous State Sync:** Update `todo.md` immediately after every successful tool call or completed milestone.
* **Error Hygiene:** Follow the Log Compaction protocol in `errorLogs.md`. Log immediately upon encountering a blocking error, and document the hypothesized fix before implementing it.
