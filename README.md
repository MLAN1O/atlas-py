# Atlas Py - Financial & Operations Co-pilot

Atlas Py is a custom AI agent I built to streamline my company's financial and operational workflow.

It works as a **smart collaborator** alongside my standard management tools. While it doesn't fully replace deep spreadsheet analysis, it eliminates the friction of daily data entry and quick information retrieval. Instead of navigating complex tables for every small task, I just use natural language to:

1. **Log Operations (Write):** Instantly record harvests, sales, or expenses via text (e.g., *"Add a sale of $500 to Client X"*).
2. **Analyze Performance (Read):** Get immediate answers on ROI, profit margins, production metrics (e.g., *"How many kg produced this month?"*), or a list of clients with pending payments.

## Architecture & Logic

The system uses **LangGraph** to handle the decision-making flow between acting as a clerk (Data Entry) and an analyst (Reporting):

1. **Orchestrator**: The routing brain. It decides if the user wants to *modify* the database or *query* it.
2. **SQL Agent**: The core interface with Supabase.
   - **Input Mode:** Converts natural language into safe `INSERT` statements for production and financial records.
   - **Query Mode:** Runs complex `SELECT` queries to calculate balances, sum production totals, and identify unpaid debts.
3. **Report Agent**: Translates raw database rows into clear, actionable business insights.

## Tech Stack

- **Python 3.10+**: Core backend logic.
- **LangChain & LangGraph**: Orchestration and state management.
- **OpenAI (GPT-4o-mini)**: Chosen for its speed and ability to understand business context at a low cost.
- **Supabase (PostgreSQL)**: The central database for all company data.
- **Pydantic**: Ensures data integrity by validating inputs before they hit the database.
- **Evolution API**: Gateway for WhatsApp messaging.

## Project Structure

- `app/agents/`: Logic for Orchestrator, SQL, and Report agents.
- `app/graph/`: Workflow nodes and edges definitions.
- `app/tools/`: Custom tools for database interactions.
- `main.py`: Entry point for the application.

## WhatsApp Integration

To make this tool truly useful for my routine, I integrated it with **WhatsApp** using the **Evolution API**.

This setup has been a huge time-saver. It allows me to log production data directly from the field or check financial status while on the go, without ever needing to open a laptop. It effectively turned my chat app into a command line for my business.

---
*Built to make business management less boring and more efficient.*