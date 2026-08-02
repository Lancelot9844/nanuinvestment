# Nanu Investment

A simple Django website for Nanu Investment Pvt. Ltd. The project includes a homepage rendered from `templates/index.html`, a Django app named `myapp`, and a root URL configuration that routes the site home page correctly.

## Project Structure

- `manage.py` — Django project management script
- `nanuinvestment/` — Django project configuration
  - `settings.py` — project settings
  - `urls.py` — root URL routing
- `myapp/` — application code
  - `views.py` — homepage view
  - `urls.py` — app route definitions
- `templates/` — HTML and static assets used by the site
- `requirements.txt` — Python dependencies

## Requirements

- Python 3.14+ (Project currently uses Python 3.14.6)
- Django 6.0.7

## Setup

1. Clone the repository:

   ```bash
   git clone <your-repo-url>
   cd nanuinvestment
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Run the project

Start the Django development server:

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in your browser.

## Important project notes

- The home page is served by `myapp.views.home`.
- `nanuinvestment/urls.py` loads the app URLs using `path('', include('myapp.urls'))`.
- `myapp/urls.py` defines `path('', home, name='home')`.
- Static files and images are served by Django using the `static` template tag in `templates/index.html`.

## Git guidance

Push these folders and files together so the project works for others:

- `manage.py`
- `nanuinvestment/`
- `myapp/`
- `templates/`
- `requirements.txt`
- `README.md`

Do not push local environment folders like `.venv/` or generated files such as `__pycache__/`.

## Troubleshooting

- If the homepage does not appear, verify `myapp/urls.py` and `nanuinvestment/urls.py` are configured correctly.
- If static assets do not load, verify `STATIC_URL` and `STATICFILES_DIRS` in `settings.py`, and confirm the template uses `{% load static %}`.
