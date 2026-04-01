# Project Guidelines

## Code Style
- Use PySpark DataFrame APIs and explicit `StructType` schemas for all ingested datasets.
- Keep transformations deterministic and column-explicit; avoid `select("*")` in transformation logic.
- Follow existing metadata pattern for ingestion outputs: add `_source_file` and `ingested_at`.
- Prefer small, composable notebook cells with one clear purpose per cell.

## Architecture
- This project follows a Medallion architecture: Bronze -> Silver -> Gold.
- Bronze ingests raw CSV data with schema enforcement and writes Delta tables.
- Silver applies cleaning and conforming transformations.
- Gold serves analytics-ready models and aggregates.
- Preserve layer boundaries: do not mix business aggregations into Bronze.

## Build and Test
- This repository is notebook-driven (Databricks/PySpark); there is no local package build or test runner defined.
- Validate changes by executing the affected notebook cells in order and confirming:
  - schemas match expected definitions,
  - metadata columns are present,
  - Delta writes succeed without unintended schema drift.
- If adding script-based modules later, include reproducible run/test commands in `README.md` and keep this file updated.

## Conventions
- Use Bronze table naming with `brz_` prefix (example: `brz_brands`).
- Keep schema definitions near data-read logic for readability and maintenance.
- Treat `bronze_data_layer.ipynb` as the canonical ingestion pattern for new entities.
- Use repo-relative paths for local development datasets under `ecomm-raw-data/` unless environment-specific paths are explicitly required.

## References
- Project overview and workflow: `README.md`
- Canonical Bronze ingestion pattern: `bronze_data_layer.ipynb`
