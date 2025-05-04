# Dockerfile  (root of repo)
FROM python:3.12-slim
ARG BUILD_ID=0

# 1. System basics
ENV PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1
ENV PYTHONPATH="/code/src"

# 2. Create working dir
WORKDIR /code

# 3. Install Poetry first
RUN pip install --upgrade pip && pip install poetry

# 4. Copy dependency list *only* and install — leverages cache
COPY pyproject.toml poetry.lock ./ 
RUN poetry install --no-root --only main,dev
COPY alembic.ini .
COPY migrations ./migrations

# 5. Copy application code
COPY src /code/src
COPY start_all.sh .
RUN chmod +x start_all.sh

# 6. Entrypoint: run script (no --reload in prod)
CMD ["./start_all.sh"]

