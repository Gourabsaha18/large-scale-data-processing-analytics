# pyrefly: ignore [missing-import]
from pyspark.sql import SparkSession
# pyrefly: ignore [missing-import]
from pyspark.sql.functions import (
    col,
    datediff,
    when
)


# --------------------------------------------------
# 1. Create Spark Session
# --------------------------------------------------

spark = (
    SparkSession.builder
    .appName("OlistOrderTransformation")
    .getOrCreate()
)


# --------------------------------------------------
# 2. Load Orders Dataset
# --------------------------------------------------

orders_df = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv("data/raw/olist_orders_dataset.csv")
)


# --------------------------------------------------
# 3. Remove Exact Duplicate Rows
# --------------------------------------------------

clean_orders_df = orders_df.dropDuplicates()


# --------------------------------------------------
# 4. Create Delivery Days
# --------------------------------------------------

clean_orders_df = clean_orders_df.withColumn(
    "delivery_days",
    datediff(
        col("order_delivered_customer_date"),
        col("order_purchase_timestamp")
    )
)


# --------------------------------------------------
# 5. Create Delivery Delay
# --------------------------------------------------

clean_orders_df = clean_orders_df.withColumn(
    "delivery_delay_days",
    datediff(
        col("order_delivered_customer_date"),
        col("order_estimated_delivery_date")
    )
)


# --------------------------------------------------
# 6. Create Delivery Performance Category
# --------------------------------------------------

clean_orders_df = clean_orders_df.withColumn(
    "delivery_performance",
    when(
        col("delivery_delay_days") <= 0,
        "On Time"
    )
    .when(
        col("delivery_delay_days") > 0,
        "Late"
    )
    .otherwise("Unknown")
)


# --------------------------------------------------
# 7. Display Transformed Data
# --------------------------------------------------

print("\n========== TRANSFORMED ORDERS ==========\n")

clean_orders_df.select(
    "order_id",
    "order_status",
    "order_purchase_timestamp",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
    "delivery_days",
    "delivery_delay_days",
    "delivery_performance"
).show(10, truncate=False)


# --------------------------------------------------
# 8. Validate Delivery Performance
# --------------------------------------------------

print("\n========== DELIVERY DELAY SUMMARY ==========\n")

clean_orders_df.select(
    "delivery_delay_days",
    "delivery_performance"
).groupBy(
    "delivery_performance"
).count().orderBy(
    "delivery_performance"
).show()


print("\n========== LATE ORDERS ==========\n")

clean_orders_df.filter(
    col("delivery_performance") == "Late"
).select(
    "order_id",
    "delivery_days",
    "delivery_delay_days",
    "delivery_performance"
).show(10, truncate=False)


print("\n========== DELIVERY DELAY STATISTICS ==========\n")

clean_orders_df.select(
    "delivery_delay_days"
).summary(
    "count",
    "mean",
    "min",
    "max"
).show()

# --------------------------------------------------
# 9. Average Delivery Time
# --------------------------------------------------

print("\n========== AVERAGE DELIVERY TIME ==========\n")

clean_orders_df.select(
    "delivery_days"
).summary("count", "mean", "min", "max").show()

# --------------------------------------------------
# 11. Save Processed Orders
# --------------------------------------------------

output_path = "data/processed/orders_cleaned"

print("\n========== SAVING PROCESSED DATA ==========\n")

clean_orders_df.write \
    .mode("overwrite") \
    .parquet(output_path)

print(f"Processed orders saved to: {output_path}")
# --------------------------------------------------
# 12. Stop Spark
# --------------------------------------------------


spark.stop()