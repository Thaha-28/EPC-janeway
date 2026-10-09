"""Idempotent EPC content seed (run via `manage.py shell < seed_epc.py`).

Creates: section, licence, author accounts, 2 issues, 4 published
articles with frozen authors + keywords. Safe to run on every boot.
Requires the press/journal bootstrap to have run first.
"""
import datetime

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from core import files as core_files
from core import models as core_models
from journal import models as journal_models
from submission import models as submission_models

JOURNAL_CODE = "epc"

ARTICLES = [
    {
        "title": "Photochemical transformation of perfluoroalkyl substances at the air water interface",
        "abstract": "We investigate interfacial photolysis pathways of selected PFAS under simulated sunlight and report quantum yields and product distributions relevant to atmospheric water films.",
        "authors": [
            {"first": "A.", "last": "Rahman", "email": "a.rahman@example.com", "institution": "Dept. of Environmental Chemistry, Univ. of Dhaka"},
            {"first": "S. L.", "last": "Chen", "email": "s.l.chen@example.com", "institution": "Institute for Atmospheric Chemistry, ETH Zurich"},
        ],
        "keywords": ["PFAS", "photochemistry", "air water interface"],
        "date_published": datetime.date(2026, 3, 15),
        "issue": 1,
        "content": (
            "<h2>Introduction</h2>"
            "<p>Perfluoroalkyl and polyfluoroalkyl substances (PFAS) are "
            "persistent contaminants that accumulate at water surfaces. The "
            "air&ndash;water interface offers a distinct reaction environment "
            "where photogenerated oxidants concentrate and photolysis rates can "
            "differ from the bulk. We quantify interfacial photolysis of three "
            "representative PFAS under simulated sunlight and resolve product "
            "distributions relevant to atmospheric water films.</p>"
            "<h2>Materials and Methods</h2>"
            "<p>Perfluorooctanoic acid (PFOA), perfluorooctane sulfonate (PFOS), "
            "and perfluorohexanoic acid (PFHxA) were dissolved in ultrapure water "
            "(1&nbsp;mg&nbsp;L<sup>&minus;1</sup>). Solutions were irradiated in a "
            "solar simulator (AM1.5G, 1000&nbsp;W&nbsp;m<sup>&minus;2</sup>) for up "
            "to 24&nbsp;h. Interfacial analyte concentrations were measured by "
            "surface tension and sum-frequency generation spectroscopy, and "
            "products were identified by liquid chromatography&ndash;high "
            "resolution mass spectrometry (LC&ndash;HRMS).</p>"
            "<h2>Results and Discussion</h2>"
            "<p>Interfacial concentrations of PFAS exceeded bulk values by factors "
            "of 10<sup>4</sup> to 10<sup>5</sup>. Observed first-order photolysis "
            "rate constants were 3&ndash;6 times larger at the interface than in "
            "the bulk for PFOA and PFHxA, consistent with enhanced attack by "
            "hydroxyl radicals generated from interfacial water. PFOS was more "
            "recalcitrant, reflecting the electron-withdrawing sulfonate headgroup. "
            "Short-chain perfluorinated carboxylic acids were the dominant "
            "products, and fluoride mass balance closed to within 12&nbsp;%.</p>"
            "<table><caption>Observed interfacial rate constants.</caption>"
            "<thead><tr><th>Compound</th>"
            "<th>k<sub>int</sub> (h<sup>&minus;1</sup>)</th>"
            "<th>Half-life (h)</th></tr></thead>"
            "<tbody><tr><td>PFOA</td><td>0.21</td><td>3.3</td></tr>"
            "<tr><td>PFHxA</td><td>0.34</td><td>2.0</td></tr>"
            "<tr><td>PFOS</td><td>0.05</td><td>13.9</td></tr></tbody></table>"
            "<h2>Conclusions</h2>"
            "<p>The air&ndash;water interface accelerates PFAS photolysis and "
            "warrants inclusion in atmospheric fate models. Interfacial reaction "
            "pathways should be parameterised separately from bulk aqueous "
            "photochemistry.</p>"
            "<h2>References</h2>"
            "<p>1. Rahman, A. et al. Interfacial photochemistry of persistent "
            "contaminants. <em>Environ. Chem. Lett.</em> (2024).</p>"
            "<p>2. Chen, S. L. et al. Radical pools at aqueous surfaces. "
            "<em>J. Phys. Chem. A</em> (2023).</p>"
        ),
    },
    {
        "title": "Microplastic aging and sorption of hydrophobic organics in estuarine gradients",
        "abstract": "Aging experiments across salinity gradients show systematic changes in surface chemistry and sorption capacity for PAHs, with implications for transport modeling.",
        "authors": [
            {"first": "M. J.", "last": "Alvarez", "email": "m.j.alvarez@example.com", "institution": "Marine Sciences, Univ. of Barcelona"},
            {"first": "K.", "last": "Osei", "email": "k.osei@example.com", "institution": "Coastal Research Lab, Ghana"},
        ],
        "keywords": ["microplastics", "sorption", "estuaries"],
        "date_published": datetime.date(2026, 3, 15),
        "issue": 1,
        "content": (
            "<h2>Introduction</h2>"
            "<p>Microplastics in estuaries undergo photo-oxidation, mechanical "
            "abrasion, and biofilm growth that alter surface chemistry and control "
            "the sorption of hydrophobic organic contaminants. Salinity gradients "
            "add a further control on both particle behaviour and contaminant "
            "activity. We quantify how aging modifies polycyclic aromatic "
            "hydrocarbon (PAH) sorption along an estuarine transect.</p>"
            "<h2>Materials and Methods</h2>"
            "<p>Polyethylene and polyethylene terephthalate microplastics "
            "(50&ndash;200&nbsp;&micro;m) were aged by accelerated UV exposure and "
            "by 8-week estuarine incubations at salinities of 0, 15, and 33. "
            "Sorption isotherms for pyrene and phenanthrene were measured by batch "
            "equilibration and quantified with the Freundlich model. Surface "
            "oxidation was characterised by Fourier-transform infrared "
            "spectroscopy and contact-angle measurements.</p>"
            "<h2>Results and Discussion</h2>"
            "<p>Aging increased the oxygen content of particle surfaces and "
            "reduced water contact angles, increasing polarity and reducing PAH "
            "affinity. Freundlich coefficients (K<sub>F</sub>) decreased by "
            "35&ndash;60&nbsp;% for aged relative to pristine particles, with the "
            "largest reductions at the highest salinity. The effect was consistent "
            "across both polymers, indicating that surface oxidation rather than "
            "polymer identity dominates sorption after aging. These results imply "
            "that weathered microplastics may act as weaker, more reversible PAH "
            "carriers than freshly released particles.</p>"
            "<h2>Conclusions</h2>"
            "<p>Models that assume constant sorption capacity for microplastics "
            "will misestimate PAH transport in estuaries. Aging state and salinity "
            "should be treated as dynamic parameters.</p>"
            "<h2>References</h2>"
            "<p>1. Alvarez, M. J. et al. Weathering controls on microplastic "
            "sorption. <em>Mar. Pollut. Bull.</em> (2024).</p>"
            "<p>2. Osei, K. et al. Estuarine gradients and contaminant "
            "partitioning. <em>Chemosphere</em> (2023).</p>"
        ),
    },
    {
        "title": "Electrochemical recovery of phosphate from municipal wastewater: a pilot comparison",
        "abstract": "Pilot scale electrochemical cells are compared for phosphate recovery efficiency, energy demand, and precipitate purity across operational modes.",
        "authors": [
            {"first": "L.", "last": "Weber", "email": "l.weber@example.com", "institution": "TU Berlin, Urban Water Systems"},
        ],
        "keywords": ["phosphate recovery", "electrochemistry", "wastewater"],
        "date_published": datetime.date(2026, 3, 15),
        "issue": 1,
        "content": (
            "<h2>Introduction</h2>"
            "<p>Recovering phosphate from municipal wastewater addresses both "
            "eutrophication risk and the need for a sustainable phosphorus source. "
            "Electrochemical precipitation offers decentralised recovery, but "
            "energy demand and precipitate purity vary strongly with cell design "
            "and operating mode. Here we compare three pilot-scale configurations.</p>"
            "<h2>Materials and Methods</h2>"
            "<p>Three pilot cells (magnesium sacrificial anode, iron sacrificial "
            "anode, and an inert anode with cathodic precipitation) each treated "
            "1&nbsp;m<sup>3</sup>&nbsp;d<sup>&minus;1</sup> of secondary effluent. "
            "Phosphate removal, energy consumption, and precipitate composition "
            "were monitored over 90&nbsp;days. Solids were characterised by X-ray "
            "diffraction and inductively coupled plasma optical emission "
            "spectrometry.</p>"
            "<h2>Results and Discussion</h2>"
            "<p>All three cells removed more than 85&nbsp;% of influent phosphate. "
            "Specific energy demand ranged from 6 to 19&nbsp;kWh&nbsp;"
            "kg<sup>&minus;1</sup> P removed, with the inert-anode cell the most "
            "efficient at low current density. Precipitates were dominated by "
            "struvite in the magnesium cell and by amorphous iron phosphates in the "
            "iron cell; the latter had lower agronomic value. Current density above "
            "8&nbsp;mA&nbsp;cm<sup>&minus;2</sup> reduced current efficiency "
            "through hydrogen evolution.</p>"
            "<h2>Conclusions</h2>"
            "<p>The inert-anode configuration with cathodic precipitation gives the "
            "best balance of recovery, energy demand, and product purity, and is a "
            "credible route to closed-loop phosphorus management.</p>"
            "<h2>References</h2>"
            "<p>1. Weber, L. et al. Electrochemical nutrient recovery at pilot "
            "scale. <em>Water Res.</em> (2024).</p>"
            "<p>2. Weber, L. Struvite precipitation and current efficiency. "
            "<em>Environ. Sci. Water Res. Technol.</em> (2023).</p>"
        ),
    },
    {
        "title": "Life cycle assessment of bio derived solvents for extraction processes",
        "abstract": "Comparative LCA of bio derived solvents shows trade offs in cumulative energy demand and aquatic toxicity that depend on feedstock and purification route.",
        "authors": [
            {"first": "P.", "last": "Nakamura", "email": "p.nakamura@example.com", "institution": "Kyoto University"},
            {"first": "J.", "last": "Patel", "email": "j.patel@example.com", "institution": "Imperial College London"},
        ],
        "keywords": ["LCA", "green solvents", "bio based"],
        "date_published": datetime.date(2026, 6, 1),
        "issue": 2,
        "content": (
            "<h2>Introduction</h2>"
            "<p>Bio-derived solvents are promoted as greener alternatives to "
            "petrochemical solvents, but their benefits depend on feedstock, "
            "purification route, and end use. We present a cradle-to-gate life "
            "cycle assessment (LCA) of four bio-derived solvents for extraction "
            "processes and compare them with the incumbents they replace.</p>"
            "<h2>Materials and Methods</h2>"
            "<p>Four solvents (ethyl lactate, cyclopentyl methyl ether from "
            "bio-methanol, 2-methyltetrahydrofuran, and a terpene blend) were "
            "assessed with a functional unit of 1&nbsp;kg of solvent delivered to "
            "the point of use. Inventory data were drawn from literature and "
            "supplier declarations and modelled in a commercial LCA database with "
            "cumulative energy demand (CED) and aquatic ecotoxicity as primary "
            "indicators.</p>"
            "<h2>Results and Discussion</h2>"
            "<p>CED ranged from 28 to 74&nbsp;MJ&nbsp;kg<sup>&minus;1</sup>, "
            "depending strongly on feedstock and purification. The terpene blend "
            "performed best on CED, while 2-methyltetrahydrofuran carried the "
            "highest aquatic ecotoxicity, largely from furfural production. "
            "Trade-offs between energy and toxicity were pervasive, and solvent "
            "recovery and recycling reduced impacts by up to 70&nbsp;%. "
            "Bio-derived does not automatically mean lower impact.</p>"
            "<h2>Conclusions</h2>"
            "<p>Solvent selection should be guided by life cycle evidence rather "
            "than feedstock origin alone. Recovery infrastructure is the single "
            "largest lever for reducing environmental burdens.</p>"
            "<h2>References</h2>"
            "<p>1. Nakamura, P. et al. Comparative LCA of green solvents. "
            "<em>Green Chem.</em> (2024).</p>"
            "<p>2. Patel, J. &amp; Nakamura, P. Feedstock and purification "
            "trade-offs. <em>J. Clean. Prod.</em> (2023).</p>"
        ),
    },
]

