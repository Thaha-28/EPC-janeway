"""Build EPC theme assets into the static folder.

Copies plain CSS/images (no SCSS toolchain needed) so the theme stays
self-contained. Runs automatically via `manage.py build_assets`, which is
invoked by docker-entrypoint.sh before collectstatic.
"""

import os
import shutil


def copy_tree(src_path, dest_path):
    if not os.path.isdir(src_path):
        return
    os.makedirs(dest_path, exist_ok=True)
    for file_name in os.listdir(src_path):
        full_src = os.path.join(src_path, file_name)
        full_dest = os.path.join(dest_path, file_name)
        if os.path.isfile(full_src):
            shutil.copy2(full_src, full_dest)
        else:
            if os.path.exists(full_dest):
                shutil.rmtree(full_dest)
            shutil.copytree(full_src, full_dest)


def build():
    try:
        from django.conf import settings
    except ImportError:
        return
    theme_assets = os.path.join(settings.BASE_DIR, "themes", "epc", "assets")
    static_epc = os.path.join(settings.BASE_DIR, "static", "epc")
    copy_tree(os.path.join(theme_assets, "css"), os.path.join(static_epc, "css"))
    copy_tree(os.path.join(theme_assets, "img"), os.path.join(static_epc, "img"))
    print("EPC theme assets installed.")
