#!/bin/bash

# Variables
PROJECT_ID="236909908642"
SERVICE_ACCOUNT_NAME="swg-svc-account"
SERVICE_ACCOUNT_DISPLAY_NAME="SWG Service Account"
KEY_PATH="service-account-key.json"

# Create a new service account
gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
    --display-name "$SERVICE_ACCOUNT_DISPLAY_NAME" \
    --project $PROJECT_ID

# Assign roles to the service account (adjust the roles as necessary)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member "serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --role "roles/viewer"  # Example role, change as needed

# Generate the JSON key file for the service account
gcloud iam service-accounts keys create $KEY_PATH \
    --iam-account "$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com"

# Encode the JSON key file (optional)
ENCODED_KEY=$(base64 $KEY_PATH | tr -d '\n')

# Output the encoded key (you might use this in your Docker environment variable)
echo "Encoded Key:"
echo $ENCODED_KEY