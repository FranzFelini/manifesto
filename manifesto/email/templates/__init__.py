from pathlib import Path
from manifesto.email.templates.base import EmailTemplate
from manifesto.email.templates.basic import BasicEmailTemplate
from manifesto.email.templates.builder import BuilderEmailTemplate
from manifesto.email.templates.custom import CustomEmailTemplate
from manifesto.email.templates.release import ReleaseEmailTemplate

__all__ = [
    "EmailTemplate",
    "BasicEmailTemplate",
    "BuilderEmailTemplate",
    "CustomEmailTemplate",
    "ReleaseEmailTemplate",
    "get_template",
]


def get_template(config) -> EmailTemplate:
    pref = config.get_template_preference()
    template_type = pref.get("type", "basic")

    if template_type == "builder":
        return BuilderEmailTemplate(pref.get("components", []))

    if template_type == "custom":
        return CustomEmailTemplate(config.get_custom_template_path())

    if template_type == "release":
        return ReleaseEmailTemplate()

    return BasicEmailTemplate()
