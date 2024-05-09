# Use an official Python runtime as a base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /service

# Copy the current directory contents into the container at /app
COPY ./service /service

# Copy the requirements file into the container
COPY requirements.txt /service

# Copy the hugging face embedding
COPY llama_index_embeddings_huggingface-0.2.0.tar.gz /service

RUN pip install llama_index_embeddings_huggingface-0.2.0.tar.gz

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that the FastAPI app will run on
EXPOSE 8082

# Command to run the FastAPI application with Uvicorn
CMD ["uvicorn", "main:service", "--host", "0.0.0.0", "--port", "8082"]