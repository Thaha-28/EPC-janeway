FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    JANEWAY_SETTINGS_MODULE=core.railway_settings

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    gettext \
    libxml2-dev \
    libxslt1-dev \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /vol/janeway

COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install gunicorn whitenoise django-anymail

COPY . .

# Guarantee directories that Django walks at startup exist even if the
# build context drops empty dirs (e.g. src/plugins ships only .gitkeep).
# migrate/collectstatic run at container boot against the live database.
RUN mkdir -p src/plugins src/media src/collected-static files && \
    python -c "import ast; ast.parse(open('src/core/janeway_global_settings.py').read()); ast.parse(open('src/core/railway_settings.py').read()); print('settings syntax OK')"

COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["gunicorn", "core.wsgi:application", "--chdir", "src", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-"]
