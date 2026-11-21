import json, os, shutil, html, itertools, sys, datetime
sys.path.insert(0, os.path.dirname(__file__))
from cost import V, best, plan_cost
ROOT = '/workspace/txmailcost'; D = ROOT + '/dist'
SITE = os.environ.get('SITE','https://basileion.github.io/txmailcost')
BASE = os.environ.get('BASE','/txmailcost')
CHECKED = '2026-11-20'
TOKEN = open(ROOT + '/.dl_token').read().strip()
PAY = os.environ.get('PAYLINK', '').strip()  # Stripe payment link, filled after creation
VOLS = [10000, 50000, 100000, 250000, 500000, 1000000]
BYID = {v['id']: v for v in V}
e = html.escape

def money(x):
    if x is None: return '—'
    if x < 10 and x != int(x): return f'${x:,.2f}'
    return f'${x:,.2f}'.replace('.00', '') if x == int(x) else f'${x:,.2f}'
def vol(n):
    if n >= 1000000: return (f'{n/1e6:g}M')
    return f'{n//1000:g}k' if n % 1000 == 0 else f'{n:,}'
def volw(n): return f'{n:,}'

CSS = """:root{--bg:#f7f5f0;--s:#fff;--ink:#141821;--ink2:#3a404c;--mut:#5f6673;--line:#e6e2d9;--acc:#1d4e89;--acc2:#e8eef7;--warn:#8a5a00;--warns:#f8efdc;--pos:#1f6b4f;--poss:#e7f2ec}
@media(prefers-color-scheme:dark){:root{--bg:#0e1117;--s:#151a22;--ink:#ecebe6;--ink2:#c6c8cc;--mut:#9aa1ad;--line:#262d38;--acc:#8fb0ff;--acc2:#1a2333;--warn:#e3b45f;--warns:#2b2312;--pos:#6fcf9f;--poss:#142a21}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 ui-sans-serif,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;font-variant-numeric:tabular-nums}
.w{max-width:1080px;margin:0 auto;padding:0 20px}header{border-bottom:1px solid var(--line);background:var(--s)}header .w{display:flex;gap:18px;align-items:center;height:60px;flex-wrap:wrap}
.brand{font:700 20px Georgia,serif;color:var(--ink);text-decoration:none}.brand span{color:var(--acc)}nav a{color:var(--mut);text-decoration:none;font-size:14px;margin-right:14px}nav a:hover{color:var(--ink)}
h1{font:600 clamp(30px,4.5vw,46px)/1.1 Georgia,serif;letter-spacing:-.02em;margin:36px 0 12px;max-width:24ch}h2{font:600 26px/1.2 Georgia,serif;margin:44px 0 10px}h3{font:600 19px Georgia,serif;margin:20px 0 6px}
a{color:var(--acc)}.lede{font-size:18px;color:var(--ink2);max-width:66ch}.mut{color:var(--mut)}.note{font-size:13px;color:var(--mut)}
.eb{font:600 12px/1 sans-serif;letter-spacing:.12em;text-transform:uppercase;color:var(--acc)}
table{border-collapse:collapse;width:100%;background:var(--s);border:1px solid var(--line);border-radius:8px;overflow:hidden;font-size:14px}th,td{padding:9px 10px;border-bottom:1px solid var(--line);text-align:right;white-space:nowrap}th:first-child,td:first-child{text-align:left}th{background:var(--acc2);font-weight:600;font-size:13px}
.tw{overflow-x:auto}.best{background:var(--poss);color:var(--pos);font-weight:700}.card{background:var(--s);border:1px solid var(--line);border-radius:10px;padding:18px 20px;margin:14px 0}
.warn{background:var(--warns);border-color:transparent}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px}.big{font:700 30px Georgia,serif}
.btn{display:inline-block;background:var(--ink);color:var(--bg);padding:10px 18px;border-radius:6px;text-decoration:none;font-weight:600;font-size:14px}.btn:hover{background:var(--acc)}
input,select{font:16px sans-serif;padding:9px 11px;border:1px solid var(--line);border-radius:6px;background:var(--s);color:var(--ink)}label{font-size:13px;color:var(--mut);display:inline-flex;flex-direction:column;gap:4px;margin-right:14px}
footer{margin-top:60px;border-top:1px solid var(--line);padding:26px 0 40px;font-size:13px;color:var(--mut)}footer a{color:var(--mut)}ul.links{columns:2;padding-left:18px}sup{color:var(--warn)}"""

