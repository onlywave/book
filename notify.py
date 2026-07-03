#!/usr/bin/env python3
"""NOTIFICHE EMAIL del Book 4-Sleeve.
- build_body(sig, kind, capital): costruisce oggetto + testo + HTML dell'email.
- rileva se il segnale è CAMBIATO rispetto alla foto precedente.
- invia via SMTP Gmail (credenziali da variabili d'ambiente: MAIL_USERNAME, MAIL_PASSWORD).
Uso (nel workflow):  python notify.py --old /tmp/old.json --new docs/signal.json [--force] [--weekly]
--force  = invia comunque (test)      --weekly = email di recap settimanale
Se mancano le credenziali stampa solo l'anteprima (utile per generare la bozza)."""
import os, json, argparse, smtplib, ssl, datetime as dt
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

DASH="https://onlywave.github.io/book/"
NOMI={"BTC":"Bitcoin","ETH":"Ethereum","SPX":"S&P 500","XAU":"Oro"}
COME={"BTC":"exchange o ETF cripto","ETH":"exchange o ETF cripto","SPX":"ETF (es. CSSPX/VUSA)","XAU":"ETF oro (es. SGLD)"}

def azione(n,s,on):
    if not on: return "VENDI TUTTO","protezione attiva: chiudi la posizione"
    if s["role"]=="detenuto": return "MANTIENI","tienilo sempre in portafoglio"
    if s["signal"]=="LONG": return "COMPRA e TIENI","prezzo sopra la media"
    return "STAI FUORI","prezzo sotto la media: resta liquido"

def fingerprint(sig):
    if not sig: return None
    sl=sig.get("sleeves",{})
    return (sig.get("l3",{}).get("on"),
            tuple(sorted((n,s.get("signal"),round(s.get("target_frac",0),3)) for n,s in sl.items())))

def build_body(sig, kind, capital=100000):
    on=sig["l3"]["on"]; bt=sig["backtest"]; sl=sig["sleeves"]
    today=dt.date.today().strftime("%d/%m/%Y")
    titolo={"alert":"***ALLERTA SEGNALE***","weekly":"***BOOK — RECAP SETTIMANALE***","test":"***ALLERTA SEGNALE*** (TEST)"}[kind]
    subject=titolo
    invested=0.0; righe=[]; hrows=[]
    for n,s in sl.items():
        frac=(s["target_frac"] if on else 0.0); eur=capital*frac; invested+=frac
        act,perche=azione(n,s,on)
        med=f"media {s['window']}gg" if s.get("window") else "detenuto (B&H)"
        px=f"{s['price']:,.0f}" if s['price']>=100 else f"{s['price']:,.2f}"
        vs=f" (prezzo {px} vs {s['ma']:,.0f})" if s.get("ma") else ""
        trig=""
        if s.get("ma"):
            trig=(f"\n      🎯 livello di scatto: COMPRA sopra {s['ma']:,.0f}" if s["signal"]=="FLAT"
                  else f"\n      🎯 livello di scatto: ESCI sotto {s['ma']:,.0f}")
        righe.append(f"  • {NOMI[n]:<9} → {act:<13} {frac*100:>3.0f}%  = € {eur:,.0f}   [{med}]{vs}{trig}")
        col={"COMPRA e TIENI":"#2ec16b","MANTIENI":"#4b93ff","STAI FUORI":"#8fa0ba","VENDI TUTTO":"#f2555a"}[act]
        htrig=""
        if s.get("ma"):
            htrig=(f"<br><span style='color:#2ec16b;font-size:12px'>🎯 compra sopra {s['ma']:,.0f}</span>" if s["signal"]=="FLAT"
                   else f"<br><span style='color:#f2555a;font-size:12px'>🎯 esci sotto {s['ma']:,.0f}</span>")
        hrows.append(f"<tr><td style='padding:8px 10px'><b>{NOMI[n]}</b><br><span style='color:#889;font-size:12px'>compra con: {COME[n]}</span></td>"
                     f"<td style='padding:8px 10px;color:{col};font-weight:700'>{act}</td>"
                     f"<td style='padding:8px 10px'>{med}{('<br><span style=\"color:#889;font-size:12px\">'+px+' vs '+format(s['ma'],',.0f')+'</span>') if s.get('ma') else ''}{htrig}</td>"
                     f"<td style='padding:8px 10px;text-align:right'><b>{frac*100:.0f}%</b><br>€ {eur:,.0f}</td></tr>")
    cash=max(0,1-invested)
    righe.append(f"  • {'Liquidità':<9} → TIENI FERMA {cash*100:>3.0f}%  = € {capital*cash:,.0f}")

    stato = "🟢 OPERATIVO" if on else "🔴 PROTEZIONE ATTIVA (tutto liquido)"
    intro = ("Un segnale è CAMBIATO. Aggiorna il portafoglio come indicato." if kind=="alert"
             else "Recap settimanale. Verifica che il conto sia allineato a queste quote." if kind=="weekly"
             else "Email di TEST del sistema di notifica. Ecco come sarà una vera allerta.")

    text=f"""{titolo}
{'='*52}
Book 4·Sleeve — {today}   ·   Stato: {stato}

{intro}

COSA FARE (capitale di riferimento € {capital:,.0f}):
{chr(10).join(righe)}

{'' if on else '>>> PROTEZIONE ATTIVA: resta 100% liquido e attendi il rientro automatico.'}

QUANDO/COME:
  - Allinea il conto alle percentuali sopra (banda ±5%).
  - S&P 500 e Oro = ETF; Bitcoin/Ethereum = exchange o ETF cripto.
  - Cadenza: 1 controllo a settimana, o subito su cambio segnale.

TRACK RECORD (walk-forward, costi inclusi, {bt['years']} anni):
  CAGR +{bt['cagr']}%  ·  Sharpe {bt['sharpe']}  ·  perdita max {bt['maxdd']}%

Dashboard live: {DASH}

— Strumento informativo/educativo, non è consulenza finanziaria. Decisioni e ordini sono tuoi. —
"""
    html=f"""<div style="font-family:-apple-system,Segoe UI,sans-serif;max-width:640px;margin:auto;background:#0d121d;color:#eaf0f8;border-radius:14px;overflow:hidden;border:1px solid #243147">
<div style="background:linear-gradient(120deg,#16233b,#0d1420);padding:18px 22px;border-bottom:1px solid #243147">
 <div style="color:#e9be5c;font-weight:800;letter-spacing:1px">{titolo}</div>
 <div style="font-size:13px;color:#8fa0ba;margin-top:3px">Book 4·Sleeve — {today} · {stato}</div></div>
<div style="padding:18px 22px">
 <p style="font-size:14px;color:#cfd8e6">{intro}</p>
 <table style="width:100%;border-collapse:collapse;font-size:14px;background:#121a29;border-radius:10px;overflow:hidden">
 <tr style="background:#182236;color:#8fa0ba;font-size:11px;text-transform:uppercase">
  <td style="padding:8px 10px">Asset</td><td style="padding:8px 10px">Azione</td><td style="padding:8px 10px">Media</td><td style="padding:8px 10px;text-align:right">Quota</td></tr>
 {''.join(hrows)}
 <tr style="border-top:1px solid #243147"><td style="padding:8px 10px" colspan="3"><b>Liquidità (cash)</b></td><td style="padding:8px 10px;text-align:right"><b>{cash*100:.0f}%</b><br>€ {capital*cash:,.0f}</td></tr>
 </table>
 <p style="font-size:13px;color:#8fa0ba;margin-top:14px"><b style="color:#e9be5c">Come:</b> allinea il conto a queste quote (banda ±5%). S&P 500 e Oro con ETF; cripto da exchange/ETF. Controllo settimanale o subito su cambio segnale.</p>
 <p style="font-size:13px;color:#8fa0ba"><b style="color:#e9be5c">Track record:</b> CAGR +{bt['cagr']}% · Sharpe {bt['sharpe']} · perdita max {bt['maxdd']}% ({bt['years']} anni, costi inclusi).</p>
 <a href="{DASH}" style="display:inline-block;margin-top:6px;background:#e9be5c;color:#1a1200;text-decoration:none;font-weight:800;padding:10px 18px;border-radius:10px">📊 Apri la Sala Operativa</a>
 <p style="font-size:11px;color:#63728c;margin-top:16px">Strumento informativo/educativo, non è consulenza finanziaria. Le decisioni e gli ordini sono tuoi.</p>
</div></div>"""
    return subject, text, html

