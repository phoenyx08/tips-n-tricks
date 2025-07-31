import markdown
import subprocess
from jinja2 import Template
from datetime import datetime
import os
import re

def markdown_to_html(md_content: str) -> str:
    return markdown.markdown(md_content, extensions=["fenced_code", "codehilite", "tables", "toc"])

def render_html(title: str, html_content: str) -> str:
    with open("./templates/article.html") as f:
        template = Template(f.read())
    return template.render(title=title, content=html_content)

def slugify(text):
    return re.sub(r'\W+', '-', text.lower()).strip('-')

def save_article_file(title: str, html: str) -> str:
    slug = slugify(title)
    filename = f"./public/{slug}.html"
    os.makedirs("./public", exist_ok=True)
    with open(filename, "w") as f:
        f.write(html)
    return filename, slug

def create_git_pr(file_path: str, title: str, branch_name: str = None):
    if branch_name is None:
        branch_name = f"article-{slugify(title)}-{datetime.now().strftime('%Y%m%d%H%M')}"

    subprocess.run(["git", "checkout", "-b", branch_name], check=True)
    subprocess.run(["git", "add", file_path], check=True)
    subprocess.run(["git", "commit", "-m", f"Add article: {title}"], check=True)
    subprocess.run(["git", "push", "-u", "origin", branch_name], check=True)
    subprocess.run(["gh", "pr", "create", "--title", title, "--body", "Automatically generated article. Please review."], check=True)
