import numpy as np
import warnings
from pyspark.sql import SparkSession
from pyspark.sql.types import DoubleType, StringType
from pyspark.ml.feature import BucketedRandomProjectionLSH
from pyspark.ml.linalg import Vectors, VectorUDT
from pyspark.sql.functions import udf

try:
    # Initialize SparkSession
    print("Initializing SparkSession...")
    spark = SparkSession.builder \
        .appName("MusicRecommendation") \
        .getOrCreate()

    # Load the audio features dataset from MongoDB into a Spark DataFrame
    print("Loading data from MongoDB...")
    df = spark.read.format("mongo").option("uri", "mongodb://localhost:27017/music_features2.audio_features2").load()

    # Define a UDF to convert array to vector
    print("Defining UDF...")
    array_to_vector_udf = udf(lambda arr: Vectors.dense(arr), VectorUDT())

    # Apply the UDF to convert "features" array to "features_vector" vector
    print("Converting features array to vector...")
    df = df.withColumn("features_vector", array_to_vector_udf("features"))

    # Drop the original "features" column as it's no longer needed
    print("Dropping original 'features' column...")
    df = df.drop("features")

    # Configure LSH parameters
    num_hash_tables = 5
    bucket_length = 10.0

    # Initialize LSH model
    print("Initializing LSH model...")
    lsh = BucketedRandomProjectionLSH(inputCol="features_vector", outputCol="hashes", numHashTables=num_hash_tables, bucketLength=bucket_length)

    # Fit the LSH model to the dataset
    print("Fitting LSH model to the dataset...")
    lsh_model = lsh.fit(df)

    # Query MongoDB to retrieve the features of the track
    track_filename = "000002.mp3"  # Example filename of the track
    print(f"Querying MongoDB to retrieve features of track {track_filename}...")
    track_features_array = df.filter(df.filename == track_filename).select("features_vector").collect()[0][0]

    # Convert features array to vector representation
    print("Converting features array to vector representation...")
    track_features_vector = Vectors.dense(track_features_array)

    # Assign the vector to the key variable
    key = track_features_vector

    # Define the number of nearest neighbors to retrieve
    numNearestNeighbors = 5

    # Perform nearest neighbor search using LSH
    print("Performing nearest neighbor search using LSH...")
    nearest_neighbors = lsh_model.approxNearestNeighbors(df, key, numNearestNeighbors)

    # Show the nearest neighbors for each data point
    print("Showing the nearest neighbors for each data point:")
    nearest_neighbors.show()

except Exception as e:
    print("An error occurred:", str(e))

finally:
    # Stop SparkSession
    print("Stopping SparkSession...")
    if 'spark' in locals():
        spark.stop()

    # BLAS Implementation warning handling
    try:
        np.dot([1, 2], [3, 4])
    except ImportError:
        warnings.warn("Failed to load BLAS implementation. Performance may be degraded.")

    # Broadcasting large task binary warning handling
    if lsh_model is not None:
        model_size = len(lsh_model._java_obj.serializeToPython())
        broadcast_threshold = 1024 * 1024  # 1 MB threshold for broadcasting warning
        if model_size > broadcast_threshold:
            warnings.warn(f"Broadcasting large task binary with size {model_size / 1024:.1f} KiB. Consider optimizing.")

    # Executor Heartbeat Timeout warning handling
    executor_timeout = 120000  # milliseconds
    if spark is not None and spark.sparkContext is not None:
        for executor_id, last_seen in spark.sparkContext._scheduler.executorLastSeen.items():
            current_time = spark.sparkContext._scheduler.clock.getTimeMillis()
            if current_time - last_seen > executor_timeout:
                warnings.warn(f"Executor {executor_id} has not sent heartbeats recently. It may have failed or be unresponsive.")

    # Error handling for killing issue
    try:
        # Add any additional cleanup code here
        pass
    except Exception as e:
        print("An error occurred during cleanup:", str(e))
