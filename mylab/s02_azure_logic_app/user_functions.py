# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import json
import datetime
from typing import Any, Callable, Set, Dict, List, Optional

# 這些是可被 agent 呼叫的用戶定義函數。


def fetch_current_datetime(format: Optional[str] = None) -> str:
    """
    以 JSON 字串形式取得目前時間，可選擇性地格式化。

    :param format (Optional[str]): 返回目前時間的格式。預設為 None，將使用標準格式。
    :return: JSON 格式的目前時間。
    :rtype: str
    """
    current_time = datetime.datetime.now()

    # 如果有提供格式則使用，否則使用預設格式
    if format:
        time_format = format
    else:
        time_format = "%Y-%m-%d %H:%M:%S"

    time_json = json.dumps({"current_time": current_time.strftime(time_format)})
    return time_json


def fetch_weather(location: str) -> str:
    """
    取得指定地點的天氣資訊。

    :param location (str): 要取得天氣的地點。
    :return: 以 JSON 字串形式的天氣資訊。
    :rtype: str
    """
    # 在實際應用中，您會整合天氣 API。
    # 這裡我們將模擬回應。
    mock_weather_data = {"New York": "Sunny, 25°C", "London": "Cloudy, 18°C", "Tokyo": "Rainy, 22°C"}
    weather = mock_weather_data.get(location, "Weather data not available for this location.")
    weather_json = json.dumps({"weather": weather})
    return weather_json


def send_email(recipient: str, subject: str, body: str) -> str:
    """
    傳送電子郵件，包含指定的主旨和內容給收件人。

    :param recipient (str): 收件人的電子郵件地址。
    :param subject (str): 電子郵件的主旨。
    :param body (str): 電子郵件的內容。
    :return: 確認訊息。
    :rtype: str
    """
    # 在實際應用中，您會使用 SMTP 伺服器或電子郵件服務 API。
    # 這裡我們將模擬電子郵件傳送。
    print(f"傳送電子郵件到 {recipient}...")
    print(f"主旨: {subject}")
    print(f"內容:\n{body}")

    message_json = json.dumps({"message": f"電子郵件已成功傳送到 {recipient}。"})
    return message_json


def send_email_using_recipient_name(recipient: str, subject: str, body: str) -> str:
    """
    傳送電子郵件，包含指定的主旨和內容給收件人。

    :param recipient (str): 收件人的姓名。
    :param subject (str): 電子郵件的主旨。
    :param body (str): 電子郵件的內容。
    :return: 確認訊息。
    :rtype: str
    """
    # 在實際應用中，您會使用 SMTP 伺服器或電子郵件服務 API。
    # 這裡我們將模擬電子郵件傳送。
    print(f"傳送電子郵件到 {recipient}...")
    print(f"主旨: {subject}")
    print(f"內容:\n{body}")

    message_json = json.dumps({"message": f"電子郵件已成功傳送到 {recipient}。"})
    return message_json


def calculate_sum(a: int, b: int) -> str:
    """計算兩個整數的總和。

    :param a (int): 第一個整數。
    :rtype: int
    :param b (int): 第二個整數。
    :rtype: int

    :return: 兩個整數的總和。
    :rtype: str
    """
    result = a + b
    return json.dumps({"result": result})


def convert_temperature(celsius: float) -> str:
    """將溫度從攝氏度轉換為華氏度。

    :param celsius (float): 攝氏度的溫度。
    :rtype: float

    :return: 華氏度的溫度。
    :rtype: str
    """
    fahrenheit = (celsius * 9 / 5) + 32
    return json.dumps({"fahrenheit": fahrenheit})


