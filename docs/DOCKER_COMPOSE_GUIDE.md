# What Happens When You Run `docker compose up --build`

This guide explains step by step what happens when you run that command. No prior Docker, Python, or Django experience assumed.

---

## 1. What Are We Even Running?

- **Docker** – Runs your app (and its dependencies) inside isolated “containers” so it behaves the same on every machine.
- **Docker Compose** – A tool that reads `docker-compose.yml` and starts **multiple** containers together (database, cache, and your app).
- **`docker compose up --build`** means:
  - **`up`** – Start all the services defined in `docker-compose.yml`.
  - **`--build`** – Before starting, (re)build any service that has a `build` section (in this project, the **web** app).

So: “Start everything, and rebuild the app image if needed.”

---

## 2. What’s in This Project? (The Three “Services”)

Your `docker-compose.yml` defines **3 services** (3 containers that work together):

| Service | What it is (in simple terms) | Why the app needs it |
|--------|-------------------------------|------------------------|
| **db**  | A **PostgreSQL database**     | Stores your app’s data (users, plans, etc.) |
| **redis** | A **Redis** in-memory store | Used for real-time features (e.g. WebSockets) and often caching |
| **web**   | Your **Django app** (Python) | The actual website/API that you visit and that talks to db and redis |

When you run `docker compose up --build`, Docker will:

1. Build the **web** image (if needed).
2. Start **db** and **redis**.
3. Start **web**, which runs migrations then the Django dev server.

Below is what happens in more detail.

---

## 3. Step-by-Step: What Actually Happens

### Phase A: Building the “web” Service

Only the **web** service is built from source; **db** and **redis** use pre-made images.

1. **Docker reads** `docker-compose.yml` and sees:
   - `web` has `build: context: ., dockerfile: docker/Dockerfile`.

2. **Docker runs the Dockerfile** (`docker/Dockerfile`):
   - **FROM python:3.11-slim**  
     Start from a minimal Linux image that already has Python 3.11.
   - **WORKDIR /app**  
     All following commands run inside `/app` in the container.
   - **ENV PYTHONDONTWRITEBYTECODE=1, PYTHONUNBUFFERED=1**  
     Python settings so you don’t clutter the image with `.pyc` files and so logs show up immediately.
   - **RUN apt-get update && apt-get install -y build-essential libpq-dev ...**  
     Install system packages needed to compile Python libraries (especially the PostgreSQL driver).
   - **COPY requirements.txt /app/requirements.txt**  
     Copy your dependency list into the image.
   - **RUN pip install -r requirements.txt**  
     Install Python packages (Django, psycopg2, channels, strawberry-graphql, etc.) **inside the container**.
   - **COPY . /app**  
     Copy the rest of your project (Django code, `manage.py`, etc.) into `/app`.

3. **Result:** A new **Docker image** for your app is created (or updated). Nothing is “running” yet; it’s just a snapshot of the environment your app will run in.

So “after run docker compose up --build” in terms of **building**: only the **web** image is built; **db** and **redis** are not built, they use existing images.

---

### Phase B: Starting the Containers

4. **Volumes**
   - Docker creates a **volume** named `pgdata` (if it doesn’t exist). This is where PostgreSQL will store its data so it survives when you stop/restart the containers.

5. **Service: db (PostgreSQL)**
   - Docker downloads the image **postgres:15** from Docker Hub (if not already on your machine).
   - Starts a container running **PostgreSQL 15**.
   - Sets environment variables: database name `ozue`, user `ozue`, password `ozue`.
   - Maps port **5432** on your machine to port 5432 in the container (so your app can connect to “db:5432”).
   - Uses the `pgdata` volume so data is stored on your disk.

6. **Service: redis**
   - Docker downloads the image **redis:7** (if needed).
   - Starts a container running **Redis 7**.
   - Maps port **6379** so the app can connect to “redis:6379”.

7. **Service: web (Django)**
   - Because of **depends_on: [db, redis]**, Compose starts **web** after **db** and **redis** (it does *not* wait until the database is “ready”, just until the containers exist).
   - Docker starts a container from the **web** image you built.
   - It mounts your **project folder** into `/app` in the container (so code changes on your machine are visible inside the container).
   - It sets environment variables the app needs:
     - **DJANGO_SETTINGS_MODULE** – tells Django which settings file to use.
     - **DATABASE_URL** – how to connect to PostgreSQL: `postgres://ozue:ozue@db:5432/ozue`.
     - **REDIS_URL** – how to connect to Redis: `redis://redis:6379/0`.
     - **DEBUG=1** – turns on Django’s debug mode for development.

So after this phase you have three running containers: **db**, **redis**, and **web**.

---

### Phase C: The “web” Container Runs Its Startup Command

8. **The `command` in docker-compose** for **web** is:
   ```text
   sh -c "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"
   ```
   So the container runs a shell that executes two Python commands in order.

9. **First: `python manage.py migrate`**
   - **manage.py** – Django’s command-line helper (lives in your project root).
   - **migrate** – Reads your app’s **migrations** (instructions for the database schema) and applies them to the PostgreSQL database.
   - In practice: creates/updates tables (e.g. for users, planners) in the `ozue` database so your Django models match the real database.
   - If this fails (e.g. database not ready), the whole command fails and the server won’t start.

10. **Second: `python manage.py runserver 0.0.0.0:8000`**
    - **runserver** – Starts Django’s **development server** (a simple HTTP server for local development).
    - **0.0.0.0:8000** – Listen on port 8000 on all network interfaces, so you can reach it from your machine as **http://localhost:8000** (because in docker-compose you have `ports: - "8000:8000"`).

So “after run docker compose up --build” in terms of **runtime**: the **web** container has run **migrate** and then started the **Django dev server** on port 8000.

---

## 4. Summary Flow (Detailed)

| Step | What happens |
|------|----------------|
| 1 | You run `docker compose up --build`. |
| 2 | Docker builds the **web** image from `docker/Dockerfile` (Python 3.11, install deps from `requirements.txt`, copy your code). |
| 3 | Docker creates/uses the **pgdata** volume for database data. |
| 4 | **db** container starts (PostgreSQL 15, DB `ozue`, port 5432). |
| 5 | **redis** container starts (Redis 7, port 6379). |
| 6 | **web** container starts (depends on db and redis). |
| 7 | Inside **web**: `python manage.py migrate` runs → database tables are created/updated. |
| 8 | Inside **web**: `python manage.py runserver 0.0.0.0:8000` runs → Django dev server listens on 8000. |
| 9 | You can open **http://localhost:8000** in your browser; your Django app is talking to PostgreSQL (**db**) and Redis (**redis**). |

---

## 5. Quick Reference

- **Database (PostgreSQL):** host `localhost`, port **5432**, database `ozue`, user/password `ozue`.
- **Redis:** host `localhost`, port **6379**.
- **Your app:** **http://localhost:8000** (Django + GraphQL, etc.).

If you run only **db** and **redis** (e.g. `docker compose up db redis -d`), then the **web** service does not run: no migrate, no runserver. Full app startup happens when you run **`docker compose up --build`** (or `docker compose up` after a previous build).
