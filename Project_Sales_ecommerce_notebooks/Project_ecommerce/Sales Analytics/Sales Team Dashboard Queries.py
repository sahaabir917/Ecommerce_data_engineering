# Databricks notebook source
# MAGIC %sql
# MAGIC
# MAGIC WITH category_product_sales AS (
# MAGIC     SELECT
# MAGIC         category_name,
# MAGIC         product_id,
# MAGIC         SUM(net_amount)                    AS total_revenue,
# MAGIC         SUM(quantity)                      AS total_quantity_sold,
# MAGIC         COUNT(DISTINCT transaction_id)     AS total_orders,
# MAGIC         DENSE_RANK() OVER (
# MAGIC             PARTITION BY category_name
# MAGIC             ORDER BY SUM(net_amount) DESC
# MAGIC         )                                  AS rank
# MAGIC     FROM ecommerce.gold.fact_transactions_denorm
# MAGIC     GROUP BY
# MAGIC         category_name,
# MAGIC         product_id
# MAGIC )
# MAGIC
# MAGIC -- Step 4 — Filter top 5 per category
# MAGIC SELECT
# MAGIC     rank,
# MAGIC     category_name,
# MAGIC     product_id,
# MAGIC     total_orders,
# MAGIC     total_quantity_sold,
# MAGIC     total_revenue
# MAGIC FROM category_product_sales
# MAGIC WHERE rank <= 5
# MAGIC ORDER BY category_name, rank;

# COMMAND ----------

from pyspark.sql import Window
from pyspark.sql.functions import col, sum as _sum, count_distinct, dense_rank

df = spark.table("ecommerce.gold.fact_transactions_denorm")

# Step 1 — aggregate first, get total revenue per product per category
df_agg = df.groupBy("category_name", "product_id").agg( _sum("net_amount").alias("total_revenue"),
                _sum("quantity").alias("total_quantity_sold"),
               count_distinct("transaction_id").alias("total_orders")
           )

# Step 2 — define window AFTER aggregation
partition = Window.partitionBy("category_name").orderBy(col("total_revenue").desc())

# Step 3 — apply dense_rank on aggregated revenue
df_wind = df_agg.withColumn("rank", dense_rank().over(partition))

# Step 4 — filter top 5 per category
df_top5 = df_wind.filter(col("rank") <= 5) \
                 .orderBy("category_name", "rank")

df_top5.display()

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 
# MAGIC     transaction_date,
# MAGIC     COUNT(DISTINCT transaction_id) AS total_orders,
# MAGIC     SUM(quantity) AS total_items_sold,
# MAGIC     SUM(gross_amount) AS total_revenue,
# MAGIC     SUM(net_amount) AS total_net_revenue
# MAGIC FROM ecommerce.gold.fact_transactions_denorm
# MAGIC GROUP BY transaction_date
# MAGIC ORDER BY transaction_date;

# COMMAND ----------

# MAGIC %md
# MAGIC Peak selling hours by day

# COMMAND ----------

from pyspark.sql import Window
from pyspark.sql.functions import (
    col, hour, sum as _sum,
    count_distinct, dense_rank
)

# Load table
df = spark.table("ecommerce.gold.fact_transactions_denorm")

# Step 1 — Aggregate by day_name and hour
df_agg = df.groupBy(
            "day_name",
            hour("transaction_ts").alias("sale_hour")
          ) \
          .agg(
              _sum("net_amount").alias("total_revenue"),
              count_distinct("transaction_id").alias("total_orders")
          )

# Step 2 — Define partition window
partition = Window.partitionBy("day_name") \
                  .orderBy(col("total_revenue").desc())

# Step 3 — Apply dense_rank
df_ranked = df_agg.withColumn("hour_rank", dense_rank().over(partition))

# Step 4 — Filter top 3 hours per day
df_top3 = df_ranked.filter(col("hour_rank") <= 3) \
                   .select(
                       "day_name",
                       "hour_rank",
                       "sale_hour",
                       "total_orders",
                       "total_revenue"
                   ) \
                   .orderBy("day_name", "hour_rank")

df_top3.display()

# COMMAND ----------

# MAGIC %sql
# MAGIC WITH ranked AS (
# MAGIC     SELECT 
# MAGIC         day_name,
# MAGIC         HOUR(transaction_ts)                       AS sale_hour,
# MAGIC         COUNT(DISTINCT transaction_id)             AS total_orders,
# MAGIC         SUM(net_amount)                            AS total_revenue,
# MAGIC         DENSE_RANK() OVER (
# MAGIC             PARTITION BY day_name
# MAGIC             ORDER BY SUM(net_amount) DESC
# MAGIC         )                                          AS hour_rank
# MAGIC     FROM ecommerce.gold.fact_transactions_denorm
# MAGIC     GROUP BY 
# MAGIC         day_name, 
# MAGIC         HOUR(transaction_ts)
# MAGIC )
# MAGIC SELECT 
# MAGIC     day_name,
# MAGIC     hour_rank,
# MAGIC     sale_hour,
# MAGIC     total_orders,
# MAGIC     total_revenue
# MAGIC FROM ranked
# MAGIC WHERE hour_rank <= 5
# MAGIC ORDER BY day_name, hour_rank;