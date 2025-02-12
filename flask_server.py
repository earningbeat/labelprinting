from flask import Flask, request, jsonify
import requests
import pandas as pd
import io
import os

app = Flask(__name__)

# GitHub 저장소 정보 (본인 저장소 URL로 변경)
GITHUB_OWNER = "earningbeat"
GITHUB_REPO = "labelprinting"
GITHUB_FILE_PATH = "data/label.xlsx"

# GitHub Raw 파일 URL
GITHUB_FILE_URL = f"https://raw.githubusercontent.com/{GITHUB_OWNER}/{GITHUB_REPO}/main/{GITHUB_FILE_PATH}"

# GitHub API URL (마지막 커밋 조회)
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/commits?path={GITHUB_FILE_PATH}&per_page=1"

# GitHub에서 엑셀 데이터 가져오기
def fetch_data_from_github():
    response = requests.get(GITHUB_FILE_URL)

    if response.status_code == 200:
        excel_data = io.BytesIO(response.content)
        df = pd.read_excel(excel_data, engine='openpyxl', header=None)

        # GitHub의 헤더 정보에서 'Last-Modified' 값 가져오기
        last_modified = response.headers.get('Last-Modified', "Unknown")

        return df, last_modified  # ✅ 여기서 두 개의 값을 반환하는지 확인
    else:
        return None, None  # ✅ 실패 시 두 개의 값을 반환해야 오류 안 남

# GitHub API를 사용하여 label.xlsx 파일의 마지막 수정 날짜 가져오기
def get_last_modified_from_github():
    """GitHub API를 사용하여 label.xlsx 파일의 마지막 수정 날짜 가져오기"""
    response = requests.get(GITHUB_API_URL)
    
    if response.status_code == 200:
        commits = response.json()
        if commits:
            last_modified = commits[0]['commit']['committer']['date']  # ISO 8601 형식 (YYYY-MM-DDTHH:MM:SSZ)
            return last_modified
    return "Unknown"

# ✅ 거래처 목록 반환
@app.route('/get_clients', methods=['GET'])
def get_clients():
    df = fetch_data_from_github()
    
    if df is None:
        return jsonify({"error": "데이터를 가져올 수 없습니다."}), 500

    clients = df.iloc[0].dropna().tolist()  # 첫 번째 행에서 거래처명 추출
    return jsonify(clients)

# ✅ 특정 거래처의 품목 목록 반환
@app.route('/get_items', methods=['GET'])
def get_items():
    client = request.args.get('client')
    if not client:
        return jsonify({"error": "거래처명이 필요합니다."}), 400

    result = fetch_data_from_github()  # ✅ 함수 호출

    # ✅ 반환값이 한 개인지 두 개인지 확인하여 처리
    if isinstance(result, tuple):  # ✅ 두 개의 값이 반환되는 경우
        df, _ = result
    else:  # ✅ 하나의 값만 반환된 경우 (예: df만 반환됨)
        df = result

    if df is None:
        return jsonify({"error": "데이터를 가져올 수 없습니다."}), 500

    try:
        if client not in df.iloc[0].values:
            return jsonify({"error": f"거래처 '{client}'가 존재하지 않습니다."}), 404

        column_index = df.iloc[0][df.iloc[0] == client].index[0]

        # ✅ 품목명과 품목번호 가져오기
        items = df.iloc[1:, column_index].dropna().tolist()
        item_numbers = df.iloc[1:, column_index + 1].dropna().tolist()

        # ✅ 리스트 길이 맞추기 (품목번호가 없는 경우 대비)
        if len(item_numbers) < len(items):
            item_numbers.extend(["번호없음"] * (len(items) - len(item_numbers)))

        # ✅ "상품번호 - 품목명" 형식으로 반환
        items_with_numbers = [f"{num} - {name}" for num, name in zip(item_numbers, items)]

        return jsonify(items_with_numbers)

    except Exception as e:
        return jsonify({"error": f"서버 내부 오류 발생: {str(e)}"}), 500

# ✅ label.xlsx의 마지막 수정 시간 반환 (GitHub API 기반)
@app.route('/get_last_modified', methods=['GET'])
def get_last_modified():
    last_modified = get_last_modified_from_github()
    
    if last_modified == "Unknown":
        return jsonify({"error": "GitHub에서 수정 시간을 가져올 수 없습니다."}), 500
    
    return jsonify({"last_modified": last_modified})

# ✅ 현재 등록된 모든 엔드포인트 확인 (디버깅용)
@app.route('/')
def home():
    """현재 Flask 서버에서 제공하는 엔드포인트 목록을 확인하는 디버깅용 API"""
    endpoints = [str(rule) for rule in app.url_map.iter_rules()]
    return jsonify({"available_endpoints": endpoints})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
