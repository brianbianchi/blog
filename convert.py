from pathlib import Path
import shutil
import markdown

root = Path(__file__).parent
dist = root / "dist"

shutil.rmtree(dist, ignore_errors=True)
dist.mkdir()

for name in ["styles.css", "icon.png"]:
    shutil.copy(root / name, dist / name)

template = (root / "template.html").read_text(encoding="utf-8")

for md_path in (root / "md").glob("*.md"):
    md_text = md_path.read_text(encoding="utf-8")

    lines = md_text.strip().splitlines()
    if lines and lines[0].startswith("# "):
        title = lines[0][2:].strip()
    else:
        title = md_path.stem.replace("-", " ").title()

    nav = "" if md_path.stem == "index" else '<nav><a href="index.html">← Brian</a></nav>'
    body = markdown.markdown(md_text, extensions=["extra"])

    html = template.format(title=title, body=body, nav=nav)
    (dist / f"{md_path.stem}.html").write_text(html, encoding="utf-8")
