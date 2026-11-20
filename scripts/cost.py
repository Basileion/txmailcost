import json
V=json.load(open('/workspace/txmailcost/data/vendors.json'))
def plan_cost(p,v):
    if v<=p['incl']: return p['base']
    if p['over'] is None: return None
    return round(p['base']+(v-p['incl'])/1000*p['over'],2)
def best(vendor,v,include_trap=False):
    r=[]
    for p in vendor['plans']:
        if p.get('trap') and not include_trap: continue
        c=plan_cost(p,v)
        if c is not None: r.append((c,p))
    if not r: return None
    r.sort(key=lambda x:(x[0],x[1]['incl']))
    return r[0]
