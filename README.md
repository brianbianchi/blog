# blog

A minimal static site generator that converts Markdown files to HTML and deploys to GitHub Pages.

## How it works

1. Write posts in `md/` as Markdown files
2. Run `convert.py` to generate HTML into `dist/`
3. Push to `master` — GitHub Actions builds and deploys automatically

## Local development

```bash
pip install -r requirements.txt
python convert.py
```
