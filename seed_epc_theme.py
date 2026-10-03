"""Idempotent EPC theme seed (run via `manage.py shell < seed_epc_theme.py`).

Sets the epc sub-theme, CMS pages (with custom templates for structured
pages), About-dropdown nav items, and editorial groups. Safe to run on
every boot. Requires press/journal bootstrap + seed_epc.py to have run.
"""
from django.contrib.contenttypes.models import ContentType

from cms import models as cms_models
from core import models as core_models
from journal import models as journal_models
from utils import setting_handler

JOURNAL_CODE = "epc"
CONTACT_EMAIL = "editors@epc-journal.org"

print("Seeding EPC theme content...")

journal = journal_models.Journal.objects.filter(code=JOURNAL_CODE).first()
if journal is None:
    print("No epc journal yet, skipping theme seed.")
    raise SystemExit(0)


def safe_save_setting(group, name, value):
    """Save a setting; warn (don't abort) if the Setting row is missing."""
    try:
        setting_handler.save_setting(group, name, journal, value)
    except core_models.Setting.DoesNotExist:
        print(f"WARNING: setting {group}.{name} missing in DB, skipped")


# --- Theme + journal settings -------------------------------------------
safe_save_setting("general", "journal_theme", "epc")
safe_save_setting("general", "journal_base_theme", "OLH")
safe_save_setting("general", "main_contact", CONTACT_EMAIL)
safe_save_setting("general", "custom_cms_templates", "custom")
safe_save_setting(
    "general",
    "journal_description",
    "Environmental Processes and Chemistry is a diamond open access, peer "
    "reviewed journal publishing rigorous research on chemical processes in "
    "natural and engineered environments.",
)
safe_save_setting(
    "styling", "editorial_group_page_name", "Editorial Board"
)

# Online ISSN: pending assignment (shown as such, per reviewer).
if journal.issn != "Pending Assignment":
    journal.issn = "Pending Assignment"
    print("journal issn set to Pending Assignment")

# Nav flags: Home, Current(custom), About(custom), Issues, Editorial Team,
# Submission, Contact, Start Submission. No news/reviewer/articles-list.
for flag, value in [
    ("nav_home", True),
    ("nav_news", False),
    ("nav_articles", False),
    ("nav_issues", True),
    ("nav_contact", True),
    ("nav_sub", True),
    ("nav_start", True),
    ("nav_review", False),
]:
    if getattr(journal, flag, None) != value:
        setattr(journal, flag, value)
        print(f"journal.{flag} set to {value}")
journal.save()

for flag, value in [
    ("enable_editorial_display", True),
    ("multi_page_editorial", False),
]:
    safe_save_setting("general", flag, value)

# --- CMS pages ------------------------------------------------------------
ct = ContentType.objects.get_for_model(journal)

