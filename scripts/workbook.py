import json,csv,os,sys
sys.path.insert(0,os.path.dirname(__file__))
from cost import V
from openpyxl import Workbook
from openpyxl.styles import Font,PatternFill,Alignment
ROOT='/workspace/txmailcost';T=open(ROOT+'/.dl_token').read().strip();C='2026-11-20'
out=f'{ROOT}/dist/dl/{T}';os.makedirs(out,exist_ok=True)
rows=[]
for v in V:
    for p in v['plans']:
        rows.append([v['name'],p['plan'],p['base'],p['incl'],p['over'] if p['over'] is not None else '',('Yes' if p['over'] is not None else 'No (tier up)'),v['source'],v['checked'],'; '.join(v['notes'][:1]) if p.get('trap') else ''])
hdr=['Provider','Plan','Base USD/mo','Included emails/mo','Overage USD per 1,000','Overage allowed','Source','Checked','Note']
with open(f'{out}/txmailcost-plans-{C}.csv','w',newline='') as f:
    w=csv.writer(f);w.writerow(hdr);w.writerows(rows)
wb=Workbook();ws=wb.active;ws.title='Plans';ws.append(hdr)
for r in rows: ws.append(r)
b=Font(bold=True);fill=PatternFill('solid',fgColor='E8EEF7')
for c in ws[1]: c.font=b;c.fill=fill
for col,wd in zip('ABCDEFGHI',[18,34,12,18,20,16,48,12,60]): ws.column_dimensions[col].width=wd
n=len(rows)+1
ws2=wb.create_sheet('Calculator',0)
ws2['A1']='TxMailCost calculator';ws2['A1'].font=Font(bold=True,size=14)
ws2['A3']='Emails per month';ws2['B3']=100000;ws2['B3'].fill=PatternFill('solid',fgColor='FFF2CC');ws2['A3'].font=b
ws2['A4']='Edit the yellow cell. Cost per plan = base if volume fits the quota, else base + overage. Plans without overage only count up to quota. Amazon SES Essentials row is the new-account default; a la carte is cheaper.'
ws2.append([]);ws2.append(['Provider','Plan','Monthly cost at volume','Annual'])
for c in ws2[6]: c.font=b;c.fill=fill
for i in range(2,n+1):
    r=i+5
    ws2[f'A{r}']=f'=Plans!A{i}';ws2[f'B{r}']=f'=Plans!B{i}'
    ws2[f'C{r}']=f'=IF($B$3<=Plans!D{i},Plans!C{i},IF(Plans!F{i}="Yes",Plans!C{i}+($B$3-Plans!D{i})/1000*Plans!E{i},"n/a"))'
    ws2[f'D{r}']=f'=IF(ISNUMBER(C{r}),C{r}*12,"n/a")'
    ws2[f'C{r}'].number_format='$#,##0.00';ws2[f'D{r}'].number_format='$#,##0.00'
ws2['F6']='Cheapest overall';ws2['F6'].font=b;ws2['F7']=f'=MIN(C7:C{n+5})';ws2['F7'].number_format='$#,##0.00'
for col,wd in zip('ABCDF',[18,34,22,16,18]): ws2.column_dimensions[col].width=wd
ws3=wb.create_sheet('About');ws3['A1']=f'Snapshot checked {C}. Sources are each vendor pricing page (see Plans!G). SendGrid, Mailgun and SMTP2GO show only entry tiers as text; large volumes on those use entry tier + overage and may overstate. Verify before buying. https://txmailcost.pages.dev/about/'
wb.save(f'{out}/txmailcost-workbook-{C}.xlsx');print(len(rows),'rows')
