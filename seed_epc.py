"""Idempotent seed for the EPC journal (run via `manage.py shell < seed_epc.py`).

Creates: press (if missing), EPC journal, section, licence, author
accounts, 2 issues, 4 published articles with frozen authors + keywords.
Safe to run on every boot.
"""
import datetime

from django.contrib.auth import get_user_model
from django.utils import timezone

from journal import models as journal_models
from press import models as press_models
from submission import models as submission_models
from utils import install

JOURNAL_CODE = "epc"
JOURNAL_NAME = "Environmental Processes and Chemistry"

ARTICLES = [
    {
        "title": "Photochemical transformation of perfluoroalkyl substances at the air water interface",
        "abstract": "We investigate interfacial photolysis pathways of selected PFAS under simulated sunlight and report quantum yields and product distributions relevant to atmospheric water films.",
        "authors": [
            {"first": "A.", "last": "Rahman", "email": "a.rahman@example.com"},
            {"first": "S. L.", "last": "Chen", "email": "s.l.chen@example.com"},
        ],
        "keywords": ["PFAS", "photochemistry", "air water interface"],
        "date_published": datetime.date(2026, 3, 15),
        "issue": 1,
    },
    {
        "title": "Microplastic aging and sorption of hydrophobic organics in estuarine gradients",
        "abstract": "Aging experiments across salinity gradients show systematic changes in surface chemistry and sorption capacity for PAHs, with implications for transport modeling.",
        "authors": [
            {"first": "M. J.", "last": "Alvarez", "email": "m.j.alvarez@example.com"},
            {"first": "K.", "last": "Osei", "email": "k.osei@example.com"},
        ],
        "keywords": ["microplastics", "sorption", "estuaries"],
        "date_published": datetime.date(2026, 3, 15),
        "issue": 1,
    },
    {
        "title": "Electrochemical recovery of phosphate from municipal wastewater: a pilot comparison",
        "abstract": "Pilot scale electrochemical cells are compared for phosphate recovery efficiency, energy demand, and precipitate purity across operational modes.",
        "authors": [
            {"first": "L.", "last": "Weber", "email": "l.weber@example.com"},
        ],
        "keywords": ["phosphate recovery", "electrochemistry", "wastewater"],
        "date_published": datetime.date(2026, 3, 15),
        "issue": 1,
    },
    {
        "title": "Life cycle assessment of bio derived solvents for extraction processes",
        "abstract": "Comparative LCA of bio derived solvents shows trade offs in cumulative energy demand and aquatic toxicity that depend on feedstock and purification route.",
        "authors": [
            {"first": "P.", "last": "Nakamura", "email": "p.nakamura@example.com"},
            {"first": "J.", "last": "Patel", "email": "j.patel@example.com"},
        ],
        "keywords": ["LCA", "green solvents", "bio based"],
        "date_published": datetime.date(2026, 6, 1),
        "issue": 2,
    },
]

print("Seeding EPC content...")

press, _ = press_models.Press.objects.get_or_create(
    name="EPC Press",
    defaults={"domain": "localhost", "main_contact": "editors@epc-journal.org"},
)
print("press:", press.name)

journal = journal_models.Journal.objects.filter(code=JOURNAL_CODE).first()
if journal is None:
    install.journal(name=JOURNAL_NAME, code=JOURNAL_CODE, base_url="localhost")
    journal = journal_models.Journal.objects.get(code=JOURNAL_CODE)
    install.update_issue_types(journal, management_command=False)
    print("journal created:", journal.code)
else:
    print("journal exists:", journal.code)

section, _ = submission_models.Section.objects.get_or_create(
    journal=journal,
    name="Research Articles",
    defaults={"number_of_reviewers": 2},
)

licence, _ = submission_models.Licence.objects.get_or_create(
    short_name="CC BY",
    journal=journal,
    defaults={
        "name": "Creative Commons Attribution 4.0",
        "url": "https://creativecommons.org/licenses/by/4.0/",
    },
)

User = get_user_model()
author_accounts = {}
for spec in ARTICLES:
    for a in spec["authors"]:
        if a["email"] not in author_accounts:
            account, _ = User.objects.get_or_create(
                email=a["email"],
                defaults={
                    "username": a["email"],
                    "first_name": a["first"],
                    "last_name": a["last"],
                    "is_active": True,
                },
            )
            author_accounts[a["email"]] = account

issue_type, _ = journal_models.IssueType.objects.get_or_create(
    code="issue", journal=journal,
)
issues = {}
for number, (title, date) in {
    1: ("Volume 1, Number 1 (2026)", datetime.date(2026, 3, 15)),
    2: ("Volume 1, Number 2 (2026)", datetime.date(2026, 6, 1)),
}.items():
    issue, _ = journal_models.Issue.objects.get_or_create(
        journal=journal, volume=1, issue=str(number),
        defaults={"issue_title": title, "issue_type": issue_type, "date": date},
    )
    issues[number] = issue
    print("issue:", issue.volume, issue.issue, issue.issue_title)

for spec in ARTICLES:
    article, created = submission_models.Article.objects.get_or_create(
        journal=journal, title=spec["title"],
        defaults={
            "abstract": spec["abstract"],
            "section": section,
            "licence": licence,
            "stage": submission_models.STAGE_PUBLISHED,
            "date_published": timezone.make_aware(
                datetime.datetime.combine(spec["date_published"], datetime.time.min)
            ),
        },
    )
    if created:
        print("article created:", article.pk, article.title[:60])
    for author_spec in spec["authors"]:
        account = author_accounts[author_spec["email"]]
        if article.owner_id is None:
            article.owner = account
            article.correspondence_author = account
            article.save()
        account.snapshot_as_author(article)
    for word in spec["keywords"]:
        keyword, _ = submission_models.Keyword.objects.get_or_create(word=word)
        article.keywords.add(keyword)
    issues[spec["issue"]].articles.add(article)

if journal.current_issue_id is None:
    journal.current_issue = issues[1]
    journal.save()
    print("current issue set to vol 1 no 1")

print("Seed complete: issues=%d articles=%d" % (
    journal_models.Issue.objects.filter(journal=journal).count(),
    submission_models.Article.objects.filter(journal=journal).count(),
))
