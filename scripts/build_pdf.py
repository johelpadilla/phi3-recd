#!/usr/bin/env python3
"""Build a publication-clean PDF from manuscript.md.

Root guarantees (fail the build if violated):
- Title page: keywords only (no internal status notes)
- Abstract: single LaTeX abstract environment (not a numbered section)
- Figures: explicit final-mode \\includegraphics (no pandocbounded wrappers)
- No export/scaffold strings in the PDF byte stream
- N embedded raster images matching the figure list

Usage (project root):
  python3 scripts/build_pdf.py
"""
from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "zenodo" / "deposition_state.json"
GITHUB_URL = "https://github.com/johelpadilla/phi3-recd"
GITHUB_SHORT = "github.com/johelpadilla/phi3-recd"
# Defaults (English); overridden by configure_language()
LANG = "en"
MANUSCRIPT = ROOT / "manuscript.md"
OUT_PDF = ROOT / "Phi3_RECD_Dynamic_Integration_v0.5.pdf"
OUT_PDF_ALIAS = ROOT / "Phi3_RECD_Dynamic_Integration_v0.5.1.pdf"
BUILD_DIR = ROOT / "build" / "pdf"
LOG_PATH = BUILD_DIR / "build.log"
VERIFY_PATH = ROOT / "PDF_VERIFY.txt"
ABSTRACT_HEADING = "Abstract"
APPENDIX_D_HEADING = "Appendix D --- Figures"
ABSTRACT_SIGNATURE = "identify critical transitions through ordinal relational reorganization"
META_TITLE = "Integrating Phi3 (excess3) into RECD Dynamics"
META_SUBJECT = "Phi3 excess3 RECD dynamics integration July 2026"
META_KEYWORDS = "Systemic Tau, RECD, excess3, ordinal synergy, early warning"
# Filled by load_deposit_ids() — Zenodo prereserved DOI + GitHub
DOI = ""
DOI_URL = ""

# Strings that must never appear in the produced PDF (bytes or text layer).
BANNED_PDF_STRINGS = (
    "mediaimage",
    "screenshot.jpeg",
    "screenshot.jpg",
    "REMAINING",
    "synthetic comparison only",
    "Default construction: P1",
    "Synthetic validation (S0",
    "TODO",
    "FIXME",
    "Reader's guide",
    "Strategic contrast",
)

PANDOC_CANDIDATES = [
    Path("/usr/local/Cellar/pandoc/3.10/bin/pandoc"),
    Path("/opt/homebrew/bin/pandoc"),
    Path("/usr/local/bin/pandoc"),
    Path(shutil.which("pandoc") or ""),
]

# Appendix D page groups: compact bar charts share a page; tall/wide panels stay alone.
# Each entry is a page: list of (filename, caption, max height as fraction of textheight).
FIG_PAGES: list[list[tuple[str, str, float]]] = [
    [
        ("fig_S0_S1_S2_overview.png", "Synthetic S0--S2 overview", 0.78),
    ],
    [
        ("fig_A3_rates.png", r"$A_3$ rates (synthetic)", 0.38),
        ("fig_T_final.png", r"$T_{\mathrm{final}}$ (synthetic)", 0.38),
    ],
    [
        ("fig_noise_robustness.png", "Noise robustness", 0.55),
    ],
    [
        (
            "fig_smoke_sddb_events.png",
            r"Holter (SDDB): pre-event series under Proposal 1 (Section 6.4)",
            0.78,
        ),
    ],
    [
        (
            "fig_smoke_sddb_bars.png",
            r"Holter: activation rates and lead (Section 6.4)",
            0.38,
        ),
        (
            "fig_smoke_far.png",
            r"Holter: FAR proxy, events vs NSRDB controls (Section 6.4)",
            0.38,
        ),
    ],
    [
        (
            "fig_smoke_dengai_events.png",
            r"DengAI: pre-outbreak series under Proposal 1 (Section 6.4)",
            0.78,
        ),
    ],
    [
        (
            "fig_smoke_dengai_bars.png",
            r"DengAI: $\Delta T$ vs chaos-band occupancy (Section 6.4)",
            0.38,
        ),
        (
            "fig_smoke_dengai_far.png",
            r"DengAI: lead vs FAR (Section 6.4)",
            0.38,
        ),
    ],
]
FIGS = [(fn, cap) for page in FIG_PAGES for fn, cap, _ in page]

# Prefer \ensuremath so symbols work in tables/text without $ escaping by pandoc
SYM = {
    "≈": r"\ensuremath{\approx}",
    "→": r"\ensuremath{\to}",
    "↔": r"\ensuremath{\leftrightarrow}",
    "⇒": r"\ensuremath{\Rightarrow}",
    "≥": r"\ensuremath{\ge}",
    "≤": r"\ensuremath{\le}",
    "≪": r"\ensuremath{\ll}",
    "⊂": r"\ensuremath{\subset}",
    "≡": r"\ensuremath{\equiv}",
    "∩": r"\ensuremath{\cap}",
    "≠": r"\ensuremath{\ne}",
    "·": r"{\textperiodcentered}",
    "×": r"\ensuremath{\times}",
    "±": r"\ensuremath{\pm}",
    "∞": r"\ensuremath{\infty}",
    "−": r"\ensuremath{-}",  # unicode minus
    "–": r"--",
    "—": r"---",
    "…": r"...",
    "†": r"\ensuremath{\dagger}",
    "′": r"\ensuremath{\prime}",
    "§": r"\S{}",
    "α": r"\ensuremath{\alpha}",
    "β": r"\ensuremath{\beta}",
    "⋅": r"{\textperiodcentered}",
}

