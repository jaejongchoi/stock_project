import requests
import json
import datetime

# 📌 API 인증 정보
APP_KEY = "PS6M6OZYHPcFUdMDi6w5GYOhfXYOhZUJzCXs"
APP_SECRET = "LWUcdYzPG+BWuPjAsnnamF5QQeDJqd0Pop26sJmJPe+VCPD5kx/tMuYkTYXe2MwEw8Siz5O04UVapKoezwXzcOiEVZPF+GjNdAwy5+EBed/ptp2REOAM/P9IfN6GgCeOTYpe43Qyavr/iOZUVRbiat4Zc1ayCaPqH3ci/n62dZXOEXFuOps="
ACCESS_TOKEN = None
TOKEN_EXPIRE_TIME = None

# 📌 토큰 자동 갱신 함수
def get_access_token():
    global ACCESS_TOKEN, TOKEN_EXPIRE_TIME
    
    url = "https://openapi.koreainvestment.com:9443/oauth2/tokenP"
    headers = {"content-type": "application/json"}
    data = {"grant_type": "client_credentials", "appkey": APP_KEY, "appsecret": APP_SECRET}

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        token_data = response.json()
        ACCESS_TOKEN = token_data["access_token"]
        expires_in = int(token_data["expires_in"])
        TOKEN_EXPIRE_TIME = datetime.datetime.now() + datetime.timedelta(seconds=expires_in)
        print(f"✅ 새 토큰 발급 완료! 유효기간: {TOKEN_EXPIRE_TIME}")
    else:
        print(f"❌ 토큰 발급 실패 - HTTP {response.status_code}")

# 📌 토큰 유효성 확인 및 자동 갱신
def ensure_valid_token():
    if ACCESS_TOKEN is None or datetime.datetime.now() >= TOKEN_EXPIRE_TIME:
        get_access_token()

# 📌 API 요청 함수 (GET 요청)
def fetch_api(url, tr_id):
    ensure_valid_token()
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": tr_id,
        "custtype": "P"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ 오류 발생 - HTTP {response.status_code}")
        return None

# 📌 1️⃣ 실시간 주가 조회 (종목 코드 입력 가능)
def get_realtime_price(stock_code):
    url = f"https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/quotations/inquire-price?fid_cond_mrkt_div_code=J&fid_input_iscd={stock_code}"
    return fetch_api(url, "FHKST01010100")

# 📌 2️⃣ 과거 주가 조회
def get_historical_prices(stock_code, start_date, end_date):
    url = f"https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice?fid_cond_mrkt_div_code=J&fid_input_iscd={stock_code}&fid_input_date_1={start_date}&fid_input_date_2={end_date}&fid_period_div_code=D&fid_org_adj_prc=1"
    return fetch_api(url, "FHKST03010100")

# 📌 3️⃣ ETF 실시간 주가 조회
def get_etf_price(etf_code):
    url = f"https://openapi.koreainvestment.com:9443/uapi/etfetn/v1/quotations/inquire-price?fid_cond_mrkt_div_code=J&fid_input_iscd={etf_code}"
    return fetch_api(url, "FHPST02400000")

# 📌 4️⃣ 주식 뉴스 조회
def get_stock_news(stock_code=""):
    url = f"https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/quotations/news-title?FID_INPUT_ISCD={stock_code}"
    return fetch_api(url, "FHKST01011800")

# 📌 5️⃣ 재무 정보 조회 함수 (재무제표, 손익계산서, 주요 지표)
def get_financial_data(stock_code, tr_id, data_type):
    url = f"https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/finance/{data_type}?fid_cond_mrkt_div_code=J&fid_input_iscd={stock_code}&fid_div_cls_code=1"
    return fetch_api(url, tr_id)

# ✅ 실행 (삼성전자 종목 예시)
stock_code = "005930"  # 삼성전자
etf_code = "069500"  # KODEX 200 ETF

# 📌 실시간 주가 조회
print("\n📌 [삼성전자 실시간 주가]")
print(json.dumps(get_realtime_price(stock_code), indent=4, ensure_ascii=False))

# 📌 과거 주가 조회 (2023년 1월~12월)
print("\n📌 [삼성전자 과거 주가]")
print(json.dumps(get_historical_prices(stock_code, "20230101", "20231231"), indent=4, ensure_ascii=False))

# 📌 ETF 실시간 주가 조회
print("\n📌 [ETF KODEX 200 실시간 주가]")
print(json.dumps(get_etf_price(etf_code), indent=4, ensure_ascii=False))

# 📌 주식 뉴스 조회
print("\n📌 [삼성전자 뉴스]")
print(json.dumps(get_stock_news(stock_code), indent=4, ensure_ascii=False))

# 📌 재무 정보 조회
financial_types = {
    "balance-sheet": "FHKST66430100",  # 재무제표
    "income-statement": "FHKST66430200",  # 손익계산서
    "financial-ratio": "FHKST66430300",  # 주요 재무 비율
    "profit-ratio": "FHKST66430400",  # 수익성 비율
    "other-major-ratios": "FHKST66430500",  # 기타 주요 비율
    "stability-ratio": "FHKST66430600",  # 안정성 비율
    "growth-ratio": "FHKST66430800"  # 성장성 비율
}

for data_type, tr_id in financial_types.items():
    print(f"\n📌 [{data_type.replace('-', ' ').title()}]")
    print(json.dumps(get_financial_data(stock_code, tr_id, data_type), indent=4, ensure_ascii=False))
