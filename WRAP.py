import streamlit as st
import pandas as pd
import yfinance as yf
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
from collections import defaultdict

# 페이지 설정
st.set_page_config(page_title="랩 거래일별 현황", layout="centered")

# CSS 스타일링
st.markdown("""
<style>
    /* 폰트 import */
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css');
    
    /* 전체 폰트 적용 */
    * {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif !important;
    }

    /* 전체 컨테이너 */
    .block-container {
        max-width: 1200px;
        padding: 2rem 1rem;
    }
    
    /* 타이틀 */
    h1 {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 2rem !important;
        color: #1f2937 !important;
    }
    
    /* 날짜 카드 전체 */
    .date-card {
        background: white;
        border-radius: 16px;
        padding: 0;
        margin-bottom: 2.5rem;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
        overflow: hidden;
    }
    
    /* 날짜 헤더 */
    .date-header {
        background: #2E4365;
        padding: 1.5rem 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 1rem;
    }
    
    .date-title {
        font-size: 2rem;
        font-weight: 700;
        color: white;
    }
    
    .header-metrics {
        display: flex;
        gap: 2.5rem;
        flex-wrap: wrap;
    }
    
    .header-metric {
        text-align: right;
    }
    
    .header-metric-label {
        font-size: 0.95rem;
        color: rgba(255,255,255,0.9);
        margin-bottom: 0.25rem;
    }
    
    .header-metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: white;
    }
    
    /* 테이블 컨테이너 */
    .table-container {
        padding: 2rem;
    }
    
    /* 커스텀 테이블 */
    .custom-table {
        width: 100%;
        border-collapse: collapse;
    }
    
    .custom-table thead {
        background: #f8fafc;
        border-bottom: 2px solid #e2e8f0;
    }
    
    .custom-table th {
        padding: 1rem;
        text-align: left;
        font-size: 1rem;
        font-weight: 700;
        color: #475569;
    }
    
    .custom-table th.text-right {
        text-align: right;
    }
    
    .custom-table th.text-center {
        text-align: center;
    }
    
    .custom-table tbody tr {
        border-bottom: 1px solid #e2e8f0;
        transition: background 0.2s;
    }
    
    .custom-table tbody tr:hover {
        background: #f8fafc;
    }
    
    .custom-table td {
        padding: 1rem;
        font-size: 1rem;
        color: #1e293b;
    }
    
    .custom-table td.text-right {
        text-align: right;
    }
    
    .custom-table td.text-center {
        text-align: center;
    }
    
    .custom-table td.font-bold {
        font-weight: 700;
    }
    
    .pl-positive {
        color: #3A866A; 
        font-weight: 700;
    }
    
    .pl-negative {
        color: #dc2626 !important;
        font-weight: 700 !important;
    }
    
    .new-badge {
        background: #E59D2C;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        display: inline-block;
    }
            
    .out-badge {
    background: #D46F2E;
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    display: inline-block;
    }
    
    /* 합계 행 */
    .total-row {
        background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
        border-top: 2px solid #cbd5e1 !important;
        font-weight: 700;
    }
    
    .total-row td {
        padding: 1.25rem 1rem !important;
        font-size: 1.2rem !important;
    }
    
    /* 빈 상태 */
    .empty-state {
        padding: 3rem 2rem;
        text-align: center;
        color: #64748b;
        font-size: 1.1rem;
    }
    
    /tab3 스타일/
    /* 월별 카드 스타일 */
    .month-card {
        background: white;
        border-radius: 16px;
        padding: 0;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
        overflow: hidden;
    }

    .month-header {
        background: #2E4365;
        padding: 1.5rem 2rem;
        color: white;
        font-size: 1.8rem;
        font-weight: 700;
        border-radius: 16px 16px 0 0;
    }

    .month-content {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0;
    }

    .column {
        padding: 2rem;
    }

    .column-left {
        border-right: 2px solid #e2e8f0;
    }

    .column-title {
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .new-title {
        color: #E59D2C;
    }

    .out-title {
        color: #dc2626;
    }

    .count-badge {
        background: #f1f5f9;
        color: #64748b;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
    }

    .ticker-list {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
    }

    .ticker-item {
        font-size: 1.1rem;
        padding-left: 1.5rem;
        position: relative;
        color: #1e293b;
    }

    .ticker-item::before {
        content: "•";
        position: absolute;
        left: 0;
        font-weight: 700;
        color: #94a3b8;
    }

    .ticker-code {
        font-weight: 700;
        color: #1e293b;
    }

    .out-item {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
        padding: 1rem;
        background: #f8fafc;
        border-radius: 8px;
        margin-bottom: 0.75rem;
    }

    .out-header {
        font-weight: 700;
        font-size: 1.2rem;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }

    .out-details {
        display: flex;
        gap: 1.5rem;
        font-size: 0.95rem;
        color: #64748b;
    }

    .detail-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .detail-label {
        color: #94a3b8;
    }

    .detail-value {
        font-weight: 600;
        color: #475569;
    }

    .profit-positive {
        color: #3A866A !important;
        font-weight: 700 !important;
    }

    .profit-negative {
        color: #dc2626 !important;
        font-weight: 700 !important;
    }

    .empty-state {
        text-align: center;
        padding: 2rem;
        color: #94a3b8;
        font-size: 1rem;
    }


</style>
""", unsafe_allow_html=True)

