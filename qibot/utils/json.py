import json
from pathlib import Path
from typing import Any, Final, overload

import json5

from qibot.assets import DATA_PATH
from qibot.utils.logging import Log
from qibot.utils.templates import Template

_ENCODING: Final[str] = "utf-8"
_INDENT_SPACES: Final[int] = 2

_JSON_FILENAME: Final[Template] = Template("${filename}.json")


@overload
def load_json_from_file(
    filename: str,
    data_type: type[dict],
    *,
    lowercase_dict_keys: bool = False,
    create_if_missing: bool = False,
    default_data: dict[str, Any] | None = None,
) -> dict[str, Any]: ...


@overload
def load_json_from_file(
    filename: str,
    data_type: type[list],
    *,
    lowercase_dict_keys: bool = False,
    create_if_missing: bool = False,
    default_data: list[Any] | None = None,
) -> list[Any]: ...


def load_json_from_file(
    filename: str,
    data_type: type[dict | list],
    *,
    lowercase_dict_keys: bool = False,
    create_if_missing: bool = False,
    default_data: dict[str, Any] | list[Any] | None = None,
) -> dict[str, Any] | list[Any]:
    """Returns the contents of a JSON file parsed as a Python object.

    This function is quite lenient and does its best to return a workable object of the
    requested type. If the source file is nonexistent, empty, or otherwise invalid, this
    will simply be an empty object.

    Args:
        filename:
            The name of the file, without the `.json` extension.
        data_type:
            The type of object (`dict` or `list`) that the file should contain.
        lowercase_dict_keys:
            If `True` and if `data_type` is `dict`, all keys in the returned `dict` will
            be lower-cased regardless of (and without modifying) their capitalization in
            the source file. Defaults to `False`. Ignored if `data_type` is `list`.
        create_if_missing:
            If `True` and if the specified file does not exist, then the file will be
            created and initialized with `default_data` (if provided) or an empty object
            of type `data_type`. Defaults to `False`.
        default_data:
            If `create_if_missing` is `True` and if the specified file does not exist,
            then it will be initialized with this data. Must match the type specified by
            `data_type`. If omitted, defaults to an empty object of type `data_type`.
            Ignored if `create_if_missing` is `False`.

    Returns:
        An object of the specified `data_type`.

    Raises:
        TypeError:
            If `data_type` is not `dict` or `list`, or if `default_data` is provided and
            its type does not match `data_type`.
    """
    if data_type not in (dict, list):
        raise TypeError(f'Expected type "dict" or "list", but got "{type(data_type)}".')

    if default_data and not isinstance(default_data, data_type):
        raise TypeError(
            f'Specified type "{data_type}", but provided default {type(default_data)}.'
        )

    empty_data: Final[dict | list] = data_type()
    file_path: Final[Path] = DATA_PATH / _JSON_FILENAME.sub(filename=filename)

    def is_valid_file_path() -> bool:
        if file_path.is_dir():
            Log.e(f'Expected "{file_path}" to be a file, but found a directory.')
            return False
        elif file_path.is_file():
            return True
        elif create_if_missing:
            data_label = "default" if default_data else "empty"
            Log.i(f'Creating file "{file_path}" with {data_label} data.')
            json_text = json.dumps(default_data or empty_data, indent=_INDENT_SPACES)
            file_path.write_text(json_text, encoding=_ENCODING)
            return True
        else:
            Log.e(f'Tried to load "{file_path}", but that file does not exist.')
            return False

    def get_json_from_file() -> dict[Any, Any] | list[Any] | None:
        # This method assumes `file_path` was checked and points to a file that exists.
        file_content = file_path.read_text(encoding=_ENCODING)

        # Some 3P JSON might begin/end with extraneous and/or unpredictable characters.
        start_index = file_content.find("{" if data_type is dict else "[")
        end_index = file_content.rfind("}" if data_type is dict else "]")

        if (start_index >= 0) and (end_index > start_index):
            file_content = file_content[start_index : end_index + 1]
            try:
                # Try the standard json module first - it's fast and handles most cases.
                return json.loads(file_content)
            except json.decoder.JSONDecodeError:
                # The json5 module is much slower, but is more lenient about formatting.
                return json5.loads(file_content)

        # If we haven't returned anything by this point, the file contents are invalid.
        Log.e(f'File "{file_path}" does not contain a valid JSON {data_type}.')
        return None

    def sanitize_dict(raw_data: dict[Any, Any]) -> dict[str, Any]:
        sanitized_data = {}
        for key, value in raw_data.items():
            if isinstance(key, str):
                new_key = key.lower() if lowercase_dict_keys else key
                new_value = sanitize_dict(value) if isinstance(value, dict) else value
                sanitized_data[new_key] = new_value
            else:
                Log.w(f'Ignoring non-string key "{key}" in file "{file_path}".')
        return sanitized_data

    data = (is_valid_file_path() and get_json_from_file()) or empty_data
    return data if isinstance(data, list) else sanitize_dict(data)