COMPOUND = [
    ("excess³", r"excess\ensuremath{^{3}}"),
    ("Φ₃", r"\ensuremath{\Phi_{3}}"),
    ("Φ₁", r"\ensuremath{\Phi_{1}}"),
    ("Φ₂", r"\ensuremath{\Phi_{2}}"),
    ("A₃", r"\ensuremath{A_{3}}"),
    ("e³", r"\ensuremath{e^{3}}"),
    ("Γ₃", r"\ensuremath{\Gamma_{3}}"),
    ("ΔT", r"\ensuremath{\Delta T}"),
    ("τ_s", r"\ensuremath{\tau_{s}}"),
    ("τₛ", r"\ensuremath{\tau_{s}}"),
]

META_AUTHOR = "Johel Padilla-Villanueva"

FIG_PAGES_ES: list[list[tuple[str, str, float]]] = [
    [
        ("fig_S0_S1_S2_overview.png", "Vista sint\\'etica S0--S2", 0.78),
    ],
    [
        ("fig_A3_rates.png", r"Tasas de $A_3$ (sint\'etico)", 0.38),
        ("fig_T_final.png", r"$T_{\mathrm{final}}$ (sint\'etico)", 0.38),
    ],
    [
        ("fig_noise_robustness.png", "Robustez al ruido", 0.55),
    ],
    [
        (
            "fig_smoke_sddb_events.png",
            r"Holter (SDDB): series pre-evento bajo Propuesta 1 (Secci\'on 6.4)",
            0.78,
        ),
    ],
    [
        (
            "fig_smoke_sddb_bars.png",
            r"Holter: tasas de activaci\'on y anticipaci\'on (Secci\'on 6.4)",
            0.38,
        ),
        (
            "fig_smoke_far.png",
            r"Holter: proxy FAR, eventos vs controles NSRDB (Secci\'on 6.4)",
            0.38,
        ),
    ],
    [
        (
            "fig_smoke_dengai_events.png",
            r"DengAI: series pre-brote bajo Propuesta 1 (Secci\'on 6.4)",
            0.78,
        ),
    ],
    [
        (
            "fig_smoke_dengai_bars.png",
            r"DengAI: $\Delta T$ vs ocupaci\'on de la banda de caos (Secci\'on 6.4)",
            0.38,
        ),
        (
            "fig_smoke_dengai_far.png",
            r"DengAI: anticipaci\'on vs FAR (Secci\'on 6.4)",
            0.38,
        ),
    ],
]


def load_deposit_ids() -> tuple[str, str]:
    """Load Zenodo DOI from deposition_state.json or env (empty if not yet reserved)."""
    import os

    doi = (os.environ.get("ZENODO_DOI") or "").strip()
    if not doi and STATE_PATH.is_file():
        try:
            import json

            st = json.loads(STATE_PATH.read_text(encoding="utf-8"))
            doi = (st.get("doi") or "").strip()
        except Exception:
            doi = ""
    doi_url = f"https://doi.org/{doi}" if doi else ""
    return doi, doi_url


def _ident_block_tex() -> str:
    """Repository + DOI lines on the title page (and PDF hyperlinks)."""
    load = load_deposit_ids()
    doi, doi_url = load
    # Always print GitHub; DOI only when reserved (so local drafts stay clean).
    if LANG == "es":
        repo_lab, doi_lab, ver_lab = "Repositorio", "DOI", "Versi\\'on"
        ver = "preprint v0.5 (borrador acad\\'emico)"
    else:
        repo_lab, doi_lab, ver_lab = "Repository", "DOI", "Version"
        ver = "preprint draft v0.5"
    lines = [
        rf"{ver_lab}: {ver}\\[0.12em]",
        rf"{repo_lab}: \href{{{GITHUB_URL}}}{{{GITHUB_SHORT}}}\\[0.12em]",
    ]
    if doi:
        lines.append(rf"{doi_lab}: \href{{{doi_url}}}{{{doi}}}")
    else:
        lines.append(rf"{doi_lab}: \textit{{(Zenodo DOI upon deposit)}}")
    return "\n    ".join(lines)