def page(path, title, desc, body, schema=None, noindex=False):
    canon = SITE + path
    sch = f'<script type="application/ld+json">{json.dumps(schema)}</script>' if schema else ''
    rob = '<meta name="robots" content="noindex,nofollow">' if noindex else ''
    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{canon}">{rob}
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{canon}"><meta property="og:type" content="website"><meta name="twitter:card" content="summary">
<link rel="alternate" type="application/rss+xml" title="TxMailCost price changes" href="/changes/feed.xml"><link rel="stylesheet" href="/style.css">{sch}</head><body>
<header><div class="w"><a class="brand" href="/">Tx<span>Mail</span>Cost</a><nav><a href="/#calc">Calculator</a><a href="/cost/100000-emails-per-month/">By volume</a><a href="/compare/">Compare</a><a href="/vendors/">Providers</a><a href="/changes/">Price log</a><a href="/workbook/">Workbook</a></nav></div></header>
<main class="w">{body}</main>
<footer><div class="w"><p><b>TxMailCost</b> tracks published transactional email prices for {len(V)} providers. Every price links to the vendor page it came from. Last checked {CHECKED}. Not affiliated with any provider; no paid placements. Verify on the vendor's page before you buy.</p>
<p><a href="/about/">Methodology</a> · <a href="/api/plans.json">JSON data</a> · <a href="/changes/feed.xml">RSS</a> · <a href="/workbook/">Workbook</a> · <a href="mailto:basileion.ops@gmail.com?subject=TxMailCost%20correction">Report a wrong price</a></p>
<p>More sourced pricing ledgers: <a href="https://vpsledger.pages.dev/">VPSLedger</a> (VPS true monthly cost) · <a href="https://authcost.pages.dev/">AuthCost</a> (auth and identity pricing) · <a href="https://o11y-watch.pages.dev/directory">O11y Watch</a> (observability free tiers)</p></div></footer></body></html>"""
    doc = doc.replace('href="/', 'href="'+BASE+'/').replace("'/vendors/'", "'"+BASE+"/vendors/'")
    out = D + path + ('index.html' if path.endswith('/') else '')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w').write(doc)
    if not noindex: URLS.append(path)

URLS = []
def dag(v): return '<sup title="Upper bound: larger tiers were not readable on the vendor page">†</sup>' if v['read'] == 'partial' else ''

def vol_table(vids=None, vols=VOLS):
    vs = [BYID[i] for i in vids] if vids else V
    h = '<div class="tw"><table><thead><tr><th>Provider</th>' + ''.join(f'<th>{vol(n)}/mo</th>' for n in vols) + '</tr></thead><tbody>'
    mins = {n: min(best(v, n)[0] for v in vs if best(v, n)) for n in vols}
    for v in vs:
        h += f'<tr><td><a href="/vendors/{v["id"]}/">{e(v["name"])}</a>{dag(v)}</td>'
        for n in vols:
            b = best(v, n)
            cls = ' class="best"' if b and b[0] == mins[n] else ''
            h += f'<td{cls} title="{e(b[1]["plan"]) if b else ""}">{money(b[0]) if b else "—"}</td>'
        h += '</tr>'
    return h + '</tbody></table></div>'

def ranked(n):
    r = [(best(v, n), v) for v in V]; r = [(b[0], b[1], v) for b, v in r if b]
    r.sort(key=lambda t: t[0]); return r

shutil.rmtree(D, ignore_errors=True); os.makedirs(D)
open(D + '/style.css', 'w').write(CSS)
DATA = [{'vendor': v['name'], 'id': v['id'], 'source': v['source'], 'checked': v['checked'], 'plans': [{k: p[k] for k in ('plan', 'base', 'incl', 'over')} for p in v['plans']]} for v in V]

# ---------- home
r100 = ranked(100000); r1m = ranked(1000000); r10 = ranked(10000)
cheap_nonses_100 = [t for t in r100 if t[2]['id'] != 'amazon-ses'][0]
spread100 = (r100[0][0], r100[-1][0])
calc_js = """<script>const D=%s;function pc(p,v){if(v<=p.incl)return p.base;if(p.over===null)return null;return p.base+(v-p.incl)/1000*p.over}
function run(){const v=Math.max(0,parseInt(document.getElementById('v').value.replace(/[^0-9]/g,''))||0);const rows=[];for(const d of D){let b=null;for(const p of d.plans){if(p.trap)continue;const c=pc(p,v);if(c!==null&&(b===null||c<b.c))b={c,p:p.plan}}rows.push({n:d.vendor,id:d.id,b})}
rows.sort((a,b)=>(a.b?a.b.c:1e12)-(b.b?b.b.c:1e12));const f=x=>x===null?'—':'$'+x.toLocaleString('en-US',{minimumFractionDigits:x%%1?2:0,maximumFractionDigits:2});
document.getElementById('out').innerHTML='<table><thead><tr><th>#</th><th>Provider</th><th>Cheapest plan at this volume</th><th>Per month</th><th>Per year</th></tr></thead><tbody>'+rows.map((r,i)=>'<tr'+(i==0?' class="best"':'')+'><td>'+(i+1)+'</td><td style="text-align:left"><a href="/vendors/'+r.id+'/">'+r.n+'</a></td><td style="text-align:left">'+(r.b?r.b.p:'no plan')+'</td><td>'+(r.b?f(Math.round(r.b.c*100)/100):'—')+'</td><td>'+(r.b?f(Math.round(r.b.c*1200)/100):'—')+'</td></tr>').join('')+'</tbody></table>'}
document.getElementById('v').addEventListener('input',run);run();</script>""" % json.dumps([{'vendor': v['name'], 'id': v['id'], 'plans': v['plans']} for v in V])
body = f"""<p class="eb" style="margin-top:34px">Transactional email pricing · checked {CHECKED}</p>
<h1>What sending app email really costs, provider by provider</h1>
<p class="lede">Receipts, magic links, password resets. Published prices for {len(V)} transactional email APIs, normalized to a monthly bill at your volume. Every number links to the vendor's own pricing page.</p>
<div class="grid">
<div class="card"><div class="mut">Cheapest at 100k emails/mo</div><div class="big">{money(r100[0][0])}</div><div>{e(r100[0][2]['name'])}, {e(r100[0][1]['plan'])}</div></div>
<div class="card"><div class="mut">Cheapest managed API at 100k</div><div class="big">{money(cheap_nonses_100[0])}</div><div>{e(cheap_nonses_100[2]['name'])}, {e(cheap_nonses_100[1]['plan'])}</div></div>
<div class="card warn"><div class="mut">Amazon SES default for new accounts</div><div class="big">$0.16/1k</div><div>vs $0.10/1k a la carte. <a href="/amazon-ses-essentials-plan/">What changed</a></div></div>
</div>
<h2 id="calc">Calculator</h2><p class="mut">Type your monthly send volume. Picks the cheapest published plan per provider, including overage.</p>
<label>Emails per month<input id="v" inputmode="numeric" value="100000"></label><div id="out" class="tw" style="margin-top:14px"></div>
<p class="note"><sup>†</sup> SendGrid, Mailgun and SMTP2GO only publish entry tiers as readable text, so large volumes use the entry tier plus its published overage rate and may overstate the bill. SES figures exclude attachment data ($0.12/GB). Free plans with daily caps (Resend 100/day, Mailtrap 150/day) are counted only up to their monthly quota.</p>
<h2>Monthly bill by volume</h2>{vol_table()}
<p class="note">Green = cheapest at that volume. Hover a cell for the plan used.</p>
<h2>What the numbers say</h2>
<ul>
<li>At 100k emails a month the published bills run from {money(spread100[0])} ({e(r100[0][2]['name'])}) to {money(spread100[1])} ({e(r100[-1][2]['name'])}).</li>
<li>At 10k a month, {e(r10[1][2]['name'])} ({money(r10[1][0])}) is the cheapest managed API after SES ({money(r10[0][0])}).</li>
<li>At 1M a month the cheapest managed API is {e([t for t in r1m if t[2]['id']!='amazon-ses'][0][2]['name'])} at {money([t for t in r1m if t[2]['id']!='amazon-ses'][0][0])}, against {money(r1m[0][0])} on SES a la carte.</li>
<li>New SES accounts now start on the Essentials plan at $0.16 per 1,000, 60% above the $0.10 a la carte rate, unless the account switches.</li>
</ul>
<h2>Popular comparisons</h2><ul class="links">{''.join(f'<li><a href="/compare/{a}-vs-{b}/">{e(BYID[a]["name"])} vs {e(BYID[b]["name"])}</a></li>' for a,b in [('resend','postmark'),('resend','sendgrid'),('amazon-ses','resend'),('postmark','sendgrid'),('mailgun','sendgrid'),('mailgun','postmark'),('mailersend','mailgun'),('mailtrap','resend')])}</ul>
<div class="card"><h3>Want it in a spreadsheet?</h3><p>Every plan, tier and overage rate above, with source links and a volume calculator built in formulas. <a href="/workbook/">See the workbook</a>.</p></div>
{calc_js}"""
page('/', 'Transactional Email Pricing Compared (Nov 2026): SES, Resend, Postmark, SendGrid, Mailgun | TxMailCost',
     f'Monthly cost to send 10k to 1M transactional emails on {len(V)} providers, from each vendor\'s published pricing. Checked {CHECKED}.', body,
     {'@context': 'https://schema.org', '@type': 'Dataset', 'name': 'Transactional email API pricing', 'url': SITE + '/', 'dateModified': CHECKED,
      'description': 'Published plan prices, included volumes and overage rates for transactional email APIs.', 'distribution': [{'@type': 'DataDownload', 'encodingFormat': 'application/json', 'contentUrl': SITE + '/api/plans.json'}]})

# ---------- vendors
lis = ''
for v in V:
    rows = ''.join(f'<tr><td>{e(p["plan"])}</td><td>{money(p["base"])}</td><td>{volw(p["incl"]) if p["incl"] else "pay per email"}</td><td>{("$%.2f" % p["over"]) if p["over"] is not None else "none / tier up"}</td></tr>' for p in v['plans'])
    alts = ''.join(f'<li><a href="/compare/{"-vs-".join(sorted([v["id"], o["id"]]))}/">{e(v["name"])} vs {e(o["name"])}</a></li>' for o in V if o['id'] != v['id'])
    costs = ''.join(f'<tr><td>{volw(n)}</td><td>{money(best(v,n)[0]) if best(v,n) else "—"}</td><td>{e(best(v,n)[1]["plan"]) if best(v,n) else "—"}</td></tr>' for n in VOLS)
    notes = ''.join(f'<li>{e(x)}</li>' for x in v['notes'])
    body = f"""<p class="eb" style="margin-top:34px"><a href="/vendors/">Providers</a> · checked {v['checked']}</p><h1>{e(v['name'])} pricing for transactional email</h1>
