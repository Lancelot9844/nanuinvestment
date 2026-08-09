# Nanu Investment Website

This project is the website and admin system for **Nanu Investment Pvt. Ltd.** It uses Django for the backend/admin panel and React/Vite for the public website frontend.

The public website is served by Django, but the main UI is built from the React app in `frontend/`. Website content such as banners, news, notices, and downloads can be managed from the Django admin panel.

## Main Features

- Public website homepage with responsive React UI
- Homepage banner slider with admin-managed banner images
- News & Activities section managed from admin
- Notice section managed from admin
- Downloads section managed from admin
- Contact/footer sections on the website
- Role-aware login page for customers and admin/staff users
- Customer portal with dashboard, profile photo upload, ticket creation, and password change
- Customer account management with KYC documents, account types, opening balance, and login credentials
- Daily collection workflow for staff/admin collectors
- Automatic transaction generation from collection records
- Printable transaction bills with PDF and JPG downloads
- Finance & Control pages for Transactions, Accounting, Approvals, and Reports
- Approval queue for pending customer KYC and staff-completed tickets
- SEO basics: meta tags, `robots.txt`, and `sitemap.xml`
- Modern customized Django admin theme with light/dark mode
- Admin favicon and logo
- Staff/sub-admin groups for limited content access
- Staff and customer profile photo upload
- Media upload support for banners, notices, downloads, news images, profile photos, website popups, and KYC documents

## Folder Guide

### `manage.py`

Django command-line entry point. Use it for running the server, migrations, admin user creation, and checks.

Examples:

```bash
python manage.py runserver
python manage.py migrate
python manage.py createsuperuser
python manage.py check
```

### `nanuinvestment/`

Main Django project configuration.

- `settings.py` contains installed apps, database settings, template/static/media settings, and Django configuration.
- `urls.py` connects all routes, including `/admin/`, the website homepage, `robots.txt`, `sitemap.xml`, and media files during development.
- `wsgi.py` and `asgi.py` are Django server entry files.

### `myapp/`

Main Django app for website data and page rendering.

- `models.py` defines the database content:
  - `Banner`: homepage slider images
  - `NewsActivity`: news and activities
  - `Notice`: notices, optionally with a document
  - `Download`: downloadable documents
  - `WebsitePopup`: optional homepage popup media
  - `AdminProfile`: staff/admin profile photo and contact details
  - `Customer`: customer account, KYC, balance, and customer login link
  - `CustomerKYCDocument`: multiple named KYC uploads per customer
  - `CollectionRecord`: staff/admin collection entries
  - `Transaction`: generated receipt/bill records from collections
  - `Ticket`: customer/admin support and staff work tickets
  - `EBankingCredential`: customer login credential handover data
  - `RecycleBinItem`: soft-delete recycle bin entries
- `views.py` collects active content from the database and sends it to the React page through `site_content`.
- `urls.py` defines website routes:
  - `/` for the homepage
  - `/login/` for role selection
  - `/customer/login/` for customer login
  - `/customer/dashboard/` for the customer portal
  - `/customer/profile/` for customer profile photo upload
  - `/customer/tickets/new/` for customer ticket creation
  - `/customer/password/` for customer password changes
- `admin.py` registers website content, customers, finance, transactions, approvals, reports, tickets, recycle bin, and custom admin pages.
- `apps.py` creates default permission groups after migrations:
  - `Content Staff`: can add/change/delete/view website content
  - `Content Viewer`: can view website content only
- `migrations/` stores database schema and seed migrations.

### `frontend/`

React/Vite source code for the public website.

- `src/App.jsx` contains the website UI and section behavior.
- `src/App.css` contains website responsive styling.
- `src/main.jsx` mounts the React app.
- `index.html` is the Vite source HTML.
- `vite.config.js` builds React output into `templates/react/` so Django can serve it.
- `package.json` contains frontend dependencies and scripts.

Important frontend commands:

```bash
cd frontend
npm install
npm run dev
npm run build
```

Use `npm run dev` while designing the React app. Use `npm run build` when you want Django to serve the latest React changes.

### `templates/`

Django template and static asset folder.