PAGES = [
    {
        "name": "aims-scope",
        "display_name": "Aims and Scope",
        "template": "custom/epc_aims_scope.html",
        "content": (
            "<p><strong>Environmental Processes and Chemistry</strong> is a peer "
            "reviewed journal that publishes rigorous mechanistic and systems "
            "level research on processes that govern environmental behavior. "
            "We welcome experimental, field, and modelling studies that advance "
            "understanding of chemical, biological, and physical processes across "
            "natural and engineered environments, with strong emphasis on "
            "processes, interfaces, transformation, and sustainability.</p>"
            "<p>The journal publishes technically correct and scientifically "
            "motivated work, including useful negative results and replication "
            "studies, through peer review.</p>"
        ),
    },
    {
        "name": "open-access",
        "display_name": "Open Access and Indexing",
        "template": "custom/epc_open_access.html",
        "content": "<p>All content is open access from day one.</p>",
    },
    {
        "name": "author-guidelines",
        "display_name": "Author Guidelines",
        "template": "",
        "content": (
            "<p>Prepare your manuscript before you log in to the submission "
            "system. Templates are provided in the system to ensure consistent "
            "formatting.</p>"
            "<h2>Before you submit</h2>"
            "<ul><li>All authors approve the submitted version. Declare "
            "contributions, funding, and competing interests.</li>"
            "<li>Obtain permissions for any reused figures or data that are "
            "not CC BY.</li>"
            "<li>Prepare a cover letter stating novelty and environmental "
            "relevance.</li></ul>"
            "<h2>Manuscript preparation</h2>"
            "<h3>Structure</h3>"
            "<p>Title, abstract 200 to 250 words, 4 to 6 keywords, introduction, "
            "materials and methods, results, discussion, conclusions, data "
            "availability, author contributions, acknowledgments, references, "
            "supporting information if needed.</p>"
            "<h3>Data and code</h3>"
            "<p>Primary data, code, and detailed methods must be available. Use "
            "repositories with DOIs and cite them.</p>"
            "<h3>References and units</h3>"
            "<p>Use consistent citation style. Use SI units. Show uncertainties "
            "where relevant. Report detection limits and QA QC.</p>"
            "<h2>Article Types</h2>"
            "<ul>"
            "<li><strong>Research Articles:</strong> Original research addressing "
            "significant advances in environmental processes, chemistry, "
            "contaminant behaviour, environmental transformation, remediation, "
            "and related interdisciplinary areas.</li>"
            "<li><strong>Review Articles:</strong> Critical and comprehensive "
            "evaluations of established and emerging research, highlighting "
            "advances, knowledge gaps, challenges, and future research "
            "directions.</li>"
            "<li><strong>Short Communications:</strong> Concise reports of novel "
            "and scientifically significant findings that warrant rapid "
            "communication to the research community.</li>"
            "<li><strong>Perspectives:</strong> Expert analyses offering "
            "forward-looking views on emerging concepts, unresolved questions, "
            "research priorities, and future directions in environmental "
            "processes and chemistry.</li>"
            "</ul>"
            "<h2>Peer review</h2>"
            "<p>Peer review is conducted by at least two independent reviewers, "
            "editor makes final decision. Typical timeline: first decision "
            "within 4 to 6 weeks.</p>"
            "<h2>After acceptance</h2>"
            "<p>Copyediting is light. Proofs are sent to corresponding authors. "
            "Articles are published with Crossref DOIs.</p>"
            "<h2>Quick checklist</h2>"
            "<ul>"
            "<li>Cover letter with environmental relevance</li>"
            "<li>Abstract 200 to 250 words, 4 to 6 keywords</li>"
            "<li>Data availability statement and repository DOI</li>"
            "<li>Competing interests and funding statement</li>"
            "<li>Figures as vector or 600 dpi, accessible colors</li>"
            "</ul>"
        ),
    },
    {
        "name": "editorial-policies",
        "display_name": "Editorial and Ethics Policies",
        "template": "",
        "content": (
            "<p>How we handle peer review, ethics, and integrity. Policies "
            "follow guidance from the Committee on Publication Ethics (COPE) "
            "and the World Association of Medical Editors (WAME) and are "
            "enforced in the editorial workflow.</p>"
            "<h2>Peer review</h2>"
            "<ul>"
            "<li>Peer review is conducted by independent experts. Authors and "
            "reviewers remain confidential where required.</li>"
            "<li>At least two independent reviewers per manuscript. A third is "
            "sought when recommendations diverge.</li>"
            "<li>Editors handle conflicts and recuse themselves when they have "
            "a competing interest.</li>"
            "<li>Reviewers agree to confidentiality and timely, constructive "
            "feedback.</li>"
            "<li>Editorial decisions are based on scientific validity and "
            "importance to the scope.</li>"
            "</ul>"
            "<h2>Research and publication ethics</h2>"
            "<h3>Authorship</h3>"
            "<p>Authorship requires substantial contribution, drafting or "
            "revision, approval of the final version, and accountability. All "
            "authors must meet authorship criteria and approve submission. Use "
            "CRediT for contributions. Changes to authorship after submission "
            "require written agreement from all authors. We follow COPE and "
            "WAME authorship guidance.</p>"
            "<h3>Plagiarism and duplication</h3>"
            "<p>All submissions are screened with similarity software. Overlap "
            "with prior work must be disclosed and cited. Duplicate submission "
            "to another journal while under review is not permitted. Text "
            "recycling should be limited and transparent.</p>"
            "<h3>Image and data integrity</h3>"
            "<p>Adjustments to images must not misrepresent data. Raw data and "
            "code should be retained and made available on request. "
            "Fabrication, falsification, and selective reporting are "
            "investigated per COPE flowcharts and WAME recommendations.</p>"
            "<h3>Human, animal, and field work</h3>"
            "<p>Studies involving humans, animals, or regulated organisms must "
            "include ethics approval and permits. Field work with environmental "
            "samples should state collection permits where applicable.</p>"
            "<h2>Competing interests and funding</h2>"
            "<p>All authors declare competing interests and funding sources "
            "using the disclosure form at submission. Editors and reviewers "
            "also declare conflicts and are reassigned when needed. Funding "
            "statements include grant numbers where applicable.</p>"
            "<h2>Corrections and retractions</h2>"
            "<p>Errors that affect interpretation will be corrected. "
            "Retractions are issued when findings are unreliable or misconduct "
            "is established. Corrections and retractions are linked to the "
            "original article, indexed, and freely accessible.</p>"
            "<h2>Appeals and complaints</h2>"
            "<p>Appeals of editorial decisions must be sent to the editorial "
            "office with a clear rebuttal and new evidence if available. "
            "Appeals are reviewed by an uninvolved editor. Complaints about the "
            "process are handled by the editors in chief per COPE and WAME "
            "guidance.</p>"
            "<h2>Archiving and preservation</h2>"
            "<p>Articles are archived via LOCKSS and CLOCKSS, plus repository "
            "copies where applicable. DOIs are registered with Crossref and "
            "metadata includes funding and ORCID.</p>"
        ),
    },
    {
        "name": "publisher",
        "display_name": "Publisher Details",
        "template": "",
        "content": (
            "<p>Ownership and publishing information for Environmental Processes "
            "and Chemistry.</p>"
            "<ul>"
            "<li><strong>Journal:</strong> Environmental Processes and "
            "Chemistry</li>"
            "<li><strong>Publisher:</strong> EnviNova Scientific Publishing</li>"
            "<li><strong>Online ISSN:</strong> Pending Assignment</li>"
            "<li><strong>Publication model:</strong> Diamond open access, "
            "continuous publication. No article processing charges.</li>"
            "<li><strong>Licensing:</strong> Creative Commons Attribution 4.0 "
            "International (CC BY 4.0). Authors retain copyright.</li>"
            "<li><strong>Editorial contact:</strong> "
            "editors@epc-journal.org</li>"
            "</ul>"
        ),
    },
    {
        "name": "privacy",
        "display_name": "Privacy Policy",
        "template": "",
        "content": (
            "<p>This journal collects only the personal data needed to operate "
            "peer review and publication (account details, submission files, "
            "editorial correspondence). Data is not sold or shared with third "
            "parties except as required for publishing services (for example "
            "DOI registration). Contact the editorial office with privacy "
            "questions.</p>"
        ),
    },
]

