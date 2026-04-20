# Databricks notebook source
# MAGIC %md
# MAGIC Three Month Comparison

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   month_name,
# MAGIC   COUNT(DISTINCT transaction_id) AS total_orders,
# MAGIC   SUM(quantity) AS total_items_sold,
# MAGIC   SUM(gross_amount) AS total_revenue,
# MAGIC   SUM(net_amount) AS net_revenue,
# MAGIC   AVG(gross_amount) AS avg_order_value
# MAGIC FROM
# MAGIC   ecommerce.gold.fact_transactions_denorm
# MAGIC WHERE
# MAGIC   month_name IN ('August', 'September', 'October')
# MAGIC GROUP BY
# MAGIC   month_name
# MAGIC ORDER BY
# MAGIC   CASE month_name
# MAGIC     WHEN 'August' THEN 1
# MAGIC     WHEN 'September' THEN 2
# MAGIC     WHEN 'October' THEN 3
# MAGIC   END

# COMMAND ----------

# MAGIC %md
# MAGIC Brand Ranking with Window Function

# COMMAND ----------

# MAGIC %sql
# MAGIC WITH brand_stats AS (
# MAGIC   SELECT
# MAGIC     brand_name,
# MAGIC     COUNT(*) as transaction_count,
# MAGIC     RANK() OVER (ORDER BY COUNT(*) DESC) as brand_rank
# MAGIC   FROM
# MAGIC     ecommerce.gold.fact_transactions_denorm
# MAGIC   GROUP BY
# MAGIC     brand_name
# MAGIC )
# MAGIC SELECT
# MAGIC   t.*,
# MAGIC   bs.brand_rank
# MAGIC FROM
# MAGIC   ecommerce.gold.fact_transactions_denorm t
# MAGIC     LEFT JOIN brand_stats bs
# MAGIC       ON t.brand_name = bs.brand_name

# COMMAND ----------

# MAGIC %md
# MAGIC Global Ecommerce Orders and Revenue by Country Summary

# COMMAND ----------

# MAGIC %sql
# MAGIC USE CATALOG `workspace`;
# MAGIC USE SCHEMA `default`;
# MAGIC
# MAGIC SELECT 
# MAGIC     customer_country,
# MAGIC     COUNT(*) AS total_orders,
# MAGIC     SUM(gross_amount) AS revenue
# MAGIC FROM ecommerce.gold.fact_transactions_denorm
# MAGIC GROUP BY customer_country
# MAGIC ORDER BY revenue DESC

# COMMAND ----------

# MAGIC %md
# MAGIC Top 5 product from each category based on the sales

# COMMAND ----------

# MAGIC %sql
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

# MAGIC %md
# MAGIC Daily Sales Trends

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
# MAGIC Top Three Revenue Hours by Day for Ecommerce Sales

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

# COMMAND ----------

# MAGIC %md
# MAGIC Cupon vs Non-Cupon reports

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 
# MAGIC     CASE 
# MAGIC         WHEN coupon_flag = 1 THEN 'Coupon'
# MAGIC         ELSE 'Non-Coupon'
# MAGIC     END                                        AS order_type,
# MAGIC     COUNT(DISTINCT transaction_id)             AS total_orders,
# MAGIC     SUM(quantity)                              AS total_items_sold,
# MAGIC     SUM(gross_amount)                          AS total_gross_revenue,
# MAGIC     SUM(net_amount)                            AS total_net_revenue,
# MAGIC     SUM(discount_amount)                       AS total_discount
# MAGIC FROM ecommerce.gold.fact_transactions_denorm
# MAGIC GROUP BY coupon_flag
# MAGIC ORDER BY coupon_flag DESC;

# COMMAND ----------

# MAGIC %md
# MAGIC Product Profitability Analysis

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   product_id,
# MAGIC   brand_name,
# MAGIC   category_name,
# MAGIC   COUNT(DISTINCT transaction_id) AS total_orders,
# MAGIC   SUM(quantity) AS total_quantity,
# MAGIC   SUM(gross_amount) AS total_revenue,
# MAGIC   SUM(net_amount) AS total_net_revenue,
# MAGIC   AVG(discount_percent) AS avg_discount_pct,
# MAGIC   SUM(discount_amount) AS total_discount,
# MAGIC   ROUND((SUM(net_amount) / NULLIF(SUM(gross_amount), 0)) * 100, 2) AS net_margin_pct,
# MAGIC   ROUND(SUM(net_amount) / NULLIF(SUM(quantity), 0), 2) AS net_revenue_per_unit
# MAGIC FROM
# MAGIC   ecommerce.gold.fact_transactions_denorm
# MAGIC GROUP BY
# MAGIC   product_id,
# MAGIC   brand_name,
# MAGIC   category_name
# MAGIC HAVING
# MAGIC   SUM(gross_amount) > 0
# MAGIC ORDER BY
# MAGIC   total_revenue DESC

