import os
import re
import time
import requests

API_KEY = os.environ["PEPY_API_KEY"]

PACKAGES = [
    {"pypi": "django-octo", "repo": "django_octo", "dp_slug": "django_octo", "docs_path": ""},
    {"pypi": "django-octo-seo", "repo": "django_octo_seo", "dp_slug": "django_octo_seo", "docs_path": "seo/"},
    {"pypi": "django-octo-security", "repo": "django_octo_security", "dp_slug": "django_octo_security", "docs_path": "security/"},
    {"pypi": "django-octo-aurora", "repo": "django_octo_aurora", "dp_slug": "django_octo_aurora", "docs_path": "aurora/"},
    {"pypi": "django-octo-uml", "repo": "django_octo_uml", "dp_slug": "django_octo_uml", "docs_path": "uml/"},
    {"pypi": "django-octo-qa", "repo": "django_octo_qa", "dp_slug": "django_octo_qa", "docs_path": "qa/"},
]

GITHUB_USER = "jeanpmodev"
API_BASE = "".join(["https:", "//", "api.", "pepy.", "tech/", "api/", "v2/", "projects/"])
WEB_BASE = "".join(["https:", "//", "pepy.", "tech/", "projects/"])
GH_BASE = "".join(["https:", "//", "github.", "com/", GITHUB_USER, "/"])
DP_BASE = "".join(["https:", "//", "djangopackages.", "org/", "packages/", "p/"])
DOCS_BASE = "https://django-octo.readthedocs.io/en/latest/"


def get_dp_score(slug):
    url = f"{DP_BASE}{slug}/rules/"
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        if res.status_code == 200:
            match = re.search(r"Package Score:\s*(\d+)", res.text)
            if match:
                return match.group(1)
    except requests.RequestException:
        pass
    return "N/A"


headers = {"X-API-Key": API_KEY}
rows = []
total_downloads = 0

for pkg in PACKAGES:
    pypi_name = pkg["pypi"]
    repo_name = pkg["repo"]
    dp_slug = pkg["dp_slug"]
    docs_path = pkg["docs_path"]
    url = API_BASE + pypi_name

    resp = requests.get(url, headers=headers, timeout=15)

    if resp.status_code == 200:
        data = resp.json()
        downloads = data.get("total_downloads", 0)
        versions = data.get("versions", [])
        latest_version = versions[-1] if versions else "N/A"
    elif resp.status_code == 404:
        downloads = 0
        latest_version = "N/A"
    else:
        resp.raise_for_status()

    score = get_dp_score(dp_slug)
    total_downloads += downloads
    downloads_fmt = f"{downloads:,}"

    repo_link = f"[{pypi_name}]({GH_BASE}{repo_name})"
    pepy_link = f"[{downloads_fmt}]({WEB_BASE}{pypi_name})"
    dp_link = f"[{score}]({DP_BASE}{dp_slug}/)"
    docs_link = f"[Read the Docs ↗]({DOCS_BASE}{docs_path})"

    rows.append(f"| {repo_link} | `{latest_version}` | {pepy_link} | {dp_link} | {docs_link} |")

    time.sleep(15)

total_fmt = f"{total_downloads:,}"

table = [
    "| Package | Latest Version | Total Downloads | Django Packages Score | Documentation |",
    "| :--- | :---: | ---: | :---: | :---: |",
    *rows,
    f"| **Ecosystem Total** | — | **{total_fmt}** | — | **[Full Hub ↗]({DOCS_BASE})** |",
]

new_content = "\n".join(table)

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

pattern = r"(<!-- START_STATS -->).*?(<!-- END_STATS -->)"
updated_readme = re.sub(
    pattern,
    rf"\1\n{new_content}\n\2",
    readme,
    flags=re.DOTALL,
)

with open("README.md", "w", encoding="utf-8") as f:
    f.write(updated_readme)
