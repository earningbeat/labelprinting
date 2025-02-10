from flask import Flask, request, jsonify
import requests
import pandas as pd
import io
import os

app = Flask(__name__)

# GitHub Raw 파일 URL (본인 저장소 URL로 변경)
GITHUB_FILE_URL = "https://raw.githubusercontent.com/earningbeat/labelprinting/main/data/label.xlsx"

# GitHub의 엑셀 데이터 가져오기
def fetch_data_from_github():
    response = requests.get(GITHUB_FILE_URL)
    if response.status_code == 200:
        excel_data = io.BytesIO(response.content)
        df = pd.read_excel(excel_data, engine='openpyxl', header=None)
        return df
    else:
        return None

# 거래처 목록 반환
@app.route('/get_clients', methods=['GET'])
def get_clients():
    df = fetch_data_from_github()
    if df is None:
        return jsonify({"error": "데이터를 가져올 수 없습니다."}), 500

    clients = df.iloc[0].dropna().tolist()  # 첫 번째 행에서 거래처명 추출
    return jsonify(clients)

# 특정 거래처의 품목 목록 반환
@app.route('/get_items', methods=['GET'])
def get_items():
    client = request.args.get('client')
    if not client:
        return jsonify({"error": "거래처명이 필요합니다."}), 400

    df = fetch_data_from_github()
    if df is None:
        return jsonify({"error": "데이터를 가져올 수 없습니다."}), 500

    try:
        column_index = df.iloc[0][df.iloc[0] == client].index[0]
    except IndexError:
        return jsonify({"error": "해당 거래처가 존재하지 않습니다."}), 404

    items = df.iloc[1:, column_index].dropna().tolist()
    return jsonify(items)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
