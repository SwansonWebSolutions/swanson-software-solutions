# Swanson Software Solutions

A professional Django-based website for Swanson Software Solutions, a website development company.

## Features

This website includes the following pages:

- **Landing Page** - Main homepage with hero section and call-to-action
- **Company** - About the company, mission, values, and what we do
- **Solutions** - Comprehensive overview of services offered
- **Pricing** - Transparent pricing plans with three tiers
- **SEO** - SEO services and packages information
- **Client Approval** - Client approval portal for project reviews
- **Contact Sales** - Contact form and company contact information

## Technology Stack

- **Backend**: Django 5.2.7
- **Frontend**: HTML5, CSS3
- **Database**: SQLite (development)
- **Python**: 3.12+

## Installation

### Prerequisites

- Python 3.12 or higher
- pip (Python package manager)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/SwansonWebSolutions/swanson-software-solutions.git
   cd swanson-software-solutions
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

5. **Start the development server**
   ```bash
   python manage.py runserver
   ```

6. **Access the website**
   
   Open your browser and navigate to `http://127.0.0.1:8000/`

## California Data Broker Registry (2025)

- A dedicated table `DataBrokers2025` stores the 2025 CA Data Broker Registry.
- Source file expected at the project root: `California Data Broker Registry 2025.csv`.

### Setup

1. Make migrations and migrate:
   - `python manage.py makemigrations website`
   - `python manage.py migrate`
2. Import the CSV into the table:
   - `python manage.py import_brokers_2025 --truncate`
   - Optional: pass a custom path with `--path /path/to/file.csv`

### Admin

- The dataset is available in Django Admin as “Data Brokers (2025)”.
- Search by name/DBA/website/email; filter by state/country.

## Project Structure

```
swanson-software-solutions/
├── swanson_site/          # Main project settings
│   ├── settings.py        # Django configuration
│   ├── urls.py           # Main URL configuration
│   └── wsgi.py           # WSGI configuration
├── website/              # Main application
│   ├── templates/        # HTML templates
│   ├── views.py         # View functions
│   └── urls.py          # App URL patterns
├── static/              # Static files (CSS, JS, images)
│   └── css/
│       └── style.css    # Main stylesheet
├── manage.py            # Django management script
└── requirements.txt     # Python dependencies
```

## Available Pages

- `/` - Landing page
- `/company/` - Company information
- `/solutions/` - Services and solutions
- `/pricing/` - Pricing plans
- `/seo/` - SEO services
- `/client-approval/` - Client approval portal
- `/contact-sales/` - Contact form

## Development

### Running Tests

```bash
python manage.py test
```

### Creating a Superuser (for admin access)

```bash
python manage.py createsuperuser
```

Then access the admin panel at `http://127.0.0.1:8000/admin/`

## Production Deployment

For production deployment:

1. Set `DEBUG = False` in `settings.py`
2. Configure `ALLOWED_HOSTS` in `settings.py`
3. Set up a production database (PostgreSQL recommended)
4. Configure static files with `python manage.py collectstatic`
5. Use a production WSGI server (Gunicorn, uWSGI)
6. Set up a reverse proxy (Nginx, Apache)

## License

Copyright © 2025 Swanson Software Solutions. All rights reserved.