<p class="lede">Published plans, included volume and overage, read from <a href="{v['source']}" rel="nofollow noopener">{e(v['source'])}</a> on {v['checked']}.</p>
<div class="card"><b>Free tier:</b> {e(v['free'])}</div>
<h2>Monthly bill at common volumes</h2><div class="tw"><table><thead><tr><th>Emails/mo</th><th>Cheapest bill{dag(v)}</th><th>Plan used</th></tr></thead><tbody>{costs}</tbody></table></div>
<h2>All published plans</h2><div class="tw"><table><thead><tr><th>Plan</th><th>Base $/mo</th><th>Included emails</th><th>Overage $/1k</th></tr></thead><tbody>{rows}</tbody></table></div>
<h2>Notes</h2><ul>{notes}</ul><h2>Compare {e(v['name'])}</h2><ul class="links">{alts}</ul>"""
    page(f'/vendors/{v["id"]}/', f'{v["name"]} Pricing (Nov 2026): Plans, Overage, Cost per 1,000 Emails | TxMailCost',
         f'{v["name"]} transactional email plans, included volume and overage rates, with monthly cost at 10k to 1M emails. Source: vendor pricing page, checked {v["checked"]}.', body)
    lis += f'<li><a href="/vendors/{v["id"]}/">{e(v["name"])}</a></li>'
page('/vendors/', 'Transactional Email Providers: Pricing Pages | TxMailCost', 'Pricing summaries for each tracked transactional email provider.', f'<h1>Providers</h1><ul class="links">{lis}</ul>')

# ---------- compare pairs
cl = ''
for a, b in itertools.combinations(sorted(BYID), 2):
    A, B = BYID[a], BYID[b]
    lines = []
    for n in VOLS:
        ba, bb = best(A, n), best(B, n)
        if ba and bb:
            if abs(ba[0] - bb[0]) < 0.005: lines.append(f'<li>At {volw(n)} emails/mo they tie at {money(ba[0])}.</li>')
            else:
                lo, hi = (A, ba, bb) if ba[0] < bb[0] else (B, bb, ba), None
                w, wl, ll = lo
                lines.append(f'<li>At {volw(n)} emails/mo, {e(w["name"])} is cheaper: {money(wl[0])} ({e(wl[1]["plan"])}) vs {money(ll[0])}.</li>')
    body = f"""<p class="eb" style="margin-top:34px"><a href="/compare/">Compare</a> · checked {CHECKED}</p><h1>{e(A['name'])} vs {e(B['name'])} pricing</h1>