# COMMAND ----------

# MAGIC %md
# MAGIC Discount Impact by Category

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   category_name,
# MAGIC   COUNT(DISTINCT transaction_id) AS total_orders,
# MAGIC   SUM(gross_amount) AS gross_revenue,
# MAGIC   SUM(net_amount) AS net_revenue,
# MAGIC   SUM(discount_amount) AS total_discount_given,
# MAGIC   ROUND(AVG(discount_percent), 2) AS avg_discount_pct,
# MAGIC   ROUND((SUM(discount_amount) / NULLIF(SUM(gross_amount), 0)) * 100, 2) AS discount_impact_pct
# MAGIC FROM
# MAGIC   ecommerce.gold.fact_transactions_denorm
# MAGIC GROUP BY
# MAGIC   category_name
# MAGIC ORDER BY
# MAGIC   total_discount_given DESC

# COMMAND ----------

High Discount Low Volume Waste

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   transaction_id,
# MAGIC   product_id,
# MAGIC   brand_name,
# MAGIC   category_name,
# MAGIC   quantity,
# MAGIC   gross_amount,
# MAGIC   discount_percent,
# MAGIC   discount_amount,
# MAGIC   net_amount,
# MAGIC   transaction_date
# MAGIC FROM
# MAGIC   ecommerce.gold.fact_transactions_denorm
# MAGIC WHERE
# MAGIC   discount_percent > 30
# MAGIC   AND quantity <= 2
# MAGIC ORDER BY
# MAGIC   discount_percent DESC,
# MAGIC   gross_amount DESC
# MAGIC LIMIT 1000  

# COMMAND ----------

# MAGIC %md
# MAGIC Top Customers by Lifetime Value

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   customer_id,
# MAGIC   customer_country,
# MAGIC   customer_region,
# MAGIC   customer_state,
# MAGIC   COUNT(DISTINCT transaction_id) AS total_orders,
# MAGIC   SUM(quantity) AS total_items_purchased,
# MAGIC   SUM(gross_amount) AS lifetime_gross_revenue,
# MAGIC   SUM(net_amount) AS lifetime_net_revenue,
# MAGIC   ROUND(AVG(gross_amount), 2) AS avg_order_value,
# MAGIC   SUM(discount_amount) AS total_discounts_used,
# MAGIC   MIN(transaction_date) AS first_purchase_date,
# MAGIC   MAX(transaction_date) AS last_purchase_date
# MAGIC FROM
# MAGIC   ecommerce.gold.fact_transactions_denorm
# MAGIC GROUP BY
# MAGIC   customer_id,
# MAGIC   customer_country,
# MAGIC   customer_region,
# MAGIC   customer_state
# MAGIC ORDER BY
# MAGIC   lifetime_net_revenue DESC
# MAGIC LIMIT 100

# COMMAND ----------

# MAGIC %md
# MAGIC Top 5 Products for Promotion - Profit Maximization

# COMMAND ----------

