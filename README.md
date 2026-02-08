# Konnect 

Aggregating Fight data from professional mix martial arts organizations

## Features

- **Athlete Management**: Store and manage athlete information including first name, last name, email, organization, and creation timestamp
- **Django Admin Interface**: Full admin interface for managing athletes
- **Web Scraping**: Built-in Scrapy integration for fetching athlete data from ONE Championship website
- **Management Commands**: Custom Django management commands for web scraping operations

## Project Structure

```
konnect/
├── athletes/              # Athletes Django app
│   ├── management/
│   │   └── commands/
│   │       └── open_onefc.py  # Scrapy command for ONE Championship
│   ├── migrations/        # Database migrations
│   ├── admin.py           # Admin configuration
│   ├── models.py          # Athlete model
│   └── tests.py           # Test cases
├── core/                  # Django project settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── manage.py             # Django management script
├── requirements.txt      # Python dependencies
└── db.sqlite3            # SQLite database (created after migrations)
```

## Requirements

- Python 3.13+
- Django 6.0.2+
- Scrapy 2.11.0+

## Installation

1. **Clone the repository** (if applicable) or navigate to the project directory:
   ```bash
   cd /path/to/konnect
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Setup

1. **Run database migrations**:
   ```bash
   python manage.py migrate
   ```

2. **Create a superuser** (for Django admin access):
   ```bash
   python manage.py createsuperuser
   ```
   Follow the prompts to create an admin account.

3. **Start the development server**:
   ```bash
   python manage.py runserver
   ```

4. **Access the application**:
   - Main site: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## Usage

### Django Admin

1. Navigate to http://127.0.0.1:8000/admin/
2. Log in with your superuser credentials
3. Click on "Athletes" to view, add, edit, or delete athlete records

### Management Commands

#### Fetch ONE Championship Athletes Page

Fetch the ONE Championship flyweight athletes page using Scrapy:

```bash
# Basic usage - fetches page and outputs HTML to console
python manage.py open_onefc

# Also open the page in your default browser
python manage.py open_onefc --open-browser
```

**Command Options:**
- `--open-browser`: Opens the page in your default browser after fetching
- `--help`: Display help message

**Output:**
The command will:
1. Fetch the page using Scrapy
2. Display the full HTML content in the console
3. Optionally open the page in your browser

## Models

### Athlete

The `Athlete` model stores athlete information:

- `first_name` (CharField, max_length=100): Athlete's first name
- `last_name` (CharField, max_length=100): Athlete's last name
- `email` (EmailField): Athlete's email address
- `organization` (CharField, max_length=200): Organization the athlete belongs to
- `created_at` (DateTimeField): Automatic timestamp when the record is created

## Database

The project uses SQLite by default. The database file (`db.sqlite3`) is created automatically when you run migrations.

### Migrations

The project includes migrations for:
- Initial athlete model creation
- Table rename migration (from `contacts_contact` to `athletes_athlete`)

To apply migrations:
```bash
python manage.py migrate
```

To create new migrations after model changes:
```bash
python manage.py makemigrations
```

## Testing

Run the test suite:

```bash
# Run all tests
python manage.py test

# Run tests for the athletes app
python manage.py test athletes

# Run specific test class
python manage.py test athletes.tests.OpenOneFCCommandTest

# Run with verbose output
python manage.py test --verbosity=2
```

## Development

### Adding New Management Commands

Management commands should be placed in:
```
athletes/management/commands/your_command.py
```

Example structure:
```python
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Your command description'

    def handle(self, *args, **options):
        # Your command logic here
        pass
```

### Extending the Scrapy Spider

The Scrapy spider in `open_onefc.py` can be extended to extract specific data from the ONE Championship website. Modify the `parse` method in the `OneFCAthletesSpider` class to extract and process athlete data.

## Configuration

### Settings

Main configuration is in `core/settings.py`. Key settings:

- `DEBUG = True`: Development mode (set to `False` in production)
- `SECRET_KEY`: Django secret key (change in production)
- `INSTALLED_APPS`: Includes `athletes` app
- `DATABASES`: SQLite configuration (default)

## Troubleshooting

### Scrapy Import Errors

If you encounter `ModuleNotFoundError: No module named 'scrapy'`:
```bash
pip install scrapy
```

### Database Migration Issues

If you encounter migration errors:
```bash
# Check migration status
python manage.py showmigrations

# Reset migrations (WARNING: This will delete data)
python manage.py migrate athletes zero
python manage.py migrate
```

### Permission Errors

If you encounter permission errors when running commands, ensure:
- Virtual environment is activated
- You have write permissions in the project directory
- Database file (`db.sqlite3`) is writable

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]

## Contact

[Add contact information here]

