import html
from typing import Dict, Any
from manifesto.email.templates.base import EmailTemplate


class BasicEmailTemplate(EmailTemplate):
    def generate(self, pr_data: Dict[str, Any]) -> tuple[str, str]:
        subject = f"PR #{pr_data['number']}: {html.escape(pr_data['title'])}"

        e = html.escape
        body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #0366d6; color: white; padding: 15px; border-radius: 5px; }}
                .content {{ background: #f6f8fa; padding: 20px; margin: 20px 0; border-radius: 5px; }}
                .field {{ margin: 10px 0; }}
                .label {{ font-weight: bold; color: #586069; }}
                .value {{ margin-left: 10px; }}
                .description {{ background: white; padding: 15px; margin: 15px 0; border-left: 4px solid #0366d6; }}
                .footer {{ color: #586069; font-size: 12px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Pull Request Notification</h2>
                </div>

                <div class="content">
                    <div class="field">
                        <span class="label">Repository:</span>
                        <span class="value">{e(pr_data['base']['repo']['full_name'])}</span>
                    </div>

                    <div class="field">
                        <span class="label">PR Number:</span>
                        <span class="value">#{pr_data['number']}</span>
                    </div>

                    <div class="field">
                        <span class="label">Title:</span>
                        <span class="value">{e(pr_data['title'])}</span>
                    </div>

                    <div class="field">
                        <span class="label">Author:</span>
                        <span class="value">{e(pr_data['user']['login'])}</span>
                    </div>

                    <div class="field">
                        <span class="label">Branch:</span>
                        <span class="value">{e(pr_data['head']['ref'])} → {e(pr_data['base']['ref'])}</span>
                    </div>

                    <div class="field">
                        <span class="label">Status:</span>
                        <span class="value">{e(pr_data['state'].upper())}</span>
                    </div>

                    <div class="description">
                        <strong>Description:</strong>
                        <p>{e(pr_data.get('body', 'No description provided.'))}</p>
                    </div>

                    <div class="field">
                        <a href="{pr_data['html_url']}" style="background: #0366d6; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">View Pull Request</a>
                    </div>
                </div>

                <div class="footer">
                    This is an automated notification from manifesto.
                </div>
            </div>
        </body>
        </html>
        """

        return subject, body