# MAGIC %sql
# MAGIC WITH product_metrics AS (
# MAGIC   SELECT
# MAGIC     product_id,
# MAGIC     brand_name,
# MAGIC     category_name,
# MAGIC     COUNT(DISTINCT transaction_id) AS total_orders,
# MAGIC     SUM(quantity) AS total_quantity,
# MAGIC     SUM(gross_amount) AS total_revenue,
# MAGIC     SUM(net_amount) AS total_net_revenue,
# MAGIC     ROUND(AVG(discount_percent), 2) AS avg_discount_pct,
# MAGIC     SUM(discount_amount) AS total_discount,
# MAGIC     ROUND((SUM(net_amount) / NULLIF(SUM(gross_amount), 0)) * 100, 2) AS net_margin_pct,
# MAGIC     ROUND(SUM(net_amount) / NULLIF(SUM(quantity), 0), 2) AS net_revenue_per_unit
# MAGIC   FROM ecommerce.gold.fact_transactions_denorm
# MAGIC   GROUP BY product_id, brand_name, category_name
# MAGIC   HAVING SUM(gross_amount) > 0
# MAGIC ),
# MAGIC avg_metrics AS (
# MAGIC   SELECT
# MAGIC     AVG(net_margin_pct) AS avg_net_margin,
# MAGIC     AVG(total_quantity) AS avg_volume,
# MAGIC     AVG(avg_discount_pct) AS avg_discount
# MAGIC   FROM product_metrics
# MAGIC ),
# MAGIC scored_products AS (
# MAGIC   SELECT
# MAGIC     p.product_id,
# MAGIC     p.brand_name,
# MAGIC     p.category_name,
# MAGIC     p.total_orders,
# MAGIC     p.total_quantity,
# MAGIC     p.total_revenue,
# MAGIC     p.total_net_revenue,
# MAGIC     p.avg_discount_pct,
# MAGIC     p.net_margin_pct,
# MAGIC     p.net_revenue_per_unit,
# MAGIC     -- Profitability score: weighted combination of key metrics
# MAGIC     (
# MAGIC       (p.net_margin_pct / NULLIF(a.avg_net_margin, 0)) * 40 +  -- 40% weight on margin
# MAGIC       (p.total_quantity / NULLIF(a.avg_volume, 0)) * 30 +       -- 30% weight on volume
# MAGIC       (1 - (p.avg_discount_pct / NULLIF(a.avg_discount, 0))) * 30  -- 30% weight on low discount dependency
# MAGIC     ) AS profit_score
# MAGIC   FROM product_metrics p
# MAGIC   CROSS JOIN avg_metrics a
# MAGIC   WHERE p.net_margin_pct >= a.avg_net_margin  -- Only products with above-average margin
# MAGIC     AND p.total_orders >= 50  -- Proven demand
# MAGIC )
# MAGIC SELECT
# MAGIC   product_id,
# MAGIC   brand_name,
# MAGIC   category_name,
# MAGIC   total_orders,
# MAGIC   total_quantity,
# MAGIC   total_revenue,
# MAGIC   total_net_revenue,
# MAGIC   avg_discount_pct,
# MAGIC   net_margin_pct,
# MAGIC   net_revenue_per_unit,
# MAGIC   ROUND(profit_score, 2) AS profit_score
# MAGIC FROM scored_products
# MAGIC ORDER BY profit_score DESC
# MAGIC LIMIT 5

# COMMAND ----------

# MAGIC %md
# MAGIC Simple Dependency Risk Score

# COMMAND ----------

# MAGIC %sql
# MAGIC WITH product_revenue AS (
# MAGIC   SELECT
# MAGIC     product_id,
# MAGIC     SUM(net_amount) AS revenue
# MAGIC   FROM
# MAGIC     ecommerce.gold.fact_transactions_denorm
# MAGIC   GROUP BY
# MAGIC     product_id
# MAGIC ),
# MAGIC product_ranked AS (
# MAGIC   SELECT
# MAGIC     product_id,
# MAGIC     revenue,
# MAGIC     ROW_NUMBER() OVER (ORDER BY revenue DESC) AS rank,
# MAGIC     SUM(revenue) OVER () AS total_revenue
# MAGIC   FROM
# MAGIC     product_revenue
# MAGIC ),
# MAGIC customer_revenue AS (
# MAGIC   SELECT
# MAGIC     customer_id,
# MAGIC     SUM(net_amount) AS revenue
# MAGIC   FROM
# MAGIC     ecommerce.gold.fact_transactions_denorm
# MAGIC   GROUP BY
# MAGIC     customer_id
# MAGIC ),
# MAGIC customer_ranked AS (
# MAGIC   SELECT
# MAGIC     customer_id,
# MAGIC     revenue,
# MAGIC     ROW_NUMBER() OVER (ORDER BY revenue DESC) AS rank,
# MAGIC     SUM(revenue) OVER () AS total_revenue
# MAGIC   FROM
# MAGIC     customer_revenue
# MAGIC )
# MAGIC SELECT
# MAGIC   'Top 100 Products' AS metric,
# MAGIC   ROUND((SUM(revenue) / MAX(total_revenue)) * 100, 1) AS concentration_pct,
# MAGIC   CASE
# MAGIC     WHEN ROUND((SUM(revenue) / MAX(total_revenue)) * 100, 1) < 20 THEN 'Low Risk - Well Diversified'
# MAGIC     WHEN ROUND((SUM(revenue) / MAX(total_revenue)) * 100, 1) < 50 THEN 'Medium Risk'
# MAGIC     ELSE 'High Risk - Too Dependent'
# MAGIC   END AS risk_level
# MAGIC FROM
# MAGIC   product_ranked
# MAGIC WHERE
# MAGIC   rank <= 100
# MAGIC UNION ALL
# MAGIC SELECT
# MAGIC   'Top 100 Customers' AS metric,
# MAGIC   ROUND((SUM(revenue) / MAX(total_revenue)) * 100, 1) AS concentration_pct,
# MAGIC   CASE
# MAGIC     WHEN ROUND((SUM(revenue) / MAX(total_revenue)) * 100, 1) < 20 THEN 'Low Risk - Well Diversified'
# MAGIC     WHEN ROUND((SUM(revenue) / MAX(total_revenue)) * 100, 1) < 50 THEN 'Medium Risk'
# MAGIC     ELSE 'High Risk - Too Dependent'
# MAGIC   END AS risk_level
# MAGIC FROM
# MAGIC   customer_ranked
# MAGIC WHERE
# MAGIC   rank <= 100

