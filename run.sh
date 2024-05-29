#!/bin/bash

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