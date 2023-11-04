"""Generate the code reference pages and navigation.

From https://mkdocstrings.github.io/recipes/
"""

from pathlib import Path

import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()

for path in sorted(Path("nowplaying").rglob("*.py")):
    module_path = path.relative_to("nowplaying").with_suffix("")
    doc_path = path.relative_to("nowplaying").with_suffix(".md")
    full_doc_path = Path("reference", doc_path)

    parts = list(module_path.parts)

    if parts[-1] == "__init__":
        continue
    elif parts[-1] == "__main__":
        continue

    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        identifier = ".".join(parts)
        print("::: " + identifier, file=fd)

    mkdocs_gen_files.set_edit_path(full_doc_path, path)  #

with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())

readme = Path("README.md").open("r")
with mkdocs_gen_files.open("index.md", "w") as index_file:
    index_file.writelines(readme.read())
