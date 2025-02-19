import os
import requests
import logging
import websocket
import json
import time

# API 정보 (한국투자증권에서 발급받은 키 입력)
APP_KEY = "PSS77BcpFVjx6mr0xU4bK02Tu2uj7nYZ18FL"
APP_SECRET = "ci2N8p4PRptjoXJAc4aobn2KxRR9L1ElmClstGHGxAmDw6dxPl+NQKWm23lnE5kAj6VpwmGu0/VIwgHWrbw7IZhfZIaxQQl/47FScPhcJDyRrYGQZGKkv6uAkZ4jdmhz6x6pJTJL2TidM4J9HPUpYHHJIGGBXIc5dMtP7uQp8RgqMo0NNBo="

# 모의투자 도메인 사용
BASE_URL = "https://openapivts.koreainvestment.com:29443"

# 웹소켓 서버 주소 (모의투자 환경)
WS_URL = "ws://ops.koreainvestment.com:31000"

# 조회할 종목 코드 (예: 삼성전자)
STOCK_CODE = "005930"

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def get_approval_key():
    """실시간 웹소켓 접속키 발급"""
    url = f"{BASE_URL}/oauth2/Approval"
    headers = {"content-type": "application/json; utf-8"}
    payload = {
        "grant_type": "client_credentials",
        "appkey": APP_KEY,
        "secretkey": APP_SECRET
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()
        approval_key = data.get("approval_key")
        if approval_key:
            logging.info(f"✅ 승인 키 발급 성공: {approval_key}")
            return approval_key
        else:
            logging.error("❌ 승인 키 응답에 'approval_key' 없음")
    else:
        logging.error(f"❌ 승인 키 발급 실패: {response.text}")

    return None


def on_message(ws, message):
    """웹소켓 메시지 수신 이벤트"""
    try:
        data = json.loads(message)

        # PINGPONG 메시지 처리
        if "header" in data and data["header"].get("tr_id") == "PINGPONG":
            logging.info("PINGPONG 메시지 수신 - 응답 전송")
            ws.send(json.dumps({"header": {"tr_id": "PINGPONG"}}))  # 서버에 응답

        # 정상적인 데이터 응답
        elif "body" in data:
            if data["body"].get("rt_cd") == "0":
                logging.info(f"삼성전자 실시간 주가 업데이트: {data['body'].get('msg1', 'N/A')}")
            else:
                error_code = data["body"].get("msg_cd", "Unknown")
                error_msg = data["body"].get("msg1", "No message")
                logging.error(f"웹소켓 오류 ({error_code}): {error_msg}")

        else:
            logging.warning("웹소켓 응답에 예상된 데이터가 없습니다.")

    except json.JSONDecodeError:
        logging.error("웹소켓 응답을 JSON으로 변환할 수 없음")


def on_error(ws, error):
    """웹소켓 오류 발생 이벤트"""
    logging.error(f"웹소켓 오류: {error}")


def on_close(ws, close_status_code, close_msg):
    """웹소켓 연결 종료 이벤트 - 자동 재연결"""
    logging.warning("웹소켓 연결이 끊어졌습니다. 5초 후 재연결 시도...")
    time.sleep(5)
    connect_websocket()


def on_open(ws):
    """웹소켓 연결 성공 시 실행되는 함수"""
    logging.info("✅ 웹소켓 연결 성공, 구독 요청 전송")

    # 웹소켓 요청 데이터
    request_data = {
        "header": {
            "approval_key": approval_key,  # 발급받은 approval_key 사용
            "custtype": "P",
            "tr_type": "1",
            "content-type": "utf-8"
        },
        "body": {
            "input": {
                "tr_id": "H0STCNT0",
                "tr_key": STOCK_CODE
            }
        }
    }

    ws.send(json.dumps(request_data))


def connect_websocket():
    """웹소켓 서버에 연결하는 함수 - 재연결 기능 포함"""
    global approval_key
    approval_key = get_approval_key()
    if not approval_key:
        logging.error("❌ 승인 키 발급 실패로 웹소켓 연결을 종료합니다.")
        return

    while True:
        try:
            ws = websocket.WebSocketApp(WS_URL,
                                        on_open=on_open,
                                        on_message=on_message,
                                        on_error=on_error,
                                        on_close=on_close)
            ws.run_forever()
        except Exception as e:
            logging.error(f"웹소켓 연결 중 오류 발생: {e}")
            logging.info("5초 후 다시 연결을 시도합니다...")
            time.sleep(5)


if __name__ == "__main__":
    connect_websocket()