def _header_tex() -> str:
    """Language-aware academic title page + shared LaTeX preamble."""
    ident = _ident_block_tex()
    if LANG == "es":
        series = r"M\'etodos y teor\'ia"
        date = r"julio de 2026"
        title_block = r"""{\color{ink}\LARGE\bfseries%
    Integraci\'on de $\Phi_3$ (excess$^{3}$)\\[0.28em]
    en la din\'amica RECD\par}
  \vspace{0.48cm}
  {\color{ink}\large De m\'etrica paralela a\\[0.08em]
    contribuci\'on estructural del reloj\par}"""
        affil = r"""{\color{muted}\normalsize
    Departamento de Salud Ambiental\\[0.08em]
    Universidad de Puerto Rico --- Recinto de Ciencias M\'edicas\par}"""
        kw_label = r"\textit{Palabras clave.}"
        kws = r"""Tau Sist\'emico \textperiodcentered\
        RECD \textperiodcentered\
        excess$^{3}$ \textperiodcentered\
        sinergia ordinal \textperiodcentered\
        alerta temprana \textperiodcentered\
        universalidad de Feigenbaum \textperiodcentered\
        conjunciones anidadas"""
        pdftitle = "Integracion de Phi3 (excess3) en la dinamica RECD"
        pdfsubject = "Phi3 excess3 RECD integracion dinamica julio 2026"
        pdfkw = "Tau Sistemico, RECD, excess3, sinergia ordinal, alerta temprana"
        es_names = r"""
\renewcommand{\contentsname}{\'Indice}
\renewcommand{\abstractname}{Resumen}
\renewcommand{\refname}{Referencias}
\renewcommand{\figurename}{Figura}
\renewcommand{\tablename}{Tabla}
\renewcommand{\appendixname}{Ap\'endice}
"""
    else:
        series = r"Methods \& theory"
        date = "July 2026"
        title_block = r"""{\color{ink}\LARGE\bfseries%
    Integrating $\Phi_3$ (excess$^{3}$)\\[0.28em]
    into RECD Dynamics\par}
  \vspace{0.48cm}
  {\color{ink}\large From Parallel Metric to\\[0.08em]
    Structural Clock Contribution\par}"""
        affil = r"""{\color{muted}\normalsize
    Department of Environmental Health\\[0.08em]
    University of Puerto Rico --- Medical Sciences Campus\par}"""
        kw_label = r"\textit{Keywords.}"
        kws = r"""Systemic Tau \textperiodcentered\
        RECD \textperiodcentered\
        excess$^{3}$ \textperiodcentered\
        ordinal synergy \textperiodcentered\
        early warning \textperiodcentered\
        Feigenbaum universality \textperiodcentered\
        nested conjunctions"""
        pdftitle = META_TITLE
        pdfsubject = META_SUBJECT
        pdfkw = META_KEYWORDS
        es_names = ""

    return rf"""
% final (never draft boxes / filename placeholders for missing art)
\usepackage[final]{{graphicx}}
\setkeys{{Gin}}{{draft=false}}
\usepackage{{microtype}}
\usepackage{{etoolbox}}
\usepackage{{float}}
\usepackage{{xcolor}}
\usepackage{{array}}
\usepackage{{tabularx}}
{es_names}

% --- brand palette (quiet academic) ---
\definecolor{{ink}}{{HTML}}{{1B2A4A}}
\definecolor{{accent}}{{HTML}}{{2C5F8A}}
\definecolor{{soft}}{{HTML}}{{E8EEF4}}
\definecolor{{muted}}{{HTML}}{{5A6577}}
% --- layout robustness ---
\sloppy
\emergencystretch=3em
\tolerance=3000
\hbadness=10000
\vbadness=10000
\hfuzz=1.5pt
\vfuzz=1.5pt
\newcommand{{\fittable}}[1]{{%
  \begingroup
  \hfuzz=\maxdimen\hbadness=10000
  \sbox0{{#1}}%
  \ifdim\wd0>\textwidth
    \resizebox{{\textwidth}}{{!}}{{\usebox0}}%
  \else
    \usebox0
  \fi
  \endgroup
}}
\AtBeginEnvironment{{tabular}}{{\setlength{{\tabcolsep}}{{3.5pt}}}}
\AtBeginEnvironment{{longtable}}{{\footnotesize\setlength{{\tabcolsep}}{{3.5pt}}}}
\makeatletter
\renewcommand{{\@tocrmarg}}{{2.55em}}
\renewcommand{{\@pnumwidth}}{{1.9em}}
\renewcommand{{\@dotsep}}{{1.8}}
\renewcommand*\l@section{{\@dottedtocline{{1}}{{0em}}{{1.4em}}}}
\renewcommand*\l@subsection{{\@dottedtocline{{2}}{{1.5em}}{{2.0em}}}}
\makeatother
\AtBeginDocument{{%
  \hypersetup{{%
    pdftitle={{{pdftitle}}},%
    pdfauthor={{Johel Padilla-Villanueva}},%
    pdfsubject={{{pdfsubject}}},%
    pdfkeywords={{{pdfkw}}},%
    pdfcreator={{pandoc+xelatex}},%
    pdfproducer={{xelatex}},%
    colorlinks=false,%
    hidelinks,%
    bookmarksnumbered=false,%
    bookmarksopen=true,%
    pdfdisplaydoctitle=true%
  }}%
}}
\renewcommand{{\maketitle}}{{%
  \begin{{titlepage}}%
  \thispagestyle{{empty}}%
  \centering
  \vspace*{{-0.4cm}}
  {{\color{{ink}}\rule{{\textwidth}}{{2.0pt}}}}\par
  \vspace{{0.18cm}}
  {{\color{{accent}}\rule{{\textwidth}}{{0.55pt}}}}\par
  \vspace{{0.85cm}}
  {{\color{{muted}}\scshape\large {series}}}\par
  \vspace{{0.22cm}}
  {{\color{{ink}}\large {date}}}\par
  \vspace{{0.55cm}}
  {{\color{{accent}}$\Phi_1 \;\to\; \Phi_2 \;\to\; \Phi_3$%
    \ \textcolor{{muted}}{{\textperiodcentered}}\ excess$^{{3}}$%
    \ \textcolor{{muted}}{{\textperiodcentered}}\ RECD\par}}
  \vspace{{0.7cm}}
  {{\color{{ink}}\rule{{0.38\textwidth}}{{0.4pt}}}}\par
  \vspace{{0.7cm}}
  {title_block}
  \vspace{{0.65cm}}
  {{\color{{accent}}\rule{{0.16\textwidth}}{{1.8pt}}}}\par
  \vspace{{0.7cm}}
  {{\color{{ink}}\large\bfseries Johel Padilla-Villanueva\par}}
  \vspace{{0.28cm}}
  {affil}
  \vspace{{0.38cm}}
  {{\small
    ORCID:
    \href{{https://orcid.org/0000-0002-5797-6931}}{{0000-0002-5797-6931}}\\[0.12em]
    \texttt{{joel.padilla2@upr.edu}}
    \textperiodcentered\
    \texttt{{johelpadilla@gmail.com}}\\[0.28em]
    {ident}\par}}
  \vspace{{0.85cm}}
  \noindent
  \colorbox{{soft}}{{%
    \begin{{minipage}}{{0.94\textwidth}}
      \centering
      \vspace{{0.55em}}
      {{\footnotesize\color{{ink}}{kw_label}
        {kws}\par}}
      \vspace{{0.55em}}
    \end{{minipage}}%
  }}\par
  \vfill
  {{\color{{accent}}\rule{{\textwidth}}{{0.55pt}}}}\par
  \vspace{{0.14cm}}
  {{\color{{ink}}\rule{{\textwidth}}{{2.0pt}}}}\par
  \end{{titlepage}}%
  \setcounter{{page}}{{1}}%
}}
"""


