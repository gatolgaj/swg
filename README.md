### Solve with Google

**1.** Make sure that you have docker installed.

**2.** Login to google gloud and setup the projrct. Make sure that Vertex AI is enabled.

````
gcloud auth application-default login
gcloud config set project <PROJECT_ID>
````

**3.**  Create a .env file and add the following env varibales
````
OPENAI_API_KEY=sk-<***************************>
QDRANT_URL=http://localhost:6333
````

Then run the script

````
chmod +x run.sh 
./run.sh
````

The Script will do the following

* Run Qdrant Database in case its not running
* Install the requirements
* extract the content of the PDF file in pdfInput folder and upload it to qdrant.
* extract the content of the text file in Pdata Folder.
* start the chatbot application
* The page is available in <http://localhost:8000>
