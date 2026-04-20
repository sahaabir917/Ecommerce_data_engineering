# Databricks notebook source
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DateType, TimestampType, FloatType

import pyspark.sql.functions as F

# COMMAND ----------

catalog_name = "ecommerce"

# COMMAND ----------

# MAGIC %md
# MAGIC Define Schema For the data files

# COMMAND ----------

brand_schema = StructType([
  StructField("brand_code", StringType(), False),
  StructField("brand_name", StringType(), True),
  StructField("category_code", StringType(), True) 
  ])

# COMMAND ----------

# MAGIC %md
# MAGIC Create data frame

# COMMAND ----------

raw_data_path = "/Volumes/ecommerce/source_data/raw/brands/*.csv"

df = spark.read.option("header", "true").option("delimiter", ",").schema(brand_schema).csv(raw_data_path)

# Add Meta data
df = df.withColumn("_source_file", F.col("_metadata.file_path")).withColumn("ingested_at", F.current_timestamp())

display(df.limit(5))

# COMMAND ----------

# MAGIC %md
# MAGIC Create Table from dataframe

# COMMAND ----------

#Create a delta table with mergeSchema true so that if we have one more column in later it will able to merge 

df.write.format("delta").mode("overwrite").option("mergeSchema", "true").saveAsTable(f"{catalog_name}.bronze.brz_brands")

# COMMAND ----------

# MAGIC %md
# MAGIC Catefgory Schema

# COMMAND ----------

category_schema = StructType([
  StructField("category_code", StringType(), False),
  StructField("category_name", StringType(), True)
  ])

# COMMAND ----------

# MAGIC %md
# MAGIC Create data frame

# COMMAND ----------

raw_data_path = "/Volumes/ecommerce/source_data/raw/category/*.csv"

df = spark.read.option("header", "true").option("delimiter", ",").schema(category_schema).csv(raw_data_path)

# Add Meta data
df = df.withColumn("_source_file", F.col("_metadata.file_path")).withColumn("ingested_at", F.current_timestamp())

display(df.limit(5))

# COMMAND ----------

# MAGIC %md
# MAGIC Create Table from dataframe

# COMMAND ----------

#Create a delta table with mergeSchema true so that if we have one more column in later it will able to merge 

df.write.format("delta").mode("overwrite").option("mergeSchema", "true").saveAsTable(f"{catalog_name}.bronze.brz_category")

# COMMAND ----------

# MAGIC %md
# MAGIC Customer Table 

# COMMAND ----------

customer_schema = StructType([
  StructField("customer_id",   StringType(), False),
  StructField("phone",          StringType(), True),
  StructField("country_code",   StringType(), True),
  StructField("country",        StringType(), True),
  StructField("state",          StringType(), True),
  ])

# COMMAND ----------

raw_data_path = "/Volumes/ecommerce/source_data/raw/customers/*.csv"

df = spark.read.option("header", "true").option("delimiter", ",").schema(customer_schema).csv(raw_data_path)

# Add Meta data
df = df.withColumn("_source_file", F.col("_metadata.file_path")).withColumn("ingested_at", F.current_timestamp())

display(df.limit(5))

# COMMAND ----------

df.write.format("delta").mode("overwrite").option("mergeSchema", "true").saveAsTable(f"{catalog_name}.bronze.brz_customer")

# COMMAND ----------

# MAGIC %md
# MAGIC Date Table

# COMMAND ----------

date_schema = StructType([
  StructField("date",          StringType(),  False),
  StructField("year",          StringType(), True),
  StructField("day_name",      StringType(),  True),
  StructField("quarter",       IntegerType(), True),
  StructField("week_of_year",  IntegerType(), True),
  ])

# COMMAND ----------

raw_data_path = "/Volumes/ecommerce/source_data/raw/date/*.csv"

df = spark.read.option("header", "true").option("delimiter", ",").schema(date_schema).csv(raw_data_path)

# Add Meta data
df = df.withColumn("_source_file", F.col("_metadata.file_path")).withColumn("ingested_at", F.current_timestamp())

display(df.limit(5))

# COMMAND ----------

df.write.format("delta").mode("overwrite").option("mergeSchema", "true").saveAsTable(f"{catalog_name}.bronze.brz_date")

# COMMAND ----------

# MAGIC %md
# MAGIC Define Schema for order_item

# COMMAND ----------

order_items_schema = StructType([
  StructField("dt",                   StringType(),  False),
  StructField("order_ts",              StringType(),  True),
  StructField("customer_id",           StringType(),  True),
  StructField("order_id",              StringType(), True),
  StructField("item_seq",              StringType(), True),
  StructField("product_id",            StringType(),  True),
  StructField("quantity",              StringType(), True),
  StructField("unit_price_currency",   StringType(),  True),
  StructField("unit_price",            StringType(),   True),
  StructField("discount_pct",          StringType(),  True),
  StructField("tax_amount",            StringType(),   True),
  StructField("channel",               StringType(),  True),
  StructField("coupon_code",           StringType(),  True),
  ])

# COMMAND ----------

raw_data_path = "/Volumes/ecommerce/source_data/raw/order_items/landing/*.csv"

df = spark.read.option("header", "true").option("delimiter", ",").schema(order_items_schema).csv(raw_data_path)

# Add Meta data
df = df.withColumn("_source_file", F.col("_metadata.file_path")).withColumn("ingested_at", F.current_timestamp())

display(df.limit(5))

# COMMAND ----------


df.write.format("delta").mode("overwrite").option("mergeSchema", "true").saveAsTable(f"{catalog_name}.bronze.brz_order_items")

# COMMAND ----------

# MAGIC %md
# MAGIC Products Schema

# COMMAND ----------

products_schema = StructType([
  StructField("product_id",    StringType(),  False),
  StructField("sku",           StringType(),  True),
  StructField("category_code", StringType(),  True),
  StructField("brand_code",    StringType(),  True),
  StructField("color",         StringType(),  True),
  StructField("size",          StringType(),  True),
  StructField("material",      StringType(),  True),
  StructField("weight_grams",  StringType(),  True),
  StructField("length_cm",     StringType(),  True),
  StructField("width_cm",      FloatType(),   True),
  StructField("height_cm",     FloatType(),   True),
  StructField("rating_count",  IntegerType(), True),
  ])

# COMMAND ----------

raw_data_path = "/Volumes/ecommerce/source_data/raw/products/*.csv"

df = spark.read.option("header", "true").option("delimiter", ",").schema(products_schema).csv(raw_data_path)

# Add Meta data
df = df.withColumn("_source_file", F.col("_metadata.file_path")).withColumn("ingested_at", F.current_timestamp())

display(df.limit(5))

# COMMAND ----------

df.write.format("delta").mode("overwrite").option("mergeSchema", "true").saveAsTable(f"{catalog_name}.bronze.brz_products")