HEADER_TEX = ""  # set in configure_language()


def configure_language(lang: str) -> None:
    """Select English or Spanish manuscript, figures, and outputs."""
    global LANG, MANUSCRIPT, OUT_PDF, OUT_PDF_ALIAS, BUILD_DIR, LOG_PATH
    global VERIFY_PATH, FIG_PAGES, FIGS, HEADER_TEX
    global ABSTRACT_HEADING, APPENDIX_D_HEADING, ABSTRACT_SIGNATURE
    global META_TITLE, META_SUBJECT, META_KEYWORDS

    lang = lang.lower().strip()
    if lang not in {"en", "es"}:
        raise SystemExit(f"unsupported language: {lang!r} (use en|es)")
    LANG = lang
    if lang == "es":
        MANUSCRIPT = ROOT / "manuscript_es.md"
        OUT_PDF = ROOT / "Phi3_RECD_Integracion_Dinamica_ES_v0.5.pdf"
        OUT_PDF_ALIAS = ROOT / "Phi3_RECD_Integracion_Dinamica_ES_v0.5.1.pdf"
        BUILD_DIR = ROOT / "build" / "pdf_es"
        LOG_PATH = BUILD_DIR / "build.log"
        VERIFY_PATH = ROOT / "PDF_VERIFY_ES.txt"
        FIG_PAGES = FIG_PAGES_ES
        FIGS = [(fn, cap) for page in FIG_PAGES for fn, cap, _ in page]
        ABSTRACT_HEADING = "Resumen"
        APPENDIX_D_HEADING = r"Ap\'endice D --- Figuras"
        ABSTRACT_SIGNATURE = (
            "identifica transiciones críticas mediante reorganización relacional ordinal"
        )
        # Accent-insensitive signature fallback checked later in verify
        META_TITLE = "Integracion de Phi3 (excess3) en la dinamica RECD"
        META_SUBJECT = "Phi3 excess3 RECD integracion dinamica julio 2026"
        META_KEYWORDS = "Tau Sistemico, RECD, excess3, sinergia ordinal, alerta temprana"
    else:
        MANUSCRIPT = ROOT / "manuscript.md"
        OUT_PDF = ROOT / "Phi3_RECD_Dynamic_Integration_v0.5.pdf"
        OUT_PDF_ALIAS = ROOT / "Phi3_RECD_Dynamic_Integration_v0.5.1.pdf"
        BUILD_DIR = ROOT / "build" / "pdf"
        LOG_PATH = BUILD_DIR / "build.log"
        VERIFY_PATH = ROOT / "PDF_VERIFY.txt"
        # FIG_PAGES already English default
        FIGS = [(fn, cap) for page in FIG_PAGES for fn, cap, _ in page]
        ABSTRACT_HEADING = "Abstract"
        APPENDIX_D_HEADING = "Appendix D --- Figures"
        ABSTRACT_SIGNATURE = (
            "identify critical transitions through ordinal relational reorganization"
        )
        META_TITLE = "Integrating Phi3 (excess3) into RECD Dynamics"
        META_SUBJECT = "Phi3 excess3 RECD dynamics integration July 2026"
        META_KEYWORDS = "Systemic Tau, RECD, excess3, ordinal synergy, early warning"
    HEADER_TEX = _header_tex()


def find_pandoc() -> Path:
    for p in PANDOC_CANDIDATES:
        if p and p.is_file():
            return p
    sys.exit("pandoc not found")


def replace_tag_balanced(text: str) -> str:
    out: list[str] = []
    i = 0
    needle = r"\tag{"
    while True:
        k = text.find(needle, i)
        if k < 0:
            out.append(text[i:])
            break
        out.append(text[i:k])
        j = k + len(needle)
        depth = 1
        start = j
        while j < len(text) and depth:
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
            j += 1
        inner = text[start : j - 1]
        out.append(r"\qquad\mathrm{(" + inner + ")}")
        i = j
    return "".join(out)


def sanitize_outside_math(text: str) -> str:
    parts = re.split(r"(\\\(.+?\\\)|\\\[.+?\\\]|\$\$.+?\$\$|\$[^$\n]+\$)", text, flags=re.S)
    for n, part in enumerate(parts):
        if n % 2 == 1:
            part = part.replace("−", "-")
            parts[n] = part
            continue
        for a, b in COMPOUND:
            part = part.replace(a, b)
        for a, b in SYM.items():
            part = part.replace(a, b)
        for dig, sup in zip("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹"):
            part = part.replace(sup, f"\\ensuremath{{^{dig}}}")
        for dig, sub in zip("0123456789", "₀₁₂₃₄₅₆₇₈₉"):
            part = part.replace(sub, f"\\ensuremath{{_{dig}}}")
        parts[n] = part
    return "".join(parts)


def strip_front_meta(text: str) -> str:
    """Drop Author/Affiliation/.../Keywords block that belongs on the cover only."""
    # Remove meta lines that start with **Label:** near the top (EN + ES)
    text = re.sub(
        r"(?ms)\A(?:\s*\*\*(?:Author|Autor|Affiliation|Afiliaci[oó]n|ORCID|Contact|Contacto|Version|Versi[oó]n|Type|Date|Fecha|Keywords|Palabras clave|Repository|Repositorio|DOI):\*\*[^\n]*\n)+",
        "",
        text,
    )
    # residual blank lines / horizontal rules before first heading
    text = re.sub(r"(?m)^---\s*$", "", text)
    text = re.sub(r"\A\s+", "", text)
    return text