def send_email(subject, text, html, to_list):
    user=os.environ.get("MAIL_USERNAME"); pw=os.environ.get("MAIL_PASSWORD")
    if not user or not pw:
        print("[notify] credenziali SMTP assenti: anteprima soltanto, nessun invio."); return False
    msg=MIMEMultipart("alternative"); msg["Subject"]=subject; msg["From"]=user; msg["To"]=", ".join(to_list)
    msg.attach(MIMEText(text,"plain","utf-8")); msg.attach(MIMEText(html,"html","utf-8"))
    ctx=ssl.create_default_context()
    with smtplib.SMTP("smtp.gmail.com",587) as srv:
        srv.starttls(context=ctx); srv.login(user,pw); srv.sendmail(user,to_list,msg.as_string())
    print(f"[notify] email inviata a {to_list}"); return True

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--old"); ap.add_argument("--new",required=True)
    ap.add_argument("--force",action="store_true"); ap.add_argument("--weekly",action="store_true")
    ap.add_argument("--capital",type=float,default=100000); ap.add_argument("--print",action="store_true")
    a=ap.parse_args()
    new=json.load(open(a.new)); old=json.load(open(a.old)) if a.old and os.path.exists(a.old) else None
    changed = fingerprint(old)!=fingerprint(new)
    kind = "test" if a.force else ("alert" if changed else "weekly")
    to=[x.strip() for x in os.environ.get("MAIL_TO","ebferreri@egonon.ch,ebferreri@gmail.com").split(",") if x.strip()]
    subject,text,html=build_body(new,kind,a.capital)
    if a.print:
        print("SUBJECT:",subject); print(text); raise SystemExit
    if a.force or changed or a.weekly:
        motivo="TEST" if a.force else ("CAMBIO SEGNALE" if changed else "RECAP SETTIMANALE")
        print(f"[notify] motivo invio: {motivo}")
        send_email(subject,text,html,to)
    else:
        print("[notify] nessun cambio segnale e non è il giorno del recap: niente email.")
