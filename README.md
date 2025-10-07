# Alinka PySide

Application for Supporting Center for Children - A PySide6 desktop application for managing educational support decisions and generating documents.

## Prerequisites

- **Python 3.12** - Required Python version for the application
- Version management tool of choice for Python, e.g. asdf or pyenv
- **Poetry** - Dependency management and virtual environment handling

## Quick Setup

### 1. Clone and Setup Project

```bash
# Install dependencies (including dev dependencies for testing and linting)
poetry install --with dev

# Create necessary directories (the application will create them automatically, but you can create them manually if needed)
# On macOS:
mkdir -p "$HOME/Library/Application Support/Alinka"
mkdir -p "$HOME/Documents/Alinka"

# On Linux:
mkdir -p "$HOME/.local/share/Alinka"
mkdir -p "$HOME/Documents/Alinka"

# Run migrations
poetry run alembic upgrade head

# Populate database with test data (WARNING: This can take a long time and may hang)
poetry run python tools/populate_database.py

# Generate documents
poetry run python tools/create_documents.py --type specjalne
```

### 2. Run the Application

```bash
poetry run python run.py
```

## Directory Structure

The application uses platform-specific directories managed by `platformdirs`:

**On macOS:**
- **Database**: `~/Library/Application Support/Alinka/alinka.sqlite`
- **Documents**: `~/Documents/Alinka/`
- **Logs**: `~/Library/Application Support/Alinka/logs/` (when running as packaged app)

**On Linux:**
- **Database**: `~/.local/share/Alinka/alinka.sqlite`
- **Documents**: `~/Documents/Alinka/`
- **Logs**: `~/.local/share/Alinka/logs/` (when running as packaged app)

The application automatically creates these directories when needed.

## Development Commands

```bash
# Run tests
poetry run pytest

# Run linting
poetry run black .
poetry run isort .
poetry run flake8 .

# Create database migration
poetry run alembic revision --autogenerate -m "your_message"

# Apply migrations
poetry run alembic upgrade head


```

## Project Structure

```
alinka-pyside/
├── alinka/                    # Main application code
│   ├── config/               # Configuration settings
│   ├── db/                   # Database models and connections
│   ├── docx/                 # Document generation
│   ├── widget/               # PySide6 GUI components
│   └── ...
├── migrations/               # Database migrations
├── tests/                    # Test files
├── tools/                    # Utility scripts
├── pyproject.toml           # Poetry configuration
├── .tool-versions           # asdf tool versions
└── run.py                   # Application entry point
```

## Technology Stack

- **GUI Framework**: PySide6 (Qt for Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Migrations**: Alembic
- **Document Generation**: Custom Word templates
- **Dependency Management**: Poetry
- **Configuration**: Pydantic Settings

## Development

If you're using Docker Compose (or Linux in general) for development, be aware
that Wayland as Windows System is causing issues and it would be wise
to switch X11 (see procedure in https://apploye.com/help/switch-from-wayland-to-xorg-ubuntu/).

## Contributing

1. Follow the existing code style (Black, isort, flake8)
2. Write tests for new features
3. Update migrations for database changes
4. Test before submitting PRs

## Release 

To make a release please follow instruction
1. Go to "Actions" tab and run "Crate release" workflow (additional instructions [here](https://docs.github.com/en/actions/how-tos/managing-workflow-runs-and-deployments/managing-workflow-runs/manually-running-a-workflow#running-a-workflow)).
2. When workflow is done (all checks are green), go back to the main repo and find release on the right.
3. In the pre-release window you need to download .exe file nad submit it for malware scan.
4. Go to: https://www.microsoft.com/en-us/wdsi/filesubmission
5. Choose "Submit as a software developer" and log in with your microsoft account.
6. Fill in the form with "Microsoft Defender Smartscreeen" option and "Code for Poznań" as a company name.
7. While, waiting for Microsoft check go to pre-release again and start editing.
8. In the content describe all the changes made based on github repo history of merged code. 
9. Once you get the confirmation from Microsoft you can uncheck pre-release tag and unkorque the champagne!
10. But first paste the latest release onto facebook group: https://www.facebook.com/groups/496335526898202
