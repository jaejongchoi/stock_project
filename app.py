from fastapi import FastAPI
import requests
import json
import datetime
from fastapi.middleware.cors import CORSMiddleware

# 📌 FastAPI 앱 생성
app = FastAPI()

# 📌 CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인 허용 (보안상 필요하면 특정 도메인만 허용)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📌 API 인증 정보 (본인 정보 입력!)
APP_KEY = "PS6M6OZYHPcFUdMDi6w5GYOhfXYOhZUJzCXs"
APP_SECRET = "LWUcdYzPG+BWuPjAsnnamF5QQeDJqd0Pop26sJmJPe+VCPD5kx/tMuYkTYXe2MwEw8Siz5O04UVapKoezwXzcOiEVZPF+GjNdAwy5+EBed/ptp2REOAM/P9IfN6GgCeOTYpe43Qyavr/iOZUVRbiat4Zc1ayCaPqH3ci/n62dZXOEXFuOps="
ACCESS_TOKEN = None
TOKEN_EXPIRE_TIME = None

# 📌 1️⃣ 토큰 자동 갱신 함수
def get_access_token():
    global ACCESS_TOKEN, TOKEN_EXPIRE_TIME
    
    url = "https://openapi.koreainvestment.com:9443/oauth2/tokenP"
    headers = {"content-type": "application/json"}
    data = {"grant_type": "client_credentials", "appkey": APP_KEY, "appsecret": APP_SECRET}

    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        token_data = response.json()
        ACCESS_TOKEN = token_data.get("access_token", None)
        expires_in = int(token_data.get("expires_in", 0))
        
        if ACCESS_TOKEN:
            TOKEN_EXPIRE_TIME = datetime.datetime.now() + datetime.timedelta(seconds=expires_in)
            print(f"✅ 새 토큰 발급 완료! 유효기간: {TOKEN_EXPIRE_TIME}")
        else:
            print(f"❌ 토큰 발급 실패 - 응답 값 오류: {token_data}")
    else:
        print(f"❌ 토큰 발급 실패 - HTTP {response.status_code}: {response.text}")

# 📌 2️⃣ 토큰 유효성 확인 및 자동 갱신
def ensure_valid_token():
    if ACCESS_TOKEN is None or datetime.datetime.now() >= TOKEN_EXPIRE_TIME:
        get_access_token()

# 📌 3️⃣ API 요청 함수 (GET 요청)
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
    
    try:
        response.raise_for_status()  # HTTP 오류 발생 시 예외 처리
        return response.json()
    except requests.exceptions.HTTPError as err:
        return {"error": f"HTTP {response.status_code}", "message": str(err)}

# 📌 4️⃣ 실시간 주가 조회
@app.get("/stock/{stock_code}")
def get_realtime_price(stock_code: str):
    url = f"https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/quotations/inquire-price?fid_cond_mrkt_div_code=J&fid_input_iscd={stock_code}"
    return fetch_api(url, "FHKST01010100")

# 📌 5️⃣ 과거 주가 조회
@app.get("/history/{stock_code}/{start_date}/{end_date}")
def get_historical_prices(stock_code: str, start_date: str, end_date: str):
    url = f"https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice?fid_cond_mrkt_div_code=J&fid_input_iscd={stock_code}&fid_input_date_1={start_date}&fid_input_date_2={end_date}&fid_period_div_code=D&fid_org_adj_prc=1"
    return fetch_api(url, "FHKST03010100")

# 📌 6️⃣ ETF 실시간 주가 조회
@app.get("/etf/{etf_code}")
def get_etf_price(etf_code: str):
    url = f"https://openapi.koreainvestment.com:9443/uapi/etfetn/v1/quotations/inquire-price?fid_cond_mrkt_div_code=J&fid_input_iscd={etf_code}"
    return fetch_api(url, "FHPST02400000")

# 📌 7️⃣ 주식 뉴스 조회
@app.get("/news/{stock_code}")
def get_stock_news(stock_code: str):
    url = f"https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/quotations/news-title?FID_INPUT_ISCD={stock_code}"
    return fetch_api(url, "FHKST01011800")

# 📌 8️⃣ 재무 정보 조회 (재무제표, 손익계산서, 주요 지표)
@app.get("/finance/{stock_code}/{data_type}")
def get_financial_data(stock_code: str, data_type: str):
    financial_types = {
        "balance-sheet": "FHKST66430100",
        "income-statement": "FHKST66430200",
        "financial-ratio": "FHKST66430300",
        "profit-ratio": "FHKST66430400",
        "other-major-ratios": "FHKST66430500",
        "stability-ratio": "FHKST66430600",
        "growth-ratio": "FHKST66430800"
    }
    
    if data_type not in financial_types:
        return {"error": "Invalid data_type"}
    
    url = f"https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/finance/{data_type}?fid_cond_mrkt_div_code=J&fid_input_iscd={stock_code}&fid_div_cls_code=1"
    return fetch_api(url, financial_types[data_type])

