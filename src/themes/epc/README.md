# EPC theme

Sub-theme for the *Environmental Processes and Chemistry* journal, based on
the OLH core theme. Only overridden templates live here; everything else
falls back to `journal_base_theme` (OLH) via
`utils/template_override_middleware.py`.

```
src/themes/epc/
  assets/
    css/epc.css        EPC design system (loaded by templates/core/base.html)
    img/               emblem, logo, editor photos
  templates/
    core/base.html             shell + epc.css link (tracks OLH base.html)
    core/nav.html              kept in sync with OLH (EPC tab markup hooks)
    elements/journal_footer.html  4-column dark footer
    journal/index.html         hero, about/scope, latest research, submit CTA
    journal/article.html       EPC article layout
    journal/issue.html         current/single issue wrapper tweaks
    journal/issues.html        archives list tweaks
    journal/editorial_team.html  photo cards
    cms/page.html              prose shell for /site/* pages
    custom/                    per-page CMS templates (selected in CMS admin)
  build_assets.py              copies assets/* into static/epc/ (runs at boot
                               via `manage.py build_assets` + collectstatic)
```

Set `general.journal_theme = epc` and `general.journal_base_theme = OLH`
(Manager > Journal Settings, or the Railway entrypoint seed).