# 구글스프레드 읽기
@st.cache_data
def load_data():
    # Google Sheets 인증 설정
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    
    # Streamlit Secrets 사용
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    
    client = gspread.authorize(creds)
    
    # 스프레드시트 열기
    spreadsheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1_jO1uKWh6ZPZ_uoQ4dE1e5ouc8MYQnnVL8xBvJNqdTc/edit?gid=0#gid=0')
    
    # WRAP 시트 데이터 읽기
    worksheet = spreadsheet.worksheet("WRAP")
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    df['거래일'] = pd.to_datetime(df['거래일'])
    
    # 투자금액 읽기 (M1 셀)
    investment_amount = worksheet.acell('M1').value
    investment_amount = float(investment_amount) if investment_amount else 0
    
    return df.sort_values('거래일'), investment_amount

# 종가 데이터 가져오기
@st.cache_data
def get_closing_prices(tickers, dates):
    prices = {}
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(start=dates[0] - timedelta(days=5), end=dates[-1] + timedelta(days=1))
            prices[ticker] = hist['Close'].to_dict()
        except Exception as e:
            st.warning(f"{ticker} 종가 데이터를 가져올 수 없습니다: {e}")
            prices[ticker] = {}
    return prices

# 선입선출 방식으로 매매손익 계산
def calculate_fifo(transactions, close_prices):
    holdings = defaultdict(list)
    cumulative_realized_pl = 0
    daily_snapshots = []
    realized_trades = [] 
    first_buy_dates = {}
    
    trade_dates = sorted(transactions['거래일'].unique())
    prev_tickers = set()
    
    for idx, date in enumerate(trade_dates):        
        day_txs = transactions[transactions['거래일'] == date]
        daily_realized_pl = 0
        
        # 거래 처리
        for _, tx in day_txs.iterrows():
            ticker = tx['종목코드']
            qty = tx['수량']
            price = tx['단가']
            
            if tx['구분'] == '매수':
                if ticker not in first_buy_dates:
                    first_buy_dates[ticker] = date
                holdings[ticker].append({'qty': qty, 'price': price})
            elif tx['구분'] == '매도':
                remaining_qty = qty
                cost_basis = 0
                sold_qty = qty
                
                # FIFO로 평균단가 계산
                total_cost = 0
                temp_remaining = qty
                for lot in holdings[ticker]:
                    if temp_remaining <= 0:
                        break
                    take_qty = min(temp_remaining, lot['qty'])
                    total_cost += take_qty * lot['price']
                    temp_remaining -= take_qty
                
                avg_purchase_price = total_cost / sold_qty if sold_qty > 0 else 0
                
                # 기존 FIFO 처리
                while remaining_qty > 0 and holdings[ticker]:
                    lot = holdings[ticker][0]
                    qty_to_sell = min(remaining_qty, lot['qty'])
                    
                    cost_basis += qty_to_sell * lot['price']
                    remaining_qty -= qty_to_sell
                    lot['qty'] -= qty_to_sell
                    
                    if lot['qty'] == 0:
                        holdings[ticker].pop(0)
                
                proceeds = sold_qty * price
                realized_pl = proceeds - cost_basis
                daily_realized_pl += realized_pl
                
                # 매도 기록 저장
                realized_trades.append({
                    'date': date,
                    'ticker': ticker,
                    'qty': sold_qty,
                    'avg_cost': avg_purchase_price,
                    'sell_price': price,
                    'realized_pl': realized_pl
                })

            elif tx['구분'] == '배당':
                dividend_amount = tx['거래금액']
                daily_realized_pl += dividend_amount
                
                realized_trades.append({
                    'date': date,
                    'ticker': ticker,
                    'type': 'dividend',
                    'qty': int(qty) if pd.notna(qty) else 0,
                    'dividend_price': price,  # 단가 (배당 단가)
                    'realized_pl': dividend_amount
                })
        
        cumulative_realized_pl += daily_realized_pl
        
        # 현재 보유 종목 현황
        current_holdings = []
        total_unrealized_pl = 0
        
        for ticker, lots in holdings.items():
            total_qty = sum(lot['qty'] for lot in lots)
            if total_qty > 0:
                avg_cost = sum(lot['qty'] * lot['price'] for lot in lots) / total_qty
                
                # 종가 가져오기
                close_price = None
                if ticker in close_prices:
                    price_dict = close_prices[ticker]
                    for price_date, price_value in sorted(price_dict.items(), reverse=True):
                        if price_date.date() <= date.date():
                            close_price = price_value
                            break
                
                if close_price is None:
                    close_price = avg_cost
                
                unrealized_pl = (close_price - avg_cost) * total_qty
                total_unrealized_pl += unrealized_pl
                is_new = ticker not in prev_tickers
                
                current_holdings.append({
                    'ticker': ticker,
                    'qty': int(total_qty),
                    'avg_cost': avg_cost,
                    'close_price': close_price,
                    'unrealized_pl': unrealized_pl,
                    'return_rate': ((close_price - avg_cost) / avg_cost * 100) if avg_cost > 0 else 0,
                    'is_new': is_new,
                    'is_out': False,
                    'first_buy_date': first_buy_dates.get(ticker, date)
                })
        
        prev_tickers = {h['ticker'] for h in current_holdings}
        
        current_holdings.sort(key=lambda x: x['avg_cost'] * x['qty'], reverse=True)
        
        daily_snapshots.append({
            'date': date,
            'holdings': current_holdings,
            'daily_realized_pl': daily_realized_pl,
            'cumulative_realized_pl': cumulative_realized_pl,
            'total_unrealized_pl': total_unrealized_pl,
            'total_pl': cumulative_realized_pl + total_unrealized_pl
        })

    for idx in range(len(daily_snapshots) - 1):
        current_tickers = {h['ticker'] for h in daily_snapshots[idx]['holdings']}
        next_tickers = {h['ticker'] for h in daily_snapshots[idx + 1]['holdings']}
        
        # 현재 보유하지만 다음날 없는 종목 = OUT
        for holding in daily_snapshots[idx]['holdings']:
            if holding['ticker'] not in next_tickers:
                holding['is_out'] = True
                holding['out_date'] = daily_snapshots[idx]['date']
    
    return daily_snapshots, realized_trades, first_buy_dates

