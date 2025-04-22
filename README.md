# SWIFT Code API Assignment

This project implements a FastAPI application providing endpoints to manage SWIFT code data and tests to test them, containerized using Docker.

## Prerequisites

*   Docker Desktop installed and running on your machine.

## Project Structure

SWIFT-API/
├── main.py # FastAPI application code
├── SWIFT-CODES.db # SQLite database file (initial data)
├── scripts/
│ └── populateDB.py # convert SWIFT-CODES.csv into populated sqlite db
├── Dockerfile # Instructions to build the Docker image
├── requirements.txt # Python dependencies
├── tests/ # Unit and integration tests (optional to include)
│ └── ...
└── README.md # These instructions
└── # other

## Running the Application

1.  **Clone/Download the Repository:** Get the project files onto your local machine.

2.  **Build the Docker Image:**
    Open a terminal, navigate to the project's root directory (`SWIFT-API/`), and run the following command:
    ```bash
    docker build -t swift-api .
    ```
    *(This will build the Docker image using the `Dockerfile` and tag it as `swift-api`)*

3.  **Run the Docker Container:**
    Once the image is built, run the container with this command:
    ```bash
    docker run -d --name swift-api-container -p 8080:8000 swift-api
    ```
    *   `-d`: Runs the container in detached mode (background).
    *   `--name swift-api-container`: Assigns a name to the container.
    *   `-p 8080:8000`: Maps port 8080 on your local machine (host) to port 8000 inside the container (where the FastAPI app runs).
    *   `swift-api`: Specifies the image to use.

4.  **Access the API:**
    The API should now be accessible on your local machine at port 8080:
    *   **Swagger UI (Interactive Docs):** [http://localhost:8080/docs](http://localhost:8080/docs)
    *   **Example Endpoint (using curl):**
        ```bash
        curl http://localhost:8080/v1/swift-codes/country/US
        ```
        *(Replace `US` with any desired country code)*

## Database Persistence

The current setup copies the `SWIFT-CODES.db` file into the Docker image during the build process. Any changes made to the database via the API while the container is running will **only exist within that container**. If the container is stopped and removed, the changes will be lost, and a new container started from the image will have the original database state.


## Stopping the Container

To stop the running container, use the following command:

```bash
docker stop swift-api-container
```


To remove the stopped container:

```bash
docker rm swift-api-container
```

