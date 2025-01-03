File Structure
visis-app/
├── .venv/                      # Virtual environment
├── app/
│   ├── __init__.py             # Initialize the app module
│   ├── main.py                 # Main application entry point
│   ├── api/                    # API endpoints
│   │   ├── endpoints/
│   │   │   ├── admin/          # Admin-specific endpoints
│   │   │   │   ├── __init__.py
│   │   │   │   ├── users.py
│   │   │   │   ├── documents.py
│   │   │   │   ├── settings.py
│   │   │   ├── user/           # User-specific endpoints
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── documents.py
│   │   │   │   ├── audiobooks.py
│   │   │   │   ├── bookmarks.py
│   │   │   │   ├── preferences.py
│   │   │   │   ├── scanning.py
│   │   │   │   ├── accessibility.py
│   │   │   │   ├── languages.py
│   │   │   │   ├── activities.py
│   │   │   │   ├── feedback.py
│   │   │   ├── middleware/      # Middleware
│   │   │   │   ├── ip_whitelist.py
│   ├── core/                   # Core functionalities
│   │   ├── __init__.py
│   │   ├── config.py           # Configuration settings
│   │   └── security.py         # Security-related functionalities
│   ├── models/                 # Database models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── document.py
│   │   ├── audiofile.py
│   │   ├── user_preference.py
│   │   ├── user_bookmark.py
│   │   ├── scanning_history.py
│   │   ├── accessibility.py
│   │   ├── language.py
│   │   ├── document_language.py
│   │   ├── audiobook_language.py
│   │   ├── user_activity.py
│   │   ├── feedback.py
│   │   └── app_setting.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── document.py
│   │   ├── audiofile.py
│   │   ├── user_preference.py
│   │   ├── user_bookmark.py
│   │   ├── scanning_history.py
│   │   ├── accessibility.py
│   │   ├── language.py
│   │   ├── document_language.py
│   │   ├── audiobook_language.py
│   │   ├── user_activity.py
│   │   ├── feedback.py
│   │   └── app_setting.py
│   ├── services/               # Business logic and services
│   │   ├── __init__.py
│   │   └── document_service.py
│   ├── utils/                  # Utility functions
│   │   ├── __init__.py
│   │   ├── helpers.py
│   │   └── send_reset_password_email.py
├── tests/                      # Unit tests
│   ├── __init__.py
│   └── test_main.py
├── .env                        # Environment variables
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation


## Setup Instructions

1. **Clone the repository**:
    ```sh
    git clone https://github.com/yourusername/visis-backend.git
    cd visis-backend/visis-app
    ```

2. **Create and activate a virtual environment**:
    ```sh
    python -m venv .venv
    .venv\Scripts\activate  # On Windows
    # source .venv/bin/activate  # On macOS/Linux
    ```

3. **Install dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

4. **Set up environment variables**:
    - Create a `.env` file in the root directory and add the necessary environment variables:
    ```properties
    SECRET_KEY=your_secret_key
    ALGORITHM=HS256
    SQLALCHEMY_DATABASE_URL=your_database_url
    ```

5. **Run the application**:
    ```sh
    uvicorn app.main:app --reload --port 8081
    ```

6. **Run tests**:
    ```sh
    pytest
    ```


## Docker
You should see this below

=> => naming to docker.io/library/visiszipnov26_app:latest                                                                                                                             0.0s
 => => unpacking to docker.io/library/visiszipnov26_app:latest                                                                                                                         12.2s

What's next:
    View a summary of image vulnerabilities and recommendations → docker scout quickview 
WARNING: Image for service app was built because it did not already exist. To rebuild this image you must use `docker-compose build` or `docker-compose up --build`.
Creating redis ... done

## Docker Container

Great job setting up your Docker environment! Now, let's proceed to **test your FastAPI application locally** using Docker Compose before moving to AWS. Here's a step-by-step guide to ensure everything is working correctly:

---

