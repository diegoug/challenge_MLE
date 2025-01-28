
# Note

First of all, I would like to apologize as I was unable to fully complete the CI/CD pipeline and the application deployment on Google Cloud. The reason is that the time allotted for the challenge was not sufficient for me, as I had previously planned family activities during the weekend, which left me with limited time to address all aspects of the challenge.

That being said, I believe I have done a solid job on the parts I was able to complete, and I am submitting my work for your review. I hope it demonstrates my capabilities and merits consideration for the opportunity to work with you.

Thank you very much for this opportunity, and I truly appreciate your time and understanding.


## Development Mode

The project supports a development mode for running the environment with Docker Compose. This includes options for building the containers, running in standard mode, and debugging.

### Makefile Commands

#### **1. Start Development**
Start the Docker Compose environment using the default configuration:
```bash
make start-development
```

This command runs `docker-compose up` with the default settings from `docker-compose.yml`.

#### **2. Start Development with Build**
If you need to rebuild the containers before starting them, use the `BUILD=1` flag:
```bash
make start-development BUILD=1
```

This command forces a rebuild of the containers by running `docker-compose up --build`.

#### **3. Start Development in Debug Mode**
For debugging, use the `DEBUG=1` flag:
```bash
make start-development DEBUG=1
```

This command runs `docker-compose` with both the `docker-compose.yml` and `docker-compose.override.yml` files. The override file includes the following configuration:
```yaml
command: tail -f /dev/null
```

This allows the container to remain running without executing the application, so you can attach to it and debug manually.

#### **4. Stop Development**
Stop the Docker Compose environment:
```bash
make stop-development
```

This command stops and removes all containers, networks, and volumes created by Docker Compose.

---

### Debugging

In debug mode, the container uses the `command: tail -f /dev/null` to keep it running without starting the application. This allows you to manually execute commands inside the container. To attach to the container:
```bash
docker exec -it <container_name> bash
```

Replace `<container_name>` with the actual name of the container.

---

### Notes

- Ensure Docker and Docker Compose are installed and running on your system.
- Use the `docker-compose.override.yml` file only for debugging.
- In standard mode, the application runs as defined in the `Dockerfile`.

# Flight Delay Prediction API Deployment

This document outlines the steps taken to deploy the `Flight Delay Prediction API` using **Google Cloud Platform (GCP)**.

---

## 1. Project Setup on GCP

1. **Create a GCP Project**:
   - Go to the [GCP Console](https://console.cloud.google.com/).
   - Create a new project or use an existing one.
   - Enable billing for the project.

2. **Enable Required APIs**:
   - Enable the following APIs:
     - **Cloud Run API**
     - **Cloud Build API**
   - Navigate to "APIs & Services > Enable APIs and Services" in the GCP Console.

---

## 2. Prepare Docker Container

1. **Create a `Dockerfile`**:
   The Dockerfile defines how the container for the API is built. Below is the `Dockerfile` used for the deployment:
   ```dockerfile
   # Use Python base image
   FROM python:3.9-slim

   # Set the working directory
   WORKDIR /app

   # Copy application files
   COPY . /app

   # Install dependencies
   RUN pip install --no-cache-dir --upgrade pip \
       && pip install --no-cache-dir -r requirements.txt

   # Expose the port Cloud Run will use
   EXPOSE 8080

   # Command to run the API
   CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]
   ```

2. **Add a `requirements.txt` File**:
   Include all necessary dependencies for the API in a `requirements.txt` file:
   ```plaintext
   fastapi
   uvicorn
   pydantic
   ```

3. **Test the Container Locally**:
   Build and run the container locally to ensure it works:
   ```bash
   docker build -t flight-delay-api .
   docker run -p 8080:8080 flight-delay-api
   ```

   Access the API locally at `http://localhost:8080`.

---

## 3. Deploy to Cloud Run

1. **Authenticate with GCP**:
   Login to GCP using the CLI:
   ```bash
   gcloud auth login
   ```

2. **Set Your GCP Project**:
   Configure the project to use:
   ```bash
   gcloud config set project [PROJECT_ID]
   ```

3. **Build and Push Docker Image**:
   Use Google Cloud Build to build and push the Docker image to Google Container Registry (GCR):
   ```bash
   gcloud builds submit --tag gcr.io/[PROJECT_ID]/flight-delay-api
   ```

4. **Deploy to Cloud Run**:
   Deploy the image to Cloud Run:
   ```bash
   gcloud run deploy flight-delay-api \
       --image gcr.io/[PROJECT_ID]/flight-delay-api \
       --platform managed \
       --region us-central1 \
       --allow-unauthenticated
   ```

   After deployment, Cloud Run will provide a public URL for the API, e.g.:
   ```
   https://flight-delay-api-xxxxx.a.run.app
   ```

---

## 4. Verify the Deployment

1. **Test the API**:
   Use `curl` or Postman to send a request to the deployed API:
   ```bash
   curl -X POST \
       -H "Content-Type: application/json" \
       -d '{"Fecha-I": "2025-01-27 12:00:00", "Vlo-I": "LA123", "Ori-I": "SCL", "Des-I": "LIM", "Emp-I": "LA", "Fecha-O": "2025-01-27 12:45:00"}' \
       https://flight-delay-api-xxxxx.a.run.app/predict
   ```

2. **Check Logs**:
   View the logs to confirm the API is functioning correctly:
   ```bash
   gcloud logs read --project [PROJECT_ID] --service flight-delay-api --region us-central1
   ```

---

## 5. Troubleshooting

- **Error: Port Not Listening**:
  Ensure the `Dockerfile` includes the following line:
  ```dockerfile
  CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]
  ```

- **Authentication Issues**:
  Ensure you are logged in to GCP using `gcloud auth login` and have set the correct project ID.

- **API Timeout**:
  Increase the Cloud Run timeout if the container takes too long to start:
  ```bash
  gcloud run services update flight-delay-api --timeout=300
  ```

---

## 6. Conclusion

The API was successfully deployed to Cloud Run and can be accessed at:
```
https://flight-delay-api-xxxxx.a.run.app
```

If there are any issues, check the logs or contact the developer.

``` 
