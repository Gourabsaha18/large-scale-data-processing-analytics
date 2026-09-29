from pyspark.sql import SparkSession

DATA_PATH = "data/processed/sales_parquet"

spark = (
    SparkSession.builder
    .appName("SalesAnalytics")
    .getOrCreate()
)

df = spark.read.parquet(DATA_PATH)
df.createOrReplaceTempView("sales")

queries = {
    "total_revenue": '''
        SELECT ROUND(SUM(Revenue), 2) AS total_revenue
        FROM sales
    ''',
    "revenue_by_category": '''
        SELECT Category, ROUND(SUM(Revenue), 2) AS revenue
        FROM sales
        GROUP BY Category
        ORDER BY revenue DESC
    ''',
    "revenue_by_region": '''
        SELECT Region, ROUND(SUM(Revenue), 2) AS revenue
        FROM sales
        GROUP BY Region
        ORDER BY revenue DESC
    ''',
    "top_products": '''
        SELECT Product_Name, ROUND(SUM(Revenue), 2) AS revenue
        FROM sales
        GROUP BY Product_Name
        ORDER BY revenue DESC
        LIMIT 10
    '''
}

for name, query in queries.items():
    print(f"\n===== {name.upper()} =====")
    spark.sql(query).show(truncate=False)

spark.stop()
