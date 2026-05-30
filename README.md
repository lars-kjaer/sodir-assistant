# SODIR Assistant

A natural-language interface over Norwegian Continental Shelf (NCS) petroleum data published by the Norwegian Offshore Directorate (SODIR). Ask questions in plain English; the system generates SQL, runs it against a local data warehouse, and returns a written answer.

This is a learning / proof-of-concept project built to explore how an LLM-powered data assistant would be architected, using patterns that mirror enterprise data platforms.

## What it does

Ask questions like:

- "How many exploration wellbores are in the Barents Sea?"
- "Which wellbores are currently being drilled?"
- "Which drilling operator has drilled the most wellbores?"

The assistant translates the question into SQL (Text-to-SQL), executes it, and phrases the result in natural language.

## Architecture

The project follows a medallion architecture, separating raw ingestion from transformation from serving:

```
SODIR factpages (CSV)
        │
        ▼
  fetch_sodir.py            ──►  data/bronze/  (raw CSVs)
        │
        ▼
  load_bronze_to_db.py      ──►  SQLite: bronze_* tables
        │
        ▼
  dbt (silver models)       ──►  cleaned, renamed, normalised
        │
        ▼
  dbt (gold models)         ──►  curated, agent-facing tables
        │
        ▼
  Text-to-SQL agent (Groq)  ──►  generates + executes SQL
        │
        ▼
  Streamlit UI              ──►  chat interface
```

- **Bronze** — raw SODIR CSVs, loaded as-is into SQLite. Faithful copy of source.
- **Silver** — cleaned and renamed via dbt. Normalised, one table per entity. The source of truth for analysis.
- **Gold** — curated, denormalised views built for the LLM agent. Optimised for query simplicity, not storage efficiency.

## Tech stack

| Layer | Tool |
|---|---|
| Language | Python 3.11 |
| Ingestion | requests, pandas |
| Warehouse | SQLite |
| Transformation | dbt (dbt-core + dbt-sqlite) |
| LLM | Groq (Llama 3.3 70B) |
| UI | Streamlit |
| Evaluation | Custom execution-accuracy framework |

## Project structure

```
sodir-assistant/
├── ingestion/          # bronze layer: fetch + load to SQLite
├── transform/sodir_dbt/ # silver + gold dbt models
├── agent/              # Text-to-SQL agent
├── app/                # Streamlit UI
├── evaluation/         # accuracy evaluation framework
└── data/               # local data (gitignored)
```

## Setup

```bash
# Clone and enter
git clone https://github.com/lars-kjaer/sodir-assistant.git
cd sodir-assistant

# Create and activate a virtual environment (Python 3.11)
py -3.11 -m venv venv
venv\Scripts\activate          # Windows

# Install dependencies
pip install -r requirements.txt

# Add your Groq API key to a .env file
echo GROQ_API_KEY=your_key_here > .env
```

## Running the pipeline

```bash
# 1. Fetch raw data from SODIR
python ingestion/fetch_sodir.py

# 2. Load raw data into SQLite
python ingestion/load_bronze_to_db.py

# 3. Build silver + gold tables
cd transform/sodir_dbt
dbt run

# 4. Launch the assistant
cd ../..
streamlit run app/streamlit_app.py
```

## Current state

- ✅ End-to-end pipeline working for **wellbore** data
- ✅ Text-to-SQL agent with natural-language answers
- ✅ Streamlit chat UI
- ✅ Evaluation framework (execution accuracy)
- 🚧 Field, production, and licence data ingested to bronze; modelling in progress

## Limitations

This is a proof of concept, not a production system. Known limitations:

- **Text-to-SQL is not 100% accurate.** LLM-generated SQL can be confidently wrong, particularly on ambiguous questions or complex joins. Answers should be verified, not trusted blindly.
- **SQLite** is used for local development; a production deployment would use a cloud warehouse.
- No access control, audit logging, or data governance.
- Single-entity scope today (wellbore); multi-entity questions requiring joins are not yet supported.

## Data source

All data is sourced from the [SODIR factpages](https://factpages.sodir.no/en), published by the Norwegian Offshore Directorate.

## Licence

This project is for educational purposes. SODIR data is subject to its own terms of use.