# Databricks notebook source
import pyspark.sql.functions as F
from pyspark.sql.types import StringType, IntegerType, DataType, TimestampType,FloatType

catalog_name = "ecommerce"

df_bronze = spark.table(f"{catalog_name}.bronze.brz_brands")
df_bronze.show(10)



# COMMAND ----------

# MAGIC %md
# MAGIC Remove Alpha Numeric Charecter

# COMMAND ----------

df_silver = df_bronze.withColumn("brand_code", F.regexp_replace(F.col("brand_code"), r'[^A-Za-z0-9]', ""))
df_silver.display(10)

# COMMAND ----------

# MAGIC %md
# MAGIC Trim the brand name for leading and trending space

# COMMAND ----------

df_silver = df_silver.withColumn("brand_name", F.trim(F.col("brand_name")))
df_silver.display(10)

# COMMAND ----------

# MAGIC %md
# MAGIC Find All Unique Category Code

# COMMAND ----------

df_silver_category = df_silver.select(F.col("category_code")).distinct()
df_silver_category.display()

# COMMAND ----------

# MAGIC %md
# MAGIC Change The Anomalies 

# COMMAND ----------

 anomalies = {
        "GROCERY": "GRCY",
        "BOOKS" : "BKS",
        "TOYS" : "TOY"
    }

df_silver = df_silver.replace(anomalies, subset=["category_code"])

df_silver.display()

# COMMAND ----------

# MAGIC %md
# MAGIC Create Brand Table In Sliver Schema (Delta Table)

# COMMAND ----------

df_silver.write.format("delta").mode("overwrite").option("mergeSchema", "true").saveAsTable(f"{catalog_name}.sliver.slv_brands")

# COMMAND ----------

# MAGIC %md
# MAGIC Access From Database

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * from ecommerce.sliver.slv_brands limit 100

# COMMAND ----------

# MAGIC %md
# MAGIC Working On Category Table
# MAGIC

# COMMAND ----------

df_bronze = spark.table(f"{catalog_name}.bronze.brz_category")
df_bronze.display()

# COMMAND ----------

from pyspark.sql.functions import *
df_duplicates = df_bronze.groupBy("category_code").agg(count("*").alias("total_count")).filter(F.col("total_count")>1)
df_duplicates.show()

# COMMAND ----------

df_silver = df_bronze.dropDuplicates(['category_code'])
display(df_silver)


# COMMAND ----------

df_silver = df_silver.withColumn("category_code", F.upper(F.col("category_code")))
df_silver.display()

# COMMAND ----------

df_silver.write.format("delta").mode("overwrite").option("mergeSchema", "true").saveAsTable(f"{catalog_name}.sliver.slv_category")

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from ecommerce.sliver.slv_category limit 3

# COMMAND ----------

df_bronze = spark.table(f"{catalog_name}.bronze.brz_products")
df_bronze.display()

# COMMAND ----------

# MAGIC %md
# MAGIC Search by brand Name with or codition

# COMMAND ----------

# DBTITLE 1,Cell 22
df_brand_wise_search = df_bronze.select(F.col("*")).filter((F.col("brand_code") == "STCR") | (F.col("brand_code") == "stcr"))
df_brand_wise_search.display(10)

# COMMAND ----------

# MAGIC %md
# MAGIC Total Row and colum of product Table

# COMMAND ----------

row_count, column_count = df_bronze.count(), len(df_bronze.columns)
print(f"Total rows: {row_count}")
print(f"Total columns: {column_count}")

# COMMAND ----------

# MAGIC %md
# MAGIC Check weight_grams column

# COMMAND ----------

df_weight = df_bronze.select("weight_grams")
df_weight.limit(5).display()

# COMMAND ----------

# MAGIC %md
# MAGIC Remove "g" and make it integer

# COMMAND ----------

df_silver = df_bronze.withColumn("weight_grams", F.regexp_replace(F.col("weight_grams"), "g", "").cast(IntegerType()))
df_silver.limit(5).display()

# COMMAND ----------

df_silver.printSchema()

# COMMAND ----------

# MAGIC %md
# MAGIC Category code and Brand Code needs to be Captial

# COMMAND ----------

df_silver = df_silver.withColumn("brand_code", F.upper(F.col("brand_code"))).withColumn("category_code", F.upper(F.col("category_code")))
df_silver.limit(10).display()

# COMMAND ----------

# MAGIC %md
# MAGIC Now convert the length_cm string to float. Need to apply the replace , and put . then make it float

# COMMAND ----------

df_silver = df_silver.withColumn("length_cm", F.regexp_replace(F.col("length_cm"), ",",".").cast(FloatType()))
df_silver.limit(5).display()

# COMMAND ----------

df_silver.printSchema()

# COMMAND ----------

df_silver.select("material").distinct().show()

# <!--  Fix spelling mistakes -->

df_silver = df_silver.withColumn("material",F.when(F.col("material") == "Coton", "Cotton").when(F.col("material") == "Alumium", "Aluminum").when(F.col("material") == "Ruber", "Rubber").otherwise(F.col("material")))