# 데이터 로드
try:
    df, investment_amount = load_data()
    
    tickers = df['종목코드'].unique().tolist()
    trade_dates = df['거래일'].unique()
    
    with st.spinner('종가 데이터를 가져오는 중...'):
        close_prices = get_closing_prices(tickers, trade_dates)
    
    snapshots, realized_trades, first_buy_dates = calculate_fifo(df, close_prices)

    # 오늘 날짜 스냅샷 추가
    if snapshots:
        last_snapshot = snapshots[-1]
        today = datetime.now()
        
        # 오늘의 최신 종가 가져오기
        today_tickers = [h['ticker'] for h in last_snapshot['holdings']]
        today_prices = {}
        
        for ticker in today_tickers:
            try:
                stock = yf.Ticker(ticker)
                # 최근 5일 데이터 가져오기
                hist = stock.history(period='5d')
                if not hist.empty:
                    today_prices[ticker] = hist['Close'].iloc[-1]
            except:
                pass
        
        # 오늘 날짜로 종가 업데이트
        today_holdings = []
        total_unrealized_pl = 0
        
        for holding in last_snapshot['holdings']:
            ticker = holding['ticker']
            
            # 오늘 종가 사용, 없으면 마지막 종가 사용
            close_price = today_prices.get(ticker, holding['close_price'])
            
            unrealized_pl = (close_price - holding['avg_cost']) * holding['qty']
            total_unrealized_pl += unrealized_pl
            
            today_holdings.append({
                'ticker': holding['ticker'],
                'qty': holding['qty'],
                'avg_cost': holding['avg_cost'],
                'close_price': close_price,
                'unrealized_pl': unrealized_pl,
                'return_rate': ((close_price - holding['avg_cost']) / holding['avg_cost'] * 100) if holding['avg_cost'] > 0 else 0,
                'is_new': False,
                'is_out': False
            })
        
        today_holdings.sort(key=lambda x: x['avg_cost'] * x['qty'], reverse=True)

        snapshots.append({
            'date': today,
            'holdings': today_holdings,
            'daily_realized_pl': 0,
            'cumulative_realized_pl': last_snapshot['cumulative_realized_pl'],
            'total_unrealized_pl': total_unrealized_pl,
            'total_pl': last_snapshot['cumulative_realized_pl'] + total_unrealized_pl
        })


    # 제목과 투자금액 표시

    if snapshots:
        latest_total_pl = snapshots[-1]['total_pl']  # 가장 최근(오늘) 총손익
        current_value = investment_amount + latest_total_pl
        total_return_rate = (latest_total_pl / investment_amount * 100) if investment_amount > 0 else 0
        return_color = '#3A866A' if total_return_rate >= 0 else '#dc2626'
        
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 2rem; margin-bottom: 2rem;">
            <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700; color: #1f2937; display: flex; align-items: center; gap: 0.75rem;">
                <img src="https://cdn-icons-png.flaticon.com/128/19006/19006225.png" style="width: 40px; height: 40px; margin-right: 10px;" />
                 랩 거래일별 현황
            </h1>
            <div style="display: flex; gap: 3rem;">
                <div style="text-align: right;">
                    <div style="font-size: 0.95rem; color: #64748b; margin-right: 0.2rem; margin-bottom: 0.25rem;">투자금액</div>
                    <div style="font-size: 1.6rem; font-weight: 700; color: #1f2937;">${investment_amount:,.2f}</div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 0.95rem; color: #64748b; margin-bottom: 0.25rem;">평가금액</div>
                    <div style="font-size: 1.6rem; font-weight: 700; color: #1f2937;">${current_value:,.2f}</div>
                    <div style="font-size: 1.1rem; font-weight: 700; color: {return_color}; margin-top: 0.25rem;">({total_return_rate:+.2f}%)</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["거래일별 현황", "실현손익 내역", "신규/매도 항목"])

    with tab1:
    
        # 결과 표시
        for snapshot in reversed(snapshots):
            date_str = snapshot['date'].strftime('%Y-%m-%d')
            daily_pl = snapshot['daily_realized_pl']
            cumul_pl = snapshot['cumulative_realized_pl']
            unrealized_pl = snapshot['total_unrealized_pl']
            total_pl = snapshot['total_pl']
            
            # 날짜 카드 시작
            html_content = f"""
            <div class="date-card">
                <div class="date-header">
                    <div class="date-title">{date_str}</div>
                    <div class="header-metrics">
                        <div class="header-metric">
                            <div class="header-metric-label">당일 실현손익</div>
                            <div class="header-metric-value">${daily_pl:,.2f}</div>
                        </div>
                        <div class="header-metric">
                            <div class="header-metric-label">누적 실현손익</div>
                            <div class="header-metric-value">${cumul_pl:,.2f}</div>
                        </div>
                        <div class="header-metric">
                            <div class="header-metric-label">총 손익</div>
                            <div class="header-metric-value">${total_pl:,.2f}</div>
                        </div>
                    </div>
                </div>
            """
            
            if snapshot['holdings']:
                html_content += '<div class="table-container"><table class="custom-table"><thead><tr>'
                html_content += '<th class="text-center">종목코드</th>'
                html_content += '<th class="text-center">수량</th>'
                html_content += '<th class="text-center">평균단가</th>'
                html_content += '<th class="text-center">현재가</th>'
                html_content += '<th class="text-center">평가손익</th>'
                html_content += '<th class="text-center">수익률</th>'
                html_content += '<th class="text-center">상태</th>'
                html_content += '</tr></thead><tbody>'
                
                for holding in snapshot['holdings']:
                    pl_class = 'pl-positive' if holding['unrealized_pl'] >= 0 else 'pl-negative'
                    return_class = 'pl-positive' if holding['return_rate'] >= 0 else 'pl-negative'  # 이 줄 추가
                    badges = ''
                    if holding['is_new']:
                        badges += '<span class="new-badge">NEW</span>'
                    if holding.get('is_out', False):
                        badges += '<span class="out-badge">OUT</span>'
                    
                    html_content += '<tr>'
                    html_content += f'<td class="text-center font-bold">{holding["ticker"]}</td>'
                    html_content += f'<td class="text-center">{holding["qty"]}</td>'
                    html_content += f'<td class="text-right">${holding["avg_cost"]:.2f}</td>'
                    html_content += f'<td class="text-right">${holding["close_price"]:.2f}</td>'
                    html_content += f'<td class="text-right {pl_class}">${holding["unrealized_pl"]:,.2f}</td>'
                    html_content += f'<td class="text-right {return_class}">{holding["return_rate"]:.2f}%</td>'  # 이 줄 추가
                    html_content += f'<td class="text-center">{badges}</td>'
                    html_content += '</tr>'
                
                # 합계 행
                total_cost = sum(h['avg_cost'] * h['qty'] for h in snapshot['holdings'])
                total_current_value = sum(h['close_price'] * h['qty'] for h in snapshot['holdings'])
                total_return_rate = (unrealized_pl / total_cost * 100) if total_cost > 0 else 0
                
                total_pl_class = 'pl-positive' if unrealized_pl >= 0 else 'pl-negative'
                total_return_class = 'pl-positive' if total_return_rate >= 0 else 'pl-negative'
                
                html_content += '<tr class="total-row">'
                html_content += '<td colspan="2" class="text-right">합계</td>'
                html_content += f'<td class="text-right">${total_cost:,.2f}</td>'
                html_content += f'<td class="text-right">${total_current_value:,.2f}</td>'
                html_content += f'<td class="text-right {total_pl_class}">${unrealized_pl:,.2f}</td>'
                html_content += f'<td class="text-right {total_return_class}">{total_return_rate:.2f}%</td>'
                html_content += '<td></td>'
                html_content += '</tr>'
                
                html_content += '</tbody></table></div>'
            else:
                html_content += '<div class="empty-state">💡 보유 종목 없음</div>'
            
            html_content += '</div>'
            
            st.markdown(html_content, unsafe_allow_html=True)

    with tab2:
        # 누적 실현손익 계산
        total_realized_pl = sum(t['realized_pl'] for t in realized_trades) if realized_trades else 0
        total_pl_class = 'pl-positive' if total_realized_pl >= 0 else 'pl-negative'
        
        # 제목과 누적 실현손익 표시
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h3 style="margin: 0; font-size: 1.5rem; font-weight: 700; color: #1f2937; margin-left: 30px;">실현손익 내역</h3>
            <div style="text-align: right;">
                <div style="font-size: 0.95rem; color: #64748b; margin-bottom: 0.25rem; margin-right: 30px;">누적 실현손익</div>
                <div style="font-size: 1.5rem; font-weight: 700; margin-right: 30px; color: {'#3A866A' if total_realized_pl >= 0 else '#dc2626'};">${total_realized_pl:,.2f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if realized_trades:
            # 역순 정렬 (최신순)
            realized_trades_sorted = sorted(realized_trades, key=lambda x: x['date'], reverse=True)
            
            # 월별로 그룹화
            from itertools import groupby
            monthly_groups = []
            for month_key, trades in groupby(realized_trades_sorted, key=lambda x: x['date'].strftime('%Y-%m')):
                monthly_groups.append((month_key, list(trades)))
            
            # HTML 테이블 생성
            html_content = '<div class="table-container"><table class="custom-table"><thead><tr>'
            html_content += '<th class="text-center">매도일</th>'
            html_content += '<th class="text-center">종목코드</th>'
            html_content += '<th class="text-center">수량</th>'
            html_content += '<th class="text-center">평균단가</th>'
            html_content += '<th class="text-center">매도단가</th>'
            html_content += '<th class="text-center">실현손익</th>'
            html_content += '</tr></thead><tbody>'
            
            for month_key, month_trades in monthly_groups:
                month_pl = 0
                
                # 월별 거래 내역
                for trade in month_trades:
                    pl_class = 'pl-positive' if trade['realized_pl'] >= 0 else 'pl-negative'
                    date_str = trade['date'].strftime('%Y-%m-%d')
                    
                    html_content += '<tr>'
                    html_content += f'<td class="text-center">{date_str}</td>'
                    html_content += f'<td class="text-center font-bold">{trade["ticker"]}</td>'
                    # 배당과 매도 구분 처리
                    if trade.get('type') == 'dividend':
                        html_content += f'<td class="text-center">{trade["qty"]}</td>'  # 수량
                        html_content += '<td class="text-right">-</td>'  # 평균단가
                        html_content += f'<td class="text-right">${trade["dividend_price"]:.2f}</td>'  # 배당단가
                    else:
                        html_content += f'<td class="text-center">{trade["qty"]}</td>'
                        html_content += f'<td class="text-right">${trade["avg_cost"]:.2f}</td>'
                        html_content += f'<td class="text-right">${trade["sell_price"]:.2f}</td>'
                    
                    html_content += f'<td class="text-right {pl_class}">${trade["realized_pl"]:,.2f}</td>'
                    html_content += '</tr>'
                    
                    month_pl += trade['realized_pl']
                
                # 월간 합계 행
                month_pl_class = 'pl-positive' if month_pl >= 0 else 'pl-negative'
                year, month = month_key.split('-')
                html_content += '<tr class="total-row" style="background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);">'
                html_content += f'<td colspan="5" class="text-right" style="font-size: 1.05rem;">{year}년 {month}월 실현손익</td>'
                html_content += f'<td class="text-right {month_pl_class}" style="font-size: 1.05rem;">${month_pl:,.2f}</td>'
                html_content += '</tr>'
            
            html_content += '</tbody></table></div>'
            
            st.markdown(html_content, unsafe_allow_html=True)
        else:
            st.markdown('<div class="empty-state">매도 거래 내역이 없습니다.</div>', unsafe_allow_html=True)

    with tab3:
            
            # 월별 데이터 수집
            monthly_data = {}
            
            for snapshot in snapshots:
                month_key = snapshot['date'].strftime('%Y-%m')
                
                if month_key not in monthly_data:
                    monthly_data[month_key] = {
                        'new_tickers': [],
                        'out_tickers': []
                    }
                
                for holding in snapshot['holdings']:
                    # 신규 종목
                    if holding['is_new']:
                        monthly_data[month_key]['new_tickers'].append(holding['ticker'])
                    
                    # 매도 종목
                    if holding.get('is_out', False):
                        first_buy = holding.get('first_buy_date', snapshot['date'])
                        out_date = holding.get('out_date', snapshot['date'])
                        holding_days = (out_date - first_buy).days
                        
                        # 해당 종목의 실현손익 합산
                        ticker_realized_pl = sum(
                            t['realized_pl'] 
                            for t in realized_trades 
                            if t['ticker'] == holding['ticker'] 
                            and t['date'].strftime('%Y-%m') == month_key
                        )
                        
                        monthly_data[month_key]['out_tickers'].append({
                            'ticker': holding['ticker'],
                            'holding_days': holding_days,
                            'realized_pl': ticker_realized_pl
                        })
            
            # 월별 역순 정렬
            sorted_months = sorted(monthly_data.keys(), reverse=True)
            
            for month_key in sorted_months:
                data = monthly_data[month_key]
                year, month = month_key.split('-')
                
                # 중복 제거
                new_tickers = list(dict.fromkeys(data['new_tickers']))
                out_tickers_dict = {}
                for item in data['out_tickers']:
                    ticker = item['ticker']
                    if ticker not in out_tickers_dict:
                        out_tickers_dict[ticker] = item
                out_tickers = list(out_tickers_dict.values())
                
                # === HTML 생성 시작 ===
                html_content = '<div class="month-card">'
                html_content += f'<div class="month-header">{year}년 {int(month)}월</div>'
                html_content += '<div class="month-content">'
                
                # 신규 종목 섹션
                html_content += '<div class="column column-left">'
                html_content += '<div class="column-title new-title">'
                html_content += '📈 NEW'
                html_content += f'<span class="count-badge">{len(new_tickers)}</span>'
                html_content += '</div>'
                
                if new_tickers:
                    for ticker in new_tickers:
                        html_content += f'<div class="ticker-item"><span class="ticker-code">{ticker}</span></div>'
                else:
                    html_content += '<div class="empty-state">신규 매수한 종목이 없습니다.</div>'
                
                html_content += '</div>'  # column-left 끝
                
                # 매도 종목 섹션
                html_content += '<div class="column">'
                html_content += '<div class="column-title out-title">'
                html_content += '📉 OUT'
                html_content += f'<span class="count-badge">{len(out_tickers)}</span>'
                html_content += '</div>'
                
                if out_tickers:
                    for item in out_tickers:
                        pl_class = 'profit-positive' if item['realized_pl'] >= 0 else 'profit-negative'
                        html_content += '<div class="out-item">'
                        html_content += f'<div class="out-header">{item["ticker"]}</div>'
                        html_content += '<div class="out-details">'
                        html_content += '<div class="detail-item">'
                        html_content += '<span class="detail-label">보유:</span>'
                        html_content += f'<span class="detail-value">{item["holding_days"]}일</span>'
                        html_content += '</div>'
                        html_content += '<div class="detail-item">'
                        html_content += '<span class="detail-label">손익:</span>'
                        html_content += f'<span class="detail-value {pl_class}">${item["realized_pl"]:,.2f}</span>'
                        html_content += '</div>'
                        html_content += '</div>'  # out-details 끝
                        html_content += '</div>'  # out-item 끝
                else:
                    html_content += '<div class="empty-state">매도한 종목이 없습니다.</div>'
                
                html_content += '</div>'  # column 끝
                html_content += '</div>'  # month-content 끝
                html_content += '</div>'  # month-card 끝
                
                st.markdown(html_content, unsafe_allow_html=True)

except FileNotFoundError:
    st.error("❌ 엑셀 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
except Exception as e:
    st.error(f"❌ 오류 발생: {str(e)}")
    st.exception(e)

