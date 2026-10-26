# generate_data.py
import yfinance as yf
import pandas as pd
import json
from datetime import datetime

def analyze_ticker(ticker, category):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="6mo")
    info = stock.info
    
    if hist.empty:
        return None

    current_price = hist['Close'].iloc[-1]
    
    # 1. Fundamental Check
    forward_pe = info.get('forwardPE', None)
    div_yield = info.get('dividendYield', 0) or 0
    
    # 2. Accumulation Detection (Wyckoff/VSA Simplified)
    recent_14 = hist.tail(14)
    up_vol = recent_14[recent_14['Close'] > recent_14['Open']]['Volume'].sum()
    down_vol = recent_14[recent_14['Close'] <= recent_14['Open']]['Volume'].sum()
    
    low_50 = hist.tail(50)['Low'].min()
    distance_from_low = ((current_price - low_50) / low_50) * 100
    
    is_accumulating = (up_vol > down_vol * 1.2) and (distance_from_low < 10)
    
    # 3. Action Zones (Swing Target 20% / Year -> ~5-6% per swing)
    support = hist.tail(30)['Low'].min()
    resistance = hist.tail(30)['High'].max()
    
    buy_zone = round(support * 1.01, 2)
    target_sell = round(max(resistance, current_price * 1.06), 2)
    stop_loss = round(support * 0.97, 2)
    
    profit_pct = ((target_sell - buy_zone) / buy_zone) * 100

    return {
        "ticker": ticker,
        "name": info.get('shortName', ticker),
        "category": category,
        "current_price": round(current_price, 2),
        "fundamental": {
            "pe_ratio": round(forward_pe, 2) if forward_pe else "N/A",
            "dividend_yield": f"{div_yield * 100:.2f}%",
            "verdict": "MURAH" if (forward_pe and forward_pe < 18) else "WAJAR" if (forward_pe and forward_pe < 25) else "MAHAL"
        },
        "collector_status": {
            "is_accumulating": is_accumulating,
            "status_text": "🔥 AKUMULASI BANDAR" if is_accumulating else "⚪ NETRAL",
            "up_vol_pct": round((up_vol / (up_vol + down_vol)) * 100, 1) if (up_vol + down_vol) > 0 else 0,
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
    # Daftar ticker yang akan dipantau (S&P 500, Dividen, dll)
    watchlist = [
        {"ticker": "SPY", "category": "Swing S&P 500"},
        {"ticker": "VOO", "category": "Swing S&P 500"},
        {"ticker": "SCHD", "category": "Dividen Play"},
        {"ticker": "QQQ", "category": "Swing Tech"}
    ]
    
    results = []
    print("[*] Memulai analisis pasar...")
    
    for item in watchlist:
        print(f"[*] Menganalisis {item['ticker']}...")
        data = analyze_ticker(item['ticker'], item['category'])
        if data:
            results.append(data)
            
    # Simpan ke JSON
    output = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "stocks": results
    }
    
    with open('data.json', 'w') as f:
        json.dump(output, f, indent=4)
        
    print("[+] Sukses! Data disimpan ke data.json")

if __name__ == "__main__":
    main()