<p class="lede">Monthly bill for the same transactional volume on each, using the cheapest published plan including overage.</p>
{vol_table([a, b])}<h2>Verdict by volume</h2><ul>{''.join(lines)}</ul>
<div class="grid"><div class="card"><h3>{e(A['name'])}</h3><p><b>Free:</b> {e(A['free'])}</p><ul>{''.join(f'<li>{e(x)}</li>' for x in A['notes'])}</ul><a href="/vendors/{a}/">All {e(A['name'])} plans</a></div>
<div class="card"><h3>{e(B['name'])}</h3><p><b>Free:</b> {e(B['free'])}</p><ul>{''.join(f'<li>{e(x)}</li>' for x in B['notes'])}</ul><a href="/vendors/{b}/">All {e(B['name'])} plans</a></div></div>
<p class="note">Price only. Deliverability, log retention, inbound routing and support differ by plan; check the vendor pages linked above.</p>"""
    page(f'/compare/{a}-vs-{b}/', f'{A["name"]} vs {B["name"]} Pricing (Nov 2026): Cost at 10k to 1M Emails | TxMailCost',
         f'{A["name"]} vs {B["name"]}: monthly transactional email cost at 10k, 50k, 100k, 250k, 500k and 1M emails, from published pricing checked {CHECKED}.', body)
    cl += f'<li><a href="/compare/{a}-vs-{b}/">{e(A["name"])} vs {e(B["name"])}</a></li>'
page('/compare/', 'Transactional Email Pricing Comparisons | TxMailCost', 'Head-to-head pricing for every pair of tracked transactional email providers.', f'<h1>Compare providers</h1><ul class="links">{cl}</ul>')

# ---------- volume pages
for n in VOLS:
    r = ranked(n)
    rows = ''.join(f'<tr{" class=best" if i==0 else ""}><td>{i+1}</td><td><a href="/vendors/{v["id"]}/">{e(v["name"])}</a>{dag(v)}</td><td style="text-align:left">{e(p["plan"])}</td><td>{money(c)}</td><td>{money(round(c*12,2))}</td><td>${c/n*1000:.2f}</td></tr>' for i, (c, p, v) in enumerate(r))
    nav = ' · '.join(f'<a href="/cost/{m}-emails-per-month/">{vol(m)}</a>' for m in VOLS)
    body = f"""<p class="eb" style="margin-top:34px">By volume · checked {CHECKED}</p><h1>Cost to send {volw(n)} transactional emails a month</h1>
