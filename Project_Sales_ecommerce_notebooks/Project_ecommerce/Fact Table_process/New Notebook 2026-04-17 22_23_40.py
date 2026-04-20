# Databricks notebook source
# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE ecommerce.source_data.aws_order_table
# MAGIC USING DELTA
# MAGIC LOCATION 's3://ecommerce-pipeline-data-store/bronze/aws_order_table'
# MAGIC AS
# MAGIC SELECT
# MAGIC   *,
# MAGIC   current_timestamp() AS ingested_at,
# MAGIC   input_file_name() AS _source_file,
# MAGIC   uuid() AS _bronze_id
# MAGIC FROM read_files(
# MAGIC   's3://ecommerce-pipeline-data-store/Orders/*.csv',
# MAGIC   format => 'csv',
# MAGIC   header => true,
# MAGIC   inferSchema => true
# MAGIC );