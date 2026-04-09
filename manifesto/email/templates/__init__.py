from pathlib import Path
from manifesto.email.templates.base import EmailTemplate
from manifesto.email.templates.basic import BasicEmailTemplate
from manifesto.email.templates.builder import BuilderEmailTemplate
from manifesto.email.templates.custom import CustomEmailTemplate

__all__ = [
    "EmailTemplate",
    "BasicEmailTemplate",
    "BuilderEmailTemplate",
    "CustomEmailTemplate",
    "get_template",
]


def get_template(config) -> EmailTemplate:
    pref = config.get_template_preference()
    template_type = pref.get("type", "basic")

    if template_type == "builder":
        return BuilderEmailTemplate(pref.get("components", []))

    if template_type == "custom":
        return CustomEmailTemplate(config.get_custom_template_path())

    return BasicEmailTemplate()
