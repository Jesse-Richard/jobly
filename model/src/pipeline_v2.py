import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.spatial.distance import cdist
import pickle
import numpy as np
import argparse
import json
import re

# Initialize NLTK downloads
nltk.download('punkt')
nltk.download('wordnet')

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()

# Preprocessing function
def preprocess_text(text):
    text = str(text)
    # Remove numbers, punctuation, and commas using regex
    text = re.sub(r'[^\w\s]', '', text)  # This removes punctuation and commas
    text = text.lower()  # Convert text to lowercase
    tokens = word_tokenize(text)
    lemmatized = [lemmatizer.lemmatize(word) for word in tokens]
    return ' '.join(lemmatized)

# Mapping function for preprocessing
def mappingfunction(dataframe, column, function):
    dataframe[f'cleaned_{column}'] = dataframe[column].apply(function)
    return dataframe

# Save reference model
def save_reference_model(reference_data_path, column, vectorizer_path, vectors_path):
    reference_data = pd.read_csv(reference_data_path)
    reference_data = mappingfunction(reference_data, column, preprocess_text)

    # Create and fit TF-IDF vectorizer
    tfidf = TfidfVectorizer()
    reference_vectors = tfidf.fit_transform(reference_data[f'cleaned_{column}'])

    reference_vectors_dense = reference_vectors.toarray()

    # Save vectorizer and reference vectors
    with open(vectorizer_path, 'wb') as f:
        pickle.dump(tfidf, f)
    np.savez_compressed(vectors_path, reference_vectors=reference_vectors_dense)

    print(f"Model saved: Vectorizer -> {vectorizer_path}, Reference Vectors -> {vectors_path}")

# Load reference model
def load_reference_model(vectorizer_path, vectors_path):
    with open(vectorizer_path, 'rb') as f:
        vectorizer = pickle.load(f)
    reference_vectors = np.load(vectors_path, allow_pickle=True)['reference_vectors']
    print(reference_vectors.shape)
    return vectorizer, reference_vectors

# Vectorize input using pre-fitted vectorizer
def vectorize_input(vectorizer, input_dataframe, column):
    input_texts = input_dataframe[column]
    input_vectors = vectorizer.transform(input_texts)
    return input_vectors

# Calculate Hamming distances
def hammingdistances(vector1, vector2):
    # Convert sparse matrices to dense if necessary
    vector1 = vector1.toarray() if hasattr(vector1, "toarray") else vector1
    vector2 = vector2.toarray() if hasattr(vector2, "toarray") else vector2

    # Ensure they are 2D arrays
    if len(vector1.shape) == 1:
        vector1 = vector1.reshape(1, -1)
    if len(vector2.shape) == 1:
        vector2 = vector2.reshape(1, -1)

    return cdist(vector1, vector2, metric='cityblock')

# Get top recommendations
def get_top_recommendations(input_dataframe, index, reference_dataframe, ref_id, distances, num_recommendations=5):
    recommendations = {}
    for i, applicant_id in enumerate(input_dataframe[index]):
        top_indices = np.argsort(distances[i])[:num_recommendations]
        recommendations[applicant_id] = reference_dataframe[ref_id].iloc[top_indices].tolist()
    return recommendations

# Create recommendations DataFrame
def create_recommendations_dataframe(recommendations):
    return pd.DataFrame([
        {'Applicant ID': applicant_id, 'Recommended Job IDs': jobs}
        for applicant_id, jobs in recommendations.items()
    ])

# Process with reference model
def process_with_reference_model(input_path, index, input_column, vectorizer_path, vectors_path, ref_id, data_path, num_recs, output_path=None):
    with open(input_path, 'r') as j:
        contents = json.loads(j.read())
        print(contents)
    series = pd.Series((contents))
    input_data = pd.DataFrame(series).T
    print(input_data)
    reference_data = pd.read_csv(data_path)

    vectorizer, reference_vectors = load_reference_model(vectorizer_path, vectors_path)

    # Preprocess data
    input_data = mappingfunction(input_data, input_column, preprocess_text)
    reference_data = mappingfunction(reference_data, ref_id, preprocess_text)

    # Vectorize input data
    input_vectors = vectorize_input(vectorizer, input_data, f'cleaned_{input_column}')

    
    # # Ensure feature space consistency
    # if input_vectors.shape[1] != reference_vectors.shape[1]:
    #     raise ValueError("Feature space mismatch. Ensure the same vectorizer is used.")

    # Compute distances and recommendations
    distances = hammingdistances(input_vectors, reference_vectors)
    recommendations = get_top_recommendations(input_data, index, reference_data, ref_id, distances, num_recs)

    # Create DataFrame and save output
    recs_df = create_recommendations_dataframe(recommendations)
    if output_path:
        recs_df.to_json(output_path, orient="records", indent=4)
        print(f"Recommendations saved to {output_path}")
    return recs_df

# Main function
def main():
    parser = argparse.ArgumentParser(description="Job Recommendation System")
    parser.add_argument('mode', choices=['save', 'run'], help="Mode: 'save' to save model, 'run' to use saved model")
    parser.add_argument('--data_path', required=True, help="Path to reference data (CSV)")
    parser.add_argument('--input_path', help="Path to input query data (JSON)")
    parser.add_argument('--vectorizer_path', default="vectorizer.pkl", help="Path to save/load vectorizer")
    parser.add_argument('--vectors_path', default="reference_vectors.npz", help="Path to save/load reference vectors")
    parser.add_argument('--index', help="Column name for applicant IDs")
    parser.add_argument('--input_column', help="Column name for input data")
    parser.add_argument('--ref_id', help="Column name for reference IDs")
    parser.add_argument('--data_field', help="Column name for reference data")
    parser.add_argument('--num_recs', type=int, default=5, help="Number of recommendations")
    parser.add_argument('--output_path', help="Path to save recommendations (JSON)")

    args = parser.parse_args()

    if args.mode == 'save':
        save_reference_model(args.data_path, args.data_field, args.vectorizer_path, args.vectors_path)
    elif args.mode == 'run':
        recs_df = process_with_reference_model(
            args.input_path, args.index, args.input_column, 
            args.vectorizer_path, args.vectors_path, 
            args.ref_id, args.data_path, args.num_recs, 
            args.output_path
        )
        print(recs_df)

if __name__ == "__main__":
    main()
