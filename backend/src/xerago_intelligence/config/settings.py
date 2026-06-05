from functools import lru_cache
import logging
from pathlib import Path
from urllib.parse import quote_plus

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

# backend/ directory (parent of src/)
_BACKEND_DIR = Path(__file__).resolve().parents[3]
_ENV_FILE = _BACKEND_DIR / ".env"


def _env_file_paths() -> tuple[str, ...]:
    """Load .env from backend/ regardless of current working directory."""
    if _ENV_FILE.is_file():
        return (str(_ENV_FILE),)
    return (".env",)


class Settings(BaseSettings):
    """Application settings loaded from environment and optional .env file."""

    model_config = SettingsConfigDict(
        env_file=_env_file_paths(),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # MySQL
    database_url: str | None = Field(default=None, alias="DATABASE_URL")
    mysql_host: str = Field(default="127.0.0.1", alias="MYSQL_HOST")
    mysql_port: int = Field(default=3306, alias="MYSQL_PORT")
    mysql_user: str = Field(default="root", alias="MYSQL_USER")
    mysql_password: str = Field(default="", alias="MYSQL_PASSWORD")
    mysql_database: str = Field(
        default="xerago_intelligence",
        alias="MYSQL_DATABASE",
    )
    mysql_charset: str = Field(default="utf8mb4", alias="MYSQL_CHARSET")
    db_echo: bool = Field(default=False, alias="DB_ECHO")

    # LLM (Sprint 3A — Ollama)
    llm_provider: str = Field(default="ollama", alias="LLM_PROVIDER")
    ollama_base_url: str = Field(
        default="http://127.0.0.1:11434",
        alias="OLLAMA_BASE_URL",
    )
    ollama_model: str = Field(default="gpt-oss:20b", alias="OLLAMA_MODEL")
    ollama_timeout_seconds: float = Field(default=300.0, alias="OLLAMA_TIMEOUT_SECONDS")
    ingest_scheduler_interval_minutes: int = Field(
        default=15,
        alias="INGEST_SCHEDULER_INTERVAL_MINUTES",
    )
    negative_filter_enabled: bool = Field(default=True, alias="NEGATIVE_FILTER_ENABLED")
    negative_score_skip_threshold: int = Field(
        default=5,
        alias="NEGATIVE_SCORE_SKIP_THRESHOLD",
    )

    # Phase 2 prototype dataset (file-backed; does not write to production artifacts)
    prototype_mode: bool = Field(default=False, alias="PROTOTYPE_MODE")
    max_articles_per_source: int = Field(
        default=10,
        alias="MAX_ARTICLES_PER_SOURCE",
    )

    # Repository root (contains registry/sources.yaml)
    project_root: Path | None = Field(default=None, alias="PROJECT_ROOT")

    @field_validator("database_url", mode="before")
    @classmethod
    def empty_url_is_none(cls, value: str | None) -> str | None:
        if value is None or str(value).strip() == "":
            return None
        return str(value).strip()

    @field_validator("project_root", mode="before")
    @classmethod
    def coerce_project_root(cls, value: str | Path | None) -> Path | None:
        if value is None or str(value).strip() == "":
            return None
        return Path(value).expanduser().resolve()

    @property
    def mysql_config_source(self) -> str:
        """Indicate whether DATABASE_URL or discrete MYSQL_* vars are used."""
        return "DATABASE_URL" if self.database_url else "MYSQL_*"

    @property
    def env_file_loaded(self) -> str | None:
        """Path to .env file if present under backend/."""
        return str(_ENV_FILE) if _ENV_FILE.is_file() else None

    def resolved_database_url(self) -> str:
        """
        Build SQLAlchemy URL.

        DATABASE_URL takes precedence when set. Otherwise builds from MYSQL_*.
        """
        if self.database_url:
            return self.database_url
        user = quote_plus(self.mysql_user)
        password = quote_plus(self.mysql_password)
        return (
            f"mysql+pymysql://{user}:{password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )

    def log_mysql_startup(self) -> None:
        """Log MySQL connection parameters (never logs password)."""
        logger.info(
            "MySQL config | host=%s port=%s database=%s username=%s source=%s env_file=%s",
            self.mysql_host,
            self.mysql_port,
            self.mysql_database,
            self.mysql_user,
            self.mysql_config_source,
            self.env_file_loaded or "(not found)",
        )
        print(
            f"  env file:   {self.env_file_loaded or '(not found — using defaults/env)'}"
        )
        print(f"  config via: {self.mysql_config_source}")
        print(f"  host:       {self.mysql_host}")
        print(f"  port:       {self.mysql_port}")
        print(f"  database:   {self.mysql_database}")
        print(f"  username:   {self.mysql_user}")

    @property
    def registry_dir(self) -> Path:
        return self.resolve_project_root() / "registry"

    @property
    def sources_yaml_path(self) -> Path:
        return self.registry_dir / "sources.yaml"

    @property
    def repos_yaml_path(self) -> Path:
        return self.registry_dir / "repos.yaml"

    @property
    def prototype_sources_yaml_path(self) -> Path:
        return self.registry_dir / "prototype_sources.yaml"

    @property
    def prototype_data_dir(self) -> Path:
        return self.resolve_project_root() / "data" / "prototype"

    @property
    def fresh_domain_data_dir(self) -> Path:
        """File-backed fresh domain corpus (enrichment pipeline; no production artifacts)."""
        return self.resolve_project_root() / "data" / "fresh_domain"

    def resolve_project_root(self) -> Path:
        if self.project_root is not None:
            root = self.project_root
        else:
            root = _discover_project_root()
        if not (root / "registry" / "sources.yaml").is_file():
            raise FileNotFoundError(
                f"Registry not found under project root: {root / 'registry'}"
            )
        return root


def _discover_project_root() -> Path:
    """Walk upward from CWD and package location to find repo root."""
    anchor = Path(__file__).resolve()
    search_roots = [
        Path.cwd(),
        anchor.parents[3],
        anchor.parents[4],
    ]
    seen: set[Path] = set()
    for start in search_roots:
        current = start.resolve()
        for _ in range(8):
            if current in seen:
                break
            seen.add(current)
            if (current / "registry" / "sources.yaml").is_file():
                return current
            parent = current.parent
            if parent == current:
                break
            current = parent
    raise FileNotFoundError(
        "Could not locate project root (registry/sources.yaml). "
        "Set PROJECT_ROOT in .env or run from the repository."
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
