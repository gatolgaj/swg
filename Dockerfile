# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any necessary dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Ensure both necessary environment variables are passed
ARG OPENAI_API_KEY
ARG QDRANT_URL
ENV OPENAI_API_KEY=$OPENAI_API_KEY
ENV QDRANT_URL=$QDRANT_URL

# Expose port 8000 for the application
EXPOSE 8000


# Perform initial data setup
RUN if [ ! -f ".data_initialized" ]; then \
        python create_rec_from_pdf.py && \
        python create_rec_from_txt.py && \
        touch .data_initialized; \
    fi

# Command to run the application
CMD ["chainlit", "run", "SolveWithGoogle.py"]