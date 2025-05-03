from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = (
        "postgresql+psycopg2://postgres:admin@db:5432/postgres"
    )

    model_config = SettingsConfigDict(env_prefix="")  # no ALL‑CAPS mess


settings = Settings()  # import this anywhere you need config