def toggle_flag(flag: bool) -> str:
    """切換布林旗標。

    :param flag (bool): 要切換的旗標。
    :rtype: bool

    :return: 切換後的旗標。
    :rtype: str
    """
    toggled = not flag
    return json.dumps({"toggled_flag": toggled})


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> str:
    """合併兩個字典。

    :param dict1 (Dict[str, Any]): 第一個字典。
    :rtype: dict
    :param dict2 (Dict[str, Any]): 第二個字典。
    :rtype: dict

    :return: 合併後的字典。
    :rtype: str
    """
    merged = dict1.copy()
    merged.update(dict2)
    return json.dumps({"merged_dict": merged})


def get_user_info(user_id: int) -> str:
    """根據用戶 ID 檢索用戶資訊。

    :param user_id (int): 用戶的 ID。
    :rtype: int

    :return: 以 JSON 字串形式的用戶資訊。
    :rtype: str
    """
    mock_users = {
        1: {"name": "Alice", "email": "alice@example.com"},
        2: {"name": "Bob", "email": "bob@example.com"},
        3: {"name": "Charlie", "email": "charlie@example.com"},
    }
    user_info = mock_users.get(user_id, {"error": "找不到用戶。"})
    return json.dumps({"user_info": user_info})


def longest_word_in_sentences(sentences: List[str]) -> str:
    """找出每個句子中最長的單詞。

    :param sentences (List[str]): 句子清單。
    :return: 將每個句子映射到其最長單詞的 JSON 字串。
    :rtype: str
    """
    if not sentences:
        return json.dumps({"error": "句子清單為空"})

    longest_words = {}
    for sentence in sentences:
        # 將句子分割為單詞
        words = sentence.split()
        if words:
            # 找出最長的單詞
            longest_word = max(words, key=len)
            longest_words[sentence] = longest_word
        else:
            longest_words[sentence] = ""

    return json.dumps({"longest_words": longest_words})


def process_records(records: List[Dict[str, int]]) -> str:
    """
    處理記錄清單，其中每個記錄是一個將字串映射到整數的字典。

    :param records: 包含將字串映射到整數的字典的清單。
    :return: 每個記錄中整數值總和的清單。
    """
    sums = []
    for record in records:
        # 將每個字典中的所有值相加，並將結果附加到總和清單中
        total = sum(record.values())
        sums.append(total)
    return json.dumps({"sums": sums})


# 每個函數的範例用戶輸入
# 1. 取得目前日期時間
#    用戶輸入: "目前的日期和時間是什麼？"
#    用戶輸入: "以 '%Y-%m-%d %H:%M:%S' 格式顯示目前的日期和時間是什麼？"

# 2. 取得天氣
#    用戶輸入: "您能提供紐約的天氣資訊嗎？"

# 3. 傳送電子郵件
#    用戶輸入: "傳送電子郵件到 john.doe@example.com，主旨是 '會議提醒'，內容是 '別忘了我們下午3點的會議。'"

# 4. 計算總和
#    用戶輸入: "45 和 55 的總和是多少？"

# 5. 轉換溫度
#    用戶輸入: "將攝氏25度轉換為華氏度。"

# 6. 切換旗標
#    用戶輸入: "切換旗標 True。"

# 7. 合併字典
#    用戶輸入: "合併這兩個字典: {'name': 'Alice'} 和 {'age': 30}。"

# 8. 取得用戶資訊
#    用戶輸入: "檢索用戶 ID 1 的用戶資訊。"

# 9. 句子中最長的單詞
#    用戶輸入: "找出這些句子中每個句子的最長單詞: ['The quick brown fox jumps over the lazy dog', 'Python is an amazing programming language', 'Azure AI capabilities are impressive']。"

# 10. 處理記錄
#     用戶輸入: "處理以下記錄: [{'a': 10, 'b': 20}, {'x': 5, 'y': 15, 'z': 25}, {'m': 30}]。"

# 快速參考用的靜態定義用戶函數
user_functions: Set[Callable[..., Any]] = {
    fetch_current_datetime,
    fetch_weather,
    send_email,
    calculate_sum,
    convert_temperature,
    toggle_flag,
    merge_dicts,
    get_user_info,
    longest_word_in_sentences,
    process_records,
}