def appendix_figures_latex() -> str:
    """Explicit final-mode figures; pack compact panels two-per-page where useful."""
    missing = [fn for fn, _ in FIGS if not (ROOT / "figures" / fn).exists()]
    if missing:
        sys.exit(f"missing figure files: {missing}")
    parts = [
        r"\clearpage",
        rf"\section{{{APPENDIX_D_HEADING}}}\label{{appendix-d-figures}}",
        r"% figures injected by scripts/build_pdf.py -- packed pages, final includegraphics",
    ]
    for page in FIG_PAGES:
        page_blocks: list[str] = []
        for i, (fn, cap, hfrac) in enumerate(page):
            # slight gap between stacked figures on the same page
            gap = r"\vspace{0.9em}" if i > 0 else ""
            page_blocks.append(
                "\n".join(
                    [
                        gap,
                        r"\begin{figure}[H]",
                        r"\centering",
                        (
                            r"\includegraphics"
                            rf"[width=\linewidth,height={hfrac:.2f}\textheight,keepaspectratio]"
                            rf"{{figures/{fn}}}"
                        ),
                        rf"\caption{{{cap}}}",
                        r"\end{figure}",
                    ]
                ).strip()
            )
        parts.append("\n".join(page_blocks) + "\n" + r"\clearpage")
    return "\n\n" + "\n\n".join(parts) + "\n"


def preprocess_md(md: str) -> str:
    text = replace_tag_balanced(md)
    # drop H1; title comes from custom titlepage
    text = re.sub(r"^# .+\n+", "", text, count=1)
    text = strip_front_meta(text)
    text = re.sub(r"(?m)^---\s*$", "", text)
    text = sanitize_outside_math(text)
    # Figures are injected in postprocess_tex as pure LaTeX (root path).
    return text


def _count_columns(colspec: str) -> int:
    """Count columns in a pandoc/LaTeX colspec (handles ll, p{...}, >{...})."""
    s = colspec
    # strip @{...} and >{...}/<{...} decorators (non-nested is enough for pandoc)
    s = re.sub(r"@\{[^{}]*\}", "", s)
    s = re.sub(r"[><]\{[^{}]*\}", "", s)
    n = 0
    i = 0
    while i < len(s):
        if s[i] in "lcr":
            n += 1
            i += 1
            continue
        if s.startswith(("p{", "m{", "b{"), i):
            n += 1
            i += 1  # p/m/b
            if i < len(s) and s[i] == "{":
                depth = 0
                while i < len(s):
                    if s[i] == "{":
                        depth += 1
                    elif s[i] == "}":
                        depth -= 1
                        if depth == 0:
                            i += 1
                            break
                    i += 1
            continue
        if s.startswith(r"\begin{minipage}", i):
            n += 1
        i += 1
    if n <= 0:
        n = colspec.count("p{") + len(re.findall(r"(?<![a-zA-Z])[lcr](?![a-zA-Z])", colspec))
    return max(n, 1)


def _table_layout(ncols: int) -> tuple[str, str, str, str]:
    """Return (font_cmd, tabcolsep, env, colspec) for consistent table typography.

    Design goals:
    - Same base size family for all tables (no stretch-to-full-width of glyphs).
    - 2--4 column text tables: tabularx at \\textwidth, footnotesize, wrap.
    - Wide numeric tables: slightly smaller base + shrink-only if needed.
    """
    X = r">{\raggedright\arraybackslash}X"
    if ncols == 2:
        # narrow label + flexible body
        return (
            r"\footnotesize",
            "4pt",
            "tabularx",
            rf"@{{}}>{{\raggedright\arraybackslash}}p{{0.22\textwidth}}{X}@{{}}",
        )
    if ncols == 3:
        return (
            r"\footnotesize",
            "3.6pt",
            "tabularx",
            rf"@{{}}>{{\raggedright\arraybackslash}}p{{0.14\textwidth}}{X}{X}@{{}}",
        )
    if ncols == 4:
        return (
            r"\footnotesize",
            "3.0pt",
            "tabularx",
            rf"@{{}}>{{\raggedright\arraybackslash}}p{{0.12\textwidth}}{X}{X}{X}@{{}}",
        )
    # 5+ cols (incl. Holter / DengAI grids): same footnotesize base;
    # \fittable shrinks only if natural width exceeds \textwidth.
    return (r"\footnotesize", "2.8pt", "tabular", "@{}" + ("l" * ncols) + "@{}")