# COMMAND ----------

# MAGIC %md
# MAGIC Discount Range ROI Analysis

# COMMAND ----------

# MAGIC %sql
# MAGIC WITH discount_ranges AS (
# MAGIC   SELECT
# MAGIC     CASE
# MAGIC       WHEN discount_percent = 0 THEN 'No Discount (0%)'
# MAGIC       WHEN
# MAGIC         discount_percent > 0
# MAGIC         AND discount_percent <= 10
# MAGIC       THEN
# MAGIC         '1-10%'
# MAGIC       WHEN
# MAGIC         discount_percent > 10
# MAGIC         AND discount_percent <= 20
# MAGIC       THEN
# MAGIC         '11-20%'
# MAGIC       WHEN
# MAGIC         discount_percent > 20
# MAGIC         AND discount_percent <= 30
# MAGIC       THEN
# MAGIC         '21-30%'
# MAGIC       WHEN discount_percent > 30 THEN '31%+'
# MAGIC     END AS discount_range,
# MAGIC     transaction_id,
# MAGIC     gross_amount,
# MAGIC     discount_amount,
# MAGIC     net_amount,
# MAGIC     quantity
# MAGIC   FROM
# MAGIC     ecommerce.gold.fact_transactions_denorm
# MAGIC )
# MAGIC SELECT
# MAGIC   discount_range,
# MAGIC   COUNT(DISTINCT transaction_id) AS total_orders,
# MAGIC   SUM(quantity) AS total_items_sold,
# MAGIC   SUM(gross_amount) AS total_gross_revenue,
# MAGIC   SUM(discount_amount) AS total_discount_given,
# MAGIC   SUM(net_amount) AS total_net_revenue,
# MAGIC   ROUND(AVG(gross_amount), 2) AS avg_order_value,
# MAGIC   ROUND(AVG(discount_amount), 2) AS avg_discount_per_order,
# MAGIC   -- ROI: Revenue generated per dollar of discount given
# MAGIC   ROUND(SUM(net_amount) / NULLIF(SUM(discount_amount), 0), 2) AS roi_revenue_per_discount_dollar,
# MAGIC   -- Conversion efficiency: Net revenue as % of gross revenue
# MAGIC   ROUND((SUM(net_amount) / NULLIF(SUM(gross_amount), 0)) * 100, 2) AS net_revenue_retention_pct
# MAGIC FROM
# MAGIC   discount_ranges
# MAGIC GROUP BY
# MAGIC   discount_range
# MAGIC ORDER BY
# MAGIC   CASE discount_range
# MAGIC     WHEN 'No Discount (0%)' THEN 1
# MAGIC     WHEN '1-10%' THEN 2
# MAGIC     WHEN '11-20%' THEN 3
# MAGIC     WHEN '21-30%' THEN 4
# MAGIC     WHEN '31%+' THEN 5
# MAGIC   END

# COMMAND ----------

# MAGIC %md
# MAGIC Minimum Discount Threshold Analysis

# COMMAND ----------

