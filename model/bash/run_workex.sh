#!/bin/bash

# Set variables (default or from environment variables)
INPUT_PATH="$1"                          # First argument: Input query data (JSON)
INDEX="${INDEX:-applicant_id}"            # Default column for applicant ID or from environment variable
INPUT_COLUMN="${INPUT_COLUMN:-experience}" # Default column for input data (skills) or from environment variable
VECTORIZER_PATH="${VECTORIZER_PATH:-./models/workEx/workEx_vectorizer.pkl}"   # Default or from environment variable
VECTORS_PATH="${VECTORS_PATH:-./models/workEx/workEx_vectors.npz}"           # Default or from environment variable
REF_ID="${REF_ID:-Job Id}"                # Default column for reference IDs or from environment variable
DATA_PATH="${DATA_PATH:-./data/dataset_first_50k.csv}"  # Default or from environment variable
NUM_RECS="${NUM_RECS:-10}"                # Default number of recommendations or from environment variable
OUTPUT_PATH="${OUTPUT_PATH:-./responses/workEx/recommendations.json}"  # Default output path or from environment variable

# Check if the query file is provided
if [ -z "$INPUT_PATH" ]; then
  echo "Usage: $0 <input_query_path>"
  exit 1
fi

# Run the Python script with the set variables
python3 ./src/pipeline_v2.py run --input_path "$INPUT_PATH" \
                           --index "$INDEX" \
                           --input_column "$INPUT_COLUMN" \
                           --vectorizer_path "$VECTORIZER_PATH" \
                           --vectors_path "$VECTORS_PATH" \
                           --ref_id "$REF_ID" \
                           --data_path "$DATA_PATH" \
                           --num_recs "$NUM_RECS" \
                           --output_path "$OUTPUT_PATH"
