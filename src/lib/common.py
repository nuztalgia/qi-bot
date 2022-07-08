import json
import re
import string
from datetime import datetime
from typing import Any, Callable, Final, Optional

from aiohttp import ClientSession
from discord import ClientUser, Member
from discord.utils import utcnow
from humanize import naturaltime


class Template(string.Template):
    sub: Final[Callable[..., str]] = string.Template.substitute
    safe_sub: Final[Callable[..., str]] = string.Template.safe_substitute


class Utils:
    _CLIENT_SESSION: Final[ClientSession] = ClientSession()

    _JSON_FILE_PATH: Final[Template] = Template("${path}/${name}.json")
    _MEMBER_NAMETAG: Final[Template] = Template("${name}#${tag}")
    _TIME_STAMP_FORMAT: Final[Template] = Template("<t:${timestamp}>")

    _TEMPLATE_KEY_PATTERN: Final[re.Pattern] = re.compile(r"\${?(\w*)", re.ASCII)

    @classmethod
    def format_time(
        cls, time: datetime, show_timestamp: bool = True, show_elapsed: bool = True
    ) -> str:
        results = []
        if show_timestamp:
            results.append(cls._TIME_STAMP_FORMAT.sub(timestamp=int(time.timestamp())))
        if show_elapsed:
            elapsed_time = naturaltime(utcnow() - time)
            results.append(f"({elapsed_time})" if results else elapsed_time)
        return " ".join(results)

    @classmethod
    def get_member_nametag(cls, member: Member | ClientUser) -> str:
        return cls._MEMBER_NAMETAG.sub(name=member.name, tag=member.discriminator)

    @classmethod
    def get_template_keys(cls, template_string: str) -> set[str]:
        return set(cls._TEMPLATE_KEY_PATTERN.findall(template_string))

    @classmethod
    async def load_content_from_url(cls, url: str) -> bytes:
        async with cls._CLIENT_SESSION.get(url) as response:
            return await response.read()

    @classmethod
    def load_json_from_file(
        cls, filename: str, path: str = "assets/data/", lowercase_keys: bool = True
    ) -> dict[str, Any] | list[Any]:
        full_path = cls._JSON_FILE_PATH.sub(path=path, name=filename)
        with open(full_path, mode="r", encoding="utf-8") as file:
            result = json.load(file)
        return cls._lowercase_keys(result) if lowercase_keys else result

    @classmethod
    def _lowercase_keys(cls, original: dict[str, Any]) -> dict[str, Any]:
        result = {}
        for key, value in original.items():
            new_value = cls._lowercase_keys(value) if isinstance(value, dict) else value
            result[key.lower()] = new_value
        return result


class Config:
    _CONFIG: Final[dict[str, Any]] = Utils.load_json_from_file(
        filename="config", path="."
    )  # type: ignore[assignment]

    BOT_TOKEN: Final[str] = _CONFIG["bot_token"]
    SERVER_ID: Final[int] = _CONFIG["server_id"]
    DEV_MODE_ENABLED: Final[bool] = _CONFIG.get("dev_mode_enabled", False)
    LOG_THRESHOLD: Final[Optional[str]] = _CONFIG.get("log_threshold")

    @classmethod
    def get_channel_id(cls, channel_name: str) -> int:
        return cls._CONFIG["channel_ids"].get(channel_name.lower(), 0)