---
docker build -t adesojialu/visiszipnov26_app:latest .
docker login
docker push adesojialu/visiszipnov26_app:latest
docker scout quickview adesojialu/visiszipnov26_app:latest
 View vulnerabilities → docker scout cves adesojialu/visiszipnov26_app:latest
    View base image update recommendations → docker scout recommendations adesojialu/visiszipnov26_app:latest
    Include policy results in your quickview by supplying an organization → docker scout quickview adesojialu/visiszipnov26_app:latest --org <organization>

docker-compose down --remove-orphans
docker-compose -f docker-compose.local.yml up -d --build

docker logs -f redis
docker logs -f fastapi_app
docker logs -f nginx_proxy

---


## **Step 1: Verify Container Status**

First, confirm that both your FastAPI app and Redis containers are running.

**Command:**
```bash
docker-compose ps
```

**Expected Output:**
```
      Name                    Command               State          Ports
--------------------------------------------------------------------------
visiszipnov26_app   gunicorn app.main:app --worker-class ...   Up      0.0.0.0:8000->8000/tcp
redis               docker-entrypoint.sh redis ...             Up      6379/tcp
```

- **State:** Both `app` and `redis` services should be in the `Up` state.
- **Ports:** Ensure that the ports are correctly mapped (e.g., `8000:8000` for the app and `6379:6379` for Redis).

---


```


(venv) adesoji@adesoji-Lenovo-Legion-7-15IMH05:~/Documents/Visis_revisions/Visiszipnov26fullperfect/Visiszipnov26$ docker run -d -p 8000:8000 adesojialu/visiszipnov26_app:latest
f8673934dc2c246918eedb6653b1379603455c6ffc80305b540aa85f5dac695d
```

## **Step 2: Access the FastAPI Application**

### **2.1. Root Endpoint**

Open your browser or use a tool like `curl` or **Postman** to send a request to the root endpoint.

**Using Browser:**

Navigate to:
```
http://localhost:8000/docs#/  or
```

**Expected Response:**
```json
{
  "message": "Welcome to the Visis App API"
}
```

### **2.2. API Documentation**

FastAPI automatically generates interactive API documentation.

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

**Verify:**

- Both documentation interfaces should load without errors.
- You should see your API endpoints listed and be able to interact with them.

### **2.3. Health Check Endpoint (Optional)**

If you've added a `/health` endpoint for health checks, verify it.

**Using Browser or Curl:**

```
http://localhost:8000/health  
```

or 

```
http://0.0.0.0:8000/
```

**Expected Response:**
```json
{
  "status": "healthy"
}
```

---

## **Step 3: Check Application Logs**

Monitoring logs can help identify issues and verify that your application is functioning correctly.

**Command:**
```bash
docker-compose logs -f app
```

- **`-f`**: Follows the log output in real-time.
- **`app`**: Specifies the service name (as defined in `docker-compose.yml`).

**What to Look For:**

- Confirmation that Uvicorn and Gunicorn are running.
- Logs indicating successful connections to Redis and the database.
- Any error messages or warnings that need attention.

**Example Log Output:**
```
app_1  | INFO:     Started server process [1]
app_1  | INFO:     Waiting for application startup.
app_1  | INFO:     Application startup complete.
app_1  | INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
app_1  | INFO:     Request path: /, Query params: 
app_1  | INFO:     Root endpoint accessed
```

---

## **Step 4: Verify Redis Connectivity**

Ensure that your application can communicate with Redis.

### **4.1. Using Redis CLI**

If you have `redis-cli` installed, connect to Redis to verify it's operational.

**Connect to Redis:**
```bash
redis-cli -h localhost -p 6379
```

**Ping Redis:**
```bash
127.0.0.1:6379> PING
```

**Expected Response:**
```
PONG
```

**Exit Redis CLI:**
```bash
127.0.0.1:6379> EXIT
```

### **4.2. Application-Level Verification**

If your application uses Redis for caching or other functionalities, perform actions that trigger Redis operations and verify through logs or application behavior that Redis is being used correctly.

