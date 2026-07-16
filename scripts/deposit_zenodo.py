#!/usr/bin/env python3
"""Reserve Zenodo DOI, inject DOI+GitHub into PDFs, upload, publish.

Workflow
--------
1. Create deposition (prereserves DOI) — needs ZENODO_TOKEN.
2. Write DOI into manuscript front matter + README; rebuild EN/ES PDFs.
3. Package source archive; upload PDFs + sources + package.
4. Publish deposition.

Environment
-----------
  ZENODO_TOKEN   PAT with deposit:write + deposit:actions
                 https://zenodo.org/account/settings/applications/tokens/new/
  ZENODO_BASE    Optional (default https://zenodo.org)

Usage
-----
  export ZENODO_TOKEN=...
  python3 scripts/deposit_zenodo.py                 # full pipeline + publish
  python3 scripts/deposit_zenodo.py --reserve-only  # reserve DOI + rebuild PDFs
  python3 scripts/deposit_zenodo.py --no-publish    # upload, leave as draft
  python3 scripts/deposit_zenodo.py --publish-only
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import zipfile
from datetime import date
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
META_PATH = ROOT / "zenodo" / "metadata.json"
STATE_PATH = ROOT / "zenodo" / "deposition_state.json"
PACKAGE_PATH = ROOT / "zenodo" / "phi3-recd-v0.5.0.zip"
GITHUB = "https://github.com/johelpadilla/phi3-recd"

PDF_EN = ROOT / "Phi3_RECD_Dynamic_Integration_v0.5.pdf"
PDF_ES = ROOT / "Phi3_RECD_Integracion_Dinamica_ES_v0.5.pdf"

# Paths included in the source archive (relative to ROOT)
ZIP_ROOT_FILES = [
    "README.md",
    "LICENSE",
    "pyproject.toml",
    "manuscript.md",
    "manuscript_es.md",
    ".gitignore",
]
ZIP_DIRS = [
    "src",
    "tests",
    "scripts",
    "figures",
    "refs",
    "data",
]


def token_and_base() -> tuple[str, str]:
    tok = os.environ.get("ZENODO_TOKEN", "").strip()
    if not tok:
        for cand in (ROOT / ".zenodo_token", Path.home() / ".zenodo_token"):
            if cand.is_file():
                tok = cand.read_text(encoding="utf-8").strip().splitlines()[0].strip()
                if tok:
                    break
    if not tok:
        # Last resort: most recent export in zsh history (local machine only)
        hist = Path.home() / ".zsh_history"
        if hist.is_file():
            cands: list[str] = []
            for line in hist.read_text(errors="ignore").splitlines():
                if line.startswith(":"):
                    parts = line.split(";", 1)
                    if len(parts) == 2:
                        line = parts[1]
                m = re.search(
                    r"""ZENODO_TOKEN\s*=\s*['\"]?([A-Za-z0-9._\-]{20,})['\"]?""",
                    line,
                )
                if m:
                    cands.append(m.group(1))
            if cands:
                tok = cands[-1]
    if not tok:
        sys.exit(
            "Missing ZENODO_TOKEN.\n"
            "Create one at https://zenodo.org/account/settings/applications/tokens/new/\n"
            "Scopes: deposit:write and deposit:actions\n"
            "Then:  export ZENODO_TOKEN='...'"
        )
    base = os.environ.get("ZENODO_BASE", "https://zenodo.org").rstrip("/")
    return tok, base


def headers(tok: str, json_body: bool = False) -> dict:
    h = {"Authorization": f"Bearer {tok}"}
    if json_body:
        h["Content-Type"] = "application/json"
    return h


def save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {STATE_PATH.relative_to(ROOT)}")


def create_deposition(tok: str, base: str, metadata: dict) -> dict:
    r = requests.post(
        f"{base}/api/deposit/depositions",
        json={},
        headers=headers(tok, json_body=True),
        timeout=60,
    )
    if r.status_code not in (200, 201):
        sys.exit(f"Create deposition failed {r.status_code}: {r.text}")
    dep = r.json()
    dep_id = dep["id"]
    doi = dep["metadata"]["prereserve_doi"]["doi"]
    print(f"Deposition id={dep_id}  reserved DOI={doi}")

    body = {"metadata": metadata}
    r = requests.put(
        f"{base}/api/deposit/depositions/{dep_id}",
        data=json.dumps(body),
        headers=headers(tok, json_body=True),
        timeout=60,
    )
    if r.status_code not in (200, 201):
        sys.exit(f"Put metadata failed {r.status_code}: {r.text}")
    dep = r.json()
    state = {
        "deposition_id": dep_id,
        "doi": doi,
        "doi_url": f"https://doi.org/{doi}",
        "bucket": dep["links"]["bucket"],
        "html": dep["links"]["html"],
        "base": base,
        "created": date.today().isoformat(),
        "github": GITHUB,
    }
    save_state(state)
    return state


