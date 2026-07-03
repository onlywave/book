#!/usr/bin/env python3
"""BOOK 4-SLEEVE — calcolo giornaliero per la dashboard web (GitHub Actions).
Autosufficiente: dati da yahoo, REGOLA L1 (minimax-plateau walk-forward),
L2 vol-target, L3 shadow con isteresi. Scrive docs/signal.json (+ storia finestre).
Nessun ordine, nessuna credenziale: solo segnali."""
import json, os, datetime as dt
import numpy as np, pandas as pd

COST=0.0010; WMIN,WMAX=9,400; STEP=20; KPLAT=3; NSUB=3; TRAIN=365; WEEK=7; PPY=365
VT=0.30; VOL_WIN=20; W=0.25; TRAIL=0.15; REARM=0.09; KILL=0.05
TIMED={"BTC":"BTC-USD","ETH":"ETH-USD"}; HELD={"SPX":"^GSPC","XAU":"GC=F"}
BINANCE={"BTC":"BTCUSDT","ETH":"ETHUSDT"}
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"docs")

def load_yf(t):
    import yfinance as yf, time
    for _ in range(4):
        df=yf.download(t,period="max",progress=False,auto_adjust=True)
        if len(df)>100: break
        time.sleep(10)
    else: raise RuntimeError(f"download {t} fallito")
    s=df["Close"][t] if isinstance(df.columns,pd.MultiIndex) else df["Close"]
    s=s.dropna().astype(float); s=s[s.values>=1.0]
    if s.index.tz is not None: s.index=s.index.tz_convert(None)
    s.index=s.index.normalize(); return s[~s.index.duplicated()]

def build_pos(close):
    T=len(close); ret=np.zeros(T); ret[1:]=close[1:]/close[:-1]-1
    Ws=np.arange(WMIN,WMAX+1); cs=np.concatenate([[0.0],np.cumsum(close)])
    P=np.zeros((T,len(Ws))); R=np.full((T,len(Ws)),np.nan)
    for j,w in enumerate(Ws):
        ma=np.full(T,np.nan); ma[w-1:]=(cs[w:]-cs[:-w])/w
        sig=(close>ma).astype(float); pos=np.roll(sig,1); pos[0]=0; pos[:w]=0; P[:,j]=pos
        turn=np.abs(np.concatenate([[0.0],np.diff(pos)])); R[:,j]=pos*ret-turn*COST
    return Ws,P,R,ret
def pick(Rtr):
    n=Rtr.shape[0]; b=[(n*i//NSUB,n*(i+1)//NSUB) for i in range(NSUB)]; subs=[]
    for a,c in b:
        s=Rtr[a:c]; mu=s.mean(0); sd=s.std(0)
        with np.errstate(invalid="ignore"): subs.append(np.where(sd>0,mu/sd*np.sqrt(PPY),np.nan))
    mn=np.min(np.vstack(subs),0)
    if not np.isfinite(mn).any(): return None
    K=np.ones(2*KPLAT+1)/(2*KPLAT+1); return int(np.argmax(np.convolve(np.nan_to_num(mn,nan=-9.0),K,"same")))
def wf_pos(Ws,P,R):
    T=R.shape[0]; pos=np.zeros(T); act=int(np.argmin(np.abs(Ws-200))); i=TRAIN; j=act
    while i<T:
        s=pick(R[i-TRAIN:i])
        if s is not None: act=act+int(np.clip(s-act,-STEP,STEP))
        j=min(max(act,0),R.shape[1]-1); hi=min(i+WEEK,T); pos[i:hi]=P[i:hi,j]; i=hi
    return pos,int(Ws[j])
def l3_shadow(r):
    r=np.asarray(r,float); T=len(r); out=np.zeros(T); eq=1.0; pk=1.0; on=True; ev=0; dd=0.0
    for t in range(T):
        out[t]=r[t] if on else 0.0
        eq*=1+r[t]; pk=max(pk,eq); dd=eq/pk-1
        if on and (dd<-TRAIL or r[t]<-KILL): on=False; ev+=1
        elif (not on) and dd>-REARM: on=True
    return out,on,ev,dd

px={n:load_yf(t) for n,t in {**TIMED,**HELD}.items()}
start=max(px[n].index[0] for n in TIMED); end=min(px[n].index[-1] for n in px)
cal=pd.date_range(start,end,freq="D")
sleeves={}; info={}
for n,s in px.items():
    ret=s.reindex(cal).ffill().pct_change().fillna(0.0)
    vol=(ret.rolling(VOL_WIN).std()*np.sqrt(PPY)).shift(1)
    size=(VT/vol).clip(upper=1.0).fillna(0.0)
    if n in TIMED:
        Ws,P,R,_=build_pos(s.values)
        posn,w_act=wf_pos(Ws,P,R)
        pos=pd.Series(posn,index=s.index).reindex(cal).ffill().fillna(0.0)
        ma=float(s.rolling(w_act).mean().iloc[-1])
    else:
        pos=pd.Series(1.0,index=cal); w_act=None; ma=None
    expo=W*pos*size
    sleeves[n]=(expo.shift(1)*ret) - expo.diff().abs().fillna(0)*COST
    info[n]={"role":"timato" if n in TIMED else "detenuto",
             "signal":("LONG" if pos.iloc[-1]>0 else "FLAT") if n in TIMED else "HOLD",
             "window":w_act,"ma":ma,"price":float(s.iloc[-1]),
             "size_l2":round(float(size.iloc[-1]),3),"weight":W,
             "target_frac":round(float(pos.iloc[-1]*size.iloc[-1]*W),4),
             "asof":str(s.index[-1].date()),"binance":BINANCE.get(n)}
bk=pd.DataFrame(sleeves).sum(axis=1).iloc[TRAIN:]
managed,on,ev,dds=l3_shadow(bk.values)
if not on:
    for n in info: info[n]["target_frac"]=0.0
eq=np.cumprod(1+managed); yrs=len(managed)/PPY
cagr=(eq[-1]**(1/yrs)-1)*100; sh=managed.mean()/managed.std()*np.sqrt(PPY)
mdd=float((eq/np.maximum.accumulate(eq)-1).min()*100)
eqs=pd.Series(eq,index=bk.index).resample("W").last().dropna()

# storia finestre (append)
os.makedirs(OUT,exist_ok=True)
whp=os.path.join(OUT,"window_history.json")
wh=json.load(open(whp)) if os.path.exists(whp) else []
today=str(dt.date.today())
if not any(r["date"]==today for r in wh):
    wh.append({"date":today,**{n:info[n]["window"] for n in TIMED}})
    wh=wh[-500:]
json.dump(wh,open(whp,"w"))

json.dump({
 "generated_utc":dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
 "l3":{"on":bool(on),"dd_shadow":round(float(dds),4),"trail":TRAIL,"rearm":REARM,
       "label":"ON" if on else "VETO ATTIVO: book FLAT finché il dd non risale sopra -9%"},
 "backtest":{"cagr":round(cagr,1),"sharpe":round(float(sh),2),"maxdd":round(mdd,0),
             "start":str(bk.index[0].date()),"years":round(yrs,1)},
 "sleeves":info,
 "equity":[[str(d.date()),round(float(v),4)] for d,v in eqs.items()],
},open(os.path.join(OUT,"signal.json"),"w"),indent=1)
print("OK signal.json —","L3",("ON" if on else "VETO"),"·",
      " ".join(f"{n}:{info[n]['signal']}" for n in info))