- `index_react.html` is the main Django template used for the public website. It loads the React build and passes backend content to React.
- `login.html` is the role-aware login selection page.
- `admin/` contains customized Django admin templates.
- `customer/` contains customer portal templates.
- `admin-modern.css` contains the custom admin panel theme.
- `admin-logo.png` is used in the admin header.
- `react/` contains built frontend files generated by Vite.
- `style.css`, `script.js`, and `index.html` are older/static website files kept in the project.
- `favicon.ico` is used as the site/admin favicon.

### `templates/react/`

Generated React build output. Django serves the public website from these files through `index_react.html`.

Do not manually edit files inside this folder for normal frontend changes. Edit `frontend/src/` and run:

```bash
cd frontend
npm run build
```

### `media/`

Uploaded files from the Django admin panel.

Examples:

- `media/banners/`
- `media/news/`
- `media/notices/`
- `media/downloads/`
- `media/admin_profiles/`
- `media/customer_profiles/`
- `media/customer_kyc/`
- `media/popups/`

This folder is used during development because `MEDIA_URL` and `MEDIA_ROOT` are configured in Django.

### `db.sqlite3`

Local SQLite database. It stores admin users, permissions, banners, news, notices, downloads, and other Django data.

### `robots.txt` and `sitemap.xml`

SEO files served by Django at:

- `/robots.txt`
- `/sitemap.xml`

## Admin Panel

Open:

```text
http://127.0.0.1:8000/admin/
```

The admin panel has been customized with:

- Nanu Investment logo
- Custom admin dashboard layout
- Left-side icon menu
- Light/dark theme toggle
- Admin footer showing `Developed by ASH Akeluwa Software Hub Company`
- Custom styling in `templates/admin-modern.css`
- Favicon on admin pages

From admin, you can manage:

- Banners
- News & Activities
- Notices
- Downloads
- Website Popups
- Customers & KYC
- E-Banking credentials
- Daily Collections
- Collection Records
- Transactions and printable bills
- Accounting overview
- Approvals
- Tickets
- Reports
- Recycle Bin
- Users
- Groups

## Finance and Control

The Finance & Control area includes:

- **Transactions**: generated from collection records. Each transaction has a receipt number, customer details, amount, balance after transaction, collector, date/time, status, PDF bill download, JPG bill download, and print view.
- **Accounting**: dashboard-style interface showing monthly income, expense totals, net surplus, unposted vouchers, search, status filter, and voucher rows from transactions.
- **Approvals**: centralized queue for pending KYC requests and staff-completed tickets waiting for admin verification.
- **Reports**: operational charts and summaries for customers, collections, KYC, tickets, and staff performance.

## Customer Portal

Customer-facing routes:

- `/customer/login/`
- `/customer/dashboard/`
- `/customer/profile/`
- `/customer/tickets/new/`
- `/customer/password/`

Customers can view their account summary, current amount, recent collections, tickets, upload a profile photo, create support tickets, and change their password.

## Staff and Sub-Admin Access

Django already supports staff users and permissions.

Recommended workflow:

1. Log in as superadmin.
2. Go to `Users`.
3. Create a user.
4. Enable `Staff status`.
5. Do not enable `Superuser status` unless the user should have full control.
6. Add the user to one of these groups:
   - `Content Staff`
   - `Content Viewer`
7. Save the user.

This allows staff/sub-admin users to access only selected admin features.

Staff users can also open **Profile Settings** from the admin header/sidebar to update phone number, address, and profile photo.

## Content Flow

1. Admin adds or edits content in Django admin.
2. Django stores content in SQLite and uploaded files in `media/`.
3. `myapp.views.home` loads active content:
   - active banners
   - active news
   - active notices
   - active downloads
4. Django sends that data into `index_react.html`.
5. React reads the data and displays it on the homepage.

## Run Backend

From the project root:

```bash
.venv\Scripts\activate
python -m pip install -r requirements.txt
python manage.py runserver 127.0.0.1:8000
```

Open:

```text
http://127.0.0.1:8000/
```

Admin:

```text
http://127.0.0.1:8000/admin/
```

## Run Frontend During Development

From the `frontend/` folder:

```bash
npm install
npm run dev
```

The Vite dev server usually opens at:

```text
http://localhost:5173/
```

The Vite server proxies backend routes such as `/admin/`, `/login/`, `/customer/`, `/api/`, `/media/`, and selected Django admin static files to Django at `http://127.0.0.1:8000`.

For the most reliable admin/backend testing, keep Django running and open:

```text
http://127.0.0.1:8000/admin/
```

