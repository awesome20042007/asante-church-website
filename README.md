# Asante Church International — Website

The official website for **Asante Church International**, Kasangati Town Council, Uganda.

Church leaders manage the content (service times, events, sermons, photos and more) through a private dashboard. No code editing is needed.

## Built with

- Python and Django
- HTML, CSS and JavaScript (no frontend framework)
- SQLite while developing (PostgreSQL planned for the live site)
- Pillow for image handling

## Main features

- 10 pages: Home, About, Leadership, Ministries, Services, Events, Sermons, Gallery, Give, Contact
- Content managed from a branded dashboard at `/dashboard/`
- Photos are shrunk automatically on upload so pages stay fast
- Contact form with spam protection; messages are saved in the dashboard
- Works on phones, tablets, laptops and large TV screens
- SEO: page titles and descriptions, `sitemap.xml`, `robots.txt`
- Accessibility: skip link, keyboard-friendly menu, high-contrast colours

## Running it on your computer

1. Get the code and open a terminal in the project folder.

2. Create and start a virtual environment.

   Windows (Git Bash):

```bash
   python -m venv venv
   source venv/Scripts/activate
```

   Mac or Linux:

```bash
   python3 -m venv venv
   source venv/bin/activate
```

3. Install the packages:

```bash
   pip install -r requirements.txt
```

4. Create your private settings file. Copy `.env.example` to a new file called `.env`:

```bash
   cp .env.example .env
```

   Then make a secret key and paste it into `.env` after `DJANGO_SECRET_KEY=`:

```bash
   python -c "import secrets; print(secrets.token_urlsafe(60))"
```

5. Create the database tables and your admin account:

```bash
   python manage.py migrate
   python manage.py createsuperuser
```

6. Start the site:

```bash
   python manage.py runserver
```

   Website: http://127.0.0.1:8000/
   Dashboard: http://127.0.0.1:8000/dashboard/

## Settings (the `.env` file)

| Name | What it does |
|---|---|
| `DJANGO_SECRET_KEY` | Long random secret. Required. Never share it. |
| `DJANGO_DEBUG` | `True` on your computer. Must be `False` on the live site. |
| `DJANGO_ALLOWED_HOSTS` | Website addresses allowed to use the site, separated by commas. |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | The live `https://` address (live site only). |
| `DJANGO_HTTPS` | `True` on the live site. Switches on secure cookies. |

The `.env` file, the database (`db.sqlite3`) and the `media/` folder are private. They are never uploaded to GitHub.

## Managing content

Log in at `/dashboard/`. Edit church details, services, events, sermons, ministries, leaders, gallery photos and social links. Read contact messages under **Contact messages**.

## Tests

```bash
python manage.py test
```

## Folder guide

```text
config/       Project settings and main URLs
church/       The website app (models, views, forms, admin, tests)
templates/    HTML pages (base.html is the shared layout)
static/       CSS, JavaScript and fixed images
media/        Photos uploaded through the dashboard (not in GitHub)
```

## Going live

Deployment steps will be added here before launch.