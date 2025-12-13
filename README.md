

## Two‑Tier Flask + MySQL App with Docker, Docker Compose & Jenkins

This project is a simple two‑tier web application:

- **Backend:** Flask + MySQL connector (Python)  
- **Database:** MySQL (Docker container)  
- **Infrastructure:** AWS EC2 (Ubuntu)  
- **Packaging & Orchestration:** Docker + Docker Compose  
- **CI/CD:** Jenkins Pipeline on the same EC2 instance  

The app exposes:

- `GET /` – renders `templates/index.html`  
- `POST /add_student` – inserts a student name into MySQL  
- `GET /get_students` – returns JSON list of student names  
- `GET /health` – health check endpoint

***

## 1. Prerequisites

On AWS:

- AWS account with an Ubuntu 22.04 EC2 instance.
- Security group allows:
  - SSH: port 22 (your IP)
  - HTTP: port 80 (0.0.0.0/0) or 8080 if you mapped that port
  - Jenkins: port 8080 (optional, for external access)

On EC2 (Ubuntu):

- Docker Engine installed and working. 
- Docker Compose plugin installed (`docker compose version` works). 
- Jenkins installed and running at `http://<EC2_PUBLIC_IP>:8080`. 
- `jenkins` user added to `docker` group:
  ```bash
  sudo usermod -aG docker jenkins
  sudo systemctl restart jenkins
  ```

***

## 2. Project Structure

Repository (root):

```text
.
├── Dockerfile
├── Jenkinsfile
├── app.py
├── config.py
├── docker-compose.yml
├── requirements.txt
└── templates/
    └── index.html
```

- `app.py`: Flask application with routes and DB logic.
- `config.py`: optional configuration/module imports.
- `templates/index.html`: frontend page with form / UI.
- `requirements.txt`: Python dependencies (Flask, mysql‑connector‑python, etc.).
- `Dockerfile`: builds the Flask backend container.
- `docker-compose.yml`: defines `app` + `db` services.
- `Jenkinsfile`: defines the CI/CD pipeline stages.

***

## 3. Dockerfile (Flask backend)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["python", "app.py"]
```

`app.py` must start Flask with:

```python
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

***

## 4. docker-compose.yml (App + MySQL)

Example (adjust ports if you changed them):

```yaml
version: "3.8"

services:
  db:
    image: mysql:8.0
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: appdb
      MYSQL_USER: appuser
      MYSQL_PASSWORD: applogin
    # Typically no host port needed; app talks to db via Docker network
    # ports:
    #   - "3306:3306"
    volumes:
      - db_data:/var/lib/mysql

  app:
    build: .
    depends_on:
      - db
    environment:
      DB_HOST: db
      DB_USER: appuser
      DB_PASSWORD: applogin
      DB_NAME: appdb
    ports:
      - "80:5000"          # or "8080:5000" if using 8080 externally

volumes:
  db_data:
```

Flask reads DB config from environment:

```python
import os
import mysql.connector

def get_db():
    db_host = os.environ.get("DB_HOST", "localhost")
    db_user = os.environ.get("DB_USER", "root")
    db_password = os.environ.get("DB_PASSWORD", "12345")
    db_name = os.environ.get("DB_NAME", "educentral")
    return mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )
```

***

## 5. Running Locally on EC2 with Docker Compose

From the project root on EC2:

```bash
docker compose build
docker compose up -d
docker compose ps
```

You should see both `app` and `db` `Up`.

Initialize the `students` table:

```bash
docker compose exec db mysql -u appuser -papplogin appdb -e \
  "CREATE TABLE IF NOT EXISTS students (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255) NOT NULL);"
```

Test from EC2:

```bash
curl http://localhost/health          # -> OK
curl http://localhost/get_students    # -> []
```

Test from outside (replace `<EC2_IP>`):

```text
http://<EC2_IP>/
http://<EC2_IP>/health
http://<EC2_IP>/get_students
```

***

## 6. Jenkins Pipeline (CI/CD)

### Jenkinsfile

```groovy
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Images') {
            steps {
                sh 'docker compose build'
            }
        }

        stage('Deploy with Docker Compose') {
            steps {
                sh 'docker compose down || true'
                sh 'docker compose up -d'
            }
        }

        stage('Integration Test') {
            steps {
                sh 'sleep 10'
                sh 'curl -f http://localhost/health'
            }
        }
    }
}
```

### Jenkins job configuration

1. Create a **Pipeline** job (e.g. `2tier-flask-pipeline`).
2. Under **Pipeline**:
   - Definition: **Pipeline script from SCM**
   - SCM: **Git**
   - Repo URL: `https://github.com/<user>/<repo>.git`
   - Credentials: GitHub PAT if repo is private.
   - Branch: `main`
   - Script Path: `Jenkinsfile`.

### GitHub webhook

In GitHub repo:

- Settings → Webhooks → Add webhook  
  - Payload URL: `http://<EC2_IP>:8080/github-webhook/`  
  - Content type: `application/json`  
  - Event: “Just the push event”  

On every `git push`:

1. GitHub sends webhook to Jenkins.
2. Jenkins:
   - Checks out repo.
   - Builds Docker images (`docker compose build`).
   - Restarts stack (`docker compose up -d`).
   - Calls `http://localhost/health`.  
3. If all stages succeed, the new version is live at `http://<EC2_IP>/`.

***

## 7. Useful Debugging Commands

- Check containers:
  ```bash
  docker compose ps
  ```
- View logs:
  ```bash
  docker compose logs app
  docker compose logs db
  ```
- Rebuild without cache:
  ```bash
  docker compose build --no-cache
  ```
- Stop everything and clean:
  ```bash
  docker compose down
  ```

***

This setup matches a common “industrial” pattern for small two‑tier apps: Dockerized services, Compose for orchestration, and Jenkins Pipeline for automated build, deploy, and basic integration testing.