---

## **Step 5: Verify Database Connectivity**

Ensure that your application can connect to the PostgreSQL database hosted on Supabase.

### **5.1. Check Application Logs**

Look for logs indicating successful database connections or any connection errors.

**Command:**
```bash
docker-compose logs -f app
```

**What to Look For:**
- Messages confirming database initialization and connectivity.
- Any error messages related to database connections.

### **5.2. Test API Endpoints That Interact with the Database**

For example, if you have endpoints to fetch users or documents, try accessing them.

**Using Browser or Curl:**

**Fetch Users:**
```
http://localhost:8000/users/
```

**Expected Response:**
A JSON array of users, e.g.,
```json
[
  {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com"
  },
  ...
]
```

**Note:** Ensure that your database has data or that you've seeded it appropriately for testing.

---

## **Step 6: Run Automated Tests (Optional)**

If you have automated tests set up using `pytest`, you can run them to ensure your application behaves as expected.

### **6.1. Adding a Test Service in `docker-compose.yml`**

Modify your `docker-compose.yml` to include a test service.

**Updated `docker-compose.yml`:**
```yaml
version: '3.8'

services:
  app:
    build: .
    container_name: fastapi_app
    command: gunicorn app.main:app --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --workers 4
    ports:
      - "8000:8000"
    env_file:
      - .env
    environment:
      - DATABASE_URL=${SQLALCHEMY_DATABASE_URL}
      - REDIS_URL=redis://redis:6379/0
      - CORS_ALLOWED_ORIGINS=https://your-production-domain.com,https://www.your-production-domain.com
      - ENV=production
    depends_on:
      - redis
    restart: unless-stopped

  redis:
    image: redis:7.0.12
    container_name: redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  test:
    build: .
    container_name: fastapi_test
    command: pytest
    env_file:
      - .env
    environment:
      - DATABASE_URL=${SQLALCHEMY_DATABASE_URL}
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis

volumes:
  redis_data:
```

### **6.2. Running Tests**

**Command:**
```bash
docker-compose run test
```

**What This Does:**
- Builds and starts the `test` service.
- Runs `pytest` inside the container.
- Outputs test results to your terminal.

**Alternative: Running Tests in the Running App Container**
```bash
docker-compose exec app pytest
```

---

## **Step 7: Refine for Production (Optional)**

While the current setup is great for development, consider additional refinements for production:

### **7.1. Use a Reverse Proxy (e.g., Nginx)**

Set up a reverse proxy to handle HTTPS, load balancing, and other functionalities.

**Add Nginx to `docker-compose.yml`:**
```yaml
version: '3.8'

services:
  app:
    # ... existing configurations ...
  
  redis:
    # ... existing configurations ...

  nginx:
    image: nginx:latest
    container_name: nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./certs:/etc/nginx/certs
    depends_on:
      - app
    restart: unless-stopped

volumes:
  redis_data:
```

**Create Nginx Configuration (`nginx/nginx.conf`):**
```nginx
events {}

http {
    server {
        listen 80;
        server_name your-production-domain.com www.your-production-domain.com;

        # Redirect HTTP to HTTPS
        return 301 https://$host$request_uri;
    }

    server {
        listen 443 ssl;
        server_name your-production-domain.com www.your-production-domain.com;

        ssl_certificate /etc/nginx/certs/fullchain.pem;
        ssl_certificate_key /etc/nginx/certs/privkey.pem;

        location / {
            proxy_pass http://app:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}

To check the logs of the running containers, you can use the `docker logs` command followed by the container name or ID. Here's how you can do it for each of your containers:

### 1. **Nginx Proxy Logs**
To view the logs for the Nginx proxy container:
```bash
docker logs nginx_proxy
```

### 2. **FastAPI App Logs**
To view the logs for the FastAPI app container:
```bash
docker logs fastapi_app
```

### 3. **Redis Logs**
To view the logs for the Redis container:
```bash
docker logs redis
```

### Additional Options:
- If you want to **follow the logs in real-time**, add the `-f` flag:
  ```bash
  docker logs -f nginx_proxy
  ```
- To **view specific lines** from the end of the logs, use the `--tail` option:
  ```bash
  docker logs --tail 50 fastapi_app
  ```
  This will show the last 50 lines of logs.

Let me know if you encounter any issues while reviewing the logs! 🚀
```

