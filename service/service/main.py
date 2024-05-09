from fastapi import FastAPI, HTTPException
from llama_index.core import StorageContext, Settings, load_index_from_storage, VectorStoreIndex, Document
from llama_index.llms.anthropic import Anthropic
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from google.cloud import storage
import logging
import sys
import os

app = FastAPI()

# Set up logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

# Configure settings for Anthropic LLM and embedding
os.environ["ANTHROPIC_API_KEY"] = "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"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "bucket.json"
root_bucket = "airflow-airbyte-fastapi"
Settings.llm = Anthropic(model="claude-3-opus-20240229")
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
Settings.num_output = 512
Settings.context_window = 3900

storage_directory_base = '/data/'

# Define route to handle POST requests
@app.get("/query")
async def query_llm(query_text: str):
    # Need to figure out how to start a session of some sort.
    # Provide a bucket/prefix and query.
    # Load Model from 
    try:
        storage_directory = storage_directory_base + 'airflow-airbyte-fastapi/PLLcWHcmX9QjXkp8ZVCb1p-xqR9TU0fUAv'
        # rebuild storage context
        storage_context = StorageContext.from_defaults(persist_dir=storage_directory)

        # load index
        index = load_index_from_storage(storage_context)
        # Query the LLM
        query_engine = index.as_query_engine()
        response = query_engine.query(query_text)

        return {"response": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/train_from_bucket")
def train_from_bucket(llm_id: str, source_id: str, metadata: str, ids: list):
    
    try:
        client = storage.Client()
        bucket = client.get_bucket(root_bucket)
        blobs = bucket.list_blobs(prefix=source_id)

        # Get Documents
        documents = []
        the_blobs = [blob for blob in blobs if blob.name in ids]
        for b in the_blobs:
            data = b.download_as_bytes(start=0, end=None)
            text_content = data.decode('utf-8')
            document = Document(
                text=text_content,
                metadata={"filename": b.name},
            )
            documents.append(document)

        # Vectorize
        storage_directory = storage_directory_base + '/' + llm_id 
        if os.path.exists(storage_directory) and len(documents) > 0:
            index = load_index_from_storage(storage_directory)
            for document in documents:
                index.insert(document)
        else:
            index = VectorStoreIndex.from_documents(documents, show_progress=True)

        # Persist the index to disk
        index.storage_context.persist(persist_dir=storage_directory)

        return {"status": True}


    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error training model: {str(e)}")
