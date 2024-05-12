# BDA_Project

Create Your Own Spotify
Team Members:
➢ Harris Hassan Syed 22i-1947
➢ Abdullah Nadeem 22i-1925
➢ Fadil Falak 22i-1815
Phase 1: Extract, Transform & Load Pipeline:
The Python script presented here addresses the challenge of extracting meaningful features from a large
audio dataset and storing them efficiently for further analysis. Initially, difficulties arose in
downloading the extensive 105 GB dataset, prompting a reevaluation of the data acquisition process.
Upon obtaining the dataset, the script employs advanced audio processing techniques facilitated by the
`librosa` library to extract Mel-Frequency Cepstral Coefficients (MFCCs), essential for capturing
nuanced audio characteristics.
To begin the feature extraction process, the script establishes a connection to a MongoDB database
using the `pymongo` library, enabling seamless storage of the extracted features. The `extract_features`
function orchestrates the core processing workflow, loading each audio file and extracting its MFCCs.
These features, encapsulated within a dictionary structure, are then inserted into the designated
MongoDB collection, ensuring organized and accessible storage of the audio data.
Throughout the execution of the script, robust error handling mechanisms are implemented to address
potential issues encountered during the feature extraction process. Any errors arising from corrupt or
problematic audio files are gracefully managed, allowing the script to continue processing the
remaining data. Upon completion, a confirmation message is provided, signaling the successful
extraction and storage of audio features, paving the way for subsequent analyses or applications such as
audio classification or recommendation systems.
Phase 2: Music Recommendation Model:
The journey towards establishing an effective model for audio feature clustering was marked by a
series of trials and errors, each contributing to the refinement of the final solution. Initially, various
models were tested, including Alternating Least Squares (ALS), Artificial Neural Networks (ANN),
and RandomForestRegression. However, each encountered its own set of challenges, ranging from data
compatibility issues to errors during execution. For instance, ALS failed due to a lack of ratings, ANN
encountered library compatibility issues, and RandomForestRegression faced type conversion errors.
Despite numerous attempts to rectify the issues, including adjustments to the feature extraction process
and data manipulation techniques, the challenges persisted. Errors such as data type mismatches and
incompatible column types continued to hinder progress, necessitating a reevaluation of the approach.
Despite these setbacks, perseverance and experimentation ultimately led to the development of a robust
solution for audio feature clustering.
The final model recommendation entails the utilization of KMeans Clustering, a powerful algorithm for
grouping data points based on similarities in feature space. Leveraging PySpark's MLlib library, the
script begins by reading audio features stored in a MongoDB collection. Following data ingestion, the
features undergo preprocessing steps, including Min-Max Scaling to normalize feature values.
Subsequently, the KMeans algorithm is applied to identify clusters within the dataset, facilitating the
grouping of similar audio tracks. Evaluation of the clustering model is performed using the Silhouette
Score, providing insights into the quality and cohesion of the generated clusters. Finally, the model
outputs tracks identified as sharing similar patterns within a designated cluster, enabling users to
explore and analyze cohesive groups of audio content.
Phase 3: Deployment
Our project's deployment phase culminated in the development of a Flask web application dedicated to
providing users with personalized audio track recommendations. This endeavor marked the synthesis of
extensive development efforts, meticulously blending data processing, machine learning, and user
interaction. The Flask application, featuring four primary pages – Login, Signup, Home, and Home2 –
orchestrates a harmonious flow of functionalities, catering to user needs and ensuring a fluid user
experience.
At the heart of the application's architecture lies a MongoDB database, housing both user credentials
and audio features. Utilizing the MongoClient class from the pymongo library, the application
establishes seamless connections to the MongoDB instance, facilitating efficient retrieval and storage
of data. This integration ensures that user authentication, track selection, and recommendation retrieval
processes are supported by a robust backend infrastructure.
The Flask application leverages Python's Flask framework to create a responsive web server capable of
managing user requests and responses. Each page within the application is meticulously crafted to
fulfill specific user requirements, such as verifying user credentials during login or facilitating track
selection through dropdown menus. Validation checks are embedded within the application logic to
ensure data integrity and prevent unauthorized access, thereby enhancing security and reliability.
Upon receiving user requests, such as login attempts or track selections, the Flask application
seamlessly interfaces with the backend Python code responsible for data processing and machine
learning tasks. The Python code, written using PySpark, harnesses the distributed computing
capabilities of Apache Spark to perform complex data operations efficiently. For instance, audio
features are extracted from the MongoDB collection and passed through a KMeans clustering model to
generate personalized track recommendations.
To ensure a smooth user experience, error handling mechanisms are integrated throughout the
application. Whether encountering invalid inputs, authentication failures, or unexpected behaviors, the
application gracefully manages exceptions and guides users with informative error messages. This
meticulous attention to detail fosters user confidence and fosters a positive interaction with the
application.
By seamlessly integrating the Flask web application with the backend Python code, our project delivers
a cohesive platform that seamlessly combines the strengths of both frameworks. This integration
empowers users to effortlessly navigate through the application, discover personalized audio
recommendations, and enjoy a seamless user experience from start to finish.
Future Plans:
Looking ahead, we aim to enhance the functionality and user experience of our application by
implementing several exciting features. One area of focus is the integration of user feedback
mechanisms, allowing users to rate recommended tracks and provide feedback on the recommendation
quality. This feedback loop will enable the system to continuously improve and refine its
recommendations, ensuring relevance and accuracy over time.
Additionally, we plan to explore collaborative filtering techniques to further personalize
recommendations based on user preferences and behavior. By analyzing user interactions and
similarities between users, we can generate more tailored recommendations that resonate with
individual tastes and preferences. Furthermore, we aspire to enhance the application's scalability and
performance to accommodate a growing user base and larger datasets. This may involve optimizing
data processing pipelines, leveraging cloud computing resources, or implementing distributed
computing frameworks to handle increasing volumes of data and user requests efficiently.
Overall, these future plans reflect our commitment to continuous improvement and innovation, as we
strive to deliver a cutting-edge recommendation platform that meets the evolving needs and preferences
of our users.
Conclusion:
In conclusion, our project journey has been marked by a meticulous exploration of audio feature
extraction, machine learning, and web application development, all culminating in the creation of a
robust platform for personalized audio track recommendations. Through careful planning and iterative
development, we have successfully integrated Flask and Python backend to deliver a seamless user
experience. From the initial phases of data acquisition to the deployment of a fully functional web
application, each stage has been driven by a commitment to excellence and innovation.
The synergy between Flask and Python backend has enabled us to create a cohesive platform that
empowers users to explore and discover audio content tailored to their preferences. By leveraging
advanced clustering techniques and user interaction mechanisms, we have provided users with an
intuitive interface for discovering new music. Through validation checks, error handling mechanisms,
and seamless integration with MongoDB, we have ensured data integrity, security, and reliability
throughout the application. Looking ahead, we are excited about the future possibilities for our project!