**Notes:**
- Replace `your-production-domain.com` with your actual domain.
- Obtain SSL certificates (e.g., using Let's Encrypt) and place them in the `certs` directory.

### **7.2. Secure Environment Variables**

Ensure sensitive data is handled securely in production:
- Use environment variables managed by your orchestration tool (e.g., AWS ECS Secrets).
- Avoid hardcoding sensitive information in your `docker-compose.yml`.

### **7.3. Optimize Dockerfile for Production**

Consider multi-stage builds to reduce image size and enhance security.

**Example Multi-Stage Dockerfile:**
```dockerfile
# Stage 1: Build
FROM python:3.11.6-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --user -r requirements.txt

COPY . .

# Stage 2: Production
FROM python:3.11.6-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.local /root/.local
COPY --from=builder /app /app

ENV PATH=/root/.local/bin:$PATH

EXPOSE 8000

CMD ["gunicorn", "app.main:app", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--workers", "4"]
```

**Benefits:**
- Reduces the final image size by excluding build dependencies.
- Enhances security by not including unnecessary tools in the production image.

---

## **Step 8: Next Steps for Deployment to AWS**

After successfully testing your application locally, you can proceed to deploy it to AWS. Here's a high-level overview:

### **8.1. Push Docker Images to AWS ECR**

1. **Create an ECR Repository:**
   - Navigate to the [Amazon ECR Console](https://console.aws.amazon.com/ecr/home).
   - Click **Create repository**.
   - Name your repository (e.g., `visiszipnov26_app`).

2. **Authenticate Docker to Your ECR Repository:**
   ```bash
   aws ecr get-login-password --region your-region | docker login --username AWS --password-stdin your-account-id.dkr.ecr.your-region.amazonaws.com
   ```

3. **Tag Your Docker Image:**
   ```bash
   docker tag visiszipnov26_app:latest your-account-id.dkr.ecr.your-region.amazonaws.com/visiszipnov26_app:latest
   ```

4. **Push the Image to ECR:**
   ```bash
   docker push your-account-id.dkr.ecr.your-region.amazonaws.com/visiszipnov26_app:latest
   ```

### **8.2. Deploy to AWS ECS with Fargate**

1. **Create an ECS Cluster:**
   - Navigate to the [Amazon ECS Console](https://console.aws.amazon.com/ecs/home).
   - Click **Create Cluster** and choose **Networking only (Fargate)**.
   - Name your cluster (e.g., `visiszipnov26_cluster`).

2. **Create a Task Definition:**
   - In ECS, go to **Task Definitions** and click **Create new Task Definition**.
   - Choose **Fargate**.
   - Configure the task:
     - **Task Definition Name:** `visiszipnov26_task`
     - **Container Definitions:**
       - **Container Name:** `visiszipnov26_app`
       - **Image:** `your-account-id.dkr.ecr.your-region.amazonaws.com/visiszipnov26_app:latest`
       - **Port Mappings:** Host port `8000` to container port `8000`
       - **Environment Variables:** Set necessary environment variables (e.g., `DATABASE_URL`, `REDIS_URL`, etc.)
       - **Secrets:** Use AWS Secrets Manager or ECS Secrets for sensitive data.

3. **Create an ECS Service:**
   - Within your ECS cluster, click **Create Service**.
   - Choose **Fargate** as the launch type.
   - Select your task definition (`visiszipnov26_task`).
   - Configure service settings:
     - **Service Name:** `visiszipnov26_service`
     - **Number of Tasks:** Start with `1` for initial deployment.
   - Set up networking:
     - **VPC:** Choose your VPC.
     - **Subnets:** Select public or private subnets as per your architecture.
     - **Security Groups:** Allow inbound traffic on port `8000` from appropriate sources (e.g., ALB).
   - (Optional) **Load Balancer:** Attach an Application Load Balancer (ALB) for better traffic management and SSL termination.

4. **Update DNS Records:**
   - Point your domain to the ALB's DNS name.

### **8.3. Set Up AWS ElastiCache for Redis**

1. **Create a Redis Cluster:**
   - Navigate to the [Amazon ElastiCache Console](https://console.aws.amazon.com/elasticache/home).
   - Click **Create** and choose **Redis**.
   - Configure your Redis cluster (node type, number of nodes, etc.).
   - Ensure it's in the same VPC as your ECS cluster.
   - Update your application’s `REDIS_URL` to point to the ElastiCache endpoint.

### **8.4. Migrate Database to AWS RDS**

As previously discussed, ensure that your database migration is complete and that the application can connect to the new RDS instance.

---

## **Step 9: Testing After Deployment to AWS**

Once deployed to AWS, perform similar tests to ensure everything works in the production environment.

### **9.1. Access the Application via Domain**

Navigate to your production domain:
```
https://your-production-domain.com/
```

**Expected Response:**
```json
{
  "message": "Welcome to the Visis App API"
}
```

### **9.2. Test API Documentation**

- **Swagger UI:** [https://your-production-domain.com/docs](https://your-production-domain.com/docs)
- **ReDoc:** [https://your-production-domain.com/redoc](https://your-production-domain.com/redoc)

### **9.3. Verify Redis and Database Connections**

Ensure that Redis and the database are correctly connected in the production environment by testing relevant endpoints and checking logs.

---

## **Summary**

You've successfully:

1. **Created and Refined Dockerfile:**
   - Optimized for your FastAPI application using a supported Python image.
   - Set up environment variables and dependencies.

2. **Set Up `docker-compose.yml`:**
   - Managed your FastAPI app and Redis for local development.
   - Configured environment variables and service dependencies.

3. **Built and Ran Docker Containers:**
   - Verified that both `app` and `redis` services are running.

4. **Tested Application Locally:**
   - Accessed the FastAPI application and its documentation.
   - Verified Redis and database connectivity.
   - Optionally ran automated tests.

5. **Prepared for Production Deployment:**
   - Pushed Docker images to AWS ECR.
   - Deployed to AWS ECS with Fargate.
   - Set up AWS ElastiCache for Redis and migrated your database to AWS RDS.

6. **Verified Deployment on AWS:**
   - Ensured the application is accessible via your production domain.
   - Verified all services are operational.

---

## **Troubleshooting Tips**

- **Port Conflicts:**
  - Ensure ports `8000` and `6379` are not used by other applications on your host machine.

- **Environment Variables:**
  - Double-check that all necessary environment variables are correctly set in your `.env` file.
  - Ensure that sensitive information is not exposed and is managed securely.

- **Service Dependencies:**
  - Ensure that Redis and the database are up and accessible before the FastAPI app starts.
  - Use `depends_on` in `docker-compose.yml` to manage service startup order.

- **Logs:**
  - Continuously monitor logs for any errors or warnings.
  - Use `docker-compose logs -f app` and `docker-compose logs -f redis` to view real-time logs.

- **Database Connectivity:**
  - Ensure that the `SQLALCHEMY_DATABASE_URL` is correct and that the database is accessible.
  - Verify that network security groups allow connections from your application to the database.

- **Redis Connectivity:**
  - Ensure that `REDIS_URL` points to the correct Redis instance.
  - Verify that Redis is running and accessible.

---

Feel free to reach out if you encounter any specific issues or need further assistance with any of these steps!


## Project Overview

This project is a backend service built with FastAPI, SQLAlchemy, and Pydantic. It includes user authentication, CRUD operations for users and documents, and unit tests.

## License

This project is licensed under the MIT License.