def convert_longtables(tex: str) -> str:
    """Turn pandoc longtables into uniform-size tabulars.

    Narrow tables used to be upscaled to \\textwidth (huge fonts); wide ones
    downscaled hard (tiny fonts). Now: fixed base size + wrap or shrink-only.
    """

    tex = re.sub(r"\{\\def\\LTcaptype\{none\}[^\n]*\n", "", tex)

    def repl(m: re.Match) -> str:
        colspec = m.group(1)
        body = m.group(2)

        body = re.sub(r"\\endfirsthead|\\endhead|\\endfoot|\\endlastfoot", "", body)
        body = re.sub(r"\\toprule\\noalign\{\}", r"\\toprule", body)
        body = re.sub(r"\\midrule\\noalign\{\}", r"\\midrule", body)
        body = re.sub(r"\\bottomrule\\noalign\{\}", r"\\bottomrule", body)

        body = re.sub(
            r"\\begin\{minipage\}\[[^\]]*\]\{[^}]*\}\\raggedright\s*(.*?)\\end\{minipage\}",
            r"\1",
            body,
            flags=re.S,
        )

        body = re.sub(
            r"(\\midrule\s*)\\bottomrule\s*",
            r"\1",
            body,
            count=1,
        )
        if r"\bottomrule" not in body:
            body = body.rstrip() + "\n\\bottomrule\n"
        else:
            parts = body.rsplit(r"\bottomrule", 1)
            if len(parts) == 2 and parts[1].strip() == "":
                pass
            else:
                body = parts[0] + parts[1] + "\n\\bottomrule\n"

        body = re.sub(r"\n{3,}", "\n\n", body)

        ncols = _count_columns(colspec)
        font, sep, env, simple_spec = _table_layout(ncols)
        body_s = body.strip()

        if env == "tabularx":
            # full width at fixed footnotesize — no glyph scaling
            return (
                f"\n\\begin{{center}}{font}\\setlength{{\\tabcolsep}}{{{sep}}}%\n"
                f"\\begin{{tabularx}}{{\\textwidth}}{{{simple_spec}}}\n"
                f"{body_s}\n"
                "\\end{tabularx}\n"
                "\\end{center}\n"
            )
        # 5+ cols: natural width, shrink only if wider than text
        return (
            f"\n\\begin{{center}}{font}\\setlength{{\\tabcolsep}}{{{sep}}}%\n"
            "\\fittable{%\n"
            f"\\begin{{tabular}}{{{simple_spec}}}\n"
            f"{body_s}\n"
            "\\end{tabular}}%\n"
            "\\end{center}\n"
        )

    pattern = re.compile(
        r"\\begin\{longtable\}\[\]\{(@\{\}.*?@\{\}|[^\}]+)\}\s*(.*?)\\end\{longtable\}",
        re.S,
    )
    tex = pattern.sub(repl, tex)
    tex = re.sub(r"\\end\{center\}\n+\}\n", r"\\end{center}\n\n", tex)
    tex = re.sub(r"\\end\{center\}\n\}", r"\\end{center}\n", tex)
    tex = re.sub(
        r"\n\}\n\n(\\textbf|La |En |No |\\paragraph|\\subsection|\\section)",
        r"\n\n\1",
        tex,
    )
    return tex


def convert_abstract_section(tex: str) -> str:
    """Turn \\section{Abstract|Resumen} into a single abstract environment."""
    m = re.search(
        r"\\section\{(?:Abstract|Resumen)\}(?:\\label\{[^}]*\})?\s*(.*?)(?=\n\\section\{)",
        tex,
        flags=re.S,
    )
    if not m:
        return tex
    body = m.group(1).strip()
    # Drop a trailing page break if pandoc inserted one before next section
    body = re.sub(r"\n*\\clearpage\s*$", "", body)
    repl = "\\begin{abstract}\n" + body + "\n\\end{abstract}\n\n"
    return tex[: m.start()] + repl + tex[m.end() :]


def strip_pandoc_figure_noise(tex: str) -> str:
    """Remove pandoc image wrappers / alt-text noise if any leaked in."""
    # \pandocbounded{\includegraphics[...]{...}} → \includegraphics[...]{...}
    tex = re.sub(
        r"\\pandocbounded\{\s*(\\includegraphics(?:\[[^\]]*\])?\{[^}]+\})\s*\}",
        r"\1",
        tex,
    )
    # drop alt={...} keys (can confuse some extractors)
    tex = re.sub(r"(\\includegraphics\[[^\]]*),alt=\{[^}]*\}([^\]]*\])", r"\1\2", tex)
    tex = re.sub(r"(\\includegraphics\[)alt=\{[^}]*\},?", r"\1", tex)
    return tex


def inject_appendix_figures(tex: str) -> str:
    """Replace any Appendix D body with explicit includegraphics figures."""
    # Drop a pandoc-generated Appendix D / Apéndice D if present
    tex = re.sub(
        r"\\section\{(?:Appendix|Ap\\'endice|Apéndice) D[^}]*\}.*?(\\end\{document\})",
        r"\1",
        tex,
        flags=re.S,
    )
    if r"\end{document}" not in tex:
        raise RuntimeError("main.tex missing \\end{document}")
    return tex.replace(r"\end{document}", appendix_figures_latex() + "\n\\end{document}\n", 1)


def postprocess_tex(tex: str) -> str:
    """Root cleanup after pandoc: abstract, figures, TOC break, wrappers."""
    tex = convert_longtables(tex)
    tex = re.sub(
        r"\\begin\{minipage\}\[[^\]]*\]\{[^}]*\}\\raggedright\s*\\end\{minipage\}",
        "",
        tex,
    )
    tex = convert_abstract_section(tex)
    tex = strip_pandoc_figure_noise(tex)
    tex = inject_appendix_figures(tex)
    # ensure TOC is followed by a clean page break into Abstract
    if r"\tableofcontents" in tex:
        before, after = tex.split(r"\tableofcontents", 1)
        # after may start with "}\n" from pandoc wrap { \tableofcontents }
        if not after.lstrip().startswith(r"\clearpage") and r"\clearpage" not in after[:120]:
            # insert after closing brace of TOC group if present
            m = re.match(r"(\s*\}\s*)", after)
            if m:
                after = after[: m.end()] + "\n\\clearpage\n" + after[m.end() :]
            else:
                after = "\n\\clearpage\n" + after
        tex = before + r"\tableofcontents" + after
    # Guard: title-page macro must not contain internal notes
    banned_in_header = (
        "synthetic comparison only",
        "Default construction: P1",
        "Synthetic validation (S0",
        "mediaimage",
        "screenshot",
    )
    low = tex.lower()
    for b in banned_in_header:
        if b.lower() in low and b.lower() in HEADER_TEX.lower():
            raise RuntimeError(f"banned phrase leaked into HEADER_TEX: {b}")
    return tex


