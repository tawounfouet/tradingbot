"""Generate the API reference pages and navigation."""

from pathlib import Path

import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()

# Define the source directory
src = Path(__file__).parent.parent / "src"
tradingbot_src = src / "tradingbot"

# Generate documentation for each Python module
for path in sorted(tradingbot_src.rglob("*.py")):
    # Skip __pycache__ and other non-source files
    if "__pycache__" in str(path) or path.name.startswith("test_"):
        continue

    # Get the module path relative to src
    module_path = path.relative_to(src).with_suffix("")
    doc_path = path.relative_to(src).with_suffix(".md")
    full_doc_path = Path("reference", doc_path)

    # Convert path to module name
    parts = tuple(module_path.parts)

    if parts[-1] == "__init__":
        parts = parts[:-1]
        doc_path = doc_path.with_name("index.md")
        full_doc_path = full_doc_path.with_name("index.md")
    elif parts[-1] == "__main__":
        continue

    # Add to navigation
    nav[parts] = doc_path.as_posix()

    # Create the documentation file
    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        ident = ".".join(parts)

        # Write the module documentation
        fd.write(f"# {ident}\n\n")
        fd.write(f"::: {ident}")

    # Set edit path
    mkdocs_gen_files.set_edit_path(full_doc_path, path)

# Generate navigation file
with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
