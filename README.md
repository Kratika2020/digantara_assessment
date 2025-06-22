# digantara_assessment

# Job Scheduler Microservice

A RESTful microservice for managing scheduled jobs and their execution logs, built with Flask and PostgreSQL.

---

## Assumptions

- The `POST /jobs/run` endpoint assumes that it is being called at the exact scheduled time for any job.
- The purpose of this endpoint is to update the database entries in `Job` table and `JobLogs` table.
- The interval should be provided in seconds.

---

## API Endpoints

### `GET /jobs`

- **Description:** Retrieve a list of all jobs.
- **Response:**
  - JSON array of job objects (API clients)
  - HTML page with job table (browsers)

---

### `GET /jobs?form=true`

- **Description:** To access the form for creating a new job.
- **Response:**
  - HTML page with Create Job Form (browsers)

---

### `POST /jobs`

- **Description:** Create a new job.
- **Request Body:**
  - `jobname` (string, required): Name of the job (min 3 chars)
  - `startdate` (date, required): Start date (YYYY-MM-DD)
  - `starttime` (time, required): Start time (HH:MM)
  - `repeat` (boolean, optional): Whether the job repeats
  - `interval` (integer, optional): Interval in seconds (required if `repeat` is true)
  - `active` (boolean, optional): Whether the job is active
- **Validation:**
  - If `repeat` is true, `interval` must be set.
  - If `repeat` is false, `interval` must not be set.
  - `jobname` must be at least 3 characters.
  - `startdate` + `starttime` must be in the future.
- **Response:**
  - Success: Created job object (JSON) or redirect to job list (HTML)
  - Error: Validation errors

---

### `GET /jobs/<id>`

- **Description:** Retrieve details and logs for a specific job.
- **Response:**
  - JSON object with job and logs (API clients)
  - HTML page with job and logs table (browsers)

---

### `POST /jobs/run`

- **Description:** Execute all pending jobs whose scheduled time has arrived.
- **Functionality:**
  - Finds all active jobs with a pending log and `nextrun` <= now.
  - For one-time jobs: marks as finished and deactivates.
  - For repeating jobs: marks current log as finished, creates a new pending log with updated `nextrun`.
- **Response:**
  - JSON message indicating processing result.

---

## Database Schema

### Table: `job`

| Column    | Type    | Constraints                              | Description           |
| --------- | ------- | ---------------------------------------- | --------------------- |
| jobid     | Integer | Primary Key, Auto-increment              | Unique job identifier |
| jobname   | String  | Not Null                                 | Name of the job       |
| startdate | Date    | Not Null                                 | Date when job starts  |
| starttime | Time    | Not Null                                 | Time when job starts  |
| repeat    | Boolean | Default: False                           | Whether job repeats   |
| interval  | Integer | Nullable, Check: if repeat then not null | Interval in seconds   |
| active    | Boolean | Default: True                            | Whether job is active |

### Table: `joblog`

| Column  | Type     | Constraints                 | Description                         |
| ------- | -------- | --------------------------- | ----------------------------------- |
| logid   | Integer  | Primary Key, Auto-increment | Unique log identifier               |
| jobid   | Integer  | Foreign Key (`job.jobid`)   | Associated job                      |
| lastrun | DateTime | Nullable                    | Last execution timestamp            |
| nextrun | DateTime | Nullable                    | Next scheduled run                  |
| status  | String   | Default: "pending"          | Log status: pending/finished/failed |

---

## Validation & Business Logic

- **Job Creation:**
  - Enforces logical consistency between `repeat` and `interval`.
  - Ensures job name length and future scheduling.
- **Job Execution:**
  - Handles both one-time and repeating jobs.
  - Maintains job activity status and execution logs.

---

## Technology Stack

- **Backend:** Flask, Flask-SQLAlchemy, Flask-Smorest, Marshmallow
- **Database:** PostgreSQL
- **Containerization:** Docker, Docker Compose
- **ORM:** SQLAlchemy
- **Validation:** Marshmallow schemas

---

## Example Job JSON

```json
{
  "jobid": 1,
  "jobname": "Backup Database",
  "startdate": "2025-06-23",
  "starttime": "02:00:00",
  "repeat": true,
  "interval": 86400,
  "active": true
}
```

---

## Example JobLog JSON

```json
{
  "logid": 1,
  "jobid": 1,
  "lastrun": "2025-06-23T02:00:00",
  "nextrun": "2025-06-24T02:00:00",
  "status": "pending"
}
```

---

## Swagger/OpenAPI

- **Interactive API docs** available at `/swagger-ui` when running the service.

---

# Steps to run

- Use `docker-compose up` to start the API, PostgreSQL, and Adminer (DB UI).
- API available at `http://localhost:5000/jobs`
- Adminer available at `http://localhost:8080`
- Swagger-Docs available at `http://localhost:5000/swagger-ui`

---

# Scaling the Job Scheduler

- As the app has been deployed using Docker, It can be scaled **horizontally**.
- Multiple containers can be run in a distributed way to handle the traffic.
- In order to avoid overlodaing of a single container, a load balancer can be implemented to handle the traffic efficiently.
- As the API and database are running as separate services, they can be scaled individually.

---
