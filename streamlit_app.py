import streamlit as st
import yfinance as yf
import numpy as np
from datetime import datetime

st.set_page_config(page_title="Supertrend 三線共振", layout="centered")
st.title("Supertrend 三線共振神器")
st.markdown("**0050．標普500．QQQ｜手機專用｜永不卡版**")

@st.cache_data(ttl=600)
def calc(ticker, atr_p, mult):
    try:
        df = yf.download(ticker, period="400d", progress=False, threads=False)
        if len(df)<50: return False, 0
        h,l,c = df.High.values, df.Low.values, df.Close.values
        tr = np.maximum.reduce([h-l, np.abs(h-np.roll(c,1)), np.abs(l-np.roll(c,1))])
        tr[0] = h[0]-l[0]
        atr = np.zeros_like(c)
        atr[0] = tr[:atr_p].mean()
        for i in range(1,len(c)): 
            atr[i] = (atr[i-1]*(atr_p-1) + tr[i]) / atr_p
        up = (h+l)/2 + mult*atr
        dn = (h+l)/2 - mult*atr
        trend = np.full(len(c), True)
        for i in range(1,len(c)):
            if c[i] > up[i-1]: trend[i] = True
            elif c[i] < dn[i-1]: trend[i] = False
            else:
                trend[i] = trend[i-1]
                if trend[i]: dn[i] = max(dn[i], dn[i-1])
                else: up[i] = min(up[i], up[i-1])
        return trend[-1], round(c[-1],2)
    except:
        return None, 0

symbols = {"0050 元大台灣50":"0050.TW", "標普500指數":"^GSPC", "QQQ 納斯達克100":"QQQ"}

for name,t in symbols.items():
    with st.container(border=True):
        a,b = st.columns([2,1])
        a.subheader(name)
        s1,p = calc(t,11,2.0)
        s2,_ = calc(t,10,1.0)
        s3,_ = calc(t,12,3.0)
        if s1 is None:
            st.error("暫無資料，5分鐘後重試")
            continue
        green = sum([s1,s2,s3])
        b.metric("現價",f"{p:,}")
        st.write(f"標準(11,2.0) → {'上' if s1 else '下'}")
        st.write(f"敏感(10,1.0) → {'上' if s2 else '下'}")
        st.write(f"保守(12,3.0) → {'上' if s3 else '下'}")
        if green==3: st.success(f"{green}/3 全綠 → 強多頭")
        elif green==2: st.info(f"{green}/3 → 多頭可進")
        elif green==1: st.warning(f"{green}/3 → 震盪觀望")
        else: st.error(f"{green}/3 → 空頭")

st.caption(f"更新時間：{datetime.now().strftime('%Y-%m-%d %H:%M')} 臺北時間")