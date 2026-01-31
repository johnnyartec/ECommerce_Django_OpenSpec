# Project Context

## Overview

**FirstTest** is a Django-based web application that serves as a learning project and template for building full-featured web applications. It currently includes a todo list management system and a blog platform with Markdown support.

## Tech Stack

### Backend

- **Python 3.12+** - Core language
- **Django 6.x** - Web framework
- **PostgreSQL** (psycopg) - Database (with SQLite for local development)
- **Uvicorn** - ASGI server

### Frontend

- **Django Templates** - Server-side rendering
- **Base HTML/CSS** - Using Django's built-in admin styling patterns

### Content & Security

- **markdown** (3.10.1+) - Markdown parsing (CommonMark spec)
- **bleach** (6.3.0+) - HTML sanitization for XSS prevention

### Development Tools

- **uv** - Package management
- **python-dotenv** - Environment configuration
- **Docker & Docker Compose** - Containerization

## Project Structure

```
FirstTest/
├── config/                 # Django project settings
│   ├── settings.py        # Main configuration
│   ├── urls.py            # Root URL routing
│   └── wsgi.py/asgi.py    # Server entry points
├── todolist_app/          # Main application
│   ├── models.py          # Data models (Todo, BlogPost)
│   ├── views.py           # View logic
│   ├── forms.py           # Form definitions
│   ├── urls.py            # App-specific routing
│   ├── templates/         # HTML templates
│   │   ├── base.html      # Base template
│   │   ├── blog/          # Blog templates
│   │   └── registration/  # Auth templates
│   ├── utils/             # Utilities
│   │   └── markdown_renderer.py
│   ├── tests/             # Test suite
│   └── migrations/        # Database migrations
├── openspec/              # OpenSpec change management
│   ├── config.yaml        # OpenSpec configuration
│   ├── changes/           # Active changes
│   └── specs/             # Main specifications
├── static/                # Static files (collected)
└── docs/                  # Project documentation
```

## Coding Conventions

### Python Style

- **PEP 8** compliance for general Python style
- **4-space indentation**
- Type hints encouraged for function signatures

### Django Conventions

- **Class-based views (CBVs)** preferred over function-based views
- **Django ORM** for all database operations
- Follow Django's "apps" pattern for organization

### Naming Conventions

- **Models**: PascalCase (e.g., `BlogPost`, `Todo`)
- **Model fields**: camelCase (e.g., `markdownContent`, `createdAt`) - **Project-specific convention**
- **Functions/methods**: snake_case (e.g., `render_markdown`)
- **URLs**: kebab-case (e.g., `/blog/my-post-title`)
- **Template files**: snake_case (e.g., `post_detail.html`)

### Database

- **Primary keys**: Auto-generated integer IDs
- **Foreign keys**: Use `on_delete=models.CASCADE` unless specific behavior needed
- **Timestamps**: Include `createdAt` (auto_now_add) and `updatedAt` (auto_now) for entities
- **User relations**: Use Django's built-in `User` model with ForeignKey

### Security

- **XSS Prevention**: All user-generated HTML content MUST be sanitized with bleach
- **Authentication**: Use Django's built-in authentication system
- **Authorization**: Implement view-level permission checks (LoginRequiredMixin, user ownership)
- **CSRF**: Django's CSRF middleware enabled by default

### Testing

- **Test location**: `todolist_app/tests/`
- **Test naming**: `test_*.py` files with `Test*` classes
- **Coverage goals**: Core business logic and user flows
- **Test types**: Unit tests for models, integration tests for views

### Markdown Handling

- **Spec**: CommonMark via `markdown` library
- **Rendering**: Convert to HTML, then sanitize with bleach
- **Allowed tags**: See `utils/markdown_renderer.py` for safe tag list
- **Storage**: Store both raw Markdown (`markdownContent`) and rendered HTML (`htmlContent`)

## Environment Configuration

Environment variables managed via `.env` files using `env_utility.py`:

- `.env` - Base configuration
- `.env.{ENV}` - Environment-specific overrides (e.g., `.env.development`, `.env.production`)

Key variables:

- `DJANGO_SECRET_KEY` - Secret key for cryptographic signing
- `DJANGO_DEBUG` - Debug mode (boolean)
- `DJANGO_ALLOWED_HOSTS` - Comma-separated allowed hosts
- Database connection settings (when using PostgreSQL)

## Domain Knowledge

### Todo System

- Users can only see/edit their own todos
- Simple CRUD operations
- Completion tracking with boolean flag

### Blog System

- **Two states**: `draft` (author-only) and `published` (public)
- **Slug generation**: Auto-generated from title, unique, used in URLs
- **Author ownership**: Only the author can edit/delete their posts
- **Public access**: Published posts accessible via `/blog/<slug>` without authentication
- **Draft access**: Drafts only visible to author at `/blog/drafts/`

## Development Workflow

### Running Locally

1. `uv sync` - Install dependencies
2. `.\.venv\Scripts\Activate.ps1` - Activate virtual environment (Windows)
3. `python manage.py migrate` - Apply migrations
4. `python manage.py runserver` - Start development server

### Database Migrations

1. `python manage.py makemigrations` - Generate migration files
2. `python manage.py migrate` - Apply migrations

### VS Code Tasks Available

- **Run Django server** - Start development server
- **Run migrations** - Apply pending migrations
- **Make migrations** - Generate new migrations
- **Collect static** - Collect static files

## OpenSpec Schema

Currently using: **spec-driven** workflow

Default artifact sequence: proposal → specs → design → tasks → implementation

## Common Patterns

### Adding a New Model

1. Define model in `models.py` with proper field naming (camelCase)
2. Add `__str__` method for readable representation
3. Create and run migrations
4. Register in `admin.py` if needed
5. Add tests in `tests/test_models.py`

### Adding a New View

1. Create view in `views.py` (prefer CBV)
2. Add URL pattern in `urls.py`
3. Create template in `templates/`
4. Add permission checks (LoginRequiredMixin, UserPassesTestMixin)
5. Add integration tests

### Handling User-Generated Content

1. Store raw content in model field
2. If Markdown, store both raw and rendered HTML
3. Sanitize with bleach before display
4. Test with XSS payloads

## Notes for AI Assistants

- **Language preference**: User understands both Chinese and English; documentation can be bilingual
- **Model field naming**: This project uses camelCase for Django model fields (non-standard but project convention)
- **Environment**: Development happens on Windows with PowerShell
- **Testing**: Always include tests for new features, especially security-critical paths
- **OpenSpec**: Follow the spec-driven workflow for feature development