for spec in PAGES:
    page, created = cms_models.Page.objects.get_or_create(
        name=spec["name"],
        content_type=ct,
        object_id=journal.pk,
        defaults={
            "display_name": spec["display_name"],
            "template": spec["template"],
            "content": spec["content"],
        },
    )
    changed = False
    for field in ("display_name", "template", "content"):
        if getattr(page, field) != spec[field]:
            setattr(page, field, spec[field])
            changed = True
    if created:
        print(f"CMS page created: {spec['name']}")
    elif changed:
        page.save()
        print(f"CMS page updated: {spec['name']}")

# --- Nav items ------------------------------------------------------------
def upsert_nav(link_name, link, sequence, has_sub_nav=False, parent=None,
                for_footer=False):
    item, created = cms_models.NavigationItem.objects.get_or_create(
        link_name=link_name,
        content_type=ct,
        object_id=journal.pk,
        defaults={
            "link": link,
            "sequence": sequence,
            "has_sub_nav": has_sub_nav,
            "top_level_nav": parent,
            "for_footer": for_footer,
        },
    )
    changed = False
    for field, value in (
        ("link", link),
        ("sequence", sequence),
        ("has_sub_nav", has_sub_nav),
        ("top_level_nav", parent),
        ("for_footer", for_footer),
    ):
        if getattr(item, field) != value:
            setattr(item, field, value)
            changed = True
    if created:
        print(f"nav item created: {link_name}")
    elif changed:
        item.save()
        print(f"nav item updated: {link_name}")
    return item

current = upsert_nav("Current Issue", "epc/issue/current/", 10)
about = upsert_nav("About", None, 20, has_sub_nav=True)
_subs = [
    ("Aims and Scope", "epc/site/aims-scope", 1),
    ("Editorial Board", "epc/editorialteam/", 2),
    ("Author Guidelines", "epc/site/author-guidelines", 3),
    ("Editorial and Ethics Policies", "epc/site/editorial-policies", 4),
    ("Open Access and Indexing", "epc/site/open-access", 5),
    ("Publisher Details", "epc/site/publisher", 6),
    ("Contact", "epc/contact/", 7),
]
for name, link, seq in _subs:
    upsert_nav(name, link, seq, parent=about)

# --- Editorial groups ------------------------------------------------------
for seq, (name, description) in enumerate(
    [
        (
            "Chief Editors",
            "Editors-in-chief of Environmental Processes and Chemistry.",
        ),
        (
            "Board of Editors",
            "Members of the editorial board.",
        ),
    ]
):
    group, created = core_models.EditorialGroup.objects.get_or_create(
        name=name,
        journal=journal,
        defaults={
            "description": description,
            "sequence": seq,
            "display_profile_images": True,
        },
    )
    if created:
        print(f"editorial group created: {name}")
    elif not group.display_profile_images:
        group.display_profile_images = True
        group.save()

print("EPC theme seed done.")
