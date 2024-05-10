from pyspark.sql import SparkSession
from pyspark.sql.types import DoubleType, ArrayType, StructType, StructField, StringType
from pyspark.ml.feature import MinMaxScaler
from pyspark.ml.linalg import Vectors, VectorUDT
from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator
from pyspark.sql.functions import udf, col, expr

# Create Spark Session
spark = SparkSession.builder \
    .appName("LSH_NearestNeighbor") \
    .getOrCreate()

# Define the schema including 'features' and 'filename' columns
schema = StructType([
    StructField("features", ArrayType(DoubleType()), nullable=False),
    StructField("filename", StringType(), nullable=False)
])

# Read data from MongoDB collection with the specified schema
df = spark.read.format("mongo") \
    .option("uri", "mongodb://localhost:27017/spotify.spotify_features") \
    .schema(schema) \
    .load()

# Print schema and count for debugging
df.printSchema()
print("Number of rows in DataFrame:", df.count())

# Check 'features' column for consistent dimensions
df.selectExpr("size(features) as feature_size").distinct().show()

# Filter out rows with inconsistent feature dimensions
df = df.filter(expr("size(features) = 25822"))

# Define UDF to convert array to dense vector
to_vector_udf = udf(lambda features: Vectors.dense(features), VectorUDT())
df = df.withColumn("features_vector", to_vector_udf(col("features")))

# Apply Min-Max Scaling
scaler = MinMaxScaler(inputCol="features_vector", outputCol="scaled_features")
scaler_model = scaler.fit(df)
scaled_df = scaler_model.transform(df)

# Train KMeans Clustering Model
kmeans = KMeans(featuresCol='scaled_features', predictionCol='prediction', k=5)
kmeans_model = kmeans.fit(scaled_df)
clustered_df = kmeans_model.transform(scaled_df)

# Evaluate the Clustering Model using Silhouette Score
evaluator = ClusteringEvaluator(distanceMeasure="squaredEuclidean", featuresCol="scaled_features", predictionCol="prediction")
silhouette = evaluator.evaluate(clustered_df)
print("Silhouette with squared Euclidean distance =", silhouette)

# Output tracks identified as having similar patterns
similar_tracks = clustered_df.select("features_vector", "prediction", "filename").filter(col("prediction") == 0).collect()
print("Tracks with similar patterns (Cluster 0):")
for track in similar_tracks:
    print(track["filename"])
