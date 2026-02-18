# Simple Markdown Blog Generator

This project provides a simple yet effective way to generate a static HTML blog from Markdown files. It uses a Python script to convert Markdown content into HTML, applying a consistent template and styling.

## Features

*   **Markdown to HTML Conversion**: Easily convert `.md` files into `.html` pages.
*   **Templating**: All generated pages inherit a common structure from `template.html`.
*   **Styling**: Global styles are applied via `styles.css`.
*   **Automatic Link Conversion**: Internal Markdown links (e.g., `[my-page](my-page)`) are automatically converted to point to the corresponding `.html` files (e.g., `<a href="my-page.html">my-page</a>`).
*   **Clean Build Process**: The output directory (`dst/`) is cleaned and recreated on each run, ensuring a fresh build.

## Project Structure

```
.
├── convert.py          # Python script for conversion
├── README.md           # This file
├── styles.css          # Global styles for the blog
├── template.html       # HTML template for all pages
├── md/                 # Contains source Markdown files
│   ├── index.md
│   └── ...
└── dst/                # Output directory for generated HTML files (created by convert.py)
    ├── index.html
    └── ...
```

## Setup

No special installation is required beyond a standard Python environment. The project uses the `markdown` and `shutil` libraries, both of which are standard for Python.

If you don't have `markdown` installed, you can install it via pip:
```bash
pip install markdown
```

## Usage

To generate the HTML blog pages from the Markdown sources:

1.  Place your Markdown files in the `md/` directory.
2.  Run the conversion script:
    ```bash
    python convert.py
    ```

This will:
*   Clear the `dst/` directory.
*   Copy `styles.css` into `dst/`.
*   Convert all `.md` files from the `md/` directory into `.html` files in the `dst/` directory, applying `template.html`.
*   Automatically adjust internal links in your Markdown to point to the correct `.html` files.

You can then open the `.html` files in the `dst/` directory with your web browser. For example, `dst/index.html`.

## Customization

*   **`template.html`**: Modify this file to change the overall layout, add headers/footers, or include additional meta tags.
*   **`styles.css`**: Update this file to customize the visual appearance of your blog.
*   **`md/`**: Add, remove, or edit your Markdown content files here.

## Technologies Used

*   Python 3
*   Python-Markdown library
*   `pathlib` (Python standard library)
*   `shutil` (Python standard library)
*   `re` (Python standard library)
