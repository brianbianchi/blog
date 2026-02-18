from pathlib import Path
import markdown
import shutil

if Path("dst").exists():
    shutil.rmtree("dst")
Path("dst").mkdir(parents=True, exist_ok=True)

shutil.copy("styles.css", "dst/styles.css")

with open("template.html", "r", encoding="utf-8") as f:
    template = f.read()

for md_path in Path("md").glob("*.md"):
    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    html_body = markdown.markdown(md_text, extensions=["extra"])
    title = md_path.stem.replace("-", " ").title()

    full_html = template.format(body=html_body)

    html_path = Path("dst") / (md_path.stem + ".html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(full_html)
