# Source Manager Application

A Flet-based application for managing source documents and projects.

## Project Structure

```
source_manager_flet/
├── src/                    # Main application source code
│   ├── main.py            # Application entry point
│   ├── controllers/       # Application controllers
│   ├── models/           # Data models and managers
│   ├── services/         # Business logic services
│   ├── utils/            # Utility functions
│   └── views/            # UI views and components
├── tests/                # Test files
├── scripts/              # Utility scripts
│   ├── development/      # Development and fix scripts
│   └── ...              # Other utility scripts
├── database/             # Database schema, migrations, and backups
├── docs/                 # Documentation
├── config/               # Configuration files
├── data/                 # Application data
│   └── databases/        # Runtime database files (.db files)
├── logs/                 # Log files
├── archive/              # Archived/backup files
└── requirements.txt      # Python dependencies
```

## Setup and Installation

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python run.py
   ```

## Development

- Main application code is in the `src/` directory
- Tests are in the `tests/` directory
- Development scripts and fixes are in `scripts/development/`
- Documentation is in the `docs/` directory

## Database

Database schema and management files are located in the `database/` directory.
Runtime database files (`.db` files) are stored in `data/databases/`.