def verify_pdf(pdf: Path) -> list[str]:
    """Hard QA on the produced PDF. Returns list of failure reasons (empty = OK)."""
    fails: list[str] = []
    raw = pdf.read_bytes()
    # latin-1 view of raw PDF (scaffolding tokens are ASCII if present as text)
    raw_txt = raw.decode("latin-1", errors="ignore")
    # High-confidence scaffolding: check raw bytes (not short words that may appear in streams)
    for s in (
        "mediaimage",
        "screenshot.jpeg",
        "screenshot.jpg",
        "[REMAINING",
        "synthetic comparison only",
        "Default construction: P1",
        "Synthetic validation (S0",
        "pandocbounded",
    ):
        if s in raw_txt or s.lower() in raw_txt.lower():
            fails.append(f"banned string in PDF bytes: {s!r}")

    t = run(["pdftotext", "-layout", str(pdf), "-"], cwd=ROOT)
    text = t.stdout if t.returncode == 0 else ""
    if not text.strip():
        fails.append("pdftotext returned empty")
        return fails

    for s in BANNED_PDF_STRINGS:
        if s in text:
            fails.append(f"banned string in text layer: {s!r}")

    # Cover must not carry internal notes (page 1)
    p1 = run(["pdftotext", "-f", "1", "-l", "1", "-layout", str(pdf), "-"], cwd=ROOT)
    cover = p1.stdout if p1.returncode == 0 else ""
    for s in (
        "Synthetic validation (S0",
        "Default construction: P1",
        "synthetic comparison only",
        "multiplicative gain",
    ):
        if s in cover:
            fails.append(f"cover still has internal note: {s!r}")

    # Abstract/Resumen body once (whitespace-normalized)
    text_ws = re.sub(r"\s+", " ", text)
    n_abs = text_ws.count(ABSTRACT_SIGNATURE)
    if n_abs != 1:
        # allow ASCII-folded fallback for Spanish accents lost by some extractors
        if LANG == "es":
            folded = (
                text_ws.replace("á", "a")
                .replace("é", "e")
                .replace("í", "i")
                .replace("ó", "o")
                .replace("ú", "u")
            )
            n_abs = folded.count(
                "identifica transiciones criticas mediante reorganizacion relacional ordinal"
            )
        if n_abs != 1:
            fails.append(f"abstract body signature appears {n_abs} times (want 1)")

    # Embedded images
    img = run(["pdfimages", "-list", str(pdf)], cwd=ROOT)
    n_img = 0
    if img.returncode == 0:
        for ln in img.stdout.splitlines():
            if re.match(r"\s*\d+\s+\d+\s+image\b", ln):
                n_img += 1
    if n_img < len(FIGS):
        fails.append(f"embedded images {n_img} < expected {len(FIGS)}")

    # No pandocbounded residue
    if "pandocbounded" in raw_txt or "pandocbounded" in text:
        fails.append("pandocbounded residue in PDF")

    return fails


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def main() -> int:
    lang = "en"
    args = [a for a in sys.argv[1:] if a]
    if args:
        if args[0] in {"-h", "--help"}:
            print("Usage: python3 scripts/build_pdf.py [--lang en|es]")
            return 0
        if args[0] in {"--lang", "-l"} and len(args) >= 2:
            lang = args[1]
        elif args[0].startswith("--lang="):
            lang = args[0].split("=", 1)[1]
        elif args[0] in {"en", "es"}:
            lang = args[0]
        else:
            print(f"unknown args: {args}", file=sys.stderr)
            return 1
    configure_language(lang)

    if not MANUSCRIPT.exists():
        print(f"missing {MANUSCRIPT.name}", file=sys.stderr)
        return 1

    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    pandoc = find_pandoc()
    body = preprocess_md(MANUSCRIPT.read_text(encoding="utf-8"))
    (BUILD_DIR / "body.md").write_text(body, encoding="utf-8")
    (BUILD_DIR / "header.tex").write_text(HEADER_TEX, encoding="utf-8")

    fig_link = BUILD_DIR / "figures"
    if fig_link.is_symlink() or fig_link.exists():
        if fig_link.is_symlink():
            fig_link.unlink()
        else:
            shutil.rmtree(fig_link)
    fig_link.symlink_to(ROOT / "figures")

    tex_path = BUILD_DIR / "main.tex"
    cmd = [
        str(pandoc),
        str(BUILD_DIR / "body.md"),
        "-o",
        str(tex_path),
        "-f",
        "markdown+tex_math_single_backslash+tex_math_dollars+raw_tex",
        "--pdf-engine=xelatex",
        "-s",
        "--toc",
        "--toc-depth=2",
        # ## in md → \section after dropping H1
        "--shift-heading-level-by=-1",
        "-V",
        "geometry:margin=1in",
        "-V",
        "fontsize=11pt",
        "-V",
        "documentclass=article",
        "-V",
        "mainfont=STIX Two Text",
        "-V",
        "mainfontoptions=BoldFont=STIX Two Text,BoldFeatures={Weight=700},ItalicFont=STIX Two Text,ItalicFeatures={Style=Italic},BoldItalicFont=STIX Two Text,BoldItalicFeatures={Weight=700,Style=Italic}",
        "-V",
        "mathfont=STIX Two Math",
        "-V",
        "monofont=Menlo",
        "-V",
        "linestretch=1.12",
        # display title still set for bookmarks fallback; maketitle is overridden
        "-M",
        f"title={META_TITLE}",
        "-M",
        f"author={META_AUTHOR}",
        "-M",
        "date=July 2026" if LANG == "en" else "date=julio de 2026",
        "-H",
        str(BUILD_DIR / "header.tex"),
        f"--resource-path={ROOT}:{ROOT / 'figures'}:{BUILD_DIR}",
    ]
    # Note: do not pass -V lang=es (babel) — Spanish percent/thinspace
    # handling conflicts with math-mode \% sequences. Localized names
    # are set explicitly in the header.
    r = run(cmd, cwd=ROOT)
    if r.returncode != 0:
        print(r.stderr or r.stdout, file=sys.stderr)
        return r.returncode

    tex = postprocess_tex(tex_path.read_text(encoding="utf-8"))
    tex_path.write_text(tex, encoding="utf-8")

    log_all = []
    for _pass_i in range(1, 3):
        r = run(
            ["xelatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
            cwd=BUILD_DIR,
        )
        log_all.append(r.stdout or "")
        log_all.append(r.stderr or "")
        if r.returncode != 0:
            LOG_PATH.write_text("\n".join(log_all), encoding="utf-8")
            print((r.stdout or "")[-3500:], file=sys.stderr)
            return r.returncode

    log = "\n".join(log_all)
    LOG_PATH.write_text(log, encoding="utf-8")
    pdf_tmp = BUILD_DIR / "main.pdf"
    if not pdf_tmp.exists():
        print("PDF not produced", file=sys.stderr)
        return 1
    shutil.copy2(pdf_tmp, OUT_PDF)
    shutil.copy2(pdf_tmp, OUT_PDF_ALIAS)

    errors = [ln for ln in log.splitlines() if ln.startswith("!")]
    missing = [ln for ln in log.splitlines() if "Missing character" in ln]
    overfull = []
    for ln in log.splitlines():
        if "Overfull \\hbox" in ln or "Overfull \\vbox" in ln:
            m = re.search(r"\(([0-9.]+)pt", ln)
            if m and float(m.group(1)) > (2.5 if LANG == "es" else 1.5):
                overfull.append(ln)

    print(f"PDF: {OUT_PDF}")
    print(f"alias: {OUT_PDF_ALIAS}")
    print(f"size: {OUT_PDF.stat().st_size} bytes")
    digest = hashlib.md5(OUT_PDF.read_bytes()).hexdigest()
    print(f"md5: {digest}")
    pi = run(["pdfinfo", str(OUT_PDF)], cwd=ROOT)
    pages = "?"
    if pi.returncode == 0:
        for ln in pi.stdout.splitlines():
            if ln.split(":", 1)[0] in {
                "Title",
                "Author",
                "Subject",
                "Keywords",
                "Pages",
                "Creator",
                "Producer",
            }:
                print(ln)
                if ln.startswith("Pages:"):
                    pages = ln.split(":", 1)[1].strip()

    print(f"LaTeX errors (!): {len(errors)}")
    print(f"Missing characters: {len(missing)}")
    if missing:
        c: Counter[str] = Counter()
        for ln in missing:
            m = re.search(r"There is no (.+?) in font", ln)
            c[m.group(1) if m else ln] += 1
        for k, v in c.most_common(12):
            print(f"  {v:3d}  {k}")
    print(f"Overfull >1.5pt: {len(overfull)}")
    for ln in overfull[:20]:
        print(" ", ln)

    residual = sorted({ch for ch in tex if ord(ch) > 127})
    # allow common punctuation that xelatex handles; flag only unexpected symbols
    ok_extra = set("áéíóúñÁÉÍÓÚÑüÜ¿¡—–“”‘’«»")
    bad = [ch for ch in residual if ch not in ok_extra]
    print(f"Non-ASCII residual (unexpected): {''.join(bad)!r}")

    # structural checks on extracted text
    t1 = run(["pdftotext", "-f", "1", "-l", "2", "-layout", str(OUT_PDF), "-"], cwd=ROOT)
    page_text = t1.stdout if t1.returncode == 0 else ""
    structural = []
    if "Author: Johel" in page_text and "Contents" in page_text:
        structural.append("author-meta-after-TOC")
    if (
        page_text.count("Appendix B") >= 2
        or "Appendix B — Figures" in page_text
        or "Appendix B --- Figures" in page_text
    ):
        structural.append("duplicate-Appendix-B")
    if "Default construction" in page_text:
        structural.append("old-section-title-Default-construction")

    qa = verify_pdf(OUT_PDF)
    if structural:
        print(f"Structural issues: {structural}")
        qa.extend(structural)
    else:
        print("Structural: cover clean; single abstract path; Appendix D figures.")

    # Write verification receipt next to the PDF (for human + re-upload checks)
    img = run(["pdfimages", "-list", str(OUT_PDF)], cwd=ROOT)
    n_img = sum(
        1
        for ln in (img.stdout or "").splitlines()
        if re.match(r"\s*\d+\s+\d+\s+image\b", ln)
    )
    VERIFY_PATH.write_text(
        "\n".join(
            [
                "Phi3–RECD PDF verification receipt",
                f"file: {OUT_PDF.name}",
                f"alias: {OUT_PDF_ALIAS.name}",
                f"md5: {digest}",
                f"bytes: {OUT_PDF.stat().st_size}",
                f"pages: {pages}",
                f"embedded_images: {n_img} (expect >= {len(FIGS)})",
                f"banned_strings_checked: {', '.join(BANNED_PDF_STRINGS)}",
                f"qa_failures: {qa if qa else 'NONE'}",
                "open with Preview/Acrobat; do not trust chat PDF extractors that inject <mediaimage>.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"VERIFY: {VERIFY_PATH}")

    if errors:
        return 1
    if qa:
        print("QA FAIL:", file=sys.stderr)
        for f in qa:
            print(f"  - {f}", file=sys.stderr)
        return 3
    if missing or overfull or bad:
        return 2
    print(
        "CLEAN: no errors, no missing glyphs, no scaffold strings, "
        "single abstract, figures embedded, cover notes removed."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
