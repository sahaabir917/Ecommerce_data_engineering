# Databricks notebook source
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DateType, BooleanType
import pyspark.sql.functions as F

# COMMAND ----------

catalog_name = 'ecommerce'

# COMMAND ----------

order_items_schema = StructType([
    StructField("dt",                 StringType(), True),
    StructField("order_ts",           StringType(), True),
    StructField("customer_id",        StringType(), True),
    StructField("order_id",           StringType(), True),
    StructField("item_seq",           StringType(), True),
    StructField("product_id",         StringType(), True),
    StructField("quantity",           StringType(), True),
    StructField("unit_price_currency",StringType(), True),
    StructField("unit_price",         StringType(), True),
    StructField("discount_pct",       StringType(), True),
    StructField("tax_amount",         StringType(), True),
    StructField("channel",            StringType(), True),
    StructField("coupon_code",        StringType(), True),
])

# COMMAND ----------

# # Load data using the schema defined
# raw_data_path = "/Volumes/ecommerce/source_data/raw/order_items/landing/*.csv"

# # Step 1: Read CSV - match aws_order_table column naming
# df_csv = spark.read \
#     .option("header", "true") \
#     .option("delimiter", ",") \
#     .schema(order_items_schema) \
#     .csv(raw_data_path) \
#     .withColumn("_source_file", F.col("_metadata.file_path")) \
#     .withColumn("ingested_at", F.current_timestamp()) \
#     .withColumn("_bronze_id", F.expr("uuid()"))

# # Step 2: Read AWS Order Table
# df_aws_raw = spark.read.table("ecommerce.source_data.aws_order_table")

# # Step 3: Cast all AWS columns to string
# df_aws = df_aws_raw \
#     .select([F.col(c).cast("string").alias(c) for c in df_aws_raw.columns])

# # Step 4: Get common columns
# common_cols = [field.name for field in order_items_schema.fields] + ["_source_file", "ingested_at", "_bronze_id"]

# # Step 5: Align both DataFrames
# df_csv_aligned = df_csv.select(common_cols) \
#     .withColumn("order_id", F.col("order_id").cast("string"))

# df_aws_aligned = df_aws.select(common_cols)

# # Step 6: Union
# df = df_csv_aligned.unionByName(df_aws_aligned)

# display(df)

from pyspark.sql import functions as F

raw_data_path = "/Volumes/ecommerce/source_data/raw/order_items/landing/*.csv"

required_cols = [field.name for field in order_items_schema.fields] + [
    "_source_file", "ingested_at", "_bronze_id"
]

# CSV
df_csv_base = (
    spark.read
    .option("header", "true")
    .option("delimiter", ",")
    .schema(order_items_schema)
    .csv(raw_data_path)
)

df_csv = (
    df_csv_base
    .selectExpr("*", "_metadata.file_path as _source_file")
    .withColumn("ingested_at", F.current_timestamp())   # timestamp
    .withColumn("_bronze_id", F.expr("uuid()"))
)

# AWS table
df_aws_raw = spark.read.table("ecommerce.source_data.aws_order_table")

for c in required_cols:
    if c not in df_aws_raw.columns:
        if c == "ingested_at":
            df_aws_raw = df_aws_raw.withColumn(c, F.lit(None).cast("timestamp"))
        else:
            df_aws_raw = df_aws_raw.withColumn(c, F.lit(None).cast("string"))

# Align types
df_csv_aligned = df_csv.select(
    *[
        F.col(c).cast("timestamp").alias(c) if c == "ingested_at"
        else F.col(c).cast("string").alias(c)
        for c in required_cols
    ]
)

df_aws_aligned = df_aws_raw.select(
    *[
        F.col(c).cast("timestamp").alias(c) if c == "ingested_at"
        else F.col(c).cast("string").alias(c)
        for c in required_cols
    ]
)

df = df_csv_aligned.unionByName(df_aws_aligned)
display(df)

# COMMAND ----------

print("CSV schema:")
df_csv_aligned.printSchema()

print("AWS schema:")
df_aws_aligned.printSchema()

# COMMAND ----------



# COMMAND ----------

display(df.limit(5))

# COMMAND ----------

# df.write.format("delta") \
#     .mode("overwrite") \
#     .option("mergeSchema", "true") \
#     .saveAsTable(f"{catalog_name}.bronze.brz_order_items")

df.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{catalog_name}.bronze.brz_order_items")

# COMMAND ----------

# print("CSV columns:", df_csv_aligned.columns)
# print("AWS columns:", df_aws_aligned.columns)
# print("Common cols:", common_cols)

# # Also check row counts
# print("CSV rows:", df_csv.count())
# print("AWS rows:", df_aws.count())
# print("Merged rows:", df.count())

common_cols = df_csv_aligned.columns
print("CSV columns:", df_csv_aligned.columns)
print("AWS columns:", df_aws_aligned.columns)
print("Common cols:", common_cols)

# Row counts
print("CSV rows:", df_csv_aligned.count())
print("AWS rows:", df_aws_aligned.count())
print("Merged rows:", df.count())

# Schema check
print("CSV schema:")
df_csv_aligned.printSchema()

print("AWS schema:")
df_aws_aligned.printSchema()

print("Merged schema:")
df.printSchema()

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from ecommerce.gold.fact_transactions_denorm where customer_id= "CUST000000001610"
# MAGIC