df_silver.select("material").distinct().show()

# COMMAND ----------

df_silver.filter(F.col('rating_count')<0).select("rating_count").show(3)
# Convert negative rating_count to positive. If null, replace with 0

df_silver = df_silver.withColumn("rating_count", F.when(F.col("rating_count").isNotNull(), F.abs(F.col("rating_count"))).otherwise(F.lit(0)))
df_silver.limit(4).display()

# COMMAND ----------

    df_silver.filter(F.col('rating_count')<0).select("rating_count").show(3)

    # Convert negative rating_count to positive. If null, replace with 0

    df_silver = df_silver.withColumn("rating_count", F.when(F.col("rating_count").isNotNull(), F.abs(F.col("rating_count"))).otherwise(F.lit(0)))

# COMMAND ----------

df_silver.select(
        "weight_grams",
        "length_cm",
        "category_code",
        "brand_code",
        "material",
        "rating_count"
    ).show(10, truncate=False)

# COMMAND ----------

df_silver.write.format("delta").mode("overwrite").option("mergeSchema", "true").saveAsTable(f"{catalog_name}.sliver.slv_products")

# COMMAND ----------

df_bronze = spark.read.table(f"{catalog_name}.bronze.brz_customer")

row_count, column_count = df_bronze.count(), len(df_bronze.columns)

# <!-- # Print the results -->
print(f"Row count: {row_count}")
print(f"Column count: {column_count}")

df_bronze.show(10)

# COMMAND ----------

null_count = df_bronze.filter(F.col("customer_id").isNull()).count()
print(null_count)



# COMMAND ----------

# There are 300 null values in customer_id column. Display some of those

df_bronze.filter(F.col("customer_id").isNull()).show(3)

# Drop rows where 'customer_id' is null

df_silver = df_bronze.dropna(subset=["customer_id"])

# Get row count

row_count = df_silver.count()
print(f"Row count after droping null values: {row_count}")

# COMMAND ----------

null_count = df_silver.filter(F.col("phone").isNull()).count()
print(f"Number of nulls in phone: {null_count}")
df_silver.filter(F.col("phone").isNull()).show(3)

### Fill null values with 'Not Available'
df_silver = df_silver.fillna("Not Available", subset=["phone"])
# sanity check (If any nulls still exist)
df_silver.filter(F.col("phone").isNull()).show()
df_silver.show(5)

# COMMAND ----------

df_silver.write.format("delta")\
.mode("overwrite")\
.option("mergeSchema", "true")\
.saveAsTable(f"{catalog_name}.sliver.slv_customers")

# COMMAND ----------

# MAGIC %md
# MAGIC Calender Data

# COMMAND ----------

df_bronze = spark.read.table(f"{catalog_name}.bronze.brz_date")

    # Get row and column count
row_count, column_count = df_bronze.count(), len(df_bronze.columns)

  # Print the results
print(f"Row count: {row_count}")
print(f"Column count: {column_count}")

df_bronze.show(3)

# COMMAND ----------

from pyspark.sql.functions import to_date
df_silver = df_bronze.withColumn("date", to_date(df_bronze["date"], "dd-MM-yyyy"))
print(df_silver.printSchema())
df_silver.show(5)

# COMMAND ----------

print(df_silver.printSchema())

df_silver.show(5)

# COMMAND ----------

# Find duplicate rows in the DataFrame
duplicates = df_silver.groupBy('date').count().filter("count > 1")

# Show the duplicate rows
print("Total duplicated Rows: ", duplicates.count())
display(duplicates)

# COMMAND ----------

# Remove duplicate rows
df_silver = df_silver.dropDuplicates(['date'])

# Get row count
row_count = df_silver.count()

print("Rows After removing Duplicates: ", row_count)

# COMMAND ----------

# Capitalize first letter of each word in day_name
df_silver = df_silver.withColumn("day_name", F.initcap(F.col("day_name")))

df_silver.show(5)

# COMMAND ----------

df_silver = df_silver.withColumn("week_of_year", F.abs(F.col("week_of_year")))  # Convert negative to positive

df_silver.show(3)

# COMMAND ----------

df_silver = df_silver.withColumn("quarter", F.concat_ws("", F.concat(F.lit("Q"), F.col("quarter"), F.lit("-"), F.col("year"))))

df_silver = df_silver.withColumn("week_of_year", F.concat_ws("-", F.concat(F.lit("Week"), F.col("week_of_year"), F.lit("-"), F.col("year"))))

df_silver.show(3)

# COMMAND ----------

# Rename a column
df_silver = df_silver.withColumnRenamed("week_of_year", "week")

# COMMAND ----------

# Write raw data to the silver layer (catalog: ecommerce, schema: silver, table: slv_calendar)
df_silver.write.format("delta") \
    .mode("overwrite") \
    .option("mergeSchema", "true") \
    .saveAsTable(f"{catalog_name}.sliver.slv_calendar")