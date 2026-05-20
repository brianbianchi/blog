from pathlib import Path
import markdown
import shutil

if Path("dist").exists():
    shutil.rmtree("dist")
Path("dist").mkdir(parents=True, exist_ok=True)

shutil.copy("styles.css", "dist/styles.css")
shutil.copy("icon.png", "dist/icon.png")

with open("template.html", "r", encoding="utf-8") as f:
    template = f.read()

for md_path in Path("md").glob("*.md"):
    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    html_body = markdown.markdown(md_text, extensions=["extra"])
    title = "Brian" if md_path.stem == "index" else md_path.stem.replace("-", " ").title()
    nav = "" if md_path.stem == "index" else '<nav><a href="index.html">home</a></nav>'

    full_html = template.format(title=title, body=html_body, nav=nav)

    html_path = Path("dist") / (md_path.stem + ".html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(full_html)
