
### Project Structure Overview

- Python 3.11+
- Docker and Docker Compose
- PostgreSQL 16
- Git

| Type      | Parent  | Name                        | Description                                            |
| --------- | ------- | --------------------------- | ------------------------------------------------------ |
| directory | .       | **devops**                | Holds Docker files, Podman files, and deployment scripts. |
| directory | .       | **docs**                  | Contains documentation such as the README, Podman configurations, and additional guides. |
| directory | .       | **migrations**            | Manages database migrations (e.g., Alembic scripts) for schema evolution. |
| directory | .       | **src**                   | Contains the application source code, including FastAPI endpoints, models, and business logic. |
| directory | .       | **tests**                 | Houses all test suites (unit, integration, etc.) for ensuring application quality. |
| file      | .       | README.md                 |                                                        |
| directory | .       | .github                   | Contains GitHub configuration files                    |
| file      | .github | ISSUE_TEMPLATE.md         | Issue template                                         |
| file      | .github | PULL_REQUEST_TEMPLATE.md  | Pull request template                                  |
| directory | .github | workflows                 | Contains GitHub Actions workflow files                 |
| file      | workflows | ci.yml                    | Example GitHub Actions workflow                        |


Below are two table examples that illustrate two common approaches to configuring one **Dockerfile** and **docker-compose** setup for multiple environments (development, production, and testing).

---

### **Table 1: Using Environment Variables & Build Arguments**

This approach uses a single Dockerfile and docker-compose file that adapt their behavior based on environment variables and external `.env` files.

| Component                  | Development                                 | Production                                  | Testing                                   | Description                                                                                                 |
| -------------------------- | ------------------------------------------- | ------------------------------------------- | ----------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| **Dockerfile Build Argument** | `--build-arg ENVIRONMENT=dev`              | `--build-arg ENVIRONMENT=prod`              | `--build-arg ENVIRONMENT=test`             | Passes an environment identifier into the Docker build process.                                           |
| **Dockerfile ENV Variable**   | `ENV ENVIRONMENT=dev` (default or via build arg) | `ENV ENVIRONMENT=prod` (default or via build arg) | `ENV ENVIRONMENT=test` (default or via build arg) | The Dockerfile can adjust behavior (e.g., install dev tools) based on the `ENVIRONMENT` value.              |
| **.env File**                | `.env.dev` (with dev-specific settings)     | `.env.prod` (with prod-specific settings)   | `.env.test` (with test-specific settings)    | Each file contains environment-specific configuration that docker-compose loads at runtime.                 |
| **docker-compose Service**   | Uses `env_file: - .env.${ENVIRONMENT}` and passes `ENVIRONMENT=${ENVIRONMENT}` | Same as development, with different values set in `.env.prod` | Same as development, with different values set in `.env.test` | The service configuration uses the external environment variable (set prior to launching) to select settings. |

**Usage Example (Shell):**

```bash
# For development:
export ENVIRONMENT=dev
docker-compose up

# For production:
export ENVIRONMENT=prod
docker-compose up

# For testing:
export ENVIRONMENT=test
docker-compose up
```

---

### **Table 2: Using docker-compose Override Files**

This approach employs a base `docker-compose.yml` file for common settings and separate override files for each environment.

| Component                     | Development                             | Production                              | Testing                                 | Description                                                                                           |
| ----------------------------- | --------------------------------------- | --------------------------------------- | --------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| **Base docker-compose.yml**       | Common settings (build context, ports, etc.)   | Common settings (build context, ports, etc.)   | Common settings (build context, ports, etc.)   | Shared configuration for all environments.                                                         |
| **Override File**             | `docker-compose.dev.yml`<br>- Sets `ENVIRONMENT=dev`<br>- Mounts local volumes for live code reload | `docker-compose.prod.yml`<br>- Sets `ENVIRONMENT=prod`<br>- Production-specific settings (e.g., no volumes, scaling) | `docker-compose.test.yml`<br>- Sets `ENVIRONMENT=test`<br>- Test-specific options (e.g., test database) | Environment-specific overrides that adjust or extend the base configuration.                          |
| **Usage Command**             | `docker-compose -f docker-compose.yml -f docker-compose.dev.yml up` | `docker-compose -f docker-compose.yml -f docker-compose.prod.yml up` | `docker-compose -f docker-compose.yml -f docker-compose.test.yml up` | Specify the base and the appropriate override file when running docker-compose.                      |

---

Both approaches allow you to maintain one Dockerfile while tailoring configurations for production, development, and testing. Choose the approach that best fits your workflow and the complexity of your environment-specific differences.