# Databricks notebook source
# MAGIC %sql 
# MAGIC CREATE CATALOG IF NOT EXISTS ecommerce;

# COMMAND ----------

# MAGIC %sql
# MAGIC Use catalog ecommerce

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE SCHEMA IF NOT EXISTS ecommerce.bronze;
# MAGIC CREATE SCHEMA IF NOT EXISTS ecommerce.sliver;
# MAGIC CREATE SCHEMA IF NOT EXISTS ecommerce.gold;

# COMMAND ----------

# MAGIC %md
# MAGIC Show Databases

# COMMAND ----------

# MAGIC %sql
# MAGIC SHOW DATABASES FROM ecommerce

# COMMAND ----------

# %sql
# DROP CATALOG IF EXISTS ecommerce CASCADE

# COMMAND ----------

