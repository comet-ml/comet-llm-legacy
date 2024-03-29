# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at https://www.comet.com
#  Copyright (C) 2015-2023 Comet ML INC
#  This source code is licensed under the MIT license found in the
#  LICENSE file in the root directory of this package.
# *******************************************************


import logging
from types import ModuleType
from typing import Dict, Optional, Tuple

from . import logging_messages, url_helpers
from .api_key import comet_api_key


def _muted_import_comet_ml() -> Tuple[ModuleType, ModuleType]:
    try:
        logging.disable(logging.CRITICAL)
        import comet_ml
        import comet_ml.config

        return comet_ml, comet_ml.config  # type: ignore
    finally:
        pass
        logging.disable(0)


comet_ml, comet_ml_config = _muted_import_comet_ml()

LOGGER = logging.getLogger(__name__)

DEFAULT_COMET_BASE_URL = "https://www.comet.com"


def _extend_comet_ml_config() -> None:
    CONFIG_MAP_EXTENSION = {
        "comet.disable": {"type": int, "default": 0},
        "comet.logging.console": {"type": str, "default": "INFO"},
        "comet.raise_exceptions_on_error": {"type": int, "default": 0},
        "comet.internal.check_tls_certificate": {"type": bool, "default": True},
        "comet.online": {"type": bool, "default": True},
        "comet.offline_directory": {"type": str, "default": ".cometllm-runs"},
        "comet.offline_batch_duration_seconds": {"type": int, "default": 300},
        "comet.url_override": {"type": str},
    }

    comet_ml_config.CONFIG_MAP.update(CONFIG_MAP_EXTENSION)


def workspace() -> Optional[str]:
    return _COMET_ML_CONFIG["comet.workspace"]  # type: ignore


def project_name() -> Optional[str]:
    return _COMET_ML_CONFIG["comet.project_name"]  # type: ignore


def comet_url() -> str:
    url = _COMET_ML_CONFIG["comet.url_override"]

    if url is None:
        return DEFAULT_COMET_BASE_URL

    return url_helpers.get_root_url(url)


def api_key() -> Optional[str]:
    api_key = comet_ml.get_api_key(None, _COMET_ML_CONFIG)
    return api_key  # type: ignore


def setup_comet_url(api_key: str) -> None:
    """
    If API key contains Comet URL which does not conflict with
    COMET_URL_OVERRIDE variable set before, the value from API key
    will be saved in config.
    """

    assert _COMET_ML_CONFIG is not None

    parsed_api_key = comet_api_key.parse_api_key(api_key)

    if parsed_api_key is None:
        return

    config_url_override = _COMET_ML_CONFIG[
        "comet.url_override"
    ]  # check if we need a getter here

    if config_url_override is not None and config_url_override != "":
        config_base_url = url_helpers.get_root_url(config_url_override)
        if (
            parsed_api_key.base_url is not None
            and parsed_api_key.base_url != config_base_url
        ):
            LOGGER.warning(
                logging_messages.BASE_URL_MISMATCH_CONFIG_API_KEY,
                config_base_url,
                parsed_api_key.base_url,
            )
        # do not change base url
        return

    if parsed_api_key.base_url is not None:
        _COMET_ML_CONFIG["comet.url_override"] = parsed_api_key.base_url


def logging_level() -> str:
    return _COMET_ML_CONFIG["comet.logging.console"]  # type: ignore


def is_ready() -> bool:
    """
    True if comet API key is set.
    """
    return api_key() is not None


def comet_disabled() -> bool:
    return bool(_COMET_ML_CONFIG["comet.disable"])


def raising_enabled() -> bool:
    return bool(_COMET_ML_CONFIG["comet.raise_exceptions_on_error"])


def logging_available() -> bool:
    if api_key() is None:
        return False

    return True


def autologging_enabled() -> bool:
    return not comet_ml.get_config("comet.disable_auto_logging")  # type: ignore


def tls_verification_enabled() -> bool:
    return _COMET_ML_CONFIG["comet.internal.check_tls_certificate"]  # type: ignore


def offline_enabled() -> bool:
    return not bool(_COMET_ML_CONFIG["comet.online"])


def offline_directory() -> str:
    return str(_COMET_ML_CONFIG["comet.offline_directory"])


def offline_batch_duration_seconds() -> int:
    return int(_COMET_ML_CONFIG["comet.offline_batch_duration_seconds"])


def init(
    api_key: Optional[str] = None,
    workspace: Optional[str] = None,
    project: Optional[str] = None,
) -> None:
    """
    An easy, safe, interactive way to set and save your settings.

    Will ask for your api_key if not already set. Your
    api_key will not be shown.

    Will save the config to .comet.config file.
    Default location is "~/" (home) or COMET_CONFIG, if set.

    Args:
        api_key: str (optional) comet API key.
        workspace: str (optional) comet workspace to use for logging.
        project: str (optional) project name to create in comet workspace.

    Valid settings include:
    """

    kwargs: Dict[str, Optional[str]] = {
        "api_key": api_key,
        "workspace": workspace,
        "project_name": project,
    }

    kwargs = {key: value for key, value in kwargs.items() if value is not None}

    comet_ml.init(**kwargs)

    global _COMET_ML_CONFIG
    # Recreate the Config object to re-read the config files
    _COMET_ML_CONFIG = comet_ml.get_config()


_extend_comet_ml_config()

_COMET_ML_CONFIG = comet_ml.get_config()
assert _COMET_ML_CONFIG is not None
