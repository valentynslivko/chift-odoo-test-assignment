# Odoo Integration Test Task

## Notes:
- **DB schema does not cover relationship between contact and invoice created by a user of this API, meaning API endpoints would also omit filtering of data by the API user that is requesting data from DB**
- This API is not deployed on 3rd party infra because existing personal AWS account with free-tier is expired, due to time constraints and the scope of the assignment I've skipped that part, for the assignment sake, I'd deploy an EC2 instance, install docker/docker compose dependencies, cloned git repo and built/ran docker images on that particular instance (for the scope of the test assignment, normally you build and push images to container registries)
- CI/CD implementation does not make a lot of sense without the CD part in this case too
- If this API needs to be deployed for the validation - the simpliest way to allow external traffic is to port-forward the server port with tools like `ngrok`
- **`/api/utils/...` endpoints contain interfaces to access/work with Odoo directly with my API as a proxy, I've left these endpoints for convenience, they're not required in the assignment requirements**

## Getting Started

1.  **Environment Setup**: Copy `.env-example` to `.env` and fill in your Odoo credentials and database configuration.
2.  **Run with Docker**:
    ```bash
    docker-compose up --build
    ```
3.  **Migrations**: Database migrations are handled automatically during startup or can be run manually via:
    ```bash
    docker-compose exec api alembic upgrade head
    ```
    or 
    ```
    uv run alembic upgrade head
    ```
    after changing env variables to `POSTGRES_PORT=5439`
4.  **API Documentation**: Once running, visit `http://localhost:8000/docs` for the interactive OpenAPI documentation.
5. Register an API user in the documentation, login with `Authorize` button in the swagger docs

### Tech stack:
- FastAPI - API framework
- Celery/Celery Beat - async task queue with option to run tasks on schedule (beat). Normally, async-native apps in python use tools like `apscheduler` that supports `AsyncScheduler`, I've used celery-beat for convenience sake, as I do not have much complexity regarding async tasks in the scope of the assignment
- PostgreSQL - relational DB
- Redis - NoSQL DB - used as message broker for Celery
- Docker/Docker Compose 