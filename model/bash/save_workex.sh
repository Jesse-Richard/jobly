#!/bin/bash

# Check if the data path is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <data_path>"
  exit 1
fi

# Set variables from command line arguments or environment variables
DATA_PATH="$1"                                      # The first argument will be the data path
DATA_FIELD="${DATA_FIELD:-Job Description}"                   # Defaults to "Job Description" if not set
VECTORIZER_PATH="${VECTORIZER_PATH:-./models/workEx/workex_vectorizer.pkl}"  # Defaults to the provided path if not set
VECTORS_PATH="${VECTORS_PATH:-./models/workEx/workex_vectors.npz}"           # Defaults to the provided path if not set

# Run the Python script with the provided parameters
python3 ./src/pipeline_v2.py save --data_path "$DATA_PATH" \
                            --data_field "$DATA_FIELD" \
                            --vectorizer_path "$VECTORIZER_PATH" \
                            --vectors_path "$VECTORS_PATH"
