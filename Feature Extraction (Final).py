import os
import librosa
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client['audio']
collection = db['audio_collection']

# Function to extract features from audio files
def extract_features(audio_files):
    for audio_file in audio_files:
        try:
            # Load audio file and extract features
            y, sr = librosa.load(audio_file)
            mfccs = librosa.feature.mfcc(y=y, sr=sr)

            # Insert features into MongoDB
            data = {'audio_file': audio_file, 'features': mfccs.tolist()}
            collection.insert_one(data)
        except Exception as e:
            print(f"Skipped {audio_file} due to error: {e}")
            continue  # Skip to the next file if an error occurs

# Path to the 'fma_medium' directory
root_folder = r'F:\BDA_Project\fma_medium'

# Iterate through folders and process all audio files while handling errors
for folder_name in os.listdir(root_folder):
    folder_path = os.path.join(root_folder, folder_name)
    if os.path.isdir(folder_path):
        audio_files = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith('.mp3')]
        extract_features(audio_files)

print("All files in fma_medium processed and stored in MongoDB.")
