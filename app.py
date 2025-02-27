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

# 📌 CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
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
        "custtype": "P"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as err:
        return {"error": f"HTTP {response.status_code}", "message": str(err)}

# 📌 4️⃣ 실시간 주가 조회
@app.get("/stock/{stock_code}")
def get_realtime_price(stock_code: str):
    url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/quotations/inquire-price"
    params = {"fid_cond_mrkt_div_code": "J", "fid_input_iscd": stock_code}
    return fetch_api(url, "FHKST01010100", params=params)

# 📌 5️⃣ 종합시황/공시 조회
@app.get("/market-news")
def get_market_news():
    url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/quotations/news-title"
    params = {
        "FID_NEWS_OFER_ENTP_CODE": "001",
        "FID_COND_MRKT_CLS_CODE": "J",
        "FID_INPUT_ISCD": "",
        "FID_TITL_CNTT": "",
        "FID_INPUT_DATE_1": "20240221",
        "FID_INPUT_HOUR_1": "00",
        "FID_RANK_SORT_CLS_CODE": "1",
        "FID_INPUT_SRNO": "1"
    }
    return fetch_api(url, "FHKST01011800", params=params)

# 📌 4️⃣ 대차대조표 조회
@app.get("/finance/balance-sheet/{stock_code}")
def get_balance_sheet(stock_code: str):
    url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/finance/balance-sheet"
    params = {"fid_cond_mrkt_div_code": "J", "fid_input_iscd": stock_code, "fid_div_cls_code": "1"}
    return fetch_api(url, "FHKST66430100", params=params)

# 📌 5️⃣ 손익계산서 조회
@app.get("/finance/income-statement/{stock_code}")
def get_income_statement(stock_code: str):
    url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/finance/income-statement"
    params = {"fid_cond_mrkt_div_code": "J", "fid_input_iscd": stock_code, "fid_div_cls_code": "1"}
    return fetch_api(url, "FHKST66430200", params=params)

# 📌 6️⃣ 재무비율 조회
@app.get("/finance/financial-ratio/{stock_code}")
def get_financial_ratio(stock_code: str):
    url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/finance/financial-ratio"
    params = {"fid_cond_mrkt_div_code": "J", "fid_input_iscd": stock_code, "fid_div_cls_code": "1"}
    return fetch_api(url, "FHKST66430300", params=params)

# 📌 7️⃣ 수익성비율 조회
@app.get("/finance/profit-ratio/{stock_code}")
def get_profit_ratio(stock_code: str):
    url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/finance/profit-ratio"
    params = {"fid_cond_mrkt_div_code": "J", "fid_input_iscd": stock_code, "fid_div_cls_code": "1"}
    return fetch_api(url, "FHKST66430400", params=params)

# 📌 8️⃣ 기타 주요비율 조회
@app.get("/finance/other-major-ratios/{stock_code}")
def get_other_major_ratios(stock_code: str):
    url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/finance/other-major-ratios"
    params = {"fid_cond_mrkt_div_code": "J", "fid_input_iscd": stock_code, "fid_div_cls_code": "1"}
    return fetch_api(url, "FHKST66430500", params=params)

# 📌 9️⃣ 안정성비율 조회
@app.get("/finance/stability-ratio/{stock_code}")
def get_stability_ratio(stock_code: str):
    url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/finance/stability-ratio"
    params = {"fid_cond_mrkt_div_code": "J", "fid_input_iscd": stock_code, "fid_div_cls_code": "1"}
    return fetch_api(url, "FHKST66430600", params=params)

# 📌 🔟 성장성비율 조회
@app.get("/finance/growth-ratio/{stock_code}")
def get_growth_ratio(stock_code: str):
    url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/finance/growth-ratio"
    params = {"fid_cond_mrkt_div_code": "J", "fid_input_iscd": stock_code, "fid_div_cls_code": "1"}
    return fetch_api(url, "FHKST66430800", params=params)

@app.get("/overseas/price-detail")
def get_overseas_price_detail(
    # 문서상 Query Parameter
    AUTH: str = "",       # 사용자권한정보(일반적으로 헤더로 쓰이지만 문서상 필수)
    EXCD: str = "",       # 거래소코드 (NYS, NAS, AMS, TSE 등)
    SYMB: str = "",       # 종목코드 (AAPL, TSLA 등)
):
    """
    해외 실시간상세현재가 조회
    - AUTH: 사용자권한정보(문서상 필수), 보통 헤더에 토큰 쓰지만 문서엔 Query Param
    - EXCD: 거래소코드 (예: NAS, NYS, AMS 등)
    - SYMB: 종목코드 (예: AAPL, TSLA 등)
    """

    url = "https://openapi.koreainvestment.com:9443/uapi/overseas-price/v1/quotations/price-detail"

    # 모든 Query Param을 딕셔너리로 구성
    params = {
        "AUTH": AUTH,
        "EXCD": EXCD,
        "SYMB": SYMB,
    }
    
    # 해외주식 현재가 상세 TR_ID: HHDFS76200200
    return fetch_api(url, "HHDFS76200200", params=params)

@app.get("/overseas/news")
def get_overseas_news(
    INFO_GB: str = "",       # 뉴스구분(전체=공백)
    CLASS_CD: str = "",      # 중분류(전체=공백)
    NATION_CD: str = "",     # 국가코드(전체=공백, CN, HK, US 등)
    EXCHANGE_CD: str = "",   # 거래소코드(전체=공백)
    SYMB: str = "",          # 종목코드(전체=공백)
    DATA_DT: str = "",       # 조회일자(YYYYMMDD), 전체=공백
    DATA_TM: str = "",       # 조회시간(HHMMSS), 전체=공백
    CTS: str = "",           # 다음키(연속조회), 전체=공백
):
    """
    해외뉴스종합(제목) 조회
    - INFO_GB: 뉴스구분 (전체=공백)
    - CLASS_CD: 중분류 (전체=공백)
    - NATION_CD: 국가코드 (CN, HK, US 등)
    - EXCHANGE_CD: 거래소코드
    - SYMB: 종목코드
    - DATA_DT: 조회일자(YYYYMMDD)
    - DATA_TM: 조회시간(HHMMSS)
    - CTS: 다음키(연속조회)
    """

    url = "https://openapi.koreainvestment.com:9443/uapi/overseas-price/v1/quotations/news-title"

    params = {
        "INFO_GB": INFO_GB,
        "CLASS_CD": CLASS_CD,
        "NATION_CD": NATION_CD,
        "EXCHANGE_CD": EXCHANGE_CD,
        "SYMB": SYMB,
        "DATA_DT": DATA_DT,
        "DATA_TM": DATA_TM,
        "CTS": CTS
    }
    
    # 해외뉴스종합(제목) TR_ID: HHPSTH60100C1
    return fetch_api(url, "HHPSTH60100C1", params=params)
