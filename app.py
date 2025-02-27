from fastapi import FastAPI, HTTPException
import requests
import datetime
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

# 📌 환경 변수 로드
load_dotenv()

# 📌 FastAPI 앱 생성
app = FastAPI()

# 📌 CORS 설정 (모든 도메인 허용, 필요시 수정)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📌 API 인증 정보
APP_KEY = os.getenv("APP_KEY")
APP_SECRET = os.getenv("APP_SECRET")

ACCESS_TOKEN = None
TOKEN_EXPIRE_TIME = None

# 📌 1️⃣ 토큰 자동 갱신
def get_access_token():
    global ACCESS_TOKEN, TOKEN_EXPIRE_TIME

    url = "https://openapi.koreainvestment.com:9443/oauth2/tokenP"
    headers = {"content-type": "application/json"}
    data = {"grant_type": "client_credentials", "appkey": APP_KEY, "appsecret": APP_SECRET}

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        token_data = response.json()

        ACCESS_TOKEN = token_data.get("access_token")
        expires_in = int(token_data.get("expires_in", 0))

        if ACCESS_TOKEN:
            TOKEN_EXPIRE_TIME = datetime.datetime.now() + datetime.timedelta(seconds=expires_in)
            print(f"✅ 새 토큰 발급 완료! 유효기간: {TOKEN_EXPIRE_TIME}")
        else:
            raise RuntimeError(f"❌ 토큰 발급 실패 - 응답 오류: {token_data}")

    except requests.RequestException as e:
        raise RuntimeError(f"❌ 토큰 요청 실패: {str(e)}")

# 📌 2️⃣ 토큰 유효성 확인
def ensure_valid_token():
    if ACCESS_TOKEN is None or TOKEN_EXPIRE_TIME is None or datetime.datetime.now() >= TOKEN_EXPIRE_TIME:
        print("🔄 토큰 갱신 필요")
        get_access_token()

# 📌 3️⃣ API 요청 함수
def fetch_api(url, tr_id, params=None):
    ensure_valid_token()
    
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": tr_id,
        "custtype": "P"  # 개인
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        raw_text = response.text  # 원본 JSON 텍스트
        response.raise_for_status()

        # 실제 JSON 데이터 파싱
        data = response.json()

        # 로깅 (콘솔에서 raw 데이터 확인 가능)
        print(f"\n=== DEBUG RAW RESPONSE ({tr_id}) ===\n{raw_text}\n")

        return data
    except requests.RequestException as err:
        # 에러 발생 시, 원본 응답도 반환
        return {
            "error": f"HTTP {response.status_code}",
            "message": str(err),
            "raw_response": response.text
        }

# 📌 루트 엔드포인트 ("/")
@app.get("/")
def root():
    """
    루트 엔드포인트 - 404 방지용
    """
    return {"message": "Hello from FastAPI Root!"}

# 📌 국내 실시간 주가 조회
@app.get("/stock/{stock_code}")
def get_realtime_price(stock_code: str):
    url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/quotations/inquire-price"
    params = {"fid_cond_mrkt_div_code": "J", "fid_input_iscd": stock_code}
    return fetch_api(url, "FHKST01010100", params=params)

# 📌 대차대조표 조회
@app.get("/finance/balance-sheet/{stock_code}")
def get_balance_sheet(stock_code: str):
    url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/finance/balance-sheet"
    params = {"fid_cond_mrkt_div_code": "J", "fid_input_iscd": stock_code, "fid_div_cls_code": "1"}
    return fetch_api(url, "FHKST66430100", params=params)

# 📌 손익계산서 조회
@app.get("/finance/income-statement/{stock_code}")
def get_income_statement(stock_code: str):
    url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/finance/income-statement"
    params = {"fid_cond_mrkt_div_code": "J", "fid_input_iscd": stock_code, "fid_div_cls_code": "1"}
    return fetch_api(url, "FHKST66430200", params=params)

# 📌 재무비율 조회
@app.get("/finance/financial-ratio/{stock_code}")
def get_financial_ratio(stock_code: str):
    url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/finance/financial-ratio"
    params = {"fid_cond_mrkt_div_code": "J", "fid_input_iscd": stock_code, "fid_div_cls_code": "1"}
    return fetch_api(url, "FHKST66430300", params=params)

# 📌 수익성비율 조회
@app.get("/finance/profit-ratio/{stock_code}")
def get_profit_ratio(stock_code: str):
    url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/finance/profit-ratio"
    params = {"fid_cond_mrkt_div_code": "J", "fid_input_iscd": stock_code, "fid_div_cls_code": "1"}
    return fetch_api(url, "FHKST66430400", params=params)

# 📌 기타 주요비율 조회
@app.get("/finance/other-major-ratios/{stock_code}")
def get_other_major_ratios(stock_code: str):
    url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/finance/other-major-ratios"
    params = {"fid_cond_mrkt_div_code": "J", "fid_input_iscd": stock_code, "fid_div_cls_code": "1"}
    return fetch_api(url, "FHKST66430500", params=params)

# 📌 안정성비율 조회
@app.get("/finance/stability-ratio/{stock_code}")
def get_stability_ratio(stock_code: str):
    url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/finance/stability-ratio"
    params = {"fid_cond_mrkt_div_code": "J", "fid_input_iscd": stock_code, "fid_div_cls_code": "1"}
    return fetch_api(url, "FHKST66430600", params=params)

# 📌 성장성비율 조회
@app.get("/finance/growth-ratio/{stock_code}")
def get_growth_ratio(stock_code: str):
    url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/finance/growth-ratio"
    params = {"fid_cond_mrkt_div_code": "J", "fid_input_iscd": stock_code, "fid_div_cls_code": "1"}
    return fetch_api(url, "FHKST66430800", params=params)

# 📌 해외 실시간 상세현재가 (AUTH 제거, EXCD와 SYMB만)
@app.get("/overseas/price-detail")
def get_overseas_price_detail(
    EXCD: str = "",    # 거래소코드 (예: NAS, NYS, AMS 등)
    SYMB: str = "",    # 종목코드 (예: AAPL, TSLA 등)
):
    """
    해외 실시간상세현재가 조회
    """
    url = "https://openapi.koreainvestment.com:9443/uapi/overseas-price/v1/quotations/price-detail"
    params = {
        "EXCD": EXCD,
        "SYMB": SYMB,
    }
    return fetch_api(url, "HHDFS76200200", params=params)