<p class="lede">Cheapest published plan on each of {len(V)} providers at exactly {volw(n)} emails a month, overage included.</p><p>Other volumes: {nav}</p>
<div class="tw"><table><thead><tr><th>#</th><th>Provider</th><th style="text-align:left">Plan</th><th>Per month</th><th>Per year</th><th>Effective $/1k</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="note"><sup>†</sup> Entry tier plus published overage; larger tiers not readable, may overstate. SES excludes attachment data. <a href="/#calc">Try another volume</a>.</p>"""
    page(f'/cost/{n}-emails-per-month/', f'Cost to Send {volw(n)} Emails a Month: {len(V)} Transactional Email APIs Compared | TxMailCost',
         f'Monthly cost to send {volw(n)} transactional emails on SES, Resend, Postmark, SendGrid, Mailgun, MailerSend, Mailtrap and SMTP2GO. Cheapest: {r[0][2]["name"]} at {money(r[0][0])}.', body)

# ---------- SES explainer
ses = BYID['amazon-ses']
srows = ''.join(f'<tr><td>{volw(n)}</td><td>{money(plan_cost(ses["plans"][0], n))}</td><td>{money(plan_cost(ses["plans"][1], n))}</td><td>{money(round(plan_cost(ses["plans"][1], n)-plan_cost(ses["plans"][0], n),2))}</td></tr>' for n in VOLS)
body = f"""<p class="eb" style="margin-top:34px">Amazon SES · checked {CHECKED}</p><h1>Amazon SES now defaults new accounts to a 60% higher rate</h1>
<p class="lede">The SES pricing page says new accounts, and account-region pairs with no metered SES activity since Jun 1, 2025, start on the Essentials plan beginning Jul 21, 2026. Essentials charges $0.16 per 1,000 emails for the first 10M. A la carte pricing is $0.10 per 1,000.</p>
<div class="tw"><table><thead><tr><th>Emails/mo</th><th>A la carte ($0.10/1k)</th><th>Essentials ($0.16/1k)</th><th>Extra per month</th></tr></thead><tbody>{srows}</tbody></table></div>
<h2>What Essentials adds</h2><p>The pricing page describes Essentials as a plan to "monitor how emails perform and get insights to help improve deliverability over time." On a la carte, the page lists Virtual Deliverability Manager separately at $0.07 per 1,000 emails for the first 10M.</p>
<h2>Switching</h2><p>The page states you can switch to a la carte at any time, and that if you were defaulted to Essentials without choosing it, your first downgrade or cancellation to a la carte takes effect immediately.</p>
<p class="note">Source: <a href="{ses['source']}" rel="nofollow noopener">{ses['source']}</a>, read {CHECKED}. Attachment data ($0.12/GB) applies on both.</p>"""
page('/amazon-ses-essentials-plan/', 'Amazon SES Essentials Plan: New Default Costs $0.16 vs $0.10 per 1,000 | TxMailCost',
     'Since Jul 21, 2026 new Amazon SES accounts start on the Essentials plan at $0.16 per 1,000 emails, vs $0.10 a la carte. Cost table and how to switch.', body)

