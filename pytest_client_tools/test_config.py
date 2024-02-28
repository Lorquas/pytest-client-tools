# SPDX-FileCopyrightText: Red Hat
# SPDX-License-Identifier: MIT

from dynaconf import Dynaconf, Validator


class TestConfig:
    def __init__(self):
        self._settings = Dynaconf(
            default_env="default",
            environments=True,
            envvar_prefix="PYTEST_CLIENT_TOOLS",
            settings_files=["settings.toml", ".secrets.toml"],
        )
        self._settings.validators.register(
            Validator("candlepin.host"),
            Validator(
                "candlepin.port",
                gt=0,
                lt=65536,
                cast=int,
                is_type_of=int,
                default=443,
            ),
            Validator("candlepin.prefix", startswith="/"),
            Validator("candlepin.insecure", cast=bool, is_type_of=bool),
            Validator("candlepin.username"),
            Validator(
                "candlepin.password",
                must_exist=True,
                when=Validator("candlepin.username", must_exist=True),
            ),
            Validator("candlepin.activation_keys", cast=list, is_type_of=list),
            Validator(
                "candlepin.org",
                must_exist=True,
                when=Validator(
                    "candlepin.activation_keys",
                    cast=list,
                    is_type_of=list,
                    must_exist=True,
                ),
            ),
            Validator("insights.legacy_upload", cast=bool, is_type_of=bool),
        )
        self._settings.validators.validate()

    @property
    def is_external(self):
        try:
            return (
                self._settings.get("candlepin.host") is not None
                and self._settings.get("candlepin.port") is not None
                and self._settings.get("candlepin.prefix") is not None
                and (
                    (
                        self._settings.get("candlepin.username") is not None
                        and self._settings.get("candlepin.password") is not None
                    )
                    or (
                        self._settings.get("candlepin.activation_keys") is not None
                        and self._settings.get("candlepin.org") is not None
                    )
                )
            )
        except KeyError:
            return False

    def get(self, *path):
        return self._settings[".".join(path)]
