#!/bin/bash

# # Function to check environment variable existence
# check_env_var() {
#     local var_name="$1"
#     local env_source="$2"
#     # Check in the environment
#     if printenv "$var_name" &> /dev/null; then
#         echo "$var_name is set in the environment."
#         return 0
#     fi
#     # Check in the .env file
#     if [ -f ".env" ] && grep -q "^$var_name=" ".env"; then
#         echo "$var_name is set in the .env file."
#         return 0
#     fi
#     # If not found in both places
#     echo "Error: $var_name is not set in the environment or .env file."
#     return 1
# }

# # Check required variables
# check_env_var "OPENAI_API_KEY" && check_env_var "QDRANT_URL"

# # If all checks pass, proceed with the rest of the script
# if [ $? -eq 0 ]; then
#     echo "All required environment variables are found."
#     # Rest of the script...
# else
#     echo "Some required environment variables are missing. Check and retry."
#     exit 1
# fi
# Check if Qdrant is running
if ! nc -z localhost 6333; then
    echo "Starting Qdrant..."
    docker pull qdrant/qdrant
    docker run -d -p 6333:6333 -p 6334:6334 qdrant/qdrant
    echo "Qdrant started."
else
    echo "Qdrant is already running."
fi

echo " Installing Libraries"
pip install -r requirements.txt
# Check if data has already been uploaded
if [ ! -f ".data_initialized" ]; then
    echo "Creating records from PDF..."
    python create_rec_from_pdf.py
    echo "Creating records from text..."
    python create_rec_from_txt.py
    touch .data_initialized
    echo "Data upload completed."
else
    echo "Data has already been uploaded."
fi

# Run the main application
echo "Running the application..."
chainlit run SolveWithGoogle.py
echo "Application is now running."