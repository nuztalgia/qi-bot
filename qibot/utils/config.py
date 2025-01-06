from typing import Any, ClassVar, Final, overload

from qibot.utils.json import load_json_from_file
from qibot.utils.logging import Log

_CONFIG_FILENAME: Final[str] = "config"

_SERVER_ID_KEY: Final[str] = "server_id"
_CHANNEL_IDS_KEY: Final[str] = "channel_ids"

_DUMMY_SERVER_OR_CHANNEL_ID: Final[int] = 111111111111111111

_INITIAL_CONFIG: Final[dict[str, Any]] = load_json_from_file(
    filename=_CONFIG_FILENAME,
    data_type=dict,
    lowercase_dict_keys=True,
    create_if_missing=True,
    default_data={
        _SERVER_ID_KEY: _DUMMY_SERVER_OR_CHANNEL_ID,
        _CHANNEL_IDS_KEY: {},
    },
)


class BotConfig:
    # TODO: Allow config (or at least channel IDs) to be reloaded while bot is online.
    _current_config: ClassVar[dict[str, Any]] = _INITIAL_CONFIG

    @classmethod
    def get_server_id(cls) -> int:
        return _get_value(cls._current_config, _SERVER_ID_KEY, 0, True)

    @classmethod
    def get_channel_id(cls, channel_name: str, required: bool) -> int:
        channel_ids = _get_value(cls._current_config, _CHANNEL_IDS_KEY, {}, True)
        return _get_value(channel_ids, channel_name.lower(), 0, required)


@overload
def _get_value(
    source: dict[str, Any],
    key: str,
    fallback_value: str,
    required: bool,
) -> str: ...


@overload
def _get_value(
    source: dict[str, Any],
    key: str,
    fallback_value: int,
    required: bool,
) -> int: ...


@overload
def _get_value(
    source: dict[str, Any],
    key: str,
    fallback_value: dict[str, Any],
    required: bool,
) -> dict[str, Any]: ...


def _get_value(
    source: dict[str, Any],
    key: str,
    fallback_value: str | int | dict[str, Any],
    required: bool,
) -> str | int | dict[str, Any]:
    if not isinstance(fallback_value, (str, int, dict)):
        raise TypeError(f'Unsupported config value type: "{type(fallback_value)}".')

    # Use `get()` to avoid raising a KeyError. Will be `None` if `key` is not found.
    value = source.get(key)

    if value is None:
        error_message = (
            f'Config file is missing {"required" if required else ""} key "{key}".'
        )
    elif type(value) != type(fallback_value):
        error_message = (
            f'Config file contains a value of the wrong type for key "{key}". '
            f'Expected type "{type(fallback_value)}", but found "{type(value)}".'
        )
    elif value == _DUMMY_SERVER_OR_CHANNEL_ID:
        error_message = f'Config file contains a dummy/unset value for key "{key}".'
    else:
        Log.d(f'Successfully retrieved config value for key "{key}".')
        return value

    (Log.e if required else Log.d)(
        f'{error_message}{Log.NEWLINE}Using fallback value: "{fallback_value}"'
    )
    return fallback_value
