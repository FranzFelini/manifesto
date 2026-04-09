import re
import html
from typing import Dict, Any
from manifesto.email.templates.base import EmailTemplate


def _detect_env(branch: str, language: str) -> str:
    b = branch.lower()
    if any(x in b for x in ("prod", "production", "main", "master")):
        return "production" if language == "en" else "produkcijski"
    if any(x in b for x in ("stg", "staging")):
        return "staging"
    if any(x in b for x in ("dev", "development")):
        return "development"
    return branch


STRINGS = {
    "en": {
        "greeting": "Dear Team,",
        "intro": "During the period from <strong>{start_time}</strong> to <strong>{end_time}</strong>, a <strong>{env}</strong> release of <strong>{repo_name} ({version})</strong> is planned. Please account for potential system downtime during this window.",
        "details_title": "Release details:",
        "version_label": "Release version:",
        "migrations_label": "Migrations:",
        "seeds_label": "Database seeds:",
        "env_label": ".env file:",
        "deploy_title": "What will be executed during this period:",
        "explanation_title": "Explanation:",
        "additional_title": "Additional:",
        "note_label": "NOTE:",
        "closing": "Thank you for your understanding and cooperation.",
        "regards": "Best regards,",
        "footer_via": "Automated release notification via",
    },
    "bs": {
        "greeting": "Poštovani,",
        "intro": "U periodu od <strong>{start_time}</strong> do <strong>{end_time}</strong>, planiran je <strong>{env}</strong> release nove verzije <strong>{repo_name} ({version})</strong>. Molimo vas da u navedenom vremenskom okviru predvidite potencijalni downtime sistema.",
        "details_title": "Detalji release-a:",
        "version_label": "Release verzija:",
        "migrations_label": "Migracije:",
        "seeds_label": "Seed-ovi u bazama:",
        "env_label": ".env fajl:",
        "deploy_title": "Šta će se izvršiti u okviru ovog perioda:",
        "explanation_title": "Obrazloženje:",
        "additional_title": "Dodatno:",
        "note_label": "NAPOMENA:",
        "closing": "Hvala na razumijevanju i saradnji.",
        "regards": "S poštovanjem,",
        "footer_via": "Automatska notifikacija putem",
    },
}


def strip_html(text: str) -> str:
    text = re.sub(r"<(style|head)[^>]*>.*?</(style|head)>", "", text, flags=re.DOTALL)
    text = re.sub(r"<li[^>]*>", "\n  • ", text, flags=re.IGNORECASE)
    text = re.sub(r"<(br|p|div|tr|h[1-6])[^>]*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = (
        text.replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&mdash;", "—")
        .replace("&nbsp;", " ")
        .replace("&#39;", "'")
    )
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


class ReleaseEmailTemplate(EmailTemplate):
    def generate(self, pr_data: Dict[str, Any]) -> tuple[str, str]:
        info = pr_data.get("_release", {})
        e = html.escape

        language = info.get("language", "bs")
        s = STRINGS.get(language, STRINGS["bs"])

        version = e(info.get("version", ""))
        start_time = e(info.get("start_time", ""))
        end_time = e(info.get("end_time", ""))
        migrations = e(info.get("migrations", ""))
        seeds = e(info.get("seeds", ""))
        env_changes = e(info.get("env_changes", ""))
        deploy_steps = info.get("deploy_steps", [])
        notes = info.get("notes", [])
        napomena = info.get("napomena", "")
        signature = e(info.get("signature", pr_data["user"]["login"]))
        repo_name = e(pr_data["base"]["repo"]["name"])

        env = _detect_env(pr_data["base"]["ref"], language)
        subject = f"Release notification: {version} - {pr_data['base']['repo']['name']} ({env})"

        intro = s["intro"].format(
            start_time=start_time,
            end_time=end_time,
            repo_name=repo_name,
            version=version,
            env=env,
        )

        deploy_html = "".join(
            f"<li style='margin:4px 0;'>{e(step)}</li>" for step in deploy_steps
        )
        notes_html = "".join(f"<li style='margin:4px 0;'>{e(n)}</li>" for n in notes)

        napomena_section = ""
        if napomena:
            napomena_section = f"""
            <p style="margin:20px 0 4px;"><strong>{s["note_label"]}</strong></p>
            <p style="margin:0;">{e(napomena)}</p>"""

        additional_section = ""
        if notes:
            additional_section = f"""
            <p style="margin:20px 0 4px;"><strong>{s["additional_title"]}</strong></p>
            <ul style="margin:0;padding-left:20px;">{notes_html}</ul>"""

        body = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family:Arial,sans-serif;font-size:14px;color:#222;line-height:1.7;margin:0;padding:0;">
<div style="max-width:640px;margin:0 auto;padding:32px 24px;">

    <p style="margin:0 0 16px;">{s["greeting"]}</p>

    <p style="margin:0 0 20px;">{intro}</p>

    <p style="margin:0 0 8px;"><strong>{s["details_title"]}</strong></p>
    <table style="border-collapse:collapse;width:100%;margin-bottom:20px;">
        <tr>
            <td style="padding:5px 16px 5px 0;width:170px;color:#555;vertical-align:top;"><strong>{s["version_label"]}</strong></td>
            <td style="padding:5px 0;">{version}</td>
        </tr>
        <tr>
            <td style="padding:5px 16px 5px 0;color:#555;vertical-align:top;"><strong>{s["migrations_label"]}</strong></td>
            <td style="padding:5px 0;">{migrations}</td>
        </tr>
        <tr>
            <td style="padding:5px 16px 5px 0;color:#555;vertical-align:top;"><strong>{s["seeds_label"]}</strong></td>
            <td style="padding:5px 0;">{seeds}</td>
        </tr>
        <tr>
            <td style="padding:5px 16px 5px 0;color:#555;vertical-align:top;"><strong>{s["env_label"]}</strong></td>
            <td style="padding:5px 0;">{env_changes}</td>
        </tr>
    </table>

    <p style="margin:0 0 8px;"><strong>{s["deploy_title"]}</strong></p>
    <ul style="margin:0 0 20px;padding-left:20px;">{deploy_html}</ul>

    <p style="margin:0 0 8px;"><strong>{s["explanation_title"]}</strong></p>
    <p style="margin:0 0 20px;white-space:pre-line;">{e(pr_data.get("body") or "")}</p>

    {additional_section}
    {napomena_section}

    <p style="margin:24px 0 4px;">{s["closing"]}</p>

    <p style="margin:16px 0 0;">
        {s["regards"]}<br>
        <strong>{signature}</strong>
    </p>

    <hr style="border:none;border-top:1px solid #ddd;margin:32px 0 16px;">
    <p style="font-size:11px;color:#999;margin:0;">
        {s["footer_via"]} <a href="https://github.com/FranzFelini/manifesto" style="color:#555;">manifesto/a</a>
        &mdash; PR <a href="{pr_data['html_url']}" style="color:#555;">#{pr_data['number']}</a>: {e(pr_data['title'])}
    </p>

</div>
</body>
</html>"""

        return subject, body
