from typing import Final

from discord import Embed, File

from qibot.utils import Template

SPACING: Final[str] = " \u200b "
DEFAULT_COLOR: Final[int] = 0x6C79FF

TEXT_WITH_EMOJI: Final[Template] = Template(f"$emoji{SPACING}$text")


def assert_valid_emoji(emoji: str) -> None:
    if (not emoji) or (len(emoji) > 2) or emoji.isascii():
        raise ValueError(f'Invalid emoji: "{emoji}" (Must be non-ascii and <=2 chars.)')


class EmbedData:
    def __init__(self, color: int, **_) -> None:
        self._required_attr_names: Final[list[str]] = []
        self._files: Final[list[File]] = []
        self._color: Final[int] = color or DEFAULT_COLOR

    def _validate(self) -> None:
        for attr_name in self._required_attr_names:
            if not getattr(self, f"_{attr_name}", None):
                raise AttributeError(
                    f'Required attribute "{attr_name}" is missing '
                    f'or empty for "{self.__class__.__name__}"!'
                )

    def build_embed(self) -> Embed:
        self._validate()
        return Embed(color=self._color)

    def get_files(self) -> list[File]:
        return self._files or Embed.Empty