def inject_doi_sources(doi: str) -> None:
    """Write DOI + GitHub into manuscript front matter and README citation."""
    doi_url = f"https://doi.org/{doi}"

    # --- English manuscript ---
    en = ROOT / "manuscript.md"
    text = en.read_text(encoding="utf-8")
    meta_lines = (
        f"**Version:** preprint draft v0.5  \n"
        f"**Repository:** [{GITHUB}]({GITHUB})  \n"
        f"**DOI:** [{doi}]({doi_url})  \n"
    )
    # Insert after Keywords line if Version/DOI not present; replace if present
    if re.search(r"(?m)^\*\*(?:Version|DOI|Repository):\*\*", text):
        text = re.sub(
            r"(?ms)(?:^\*\*(?:Version|Versión|Repository|Repositorio|DOI):\*\*[^\n]*\n)+",
            meta_lines,
            text,
            count=1,
        )
    else:
        text = re.sub(
            r"(?m)^(\*\*Keywords:\*\*[^\n]*\n)",
            r"\1" + meta_lines,
            text,
            count=1,
        )
    en.write_text(text, encoding="utf-8")
    print(f"Injected DOI into {en.name}")

    # --- Spanish manuscript ---
    es = ROOT / "manuscript_es.md"
    text = es.read_text(encoding="utf-8")
    meta_es = (
        f"**Versión:** preprint v0.5 (borrador académico)  \n"
        f"**Repositorio:** [{GITHUB}]({GITHUB})  \n"
        f"**DOI:** [{doi}]({doi_url})  \n"
    )
    if re.search(r"(?m)^\*\*(?:Versión|Version|DOI|Repositorio|Repository):\*\*", text):
        text = re.sub(
            r"(?ms)(?:^\*\*(?:Version|Versión|Repository|Repositorio|DOI):\*\*[^\n]*\n)+",
            meta_es,
            text,
            count=1,
        )
    else:
        text = re.sub(
            r"(?m)^(\*\*Palabras clave:\*\*[^\n]*\n)",
            r"\1" + meta_es,
            text,
            count=1,
        )
    es.write_text(text, encoding="utf-8")
    print(f"Injected DOI into {es.name}")

    # --- README citation ---
    readme = ROOT / "README.md"
    rtxt = readme.read_text(encoding="utf-8")
    cite = (
        f"## Citation\n\n"
        f"Padilla-Villanueva, J. (2026). *Integrating Φ₃ (excess³) into RECD Dynamics: "
        f"From Parallel Metric to Structural Clock Contribution* (Preprint draft v0.5). "
        f"Zenodo. https://doi.org/{doi}\n\n"
        f"**DOI:** [{doi}]({doi_url})  \n"
        f"**GitHub:** {GITHUB}\n"
    )
    if "## Citation" in rtxt or "## Recommended citation" in rtxt:
        rtxt = re.sub(
            r"## (?:Recommended )?Citation(?: \(placeholder\))?\n\n.*?(?=\n## |\Z)",
            cite + "\n",
            rtxt,
            count=1,
            flags=re.S,
        )
    elif "## Zenodo" in rtxt:
        rtxt = re.sub(
            r"## Zenodo\n\n.*?(?=\n## |\Z)",
            cite + "\n",
            rtxt,
            count=1,
            flags=re.S,
        )
    else:
        rtxt = rtxt.rstrip() + "\n\n" + cite
    # Badge-like line near top if missing
    if "doi.org/10.5281" not in rtxt.split("\n", 20)[0:15].__str__():
        rtxt = rtxt.replace(
            f"**Repository:** {GITHUB}",
            f"**Repository:** {GITHUB}  \n"
            f"**DOI:** [{doi}]({doi_url})",
            1,
        )
        if f"**DOI:** [{doi}]" not in rtxt:
            rtxt = rtxt.replace(
                f"**Repository:** https://github.com/johelpadilla/phi3-recd",
                f"**Repository:** https://github.com/johelpadilla/phi3-recd  \n"
                f"**DOI:** [{doi}]({doi_url})",
                1,
            )
    readme.write_text(rtxt, encoding="utf-8")
    print("Updated README.md citation")

    # --- CITATION.cff ---
    cff = ROOT / "CITATION.cff"
    cff.write_text(
        "\n".join(
            [
                "cff-version: 1.2.0",
                "message: If you use this preprint or the phi3-recd package, please cite it.",
                'title: "Integrating Φ₃ (excess³) into RECD Dynamics: From Parallel Metric to Structural Clock Contribution"',
                "authors:",
                "  - family-names: Padilla-Villanueva",
                "    given-names: Johel",
                "    orcid: https://orcid.org/0000-0002-5797-6931",
                "    affiliation: Department of Environmental Health, University of Puerto Rico — Medical Sciences Campus",
                "type: article",
                "version: 0.5.0",
                f'doi: "{doi}"',
                f'url: "{doi_url}"',
                f'repository-code: "{GITHUB}"',
                "date-released: 2026-07-16",
                "license: CC-BY-4.0",
                "keywords:",
                "  - Systemic Tau",
                "  - RECD",
                "  - excess3",
                "  - Phi3",
                "  - early warning",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print("Wrote CITATION.cff")


def rebuild_pdfs() -> None:
    for lang in ("en", "es"):
        print(f"Building PDF lang={lang} ...")
        r = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "build_pdf.py"), "--lang", lang],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        sys.stdout.write(r.stdout or "")
        if r.returncode not in (0, 2):  # 2 = soft warnings (overfull)
            sys.stderr.write(r.stderr or "")
            sys.exit(f"build_pdf.py --lang {lang} failed rc={r.returncode}")
        if r.returncode == 2:
            print(f"(soft warnings on {lang}; continuing)")
    # Verify DOI and GitHub appear in PDF text layer
    for pdf in (PDF_EN, PDF_ES):
        if not pdf.exists():
            sys.exit(f"missing {pdf.name}")
        t = subprocess.run(
            ["pdftotext", "-f", "1", "-l", "1", "-layout", str(pdf), "-"],
            capture_output=True,
            text=True,
        )
        page1 = t.stdout or ""
        if "github.com/johelpadilla/phi3-recd" not in page1 and "phi3-recd" not in page1:
            sys.exit(f"GitHub URL not found on page 1 of {pdf.name}")
        if "10.5281/zenodo." not in page1:
            sys.exit(f"Zenodo DOI not found on page 1 of {pdf.name}")
        print(f"OK cover identifiers in {pdf.name}")


def make_package() -> Path:
    PACKAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if PACKAGE_PATH.exists():
        PACKAGE_PATH.unlink()
    skip_suffix = {
        ".pyc",
        ".pyo",
        ".aux",
        ".log",
        ".out",
        ".toc",
        ".synctex.gz",
    }
    skip_names = {".DS_Store", "__pycache__", ".pytest_cache", "phi3_recd.egg-info"}
    with zipfile.ZipFile(PACKAGE_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name in ZIP_ROOT_FILES:
            p = ROOT / name
            if p.exists():
                zf.write(p, arcname=name)
        if (ROOT / "CITATION.cff").exists():
            zf.write(ROOT / "CITATION.cff", arcname="CITATION.cff")
        for d in ZIP_DIRS:
            base = ROOT / d
            if not base.exists():
                continue
            for path in base.rglob("*"):
                if path.is_dir():
                    continue
                if path.suffix in skip_suffix:
                    continue
                if any(part in skip_names for part in path.parts):
                    continue
                if path.name.endswith(".egg-info"):
                    continue
                zf.write(path, arcname=str(path.relative_to(ROOT)))
    print(f"Package {PACKAGE_PATH.name} ({PACKAGE_PATH.stat().st_size // 1024} KB)")
    return PACKAGE_PATH


def upload_files(tok: str, base: str, state: dict) -> None:
    bucket = state["bucket"]
    dep_id = state["deposition_id"]
    files = [
        PDF_EN,
        PDF_ES,
        ROOT / "manuscript.md",
        ROOT / "manuscript_es.md",
        PACKAGE_PATH,
        ROOT / "CITATION.cff",
        ROOT / "README.md",
        ROOT / "LICENSE",
    ]
    for path in files:
        if not path.exists():
            sys.exit(f"Missing upload file: {path}")
        url = f"{bucket}/{path.name}"
        print(f"Uploading {path.name} ({path.stat().st_size // 1024} KB) ...")
        with path.open("rb") as fp:
            r = requests.put(url, data=fp, headers=headers(tok), timeout=600)
        if r.status_code not in (200, 201):
            sys.exit(f"Upload failed for {path.name}: {r.status_code} {r.text[:500]}")
    r = requests.get(
        f"{base}/api/deposit/depositions/{dep_id}",
        headers=headers(tok),
        timeout=60,
    )
    r.raise_for_status()
    state["files"] = [f["filename"] for f in r.json().get("files", [])]
    save_state(state)
    print("Uploaded files:", ", ".join(state["files"]))


def publish(tok: str, base: str, dep_id: int) -> dict:
    r = requests.post(
        f"{base}/api/deposit/depositions/{dep_id}/actions/publish",
        headers=headers(tok),
        timeout=120,
    )
    if r.status_code not in (200, 201, 202):
        sys.exit(f"Publish failed {r.status_code}: {r.text}")
    dep = r.json()
    doi = dep.get("doi") or dep.get("metadata", {}).get("doi")
    print("PUBLISHED")
    print("  DOI:", doi)
    print(
        "  record:",
        dep.get("links", {}).get("record_html")
        or dep.get("links", {}).get("latest_html")
        or dep.get("links", {}).get("html"),
    )
    state = json.loads(STATE_PATH.read_text(encoding="utf-8")) if STATE_PATH.exists() else {}
    state.update(
        {
            "deposition_id": dep_id,
            "doi": doi,
            "doi_url": f"https://doi.org/{doi}" if doi else state.get("doi_url"),
            "published": date.today().isoformat(),
            "record_html": dep.get("links", {}).get("record_html")
            or dep.get("links", {}).get("html"),
            "files": [f["filename"] for f in dep.get("files", [])],
        }
    )
    save_state(state)
    return dep


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--reserve-only", action="store_true")
    ap.add_argument("--upload-only", action="store_true")
    ap.add_argument("--publish-only", action="store_true")
    ap.add_argument("--no-publish", action="store_true")
    ap.add_argument("--deposition-id", type=int)
    args = ap.parse_args()

    if args.publish_only:
        tok, base = token_and_base()
        dep_id = args.deposition_id
        if not dep_id and STATE_PATH.exists():
            dep_id = json.loads(STATE_PATH.read_text())["deposition_id"]
        if not dep_id:
            sys.exit("Need --deposition-id or deposition_state.json")
        publish(tok, base, dep_id)
        return

    if args.upload_only:
        tok, base = token_and_base()
        state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        if args.deposition_id:
            state["deposition_id"] = args.deposition_id
        # refresh bucket
        r = requests.get(
            f"{base}/api/deposit/depositions/{state['deposition_id']}",
            headers=headers(tok),
            timeout=60,
        )
        r.raise_for_status()
        state["bucket"] = r.json()["links"]["bucket"]
        make_package()
        upload_files(tok, base, state)
        if not args.no_publish:
            publish(tok, base, state["deposition_id"])
        return

    metadata = json.loads(META_PATH.read_text(encoding="utf-8"))
    tok, base = token_and_base()

    if STATE_PATH.exists() and not args.reserve_only:
        # Resume existing draft if present and unpublished
        prev = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        if prev.get("doi") and prev.get("deposition_id") and not prev.get("published"):
            print(f"Resuming draft deposition {prev['deposition_id']} DOI={prev['doi']}")
            state = prev
            # refresh bucket
            r = requests.get(
                f"{base}/api/deposit/depositions/{state['deposition_id']}",
                headers=headers(tok),
                timeout=60,
            )
            if r.status_code == 200:
                state["bucket"] = r.json()["links"]["bucket"]
                save_state(state)
            else:
                state = create_deposition(tok, base, metadata)
        else:
            state = create_deposition(tok, base, metadata)
    else:
        state = create_deposition(tok, base, metadata)

    doi = state["doi"]
    inject_doi_sources(doi)
    rebuild_pdfs()
    make_package()

    if args.reserve_only:
        print("Reserved DOI and rebuilt PDFs. Review, then re-run without --reserve-only.")
        print(f"  DOI: {doi}")
        print(f"  draft: {state.get('html')}")
        return

    upload_files(tok, base, state)
    if args.no_publish:
        print(f"Draft ready (not published): {state.get('html')}")
        print(f"DOI (prereserved): {doi}")
        return

    publish(tok, base, state["deposition_id"])


if __name__ == "__main__":
    main()
