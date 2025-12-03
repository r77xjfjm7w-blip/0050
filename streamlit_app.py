import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Supertrend 三線共振", layout="centered")
st.title("Supertrend 三線共振系統")
st.markdown("0050 / 標普500 / QQQ • 即時更新")

def get_supertrend(ticker, period, multiplier):
    try:
        df = yf.download(ticker, period="400d", progress=False, auto_adjust=True)
        if len(df) < 50: return False, 0
        high, low, close = df['High'], df['Low'], df['Close']
        tr = pd.concat([high-low, abs(high-close.shift()), abs(low-close.shift())], axis=1).max(axis=1)
        atr = tr.ewm(alpha=1/period, adjust=False).mean()
        hl2 = (high + low)/2
        upper = hl2 + multiplier*atr
        lower = hl2 - multiplier*atr
        trend = [True]
        for i in range(1,len(df)):
            curr = close.iloc[i]
            if curr > upper.iloc[i-1]: t = True
            elif curr < lower.iloc[i-1]: t = False
            else: 
                t = trend[-1]
                if t: lower.iloc[i] = max(lower.iloc[i], lower.iloc[i-1])
                else: upper.iloc[i] = min(upper.iloc[i], upper.iloc[i-1])
            trend.append(t)
        return trend[-1], round(close.iloc[-1], 2)
    except: return None, 0

symbols = {"0050 元大台灣50":"0050.TW", "標普500指數":"^GSPC", "QQQ 納斯達克100":"QQQ"}

for name, t in symbols.items():
    with st.container(border=True):
        c1, c2 = st.columns([2,1])
        c1.subheader(name)
        s1, price = get_supertrend(t,11,2.0)
        if s1 is None:
            st.error("暫時抓不到資料")
            continue
        s2, _ = get_supertrend(t,10,1.0)
        s3, _ = get_supertrend(t,12,3.0)
        green = sum([s1, s2, s3])
        c2.metric("現價", price)
        st.write(f"標準線 (11,2.0) → {'上' if s1 else '下'}")
        st.write(f"敏感線 (10,1.0) → {'上' if s2 else '下'}")
        st.write(f"保守線 (12,3.0) → {'上' if s3 else '下'}")
        if green==3: st.success("3/3 全綠 → 強多頭")
        elif green==2: st.info("2/3 綠 → 多頭可進")
        elif green==1: st.warning("1/3 綠 → 震盪觀望")
        else: st.error("0/3 → 空頭注意")

st.caption(f"更新時間：{datetime.now().strftime('%Y-%m-%d %H:%M')} 臺北時間")
