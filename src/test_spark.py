# pyrefly: ignore [missing-import]
from pyspark.sql import SparkSession

# Create a Spark session
spark = (
    SparkSession.builder
    .appName("OlistDataAnalytics")
    .getOrCreate()
)

print("Spark started successfully!")
print("Spark version:", spark.version)

spark.stop()