# MAGIC %sql
# MAGIC WITH discount_segments AS (
# MAGIC   SELECT
# MAGIC     CASE
# MAGIC       WHEN discount_percent = 0 THEN '0% (No Discount)'
# MAGIC       WHEN
# MAGIC         discount_percent > 0
# MAGIC         AND discount_percent <= 5
# MAGIC       THEN
# MAGIC         '1-5%'
# MAGIC       WHEN
# MAGIC         discount_percent > 5
# MAGIC         AND discount_percent <= 10
# MAGIC       THEN
# MAGIC         '6-10%'
# MAGIC       WHEN
# MAGIC         discount_percent > 10
# MAGIC         AND discount_percent <= 15
# MAGIC       THEN
# MAGIC         '11-15%'
# MAGIC       WHEN
# MAGIC         discount_percent > 15
# MAGIC         AND discount_percent <= 20
# MAGIC       THEN
# MAGIC         '16-20%'
# MAGIC       WHEN
# MAGIC         discount_percent > 20
# MAGIC         AND discount_percent <= 25
# MAGIC       THEN
# MAGIC         '21-25%'
# MAGIC       WHEN
# MAGIC         discount_percent > 25
# MAGIC         AND discount_percent <= 30
# MAGIC       THEN
# MAGIC         '26-30%'
# MAGIC       WHEN discount_percent > 30 THEN '31%+'
# MAGIC     END AS discount_tier,
# MAGIC     transaction_id,
# MAGIC     gross_amount,
# MAGIC     discount_amount,
# MAGIC     net_amount,
# MAGIC     quantity,
# MAGIC     discount_percent
# MAGIC   FROM
# MAGIC     ecommerce.gold.fact_transactions_denorm
# MAGIC )
# MAGIC SELECT
# MAGIC   discount_tier,
# MAGIC   COUNT(DISTINCT transaction_id) AS order_count,
# MAGIC   SUM(quantity) AS items_sold,
# MAGIC   ROUND(AVG(discount_percent), 2) AS avg_discount_in_tier,
# MAGIC   SUM(gross_amount) AS gross_revenue,
# MAGIC   SUM(net_amount) AS net_revenue,
# MAGIC   ROUND(AVG(gross_amount), 2) AS avg_order_value,
# MAGIC   -- Order velocity index (normalized to no-discount baseline)
# MAGIC   ROUND(
# MAGIC     COUNT(DISTINCT transaction_id)
# MAGIC       * 1.0
# MAGIC       / (
# MAGIC         SELECT
# MAGIC           COUNT(DISTINCT transaction_id)
# MAGIC         FROM
# MAGIC           discount_segments
# MAGIC         WHERE
# MAGIC           discount_percent = 0
# MAGIC       )
# MAGIC       * 100,
# MAGIC     1
# MAGIC   ) AS order_velocity_index
# MAGIC FROM
# MAGIC   discount_segments
# MAGIC GROUP BY
# MAGIC   discount_tier
# MAGIC ORDER BY
# MAGIC   CASE discount_tier
# MAGIC     WHEN '0% (No Discount)' THEN 1
# MAGIC     WHEN '1-5%' THEN 2
# MAGIC     WHEN '6-10%' THEN 3
# MAGIC     WHEN '11-15%' THEN 4
# MAGIC     WHEN '16-20%' THEN 5
# MAGIC     WHEN '21-25%' THEN 6
# MAGIC     WHEN '26-30%' THEN 7
# MAGIC     WHEN '31%+' THEN 8
# MAGIC   END

# COMMAND ----------

# MAGIC %md
# MAGIC Product Demand Stability Analysis

# COMMAND ----------

