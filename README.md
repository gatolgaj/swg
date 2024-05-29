### Solve with Google
Make sure that you have docker installed. 

Then run the script 
````
./run.sh
````


The Script will do the following 
* Run Qdrant Database in case its not dunning 
* Install the requirements 
* extract the content of the PDF file in pdfInput folder and upload it to qdrant.
*  extract the content of the text file in Pdata Folder.
*  start the chatbot application 
*  The page is available in http://localhost:8000