# ---------- changes
chg = [{'date': CHECKED, 'title': f'Baseline: {len(V)} providers, {sum(len(v["plans"]) for v in V)} plan rows', 'text': 'First published snapshot. Future price changes will be logged here with old and new values.'},
       {'date': CHECKED, 'title': 'Amazon SES: Essentials plan is the default for new accounts', 'text': 'Per the SES pricing page, from Jul 21, 2026 new accounts start on Essentials at $0.16 per 1,000 emails; a la carte remains $0.10 per 1,000.'}]
page('/changes/', 'Transactional Email Price Change Log | TxMailCost', 'Dated log of transactional email price changes.',
     '<h1>Price log</h1><p class="mut">Subscribe via <a href="/changes/feed.xml">RSS</a>.</p>' + ''.join(f'<div class="card"><div class="note">{c["date"]}</div><h3>{e(c["title"])}</h3><p>{e(c["text"])}</p></div>' for c in chg))
rss = '<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>TxMailCost price log</title><link>' + SITE + '/changes/</link><description>Transactional email price changes</description>' + ''.join(f'<item><title>{e(c["title"])}</title><link>{SITE}/changes/</link><guid isPermaLink="false">{c["date"]}-{i}</guid><pubDate>{datetime.datetime.strptime(c["date"],"%Y-%m-%d").strftime("%a, %d %b %Y 12:00:00 -0500")}</pubDate><description>{e(c["text"])}</description></item>' for i, c in enumerate(chg)) + '</channel></rss>'
open(D + '/changes/feed.xml', 'w').write(rss)

