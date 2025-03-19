"""Check patching resource updates."""

from environs import Env
from loguru import logger

from main import get_app
from src.config import RevancedConfig
from src.manager.github import GitHubManager
from src.utils import default_build, patches_dl_key, patches_versions_key


def check_if_build_is_required() -> bool:
    """Read resource version."""
    env = Env()
    env.read_env()
    config = RevancedConfig(env)
    needs_to_repatched = []
    for app_name in env.list("PATCH_APPS", default_build):
        logger.info(f"Checking {app_name}")
        app_obj = get_app(config, app_name)
        old_patches_versions = GitHubManager(env).get_last_version(app_obj, patches_versions_key)
        old_patches_source = GitHubManager(env).get_last_version_source(app_obj, patches_dl_key)
        app_obj.download_patch_resources(config)
        if not isinstance(old_patches_versions, list):
            msg = "`old_patches_version` should be a list of strings (versions)."
            raise TypeError(msg)
        for old_patches_version, patches_rs, patches_dl in zip(
            old_patches_versions,
            app_obj.resource["patches"],
            app_obj.patches_dl,
            strict=False,
        ):
            if GitHubManager(env).should_trigger_build(
                old_patches_version,
                old_patches_source,
                patches_rs["version"],
                patches_dl,
            ):
                caused_by = {
                    "app_name": app_name,
                    "patches": {
                        "old": old_patches_version,
                        "new": patches_rs["version"],
                    },
                }
                logger.info(f"New build can be triggered caused by {caused_by}")
                needs_to_repatched.append(app_name)
                break
    logger.info(f"{needs_to_repatched} are need to repatched.")
    if needs_to_repatched:
        print(",".join(needs_to_repatched))  # noqa: T201
        return True
    return False


check_if_build_is_required()