If you use `http://127.0.0.1:5173/admin/` during frontend development, restart `npm run dev` after changing `frontend/vite.config.js`.

## Build Frontend for Django

After changing React files:

```bash
cd frontend
npm run build
```

This updates:

- `templates/react/index.html`
- `templates/react/assets/index.css`
- `templates/react/assets/index.js`

Django then serves the updated website through `templates/index_react.html`.

## Database and Migrations

Install Python dependencies first:

```bash
python -m pip install -r requirements.txt
```

`Pillow` is required for profile image handling and transaction bill export as PDF/JPG.

Run migrations after pulling new model changes:

```bash
python manage.py migrate
```

Check project health:

```bash
python manage.py check
```

Create a superadmin:

```bash
python manage.py createsuperuser
```

## Current Models

### `Banner`

Used for the homepage slider.

Fields:

- `title`
- `image`
- `display_order`
- `is_active`
- `created_at`
- `updated_at`

### `NewsActivity`

Used for News & Activities.

Fields:

- `title`
- `description`
- `image`
- `is_active`
- `published_at`
- `created_at`
- `updated_at`

### `Notice`

Used for notice information.

Fields:

- `title`
- `description`
- `document`
- `is_active`
- `published_at`
- `created_at`
- `updated_at`

### `Download`

Used for downloadable files.

Fields:

- `title`
- `description`
- `document`
- `is_active`
- `published_at`
- `created_at`
- `updated_at`

### `WebsitePopup`

Used for optional homepage popup media and message content.

### `AdminProfile`

Stores staff/admin profile photo, phone number, and address for the profile settings page.

### `Customer`

Stores customer account details, balance, account type, KYC status, profile photo, and optional linked customer login user.

### `CustomerKYCDocument`

Stores named KYC documents uploaded for a customer.

### `CollectionRecord`

Stores daily amount collections made by admin or collector staff. Completed collection records generate transaction receipts.

### `Transaction`

Stores receipt/bill details generated from collection records, including receipt number, customer, amount, collector, balance after transaction, payment method, status, and remarks.

### `Ticket`

Stores customer support requests and internal staff work tickets. Staff-completed tickets can be sent to approvals for admin verification.

### `EBankingCredential`

Stores customer login credential handover records.

### `RecycleBinItem`

Stores soft-deleted admin records for recycle bin restore/permanent delete workflows.

## Important Files to Edit

- Website design: `frontend/src/App.jsx` and `frontend/src/App.css`
- Django page data: `myapp/views.py`
- Website content models: `myapp/models.py`
- Forms and upload validation: `myapp/forms.py`
- Admin content settings: `myapp/admin.py`
- Admin design: `templates/admin-modern.css`
- Admin templates: `templates/admin/`
- Customer portal templates: `templates/customer/`
- SEO template meta tags: `templates/index_react.html`
- Routes: `myapp/urls.py` and `nanuinvestment/urls.py`
- Python dependencies: `requirements.txt`

## Notes

- This project currently uses SQLite for local development.
- Uploaded media files are served only in development through Django when `DEBUG = True`.
- For production, configure a proper static/media file hosting setup and set secure Django settings.
- Avoid manually changing Vite build output in `templates/react/`; change the React source files and rebuild.

## Troubleshooting

If website changes do not appear:

1. If you edited React files, run `npm run build` inside `frontend/`.
2. Restart the Django server.
3. Hard refresh the browser with `Ctrl + F5`.

If `/admin/` or login opens the public website on port `5173`:

1. Confirm Django is running on `http://127.0.0.1:8000/`.
2. Restart the Vite dev server after changes to `frontend/vite.config.js`.
3. Use `http://127.0.0.1:8000/admin/` for direct Django admin access.
4. If using Vite, confirm `/admin/`, `/login/`, `/customer/`, `/api/`, and `/media/` are still listed in the proxy config.

If admin CSS changes do not appear:

1. Hard refresh with `Ctrl + F5`.
2. Restart Django if needed.
3. Confirm the file changed: `templates/admin-modern.css`.

If uploaded files do not show:

1. Confirm `MEDIA_URL = '/media/'`.
2. Confirm `MEDIA_ROOT = BASE_DIR / 'media'`.
3. Confirm `nanuinvestment/urls.py` serves media during `DEBUG`.

If admin access is blocked:

1. Confirm the user has `Staff status`.
2. Confirm the user is active.
3. Confirm permissions or group membership are assigned.
