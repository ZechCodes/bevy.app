from bevy.injection import AutoInject, detect_dependencies
from bevy.app.args import ArgumentParser, CLIArgs
from typing import Any
import os


@detect_dependencies
class Options(AutoInject):
    """The options object aggregates all options values that the Bevy.App application pulls in from the environment."""

    args: CLIArgs

    var_prefix = "BEVY_APP_"
    path_key = "PATH"
    config_file_key = "CONFIG_FILE"
    logger_level_key = "LOGGER_LEVEL"
    logger_name_key = "LOGGER_NAME"

    def __init__(self):
        self._cli_options = {}
        self._env_options = self._load_env()
        self._options = self._build_base_options()

    def __getitem__(self, item: str) -> Any:
        if item in self._cli_options:
            return self._cli_options[item]

        if item in self._env_options:
            return self._env_options[item]

        return self._options[item]

    def __contains__(self, item: str) -> bool:
        return item in (self._cli_options | self._env_options | self._options)

    @property
    def cli(self) -> dict[str, Any]:
        return self._cli_options.copy()

    @property
    def env(self) -> dict[str, Any]:
        return self._env_options.copy()

    def add_using_arg_parser(self, parser: ArgumentParser):
        """Uses an ArgumentParser to populate the CLI options."""
        self._cli_options.update(self.args.parse_args(parser).to_dict())

    def get(self, item: str, default: Any | None = None) -> Any | None:
        try:
            return self[item]
        except KeyError:
            return default

    def _build_base_options(self) -> dict[str, Any]:
        return {self.path_key: self._get_path()}

    def _get_path(self):
        return os.getcwd()

    def _load_env(self) -> dict[str, Any]:
        return {
            key.removeprefix(self.prefix): value
            for key, value in os.environ.items()
            if key.startswith(self.prefix)
        }
