# pyrefly: ignore [missing-import]
from pyspark.sql import SparkSession


# ============================================
# CREATE SPARK SESSION
# ============================================

spark = (
    SparkSession.builder
    .appName("OlistSQLAnalytics")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")


# ============================================
# LOAD PROCESSED ANALYTICS DATA
# ============================================

df = spark.read.parquet(
    "data/processed/order_analytics"
)


# ============================================
# CREATE TEMPORARY SQL VIEW
# ============================================

df.createOrReplaceTempView("orders")


print("\n========== DATASET SCHEMA ==========\n")

df.printSchema()


# ============================================
# 1. TOTAL REVENUE
# ============================================

print("\n========== TOTAL REVENUE ==========\n")

total_revenue = spark.sql("""
    SELECT
        ROUND(SUM(price), 2) AS total_revenue
    FROM orders
""")

total_revenue.show()


# ============================================
# 2. REVENUE BY PRODUCT CATEGORY
# ============================================

print("\n========== REVENUE BY PRODUCT CATEGORY ==========\n")

revenue_by_category = spark.sql("""
    SELECT
        product_category_name,
        ROUND(SUM(price), 2) AS total_revenue,
        COUNT(*) AS order_items
    FROM orders
    WHERE product_category_name IS NOT NULL
    GROUP BY product_category_name
    ORDER BY total_revenue DESC
""")

revenue_by_category.show(20)


# ============================================
# 3. ORDERS BY CUSTOMER STATE
# ============================================

print("\n========== ORDERS BY CUSTOMER STATE ==========\n")

orders_by_state = spark.sql("""
    SELECT
        customer_state,
        COUNT(*) AS order_items,
        ROUND(SUM(price), 2) AS total_revenue
    FROM orders
    WHERE customer_state IS NOT NULL
    GROUP BY customer_state
    ORDER BY order_items DESC
""")

orders_by_state.show(20)


# ============================================
# 4. PAYMENT METHOD ANALYSIS
# ============================================

print("\n========== PAYMENT METHOD ANALYSIS ==========\n")

payment_analysis = spark.sql("""
    SELECT
        payment_type,
        COUNT(*) AS order_items,
        ROUND(AVG(price), 2) AS average_price
    FROM orders
    WHERE payment_type IS NOT NULL
    GROUP BY payment_type
    ORDER BY order_items DESC
""")

payment_analysis.show()


# ============================================
# 5. DELIVERY PERFORMANCE
# ============================================

print("\n========== DELIVERY PERFORMANCE ==========\n")

delivery_analysis = spark.sql("""
    SELECT
        delivery_performance,
        COUNT(*) AS order_items,
        ROUND(AVG(delivery_days), 2) AS average_delivery_days
    FROM orders
    GROUP BY delivery_performance
    ORDER BY order_items DESC
""")

delivery_analysis.show()


# ============================================
# 6. LATE DELIVERY ANALYSIS
# ============================================

print("\n========== LATE DELIVERY ANALYSIS ==========\n")

late_orders = spark.sql("""
    SELECT
        COUNT(*) AS late_orders,
        ROUND(AVG(delivery_delay_days), 2) AS average_delay_days,
        MAX(delivery_delay_days) AS maximum_delay_days
    FROM orders
    WHERE delivery_performance = 'Late'
""")

late_orders.show()


# ============================================
# 7. TOP PRODUCT CATEGORIES
# ============================================

print("\n========== TOP 10 PRODUCT CATEGORIES ==========\n")

top_categories = spark.sql("""
    SELECT
        product_category_name,
        ROUND(SUM(price), 2) AS revenue
    FROM orders
    WHERE product_category_name IS NOT NULL
    GROUP BY product_category_name
    ORDER BY revenue DESC
    LIMIT 10
""")

top_categories.show()


# ============================================
# STOP SPARK
# ============================================

spark.stop()