# ---------- about
page('/about/', 'Methodology | TxMailCost', 'How TxMailCost reads and normalizes transactional email prices.', f"""<h1>Methodology</h1>
<ul><li>Prices are read from each provider's public pricing page (or the calculator data that page loads) and stored with the source URL and check date.</li>
<li>For a volume, each plan's bill is base price if the volume fits its quota, otherwise base plus published overage per 1,000. The cheapest plan per provider is shown.</li>
<li>Plans with no published overage (free tiers, Mailtrap tiers) only count up to their quota.</li>
<li>Where a provider shows only entry tiers as text (SendGrid, Mailgun, SMTP2GO) the bill is entry tier plus overage and is marked <sup>†</sup> as a possible overstatement.</li>
<li>Monthly billing, USD, before tax. Annual discounts, credits and dedicated IPs are noted per provider but not included.</li>
<li>No numbers are estimated or invented. If a price could not be read, it is left out.</li></ul>
<p>Found a wrong price? <a href="mailto:basileion.ops@gmail.com?subject=TxMailCost%20correction">Email a correction</a> with the vendor link.</p>""")

# ---------- workbook (product) + dl
cta = f'<p><a class="btn" href="{PAY}">Buy the workbook: $19</a></p><p class="note">One-time payment via Stripe. Download link shown right after checkout.</p>' if PAY else '<p class="mut">Checkout coming shortly.</p>'
page('/workbook/', 'Transactional Email Pricing Workbook (XLSX + CSV) | TxMailCost', f'Spreadsheet of {sum(len(v["plans"]) for v in V)} transactional email plans from {len(V)} providers, with sources and a volume calculator.', f"""<p class="eb" style="margin-top:34px">Workbook · snapshot {CHECKED}</p><h1>The transactional email pricing workbook</h1>
<p class="lede">All {sum(len(v["plans"]) for v in V)} plan rows from {len(V)} providers in one spreadsheet: base price, included emails, overage per 1,000, source URL and check date. A calculator sheet prices any volume across every provider with live formulas.</p>
<ul><li>XLSX (Excel, Google Sheets, Numbers) plus a CSV</li><li>Calculator sheet: enter a volume, see each provider's cheapest plan and bill</li><li>Every row links to the vendor page it came from</li><li>Same data as this site, in a form you can paste into a budget or vendor review</li></ul>
{cta}<p class="note">The site and <a href="/api/plans.json">JSON data</a> stay free. The workbook is for people who want it as a file.</p>""")

os.makedirs(D + f'/dl/{TOKEN}', exist_ok=True)
page(f'/dl/{TOKEN}/', 'Your TxMailCost workbook', 'Download', f'<h1>Thanks. Your downloads:</h1><p><a class="btn" href="/dl/{TOKEN}/txmailcost-workbook-{CHECKED}.xlsx">Download XLSX</a> &nbsp; <a href="/dl/{TOKEN}/txmailcost-plans-{CHECKED}.csv">Download CSV</a></p><p class="mut">Bookmark this page. Questions: basileion.ops@gmail.com</p>', noindex=True)

# ---------- data / seo files
os.makedirs(D + '/api', exist_ok=True)
json.dump({'checked': CHECKED, 'unit': 'USD per month; overage USD per 1,000 emails', 'providers': DATA}, open(D + '/api/plans.json', 'w'), indent=1)
open(D + '/robots.txt', 'w').write(f'User-agent: *\nDisallow: /dl/\nSitemap: {SITE}/sitemap.xml\n')
open(D + '/sitemap.xml', 'w').write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{SITE}{u}</loc><lastmod>{CHECKED}</lastmod></url>' for u in URLS) + '</urlset>')
open(D + '/llms.txt', 'w').write(f'# TxMailCost\n> Published transactional email API pricing for {len(V)} providers, normalized to monthly cost by volume. Checked {CHECKED}.\n\n- Data: {SITE}/api/plans.json\n- Cost at 100k/mo: {SITE}/cost/100000-emails-per-month/\n- SES Essentials default: {SITE}/amazon-ses-essentials-plan/\n' + ''.join(f'- {v["name"]}: {SITE}/vendors/{v["id"]}/ (source {v["source"]})\n' for v in V))
open(D + '/_headers', 'w').write('/dl/*\n  X-Robots-Tag: noindex, nofollow\n/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n')
page('/404.html'.replace('.html', '/'), 'Not found | TxMailCost', 'Not found', '<h1>Page not found</h1><p><a href="/">Back to the calculator</a></p>', noindex=True)
shutil.move(D + '/404/index.html', D + '/404.html'); os.rmdir(D + '/404')
K=open(ROOT+'/indexnow.key').read().strip();open(D+f'/{K}.txt','w').write(K)
print('pages', len(URLS))
