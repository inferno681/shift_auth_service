from pathlib import Path

import yaml
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class _SettingsModel(BaseSettings):

    @classmethod
    def from_yaml(cls, config_path: str) -> '_SettingsModel':
        return cls(
            **yaml.safe_load(Path(config_path).read_text(encoding='utf-8')),
        )

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_prefix='EMP_',
        env_nested_delimiter='__',
    )

    @classmethod
    def customise_sources(
        cls,
        init_settings,
        env_settings,
        file_secret_settings,
    ):
        """Определяем приоритет использования переменных."""
        return init_settings, env_settings, file_secret_settings


class _ServiceSettings(_SettingsModel):
    title: str
    description: str
    host: str
    port: int
    debug: bool
    tags_metadata_auth: dict[str, str]
    tags_metadata_check: dict[str, str]


class _SettingsSecret(BaseSettings):
    """Базовый класс настроек."""

    SECRET: SecretStr = SecretStr('default_secret')

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
    )


class Settings(_SettingsModel, _SettingsSecret):
    """Настройки сервиса."""

    service: _ServiceSettings


config = Settings.from_yaml('./config/config.yaml')
