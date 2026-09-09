"""A SQL-derived, portable hardware reference. Rendering never writes the DB."""
from __future__ import annotations

import html
import json
import mimetypes
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit
from wsgiref.simple_server import make_server

from .db import PROJECT_ROOT, connect
from .web import safe_external_url


def esc(value) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "unknown"


def company(value: str) -> str:
    # Display/search aliases only; never rewrite the evidence or create ownership edges.
    lowered = value.lower()
    for token, label in (("intel", "Intel"), ("amd", "AMD"), ("advanced micro", "AMD"),
                         ("nvidia", "NVIDIA"), ("samsung", "Samsung"), ("3dfx", "3dfx"),
                         ("ati", "ATI"), ("matrox", "Matrox"), ("quantum", "Quantum"),
                         ("ibm", "IBM"), ("maxtor", "Maxtor"), ("canopus", "Canopus"),
                         ("melco", "Melco"), ("3dlabs", "3Dlabs"), ("s3", "S3")):
        if lowered.startswith(token):
            return label
    return value or "Unknown manufacturer"


def category(value: str) -> str:
    lowered = value.lower()
    if "cpu" in lowered or "processor" in lowered: return "CPU"
    if "gpu" in lowered or "graphic" in lowered: return "GPU"
    if "hdd" in lowered or "ssd" in lowered or "storage" in lowered: return "Storage"
    return value or "Unclassified"


def source_link(title: str, url: str | None) -> str:
    safe = safe_external_url(url)
    return f'<a href="{esc(safe)}" rel="noreferrer">{esc(title)} <span aria-hidden="true">↗</span></a>' if safe else esc(title)


def load_records(c) -> list[dict]:
    records = []
    rows = c.execute("""SELECT i.*, e.name, e.entity_key, e.record_status,
        b.batch_key FROM intake_candidate_records i JOIN entities e ON e.id=i.entity_id
        JOIN research_import_runs r ON r.id=i.import_run_id
        JOIN research_batches b ON b.id=r.research_batch_id ORDER BY e.entity_key""")
    for row in rows:
        r = dict(row)
        norm = c.execute("SELECT * FROM normalization_proposals WHERE intake_candidate_record_id=? ORDER BY id DESC LIMIT 1", (r["id"],)).fetchone()
        r["normalization"] = dict(norm) if norm else None
        r["title"] = norm["normalized_display_name"] if norm else r["product_name_raw"]
        r["manufacturer"] = company(norm["normalized_manufacturer"] if norm else r["manufacturer_raw"])
        r["category"] = category(norm["normalized_category"] if norm else r["product_type_raw"])
        match = re.search(r"\b(1997|1998)\b", r["batch_key"])
        r["year"] = match.group(1) if match else None
        r["kind"] = "historical"
        r["description"] = f"{r['category']} · {r['manufacturer']} · {r['year']} research cohort"
        records.append(r)
    for row in c.execute("SELECT r.*, e.entity_key, e.name, e.record_status, e.entity_type_code FROM reference_entities r JOIN entities e ON e.id=r.entity_id ORDER BY e.entity_key"):
        r = dict(row)
        r.update(title=r["name"], description=r["short_description"], kind="connected", year=str(r["context_year"]) if r["context_year"] else None)
        if r["manufacturer"]: r["manufacturer"] = company(r["manufacturer"])
        records.append(r)
    return records


class ReferenceRenderer:
    def __init__(self, c, root: Path, status: dict):
        self.c, self.root, self.status = c, root, status
        self.records = load_records(c)
        self.by_key = {r["entity_key"]: r for r in self.records}

    def link(self, r, prefix="") -> str:
        return f'{prefix}entities/{quote(r["entity_key"], safe="")}.html'

    def cards(self, records, prefix="") -> str:
        items = []
        for r in records:
            tag = "Connected reference" if r["kind"] == "connected" else f'{r["year"]} cohort · {r["category"]}'
            items.append(f'<li><a class="record-link" href="{self.link(r,prefix)}"><span class="eyebrow">{esc(tag)}</span><strong>{esc(r["title"])}</strong><span>{esc(r["description"])}</span></a></li>')
        return '<ul class="records">'+"".join(items)+'</ul>' if items else '<p class="empty">No records in this view yet.</p>'

    def page(self, path: str, title: str, body: str, description: str = "", crumbs: list | None = None):
        prefix = "../" * (len(Path(path).parts)-1)
        def a(url, text): return f'<a href="{prefix}{url}">{text}</a>'
        breadcrumbs = a("index.html", "Home")
        for url, label in crumbs or []: breadcrumbs += " <span aria-hidden='true'>/</span> " + a(url, esc(label))
        if path != "index.html": breadcrumbs += " <span aria-hidden='true'>/</span> " + f'<span aria-current="page">{esc(title)}</span>'
        nav = '<nav aria-label="Main">'+"".join(a(url,label) for url,label in [("years.html","By year"),("categories.html","By category"),("manufacturers.html","By manufacturer"),("connected.html","Connected hardware")])+'</nav>'
        search = f'''<form class="search" action="{prefix}search.html" role="search"><label for="site-query" class="sr-only">Search hardware, companies or standards</label><input id="site-query" name="q" type="search" placeholder="Search hardware, companies, standards…" autocomplete="off"><button type="submit">Search</button></form>'''
        description = description or title + " — evidence and context in Structura."
        document = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="{esc(description)}"><title>{esc(title)} · Structura</title><link rel="stylesheet" href="{prefix}assets/reference.css"><script defer src="{prefix}assets/search-index.js"></script><script defer src="{prefix}assets/reference.js"></script></head>