print("Seeding EPC content...")

journal = journal_models.Journal.objects.filter(code=JOURNAL_CODE).first()
if journal is None:
    print("No epc journal yet, skipping seed.")
    raise SystemExit(0)

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
    1: ("Volume 1, Number 1 (2026)", datetime.datetime(2026, 3, 15)),
    2: ("Volume 1, Number 2 (2026)", datetime.datetime(2026, 6, 1)),
}.items():
    issue, _ = journal_models.Issue.objects.get_or_create(
        journal=journal, volume=1, issue=str(number),
        defaults={
            "issue_title": title,
            "issue_type": issue_type,
            "date": timezone.make_aware(date),
        },
    )
    issues[number] = issue
    print("issue:", issue.volume, issue.issue, issue.issue_title)


def ensure_html_galley(article, html, owner):
    """Create or refresh the article's HTML full-text galley (idempotent).

    The HTML galley is what Janeway renders on the article page and what the
    frontend reads via the API / galley download, so it is the single source
    of truth for an article's body.
    """
    if not html:
        return None
    galley = core_models.Galley.objects.filter(
        article=article,
        file__mime_type__in=core_files.HTML_MIMETYPES,
    ).first()
    if galley is None:
        upload = SimpleUploadedFile(
            "article-%d.html" % article.pk,
            html.encode("utf-8"),
            content_type="text/html",
        )
        new_file = core_files.save_file_to_article(
            upload, article, owner, label="HTML", is_galley=True,
        )
        # Guard against MIME sniffers that miss .html files.
        new_file.mime_type = "text/html"
        new_file.save()
        galley = core_models.Galley.objects.create(
            article=article,
            file=new_file,
            label="HTML",
            type="html",
            sequence=article.get_next_galley_sequence(),
            public=True,
        )
        print("html galley created:", article.pk)
    else:
        # Rewrite the stored file so edits to the seed content propagate.
        with open(galley.file.self_article_path(), "w", encoding="utf-8") as fh:
            fh.write(html)
        if galley.file.mime_type != "text/html":
            galley.file.mime_type = "text/html"
            galley.file.save()
        if galley.type != "html" or galley.label != "HTML" or not galley.public:
            galley.type = "html"
            galley.label = "HTML"
            galley.public = True
            galley.save()
    if article.render_galley_id != galley.pk:
        article.render_galley = galley
        article.save()
        print("render galley set:", article.pk)
    return galley


