# OpsAny Artifact Repository (repo)

[简体中文](./README.md) | [繁體中文](./README.zh-TW.md)

The OpsAny Artifact Repository platform is a DevOps application of the [OpsAny intelligent operations platform](https://www.opsany.com). It integrates with Nexus to provide repository management, artifact upload/download/delete, version resource retrieval, and application association, helping enterprises centrally manage artifacts throughout the DevOps process.

## Features

- **Repository management**: Integrates with Nexus to create, delete, view, and edit repositories
- **Repository formats**: Supports Nexus artifact formats such as Maven, npm, Docker, and PyPI
- **Component / asset management**: Manages artifact components and assets, supporting upload, download, and delete
- **Version resource retrieval**: Retrieves artifact version resources by component or tree structure
- **Artifact search**: Searches artifact components
- **Artifact tags**: Adds tags (favorites) to repositories
- **Application association**: Associates repositories with applications in the application platform
- **Project cloning**: Clones code repositories onto deployment hosts
- **Artifact download**: Downloads artifacts from repositories
- **Overview statistics**: Dashboards for repository counts, recent activity, and volume rankings

## Tech Stack

- Backend: Python 3.6 + Django 2.2
- Frontend: Vue 2.6
- Database: MySQL + MongoDB (mongoengine)
- Containerization: Docker

## Project Structure

```bash
.
|-- blueapps                        # Python development framework module
|-- blueking                        # ESB invocation module
|-- component                       # Shared components
|-- config                          # Application configuration directory
|   |-- __init__.py                 # RUN_VER, APP_CODE, SECRET_KEY and other configs
|   |-- dev.py                      # Local development configuration
|   |-- default.py                  # Global configuration
|   |-- prod.py                     # Production configuration
|   |-- stag.py                     # Staging configuration
|-- docker                          # Docker containerization files
|-- frontend                        # Frontend source code
|-- index                           # Platform entry
|-- repo                            # Core repository business logic
|-- static                          # Frontend build artifacts
|-- templates                       # Shared template files
|-- app.yml                         # Production packaging/deployment config
|-- manage.py                       # Django manage.py
|-- requirements.txt                # Python dependency list
|-- runtime.txt                     # Python version configuration
|-- LICENSE                         # Apache License 2.0
```

## Dependencies

- **OpsAny PaaS**: Runs on top of OpsAny PaaS, relying on unified login, the ESB API gateway, and other services
- **Nexus**: The artifact repository service; the core service for repository management
- **OpsAny Application Platform (devops)**: Application association depends on the application platform

## Quick Start

### Local Development

1. Clone the code and install dependencies:

```bash
pip install -r requirements.txt
```

2. Configure the database connection (`config/dev.py`) and initialize the database:

```bash
python manage.py migrate
```

3. Start the backend service:

```bash
python manage.py runserver 127.0.0.1:8000
```

4. Start the frontend:

```bash
cd frontend
npm install
npm run serve
```

> For more deployment and usage instructions, please refer to the [OpsAny official documentation](https://docs.opsany.com).

## License

This project is open sourced under the [Apache License 2.0](./LICENSE). Copyright © OpsAny.
