import yfinance as yf
import pandas as pd
import json
from datetime import datetime
import time

def analyze_ticker(ticker, category):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="6mo")
    info = stock.info
    
    if hist.empty:
        return None

    current_price = float(hist['Close'].iloc[-1])
    
    # 1. Fundamental Check
    pe_ratio = info.get('forwardPE') or info.get('trailingPE')
    
    # FIX BUG DIVIDEN
    div_yield = info.get('dividendYield', 0)
    if div_yield is None:
        div_yield = 0
    div_yield = float(div_yield)
    
    if div_yield > 0.5:
        if div_yield > 50:
            div_yield = div_yield / 100
    # else: sudah dalam desimal (0.03 = 3%)
    
    # 2. Accumulation Detection
    recent_14 = hist.tail(14)
    up_vol = recent_14[recent_14['Close'] > recent_14['Open']]['Volume'].sum()
    down_vol = recent_14[recent_14['Close'] <= recent_14['Open']]['Volume'].sum()
    
    low_50 = float(hist.tail(50)['Low'].min())
    distance_from_low = ((current_price - low_50) / low_50) * 100
    
    is_accumulating = bool((up_vol > down_vol * 1.2) and (distance_from_low < 10))
    
    # 3. Action Zones
    support = float(hist.tail(30)['Low'].min())
    resistance = float(hist.tail(30)['High'].max())
    
    buy_zone = round(support * 1.01, 2)
    target_sell = round(max(resistance, current_price * 1.06), 2)
    stop_loss = round(support * 0.97, 2)
    
    profit_pct = ((target_sell - buy_zone) / buy_zone) * 100

    # Logika Verdict
    if pe_ratio:
        pe_float = float(pe_ratio)
        if pe_float < 0:
            verdict = "N/A (ETF)"
            pe_display = "N/A"
        else:
            pe_display = round(pe_float, 2)
            verdict = "MURAH" if pe_float < 18 else "WAJAR" if pe_float < 25 else "MAHAL"
    else:
        verdict = "N/A (ETF)"
        pe_display = "N/A"

    return {
        "ticker": ticker,
        "name": info.get('shortName', ticker),
        "category": category,
        "current_price": round(current_price, 2),
        "fundamental": {
            "pe_ratio": pe_display,
            "dividend_yield": f"{div_yield * 100:.2f}%",
            "verdict": verdict
        },
        "collector_status": {
            "is_accumulating": is_accumulating,
            "status_text": "🔥 AKUMULASI BANDAR" if is_accumulating else "⚪ NETRAL",
            "up_vol_pct": round((float(up_vol) / (float(up_vol) + float(down_vol))) * 100, 1) if (up_vol + down_vol) > 0 else 0,
            "distance_from_low": f"{distance_from_low:.1f}%"
        },
        "action_plan": {
            "buy_zone": buy_zone,
            "target_sell": target_sell,
            "stop_loss": stop_loss,
            "potential_profit": f"{profit_pct:.1f}%"
        }
    }

def main():
    watchlist = [
        {"ticker": "SCHD", "category": "Dividen Growth"},
        {"ticker": "VIG", "category": "Dividen Growth"},
        {"ticker": "DGRO", "category": "Dividen Growth"},
        {"ticker": "NOBL", "category": "Dividen Growth"},
        {"ticker": "DVY", "category": "Dividen Growth"},
        {"ticker": "HDV", "category": "Dividen Growth"},
        {"ticker": "SPY", "category": "Broad Market"},
        {"ticker": "VOO", "category": "Broad Market"},
        {"ticker": "IVV", "category": "Broad Market"},
        {"ticker": "RSP", "category": "Broad Market"},
        {"ticker": "VTI", "category": "Broad Market"},
        {"ticker": "QQQ", "category": "Tech & Growth"},
        {"ticker": "QQQM", "category": "Tech & Growth"},
        {"ticker": "VGT", "category": "Tech & Growth"},
        {"ticker": "XLK", "category": "Tech & Growth"},
        {"ticker": "SMH", "category": "Tech & Growth"},
        {"ticker": "SOXX", "category": "Tech & Growth"},
        {"ticker": "ARKK", "category": "Tech & Growth"},
        {"ticker": "XLF", "category": "Sektor"},
        {"ticker": "XLV", "category": "Sektor"},
        {"ticker": "XLE", "category": "Sektor"},
        {"ticker": "XLI", "category": "Sektor"},
        {"ticker": "XLC", "category": "Sektor"},
        {"ticker": "XLY", "category": "Sektor"},
        {"ticker": "XLP", "category": "Sektor"},
        {"ticker": "XLRE", "category": "Sektor"},
        {"ticker": "XLU", "category": "Sektor"},
        {"ticker": "XLB", "category": "Sektor"},
        {"ticker": "IWM", "category": "Small Cap"},
        {"ticker": "VB", "category": "Small Cap"},
        {"ticker": "VXUS", "category": "International"},
        {"ticker": "VEA", "category": "International"},
        {"ticker": "VWO", "category": "International"},
        {"ticker": "EFA", "category": "International"},
        {"ticker": "EEM", "category": "International"},
        {"ticker": "BND", "category": "Bond"},
        {"ticker": "AGG", "category": "Bond"},
        {"ticker": "TLT", "category": "Bond"},
        {"ticker": "SHY", "category": "Bond"},
        {"ticker": "LQD", "category": "Bond"},
        {"ticker": "HYG", "category": "Bond"},
        {"ticker": "JNK", "category": "Bond"},
        {"ticker": "GLD", "category": "Komoditas"},
        {"ticker": "SLV", "category": "Komoditas"},
        {"ticker": "USO", "category": "Komoditas"},
        {"ticker": "DBA", "category": "Komoditas"},
        {"ticker": "VNQ", "category": "REITs"},
        {"ticker": "IYR", "category": "REITs"},
        {"ticker": "BITO", "category": "Crypto"},
        {"ticker": "UVXY", "category": "Volatility"},
    ]
    
    results = []
    total = len(watchlist)
    print(f"[*] Memulai analisis {total} ETF...\n")
    
    for idx, item in enumerate(watchlist, 1):
        print(f"[{idx}/{total}] Menganalisis {item['ticker']}...", end=" ")
        try:
            data = analyze_ticker(item['ticker'], item['category'])
            if data:
                results.append(data)
                print("✅")
            else:
                print("⚠️ Data kosong")
        except Exception as e:
            print(f"❌ Error: {e}")
        time.sleep(0.5)
            
    output = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_etf": len(results),
        "stocks": results
    }
    
    with open('data.json', 'w') as f:
        json.dump(output, f, indent=4)
        
    print(f"\n[+] Sukses! {len(results)} ETF dianalisis. Data disimpan ke data.json")

if __name__ == "__main__":
    main()
