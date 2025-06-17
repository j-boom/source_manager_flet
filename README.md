# Source Manager

A modern desktop application built with Python and Flet for managing source code projects and customer data.

## Features

- **Project Management**: Create and manage projects with customer associations
- **Database Integration**: SQLite3 database with proper relationships and analytics capabilities
- **Modern UI**: Clean, responsive interface with dark/light theme support
- **Recent Projects**: Quick access to recently visited projects and sites
- **Analytics**: Built-in analytics and reporting capabilities

## Project Structure

```
source_manager_flet/
├── 📁 src/                          # Source code
│   ├── main.py                      # Application entry point
│   ├── controllers/                 # Application controllers
│   ├── models/                      # Data models and database management
│   ├── services/                    # Business logic and services
│   ├── views/                       # UI components and pages
│   └── utils/                       # Utility functions
├── 📁 config/                       # Configuration files
├── 📁 data/                         # Application data
│   ├── databases/                   # SQLite databases and schema
│   ├── projects/                    # Project files
│   ├── user_data/                   # User-specific data
│   └── temp/                        # Temporary files
├── 📁 tests/                        # Test suite
│   ├── unit/                        # Unit tests
│   ├── integration/                 # Integration tests
│   └── fixtures/                    # Test fixtures
├── 📁 scripts/                      # Utility scripts
├── 📁 docs/                         # Documentation
├── 📁 logs/                         # Application logs
├── requirements.txt                 # Python dependencies
└── run.py                          # Application launcher
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd source_manager_flet
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python run.py
   ```

## Development

### Setting up Development Environment

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run tests**
   ```bash
   python -m pytest tests/
   ```

### Database

The application uses SQLite3 for data persistence with the following entities:
- **Customers**: Customer information and details
- **Projects**: Project data linked to customers
- **Sources**: Source files and directories
- **Associations**: Relationships between projects and sources

Database schema is located at `data/databases/database_schema.sql`.

### Configuration

Application configuration is managed through the `config/` directory:
- `app_config.py`: Main application settings
- `logging_config.py`: Logging configuration

## Testing

Run the test suite:
```bash
# Run all tests
python -m pytest tests/

# Run specific test category
python -m pytest tests/unit/
python -m pytest tests/integration/

# Run with coverage
python -m pytest tests/ --cov=src
```

## Scripts

Utility scripts are located in the `scripts/` directory:
- `demo_analytics.py`: Analytics demonstration
- `add_sample_data.py`: Sample data generation

## Documentation

Detailed documentation is available in the `docs/` directory:
- Development guides
- Database migration information
- API documentation

## License

[Add your license information here]

## Contributing

[Add contributing guidelines here]
