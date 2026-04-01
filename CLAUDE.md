# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

End-to-end eCommerce data engineering pipeline using **PySpark + Delta Lake** on Databricks, following the **Medallion architecture** (Bronze → Silver → Gold). Development uses an agentic workflow: define a task via GitHub issue, plan implementation, then generate code using AI (GitHub Copilot / Claude).

## Architecture

### Medallion Layers
- **Bronze** — Raw CSV ingestion with schema enforcement. Writes Delta tables with `mergeSchema = true`. Adds `_source_file` and `ingested_at` metadata columns to every table.
- **Silver** — Cleaning and conforming transformations (not yet implemented).
- **Gold** — Analytics-ready models and aggregates (not yet implemented).

**Do not mix business aggregations into Bronze.** Layer boundaries are strict.

### Catalog / Namespace
All tables live under the `ecommerce` Unity Catalog:
- `ecommerce.bronze.brz_<entity>` — Bronze layer tables
- Data read from `/Volumes/ecommerce/source_data/raw/<entity>/*.csv` on Databricks

### Source Data (`ecomm-raw-data/`)
Static reference files (brands, category, customers, date, products) and daily incremental files for `order_items` partitioned under `order_items/landing/order_items_YYYY-MM-DD.csv`.

## Comments

Only add comments for complex or non-obvious logic. Do not comment repetitive patterns (e.g., each schema definition, each Delta write) — the code is self-explanatory for standard ingestion steps.

## Conventions

- **Table naming**: `brz_` prefix for Bronze (e.g., `brz_brands`, `brz_category`).
- **Schema**: Always define explicit `StructType` schemas; never infer schema from CSV.
- **Transformations**: Column-explicit; avoid `select("*")` in transformation logic.
- **Notebook cells**: Small and composable — one clear purpose per cell.
- **Canonical ingestion pattern**: [bronze_data_layer.ipynb](bronze_data_layer.ipynb) — follow this as the reference when adding new entities.
- Schema definitions belong near their data-read logic.

## Running / Validating

This is a **notebook-driven Databricks project** — there is no local build or test runner.

To validate changes:
1. Execute affected notebook cells in order inside Databricks.
2. Confirm schemas match expected `StructType` definitions.
3. Confirm `_source_file` and `ingested_at` metadata columns are present.
4. Confirm Delta writes succeed without unintended schema drift.

For local data references during development, use paths under `ecomm-raw-data/`.