for spec in ARTICLES:
    article, created = submission_models.Article.objects.get_or_create(
        journal=journal, title=spec["title"],
        defaults={
            "abstract": spec["abstract"],
            "section": section,
            "license": licence,
            "stage": submission_models.STAGE_PUBLISHED,
            "date_published": timezone.make_aware(
                datetime.datetime.combine(spec["date_published"], datetime.time.min)
            ),
            "article_agreement": "Seeded demo content",
        },
    )
    if created:
        print("article created:", article.pk, article.title[:60])
    for order, author_spec in enumerate(spec["authors"]):
        account = author_accounts[author_spec["email"]]
        if article.owner_id is None:
            article.owner = account
            article.correspondence_author = account
            article.save()
        # Direct FrozenAuthor (snapshot_as_author needs role fixtures).
        fa, fa_created = submission_models.FrozenAuthor.objects.get_or_create(
            article=article,
            author=account,
            defaults={
                "first_name": author_spec["first"],
                "last_name": author_spec["last"],
                "frozen_email": author_spec["email"],
                "order": order,
            },
        )
        if fa_created and author_spec.get("institution"):
            fa.institution = author_spec["institution"]
    for word in spec["keywords"]:
        keyword, _ = submission_models.Keyword.objects.get_or_create(word=word)
        if not submission_models.KeywordArticle.objects.filter(
            article=article, keyword=keyword,
        ).exists():
            article.keywords.add(keyword)
    ensure_html_galley(article, spec.get("content"), article.owner or account)
    issues[spec["issue"]].articles.add(article)

if journal.current_issue_id is None:
    journal.current_issue = issues[1]
    journal.save()
    print("current issue set to vol 1 no 1")

print("Seed complete: issues=%d articles=%d" % (
    journal_models.Issue.objects.filter(journal=journal).count(),
    submission_models.Article.objects.filter(journal=journal).count(),
))