# MAGIC %sql
# MAGIC WITH daily_product_sales AS (
# MAGIC   SELECT
# MAGIC     product_id,
# MAGIC     brand_name,
# MAGIC     category_name,
# MAGIC     transaction_date,
# MAGIC     COUNT(DISTINCT transaction_id) AS daily_orders,
# MAGIC     SUM(quantity) AS daily_quantity,
# MAGIC     SUM(net_amount) AS daily_revenue
# MAGIC   FROM
# MAGIC     ecommerce.gold.fact_transactions_denorm
# MAGIC   GROUP BY
# MAGIC     product_id,
# MAGIC     brand_name,
# MAGIC     category_name,
# MAGIC     transaction_date
# MAGIC ),
# MAGIC product_volatility AS (
# MAGIC   SELECT
# MAGIC     product_id,
# MAGIC     brand_name,
# MAGIC     category_name,
# MAGIC     COUNT(DISTINCT transaction_date) AS days_active,
# MAGIC     AVG(daily_quantity) AS avg_daily_quantity,
# MAGIC     STDDEV(daily_quantity) AS stddev_daily_quantity,
# MAGIC     SUM(daily_quantity) AS total_quantity_sold,
# MAGIC     SUM(daily_revenue) AS total_revenue,
# MAGIC     -- Coefficient of Variation (CV) = (Std Dev / Mean) * 100
# MAGIC     ROUND(
# MAGIC       (STDDEV(daily_quantity) / NULLIF(AVG(daily_quantity), 0)) * 100,
# MAGIC       2
# MAGIC     ) AS demand_volatility_pct
# MAGIC   FROM
# MAGIC     daily_product_sales
# MAGIC   GROUP BY
# MAGIC     product_id,
# MAGIC     brand_name,
# MAGIC     category_name
# MAGIC   HAVING
# MAGIC     COUNT(DISTINCT transaction_date) >= 5 -- Products with at least 5 days of sales
# MAGIC     AND AVG(daily_quantity) > 0
# MAGIC )
# MAGIC SELECT
# MAGIC   product_id,
# MAGIC   brand_name,
# MAGIC   category_name,
# MAGIC   days_active,
# MAGIC   ROUND(avg_daily_quantity, 2) AS avg_daily_quantity,
# MAGIC   ROUND(stddev_daily_quantity, 2) AS stddev_daily_quantity,
# MAGIC   total_quantity_sold,
# MAGIC   ROUND(total_revenue, 2) AS total_revenue,
# MAGIC   demand_volatility_pct,
# MAGIC   CASE
# MAGIC     WHEN demand_volatility_pct <= 50 THEN 'Stable Demand'
# MAGIC     WHEN demand_volatility_pct <= 100 THEN 'Moderate Volatility'
# MAGIC     ELSE 'Volatile Demand'
# MAGIC   END AS demand_stability
# MAGIC FROM
# MAGIC   product_volatility
# MAGIC WHERE
# MAGIC   demand_volatility_pct IS NOT NULL
# MAGIC ORDER BY
# MAGIC   demand_volatility_pct ASC
# MAGIC LIMIT 500

# COMMAND ----------

# MAGIC %md
# MAGIC Trend for revenue (Lag)

# COMMAND ----------

# MAGIC %sql
# MAGIC WITH monthly AS (
# MAGIC     SELECT
# MAGIC         YEAR(transaction_date)                     AS year,
# MAGIC         MONTH(transaction_date)                    AS month_no,
# MAGIC         SUM(net_amount)                            AS total_revenue
# MAGIC     FROM ecommerce.gold.fact_transactions_denorm
# MAGIC     GROUP BY
# MAGIC         YEAR(transaction_date),
# MAGIC         MONTH(transaction_date)
# MAGIC )
# MAGIC SELECT
# MAGIC     year,
# MAGIC     month_no,
# MAGIC     total_revenue                                  AS current_month_revenue,
# MAGIC
# MAGIC     -- Previous month
# MAGIC     LAG(total_revenue) OVER (
# MAGIC         ORDER BY year, month_no
# MAGIC     )                                              AS prev_month_revenue,
# MAGIC
# MAGIC     -- Difference vs last month
# MAGIC     total_revenue - LAG(total_revenue) OVER (
# MAGIC         ORDER BY year, month_no
# MAGIC     )                                              AS revenue_change,
# MAGIC
# MAGIC     -- Growth % vs last month
# MAGIC     ROUND(
# MAGIC         (total_revenue - LAG(total_revenue) OVER (
# MAGIC             ORDER BY year, month_no
# MAGIC         )) * 100.0 /
# MAGIC         LAG(total_revenue) OVER (
# MAGIC             ORDER BY year, month_no
# MAGIC         ), 2
# MAGIC     )                                              AS mom_growth_pct,
# MAGIC
# MAGIC     -- Trend signal
# MAGIC     CASE
# MAGIC         WHEN total_revenue > LAG(total_revenue) OVER (
# MAGIC             ORDER BY year, month_no
# MAGIC         )                                          THEN 'Growing'
# MAGIC         WHEN total_revenue < LAG(total_revenue) OVER (
# MAGIC             ORDER BY year, month_no
# MAGIC         )                                          THEN 'Declining'
# MAGIC         ELSE                                            'Flat'
# MAGIC     END                                            AS trend
# MAGIC FROM monthly
# MAGIC ORDER BY year, month_no;