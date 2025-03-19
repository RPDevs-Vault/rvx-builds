"""Revanced Configurations."""

from pathlib import Path
from typing import Self

from environs import Env

from src.utils import default_build, default_cli, default_patches, resource_folder


class RevancedConfig(object):
    """Revanced Configurations."""

    def __init__(self: Self, env: Env) -> None:
        self.env = env
        self.temp_folder_name = resource_folder
        self.temp_folder = Path(self.temp_folder_name)
        self.ci_test = env.bool("CI_TEST", False)
        self.rip_libs_apps: list[str] = []
        self.existing_downloaded_apks = env.list("EXISTING_DOWNLOADED_APKS", [])
        self.personal_access_token = env.str("PERSONAL_ACCESS_TOKEN", None)
        self.dry_run = env.bool("DRY_RUN", False)
        self.global_cli_dl = env.str("GLOBAL_CLI_DL", default_cli)
        self.global_patches_dl = self.get_patch_dls("GLOBAL", [default_patches])
        self.global_keystore_name = env.str("GLOBAL_KEYSTORE_FILE_NAME", "revanced.keystore")
        self.global_options_file = env.str("GLOBAL_OPTIONS_FILE", "options.json")
        self.global_archs_to_build = env.list("GLOBAL_ARCHS_TO_BUILD", [])
        self.extra_download_files: list[str] = env.list("EXTRA_FILES", [])
        self.apk_editor = "apkeditor-output.jar"
        self.extra_download_files.append("https://github.com/REAndroid/APKEditor@apkeditor.jar")
        self.apps = env.list("PATCH_APPS", default_build)
        self.global_old_key = env.bool("GLOBAL_OLD_KEY", True)
        self.global_space_formatted = env.bool("GLOBAL_SPACE_FORMATTED_PATCHES", True)

    def get_patch_dls(self: Self, prefix: str, default: list[str]) -> list[str]:
        """Set the patch dls for a given prefix."""
        patches_dl = list(
            filter(
                lambda item: item,
                [item.strip() for item in self.env.list(f"{prefix}_PATCHES_DL".upper(), default, delimiter="|")],
            ),
        )
        # Remove duplicates
        for index, item in enumerate(patches_dl):
            for i in range(index + 1, len(patches_dl)):
                if item == patches_dl[i]:
                    patches_dl.pop(i)
        self.env._values[f"{prefix}_PATCHES_DL"] = patches_dl  # noqa: SLF001
        return patches_dl