<body data-root="{prefix}"><a class="skip" href="#main">Skip to content</a><header><div class="masthead">{a('index.html','<span class="wordmark">Structura</span>')}<span class="edition">Hardware reference · working edition</span></div>{search}{nav}</header>
<main id="main" tabindex="-1"><nav class="breadcrumbs" aria-label="Breadcrumb">{breadcrumbs}</nav>{body}</main>
<footer><div><strong>Structura</strong><p>Evidence-backed hardware knowledge. This working edition retains provisional records and open questions.</p></div><nav aria-label="Research and site information">{a('sources.html','Sources')}{a('discrepancies.html','Discrepancies')}{a('method.html','Method')}{a('about.html','About')}{a('sitemap.html','Sitemap')}</nav><p class="fine">Read-only reference · Sources retain their own rights · No claim of census completeness</p></footer></body></html>'''
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(document, encoding="utf-8", newline="\n")

    def evidence(self, rows) -> str:
        return '<ul class="evidence-list">'+"".join(f'<li>{source_link(r["title"],r["url"])}<p class="fine">{esc(r.get("publisher", ""))} · {esc(r.get("locator", ""))}</p><p>{esc(r.get("evidence_note", ""))}</p></li>' for r in rows)+'</ul>'

    def historical(self, r):
        key, cid = r["entity_key"], r["id"]
        n = r["normalization"]
        evidence = [dict(row) for row in self.c.execute("SELECT ee.*,s.title,s.url,s.publisher FROM entity_evidence ee JOIN sources s ON s.id=ee.source_id WHERE ee.entity_id=? ORDER BY ee.id",(r["entity_id"],))]
        verification = [dict(row) for row in self.c.execute("SELECT v.*,s.title,s.url,s.publisher FROM verification_records v JOIN sources s ON s.id=v.source_id WHERE v.intake_candidate_record_id=? ORDER BY v.id",(cid,))]
        purposes = [dict(row) for row in self.c.execute("SELECT i.*,s.title,s.url FROM product_intent_claims i JOIN sources s ON s.id=i.source_id WHERE intake_candidate_record_id=? ORDER BY i.id",(cid,))]
        reviews = [dict(row) for row in self.c.execute("SELECT d.* FROM candidate_discrepancy_reviews d WHERE intake_candidate_record_id=? ORDER BY d.id DESC",(cid,))]
        audits = [dict(row) for row in self.c.execute("SELECT a.* FROM audit_findings a JOIN audit_finding_candidate_refs ar ON ar.audit_finding_id=a.id WHERE ar.intake_candidate_record_id=? ORDER BY a.finding_key",(cid,))]
        benchmarks = [dict(row) for row in self.c.execute("SELECT b.*,s.title,s.url FROM benchmark_observations b JOIN sources s ON s.id=b.source_id WHERE intake_candidate_record_id=? ORDER BY b.id",(cid,))]
        flags = f'<a class="status" href="#uncertainty">{esc(reviews[0]["discrepancy_level"])} · reviewed discrepancy</a>' if reviews else '<span class="status">Candidate · no owner discrepancy decision</span>'
        body = f'<p class="eyebrow">{esc(r["year"])} research cohort / {esc(r["category"])}</p><h1>{esc(r["title"])}</h1><p class="lede">{esc(r["manufacturer"])} · {esc(n["entity_granularity"].replace("_"," ") if n else "Identity under review")}</p>{flags}'
        body += '<nav class="sections" aria-label="On this page"><a href="#overview">Overview</a><a href="#purpose">Why it existed</a><a href="#performance">Performance</a><a href="#release">Release evidence</a><a href="#uncertainty">Open questions</a><a href="#evidence">Evidence</a></nav>'
        body += f'<section id="overview"><h2>What it was</h2><p>{esc(r["title"])} is recorded in the {esc(r["year"])} {esc(r["category"])} research cohort under {esc(r["manufacturer"])}. The current display name and classification are normalization proposals.</p><dl class="facts"><dt>Source product name</dt><dd>{esc(r["product_name_raw"])}</dd><dt>Source model number</dt><dd>{esc(r["model_number_raw"] or "Not established")}</dd><dt>Source manufacturer</dt><dd>{esc(r["manufacturer_raw"])}</dd><dt>Research scope</dt><dd>{esc(r["market_scope_raw"] or "See release evidence")}</dd></dl></section>'
        body += '<section id="purpose"><h2>Why it existed</h2>'
        for p in purposes:
            body += f'<article class="claim"><span class="eyebrow">{esc(p["claim_scope"].replace("_"," "))}</span><p>{esc(p["problem_addressed"])}</p><p><strong>Intended users:</strong> {esc(p["target_user"])}</p><p><strong>Engineering response:</strong> {esc(p["engineering_response"])}</p><details><summary>Evidence and limits</summary><p>{source_link(p["title"],p["url"])} · {esc(p["source_locator"])}</p><p>{esc(p["evidence_note"])}</p><p>{esc(p["limitations"])}</p></details></article>'
        if not purposes: body += '<p>No sourced purpose statement has been added.</p>'
        body += '</section><section id="performance"><h2>What difference it made</h2>'
        if benchmarks:
            body += '<p>These observations can only be compared within the same named comparison group. Configuration and provenance matter.</p>'
            for b in benchmarks:
                peers = self.c.execute("SELECT i.candidate_key,e.name,b.result_value FROM benchmark_observations b JOIN intake_candidate_records i ON i.id=b.intake_candidate_record_id JOIN entities e ON e.id=i.entity_id WHERE b.comparison_group_key=? AND b.benchmark_name=? AND b.metric_name=? ORDER BY e.name",(b["comparison_group_key"],b["benchmark_name"],b["metric_name"])).fetchall()
                body += f'<article class="claim"><h3>{esc(b["benchmark_name"])} · {esc(b["metric_name"])}</h3><p><strong>{esc(b["result_value"])} {esc(b["result_unit"])}</strong> · {"Higher" if b["higher_is_better"] else "Lower"} is better</p><p>{esc(b["system_configuration"])}</p><p class="fine">{esc(b["result_provenance"].replace("_"," "))} · Group: {esc(b["comparison_group_key"])}</p><ul>'
                body += ''.join(f'<li><a href="{quote(p["candidate_key"])}.html">{esc(p["name"])}</a>: {esc(p["result_value"])} {esc(b["result_unit"])}</li>' for p in peers)
                body += f'</ul><details><summary>Source and limitations</summary><p>{source_link(b["title"],b["url"])} · {esc(b["source_locator"])}</p><p>{esc(b["limitations"])}</p></details></article>'
        else: body += '<p class="empty">Comparable benchmark evidence has not been established for this record. Missing results do not imply poor performance.</p>'
        body += '</section><section id="release"><h2>Release evidence</h2><p>The year above is a research-cohort label. Announcement, production, shipment and retail availability are distinct events.</p>'
        if n:
            body += f'<dl class="facts"><dt>Proposed event</dt><dd>{esc(n["qualifying_event_type"].replace("_"," "))}</dd><dt>Proposed timing</dt><dd>{esc(n["normalized_launch_date"] or "Unknown")} · {esc(n["date_precision"])} precision</dd><dt>Assessment</dt><dd>{esc(n["decision_status"].replace("_"," "))}</dd></dl><p>{esc(n["rationale"])}</p>'
        body += self.evidence(verification) + '</section><section id="uncertainty"><h2>Open questions and review</h2>'
        if reviews:
            for d in reviews:
                body += f'<article class="claim caution"><h3>{esc(d["discrepancy_level"])} · {esc(d["disposition"].replace("_"," "))}</h3><p>{esc(d["decision_rationale"])}</p><p><strong>What would resolve it:</strong> {esc(d["resolving_evidence"])}</p></article>'
        if n and n["open_questions"]: body += f'<p>{esc(n["open_questions"])}</p>'
        if not reviews: body += '<p>No owner discrepancy decision is recorded. This does not mean there are no unresolved issues.</p>'
        for a in audits:
            body += f'<details><summary>{esc(a["finding_type"].replace("_"," "))} · {esc(a["disposition"].replace("_"," "))}</summary><p>{esc(a["finding"])}</p><p>{source_link("Audit source",a["source_url"])} · {esc(a["source_locator"])}</p><p>{esc(a["source_evidence"])}</p><p><strong>Follow-up:</strong> {esc(a["recommended_next_action"])}</p></details>'
        body += '</section><section id="evidence"><h2>Original intake sources</h2><p>These notes preserve the state at intake. Later verification is shown under Release evidence above; an original note saying verification had not occurred is not the current assessment.</p>'+self.evidence(evidence)+'<details><summary>Original research note</summary><p>'+esc(r["notes"])+'</p></details></section>'
        body += f'<section><h2>Continue exploring</h2><p><a href="../years/{r["year"]}-{slug(r["category"])}.html">{r["year"]} {esc(r["category"])} cohort</a> · <a href="../manufacturers/{slug(r["manufacturer"])}.html">{esc(r["manufacturer"])} records</a></p>'
        if n and n["parent_intake_candidate_record_id"]:
            parent = self.c.execute("SELECT candidate_key FROM intake_candidate_records WHERE id=?",(n["parent_intake_candidate_record_id"],)).fetchone()
            if parent: body += f'<p>Proposed parent family: <a href="{quote(parent[0])}.html">{esc(self.by_key[parent[0]]["title"])}</a></p>'
        body += '</section>'
        self.page(f'entities/{key}.html',r["title"],body,r["description"],[("years.html","By year"),(f'years/{r["year"]}.html',r["year"])])

    def connected_entity(self, r):
        key, eid = r["entity_key"], r["entity_id"]
        outgoing = [dict(row) for row in self.c.execute("""SELECT r.*,d.*,p.label,p.relationship_family,e.entity_key AS target_key,e.name AS target_name
            FROM relationships r JOIN relationship_details d ON d.relationship_id=r.id JOIN predicates p ON p.code=r.predicate_code JOIN entities e ON e.id=r.object_id WHERE r.subject_id=? ORDER BY d.relationship_key""",(eid,))]
        incoming = [dict(row) for row in self.c.execute("SELECT d.relationship_key,p.label,e.entity_key,e.name FROM relationships r JOIN relationship_details d ON d.relationship_id=r.id JOIN predicates p ON p.code=r.predicate_code JOIN entities e ON e.id=r.subject_id WHERE r.object_id=? ORDER BY e.name",(eid,))]
        claims = [dict(row) for row in self.c.execute("SELECT cl.*,s.title AS source_title,s.url FROM reference_claims cl JOIN sources s ON s.id=cl.source_id WHERE cl.entity_id=? OR cl.related_entity_id=? ORDER BY cl.kind,cl.claim_key",(eid,eid))]
        body = f'<p class="eyebrow">Connected hardware / {esc(r["entity_type_code"].replace("_"," "))}</p><h1>{esc(r["title"].split(" (")[0])}</h1><p class="lede">{esc(r["description"])}</p><span class="status">Sourced reference · provisional</span><nav class="sections" aria-label="On this page"><a href="#inside">Inside</a><a href="#overview">Overview</a><a href="#connections">Connections</a><a href="#evidence">Evidence</a></nav>'
        overview=f'<section id="overview"><h2>Overview</h2><p>{esc(r["role_note"])}</p>'
        if r["model_number"]: overview += f'<p><strong>Model:</strong> {esc(r["model_number"])}</p>'
        if r["context_year"]: overview += f'<p><strong>Document context:</strong> {r["context_year"]} · {esc(r["context_year_basis"])}</p>'
        overview += '</section>'
        body += '<section id="inside"><h2>Inside</h2>'
        regions = [dict(row) for row in self.c.execute("SELECT v.*,e.entity_key,e.name FROM visual_regions v JOIN entities e ON e.id=v.entity_id WHERE parent_entity_id=? ORDER BY x",(eid,))]
        if regions:
            body += f'<figure class="schematic"><p class="diagram-heading">{esc(r["title"].split(" (")[0])} · documented constituents</p><div class="diagram-grid" aria-label="Conceptual component map">'
            for v in regions:
                body += f'<a class="diagram-node" href="{quote(v["entity_key"])}.html"><strong>{esc(v["label"])}</strong><span>Open component →</span></a>'
            body += '</div><figcaption>Conceptual diagram · not to scale · package counts and positions remain unverified.</figcaption></figure>'
        else:
            body += '<p>Use the connections below to see where this entity fits. No physical layout has been established for this entry.</p>'
        body += '</section>'+overview+'<section id="connections"><h2>Connections</h2><p>Each arrow is a scoped assertion. Select its label for evidence, or its destination to keep exploring.</p><ul class="connections">'
        for edge in outgoing:
            body += f'<li><span class="relation-family">{esc(edge["relationship_family"])}</span><a class="edge" href="../relationships/{edge["relationship_key"]}.html">{esc(edge["label"])} <span aria-hidden="true">→</span></a><a class="target" href="{quote(edge["target_key"])}.html">{esc(edge["target_name"])}</a><span class="fine">{esc(edge["assessment"])} · provisional</span></li>'
        if not outgoing: body += '<li>No outgoing assertions are included in this bounded example.</li>'
        body += '</ul>'
        if incoming:
            body += '<h3>Connected from</h3><ul class="incoming">'+''.join(f'<li><a href="{quote(i["entity_key"])}.html">{esc(i["name"])}</a> <a href="../relationships/{i["relationship_key"]}.html">{esc(i["label"])} →</a> this entry</li>' for i in incoming)+'</ul>'
        body += '</section><section id="evidence"><h2>Claims, comparisons and evidence</h2>'
        identity_evidence=[dict(row) for row in self.c.execute('SELECT ee.*,s.title,s.url,s.publisher FROM entity_evidence ee JOIN sources s ON s.id=ee.source_id WHERE ee.entity_id=? ORDER BY ee.id',(eid,))]
        body += '<h3>Identity and description</h3>'+self.evidence(identity_evidence)
        for cl in claims:
            body += f'<article class="claim {"caution" if cl["kind"]=="unresolved" else ""}" id="{esc(cl["claim_key"])}"><p class="eyebrow">{esc(cl["kind"])} · {esc(cl["status"])}</p><h3>{esc(cl["title"])}</h3><p>{esc(cl["statement"])}</p><p>{esc(cl["limits"])}</p><details><summary>Source and assessment</summary><p>{source_link(cl["source_title"],cl["url"])} · {esc(cl["locator"])}</p><p>Evidence role: {esc(cl["evidence_role"])}. {esc(cl["verifier_note"])}</p></details>'
            if cl["related_entity_id"]:
                other = self.c.execute("SELECT entity_key,name FROM entities WHERE id=?",(cl["related_entity_id"] if cl["entity_id"]==eid else cl["entity_id"],)).fetchone()
                body += f'<p><a href="{quote(other["entity_key"])}.html">Compare with {esc(other["name"])} →</a></p>'
            body += '</article>'
        body += '<p>Relationship evidence is attached to each arrow above. These assessments do not constitute canonical approval.</p></section>'
        self.page(f'entities/{key}.html',r["title"],body,r["description"],[("connected.html","Connected hardware")])

    def relationship_pages(self):
        for row in self.c.execute("""SELECT r.*,d.*,p.label,s.name AS subject_name,s.entity_key AS subject_key,o.name AS object_name,o.entity_key AS object_key
            FROM relationships r JOIN relationship_details d ON d.relationship_id=r.id JOIN predicates p ON p.code=r.predicate_code JOIN entities s ON s.id=r.subject_id JOIN entities o ON o.id=r.object_id ORDER BY d.relationship_key"""):
            r=dict(row)
            ev=[dict(e) for e in self.c.execute("SELECT re.*,s.title,s.url,s.publisher FROM relationship_evidence re JOIN sources s ON s.id=re.source_id WHERE relationship_id=? ORDER BY re.id",(r["relationship_id"],))]
            body=f'<p class="eyebrow">Relationship evidence</p><h1>{esc(r["label"]).capitalize()}</h1><div class="relation-path"><a href="../entities/{r["subject_key"]}.html">{esc(r["subject_name"])}</a><span aria-hidden="true">→</span><a href="../entities/{r["object_key"]}.html">{esc(r["object_name"])}</a></div><span class="status">{esc(r["assessment"])} · provisional assertion</span><h2>Scope</h2><p>{esc(r["scope"])}</p><h2>Evidence</h2>{self.evidence(ev)}<h2>Independent assessment</h2><p>{esc(r["verifier_note"])}</p><p class="fine">Stable relationship: {esc(r["relationship_key"])}. Vocabulary remains proposed. Neither endpoint implies compatibility or interchangeability.</p>'
            self.page(f'relationships/{r["relationship_key"]}.html',r["label"].capitalize(),body,crumbs=[("connected.html","Connected hardware")])

    def render(self):
        historical = [r for r in self.records if r["kind"]=="historical"]
        connected = [r for r in self.records if r["kind"]=="connected"]
        body = '<h1>An evidence-backed map of computer hardware.</h1><p class="lede">Find a product. Understand its parts. Follow the evidence.</p><div class="home-columns"><section><h2>Explore by year</h2><div class="year-links"><a href="years/1997.html">1997 <span>Launch-cohort research →</span></a><a href="years/1998.html">1998 <span>Launch-cohort research →</span></a></div><h2>Explore by category</h2><div class="pills"><a href="categories/cpu.html">CPU</a><a href="categories/gpu.html">GPU</a><a href="categories/storage.html">Storage</a></div></section><section class="feature"><span class="eyebrow">Connected example</span><h2>One SSD. Three different descriptions.</h2><p>M.2 names its physical format. PCIe describes its interface. NVMe describes its command protocol.</p>'
        if connected: body += '<p><a class="primary-link" href="entities/samsung-970-evo-500gb.html">Explore the Samsung 970 EVO →</a></p><p class="fine">Follow its components, interface and protocol to their sources.</p>'
        else: body += '<p>The connected example is being prepared. Browse the historical catalogue below.</p>'
        body += '</section></div><section><h2>From the yearbook</h2>'+self.cards(historical[:6])+'</section>'
        body += f'<section class="data-note"><h2>About this edition</h2><p><strong>{self.status["historical_candidates"]}</strong> historical candidates · <strong>2</strong> research years · <strong>{self.status["relationships"]}</strong> connected assertions</p><p>The historical sample mixes families, chips and boards; these are record counts, not equivalent products or a complete market census. The connected example is a separate documented reference.</p><a href="method.html">Read the method and limits →</a></section>'
        self.page('index.html','Hardware reference',body,'Explore historical computer hardware and one connected SSD through sourced relationships.')
        self.page('years.html','By year','<h1>By year</h1><p class="lede">Browse the bounded launch-cohort research. A cohort label does not resolve every release date.</p><div class="year-links"><a href="years/1997.html">1997 →</a><a href="years/1998.html">1998 →</a></div>')
        for year in ['1997','1998']:
            rows=[r for r in historical if r["year"]==year]
            links=''.join(f'<a href="{year}-{slug(cat)}.html">{cat} ({sum(r["category"]==cat for r in rows)})</a>' for cat in ['CPU','GPU','Storage'])
            self.page(f'years/{year}.html',year,f'<p class="eyebrow">Historical catalogue</p><h1>{year}</h1><p class="lede">{len(rows)} candidate records across CPU, GPU and storage. Event evidence remains attached to each dossier.</p><div class="pills">{links}</div>'+self.cards(rows,'../'),crumbs=[('years.html','By year')])
            for cat in ['CPU','GPU','Storage']:
                self.page(f'years/{year}-{slug(cat)}.html',f'{year} · {cat}',f'<h1>{year} · {cat}</h1><p>Bounded research cohort. Proposed identity and release timing are shown on each record.</p>'+self.cards([r for r in rows if r["category"]==cat],'../'),crumbs=[('years.html','By year'),(f'years/{year}.html',year)])
        for group, field, label in [('categories','category','By category'),('manufacturers','manufacturer','By manufacturer')]:
            values=sorted({r[field] for r in self.records if r.get(field)})
            self.page(group+'.html',label,f'<h1>{label}</h1><p>Browse proposed catalogue labels. Original source wording remains available in every dossier.</p><ul class="directory">'+''.join(f'<li><a href="{group}/{slug(v)}.html">{esc(v)} <span>{sum(r.get(field)==v for r in self.records)} records →</span></a></li>' for v in values)+'</ul>')
            for value in values:
                self.page(f'{group}/{slug(value)}.html',value,f'<h1>{esc(value)}</h1>'+self.cards([r for r in self.records if r.get(field)==value],'../'),crumbs=[(group+'.html',label)])
        self.page('connected.html','Connected hardware','<h1>Connected hardware</h1><p class="lede">Begin with the SSD, then follow its constituents and standards. Every connection has a scope and source.</p>'+self.cards(sorted(connected,key=lambda r:(r['entity_key']!='samsung-970-evo-500gb',r['title']))))
        self.page('search.html','Search','<h1>Search Structura</h1><p id="search-status" role="status" aria-live="polite">Use the search box above to find hardware, manufacturers, components and standards.</p><div id="search-results"></div><section id="search-fallback"><h2>All reference entries</h2><p>All records are available here even when JavaScript is disabled.</p>'+self.cards(self.records)+'</section>')
        for r in self.records:
            self.historical(r) if r['kind']=='historical' else self.connected_entity(r)
        self.relationship_pages()
        self.research_pages()
        index=[{'title':r['title'],'description':r['description'],'key':r['entity_key'],'url':'entities/'+quote(r['entity_key'])+'.html','terms':' '.join(str(r.get(k) or '') for k in ['title','entity_key','manufacturer','category','year','model_number','product_name_raw','model_number_raw','description'])} for r in self.records]
        for label in sorted({r['manufacturer'] for r in self.records if r.get('manufacturer')}):
            index.append({'title':label,'description':'Manufacturer records','key':slug(label),'url':'manufacturers/'+slug(label)+'.html','terms':label})
        (self.root/'assets/search-index.js').write_text('window.structuraSearch = '+json.dumps(index,ensure_ascii=False).replace('<','\\u003c')+';\n',encoding='utf-8')

    def research_pages(self):
        sources=[dict(s) for s in self.c.execute('SELECT * FROM sources ORDER BY publisher,title')]
        body='<h1>Sources</h1><p class="lede">Source quality depends on the claim. A manufacturer can establish its published specifications; that does not make its performance figures independent measurements.</p><ul class="source-directory">'
        for s in sources:
            body+=f'<li><a href="sources/{s["source_key"]}.html">{esc(s["title"])}</a><span>{esc(s["publisher"])} · Tier {s["source_tier"]}</span></li>'
            used=self.c.execute("SELECT DISTINCT e.entity_key,e.name FROM entities e JOIN entity_evidence ee ON ee.entity_id=e.id WHERE ee.source_id=? UNION SELECT DISTINCT e.entity_key,e.name FROM relationships r JOIN relationship_evidence re ON re.relationship_id=r.id JOIN entities e ON e.id=r.subject_id WHERE re.source_id=? UNION SELECT DISTINCT e.entity_key,e.name FROM reference_claims cl JOIN entities e ON e.id=cl.entity_id WHERE cl.source_id=?",(s['id'],s['id'],s['id'])).fetchall()
            content=f'<h1>{esc(s["title"])}</h1><p>{source_link("Open original source",s["url"] or s["archive_url"])}</p><dl class="facts"><dt>Publisher</dt><dd>{esc(s["publisher"])}</dd><dt>Source tier</dt><dd>{s["source_tier"]}</dd><dt>Publication date</dt><dd>{esc(s["publication_date"] or "Not recorded")}</dd><dt>Accessed</dt><dd>{esc(s["accessed_date"])}</dd></dl><p>{esc(s["notes"])}</p><h2>Referenced records</h2><ul>'+''.join(f'<li><a href="../entities/{u["entity_key"]}.html">{esc(u["name"])}</a></li>' for u in used)+'</ul><p class="fine">Locators and individual assessments appear on the linked records and relationships. Original material retains its own rights.</p>'
            self.page(f'sources/{s["source_key"]}.html',s['title'],content,crumbs=[('sources.html','Sources')])
        self.page('sources.html','Sources',body+'</ul>')
        reviews=[dict(d) for d in self.c.execute("SELECT d.*,i.candidate_key,e.name FROM candidate_discrepancy_reviews d JOIN intake_candidate_records i ON i.id=d.intake_candidate_record_id JOIN entities e ON e.id=i.entity_id WHERE d.id=(SELECT MAX(d2.id) FROM candidate_discrepancy_reviews d2 WHERE d2.intake_candidate_record_id=i.id) ORDER BY d.discrepancy_level DESC,e.name")]
        body='<h1>Discrepancies and open questions</h1><p class="lede">Unknown dates, disputed identities and incomplete evidence remain visible. A missing review is not a clean bill of health.</p><details><summary>Understanding review levels</summary><dl><dt>L0</dt><dd>No material discrepancy identified.</dd><dt>L1</dt><dd>Precision or channel detail is missing.</dd><dt>L2</dt><dd>Shipment or availability is unknown or forecast-only.</dd><dt>L3</dt><dd>Identity, granularity or cohort boundary remains open.</dd><dt>L4</dt><dd>Sources or interpretations materially conflict.</dd></dl><p>OL marks a deferred omission lead, not a reviewed product.</p></details>'
        for d in reviews: body+=f'<article class="claim"><p class="eyebrow">{d["discrepancy_level"]} · {esc(d["disposition"].replace("_"," "))}</p><h2><a href="entities/{d["candidate_key"]}.html#uncertainty">{esc(d["name"])}</a></h2><p>{esc(d["decision_rationale"])}</p></article>'
        for cl in self.c.execute("SELECT cl.*,e.entity_key FROM reference_claims cl JOIN entities e ON e.id=cl.entity_id WHERE kind='unresolved'"):
            body+=f'<article class="claim caution"><p class="eyebrow">Connected example · unknown</p><h2><a href="entities/{cl["entity_key"]}.html#{cl["claim_key"]}">{esc(cl["title"])}</a></h2><p>{esc(cl["statement"])}</p></article>'
        body+=f'<h2>Audit follow-up</h2><p>{self.status["open_audit_findings"]} audit findings have an open or follow-up disposition. They are not equivalent to {self.status["open_audit_findings"]} disputed products. Candidate-specific findings appear in dossiers.</p><details><summary>Deferred omission leads</summary><ul>'
        for a in self.c.execute("SELECT a.finding,a.source_url,a.source_locator FROM audit_findings a WHERE finding_type='omission_lead' ORDER BY id"):
            body+=f'<li><p>{esc(a["finding"])}</p>{source_link("Lead evidence",a["source_url"])} · {esc(a["source_locator"])}</li>'
        self.page('discrepancies.html','Discrepancies',body+'</ul></details>')
        self.page('method.html','Method','''<h1>How to read Structura</h1><p class="lede">Evidence travels with the claim. Uncertainty is part of the reference.</p><section><h2>Historical cohorts</h2><p>The 1997 and 1998 samples investigate new introductions or first commercial shipment in those years. They are not inventories of everything sold that year. Some records retain an unresolved qualifying event. Family, model and board records are labelled separately and should not be counted as equivalent products.</p></section><section><h2>Research and review</h2><p>Discovery, verification, normalization and audit produce separate records. Normalization proposes a label; verification records an assessment. Neither automatically approves a fact. Owner discrepancy decisions are preserved separately. This working edition contains no canonically approved records.</p></section><section><h2>Connected assertions</h2><p>Each relationship has its own source, locator and scope. Supported means a verifier found support for the bounded assertion; qualified means important limits remain. Both remain provisional. Similar interfaces do not establish compatibility with a particular host.</p></section><section><h2>Source quality and independence</h2><p>First-party specifications are strong evidence for what a manufacturer declares. Repeated claims from the same publisher are not independent confirmation. Performance figures retain their source and conditions. Missing measurements are not replaced with estimated rankings.</p></section><section><h2>The diagram</h2><p>The SSD diagram is a conceptual map of documented constituents. It is not a photograph, teardown, wiring diagram or assertion about package positions. Each visible component links to a stable reference entity.</p></section><section><h2>Current checkpoint</h2><p>This site is generated from one SQLite snapshot. It offers no editing or contribution endpoint. Rebuilds validate frozen inputs and keep the previous successful snapshot until all build gates pass.</p><p><a href="build-status.json">Read generated build status</a></p></section>''')
        self.page('about.html','About','''<h1>What is Structura?</h1><p class="lede">A hardware reference for understanding what products are, how they fit together and what evidence supports that understanding.</p><p>The historical catalogue asks what existed and why. The connected explorer asks how an object relates to components, interfaces, protocols and institutions. Both use the same evidence-aware data model.</p><h2>Working edition</h2><p>Coverage is deliberately bounded. This edition is intended for technically curious learners and is still awaiting real-person usability testing. It does not provide purchasing advice, compatibility certification or repairability scores.</p><h2>Rights and reuse</h2><p>Sources retain their own copyright and licensing conditions. Structura stores concise evidence notes and links. This local checkpoint does not grant reuse rights to source documents. Software and dataset publication licences remain undecided.</p>''')
        routes=sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob('*.html'))
        self.page('sitemap.html','Sitemap','<h1>Sitemap</h1><ul class="sitemap">'+''.join(f'<li><a href="{esc(p)}">{esc(p.removesuffix(".html").replace("/"," / "))}</a></li>' for p in routes)+'</ul>')


def render_explorer(db: Path, output: Path, status: dict) -> None:
    output.mkdir(parents=True,exist_ok=False)
    assets=output/'assets';assets.mkdir()
    for name in ('reference.css','reference.js'):
        (assets/name).write_bytes((PROJECT_ROOT/'structura/assets'/name).read_bytes())
    with connect(db,read_only=True) as c:
        ReferenceRenderer(c,output,status).render()
    (output/'build-status.json').write_text(json.dumps(status,indent=2)+'\n',encoding='utf-8')


def validate_site(root: Path) -> list[str]:
    class Links(HTMLParser):
        def __init__(self):super().__init__();self.links=[];self.ids=set()
        def handle_starttag(self,tag,attrs):
            values=dict(attrs)
            if values.get('id'):self.ids.add(values['id'])
            if tag in ('a','link') and values.get('href'):self.links.append(values['href'])
            if tag=='script' and values.get('src'):self.links.append(values['src'])
            if tag=='form' and values.get('action'):self.links.append(values['action'])
    parsed={}
    for path in root.rglob('*.html'):
        parser=Links();parser.feed(path.read_text(encoding='utf-8'));parsed[path.resolve()]=parser
    issues=[]
    for path,parser in parsed.items():
        for link in parser.links:
            url=urlsplit(link)
            if url.scheme or url.netloc:continue
            target=(path.parent/unquote(url.path)).resolve() if url.path else path
            if not target.is_relative_to(root.resolve()) or not target.is_file():
                issues.append(f'{path.name}: missing local target {link}')
            elif url.fragment and (target not in parsed or unquote(url.fragment) not in parsed[target].ids):
                issues.append(f'{path.name}: missing fragment {link}')
    return issues


def create_reference_app(site: Path):
    site=site.resolve()
    def app(environ,start_response):
        method=environ.get('REQUEST_METHOD','GET')
        if method not in ('GET','HEAD'):
            start_response('405 Method Not Allowed',[('Allow','GET, HEAD'),('Content-Type','text/plain')]);return [b'Read-only reference']
        raw=unquote(environ.get('PATH_INFO','/'))
        path=(site/raw.lstrip('/')).resolve()
        if path.is_dir():path=path/'index.html'
        allowed=path.is_relative_to(site) and path.suffix in {'.html','.css','.js','.json'} and path.is_file()
        content=path.read_bytes() if allowed else b'<!doctype html><title>Not found - Structura</title><h1>Record not found</h1><p><a href="/">Return to Structura</a></p>'
        mime=mimetypes.guess_type(str(path))[0] if allowed else 'text/html'
        start_response('200 OK' if allowed else '404 Not Found', [('Content-Type',(mime or 'text/plain')+'; charset=utf-8'),('Content-Length',str(len(content))),('Content-Security-Policy',"default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'"),('X-Content-Type-Options','nosniff'),('Referrer-Policy','no-referrer'),('Cache-Control','no-cache')])
        return [] if method=='HEAD' else [content]
    return app


def serve_explorer(site: Path,host='127.0.0.1',port=8000,follow_current=False):
    print(f'Structura reference: http://{host}:{port}',flush=True)
    fixed_app=create_reference_app(site)
    def app(environ,start_response):
        if follow_current:
            from .build import current_snapshot
            snapshot=current_snapshot()
            if snapshot is not None:
                return create_reference_app(snapshot/'site')(environ,start_response)
        return fixed_app(environ,start_response)
    with make_server(host,port,app) as server:
        try:server.serve_forever()
        except KeyboardInterrupt:print('Structura reference stopped.')
