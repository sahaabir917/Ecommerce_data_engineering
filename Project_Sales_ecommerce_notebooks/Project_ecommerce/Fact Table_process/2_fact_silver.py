# Databricks notebook source
# MAGIC %md
# MAGIC ## Bronze to Silver: Data Cleansing and Transformation

# COMMAND ----------

from pyspark.sql.types import StringType, IntegerType, DateType, BooleanType
import pyspark.sql.functions as F

# COMMAND ----------

catalog_name = 'ecommerce'

# COMMAND ----------

df = spark.table(f'{catalog_name}.bronze.brz_order_items')
display(df)

# COMMAND ----------

df.printSchema()

# COMMAND ----------

display(df)

# COMMAND ----------

# Transformation: Drop any duplicates
df = df.dropDuplicates(["order_id", "item_seq"])

# Transformation: Convert 'Two' → 2 and cast to Integer
df = df.withColumn(
    "quantity",
    F.when(F.col("quantity") == "Two", 2).otherwise(F.col("quantity")).cast("int")
)

# Transformation : Remove any '$' or other symbols from unit_price, keep only numeric
df = df.withColumn(
    "unit_price",
    F.regexp_replace("unit_price", "[$]", "").cast("double")
)

# Transformation : Remove '%' from discount_pct and cast to double
df = df.withColumn(
    "discount_pct",
    F.regexp_replace("discount_pct", "%", "").cast("double")
)

# Transformation : coupon code processing (convert to lower)
df = df.withColumn(
    "coupon_code", F.lower(F.trim(F.col("coupon_code")))
)

# Transformation : channel processing 
df = df.withColumn(
    "channel",
    F.when(F.col("channel") == "web", "Website")
    .when(F.col("channel") == "app", "Mobile")
    .otherwise(F.col("channel")),
)

# COMMAND ----------

display(df)

# COMMAND ----------


# Transformation: datatype conversions
# 1) Convert dt (string → date)
# df = df.withColumn(
#     "dt",
#     F.to_date("dt", "yyyy-MM-dd")     
# )

# 1) Convert dt (string → date)
df = df.withColumn(
    "dt",
    F.coalesce(
        F.expr("try_to_date(dt, 'yyyy-MM-dd')"),    # 2025-08-05
        F.expr("try_to_date(dt, 'M/d/yyyy')"),      # 8/5/2025
        F.expr("try_to_date(dt, 'MM/dd/yyyy')"),    # 08/05/2025
        F.expr("try_to_date(dt, 'dd-MM-yyyy')"),    # 05-08-2025
    )
)

# 2) Convert order_ts (string → timestamp)
df = df.withColumn(
    "order_ts",
    F.coalesce(
        F.expr("try_to_timestamp(order_ts, 'yyyy-MM-dd HH:mm:ss')"),  # 2025-08-01 22:53:52
        F.expr("try_to_timestamp(order_ts, 'dd-MM-yyyy HH:mm')"),     # 01-08-2025 22:53
        F.expr("try_to_timestamp(order_ts, 'M/d/yyyy HH:mm')"),       # 8/5/2025 22:41  ← new
        F.expr("try_to_timestamp(order_ts, 'MM/dd/yyyy HH:mm')"),     # 08/05/2025 22:41
    )
)




# 3) Convert item_seq (string → integer)
df = df.withColumn(
    "item_seq",
    F.col("item_seq").cast("int")
)

# 4) Convert tax_amount (string → double, strip non-numeric characters)
df = df.withColumn(
    "tax_amount",
    F.regexp_replace("tax_amount", r"[^0-9.\-]", "").cast("double")
)


#Transformation : Add processed time 
df = df.withColumn(
    "processed_time", F.current_timestamp()
)

# COMMAND ----------

display(df.limit(5))

# COMMAND ----------

# check the final datatypes
df.printSchema()

# COMMAND ----------

# Write raw data to the silver layer (catalog: ecommerce, schema: silver, table: slv_brands)
df.write.format("delta") \
    .mode("overwrite") \
    .option("mergeSchema", "true") \
    .saveAsTable(f"{catalog_name}.sliver.slv_order_items")