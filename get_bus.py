import re
import json
import time
import requests
from concurrent.futures import ThreadPoolExecutor

courses = [
{
    "courseId": "0001600990",
     "route": "8系統",
    "destination": "本牧市民公園経由 本牧車庫前行",
    "direction": "honmoku"
},
{
    "courseId": "0001600980",
    "route": "8系統",
    "destination": "本牧車庫前行",
    "direction": "honmoku"
},
{
    "courseId": "0001601028",
    "route": "8系統",
    "destination": "本牧車庫前行",
    "direction": "honmoku"
},
{
    "courseId": "0001600989",
    "route": "8系統",
    "destination": "本牧市民公園経由 横浜駅前行",
    "direction": "up"
},
{
    "courseId": "0001600989",
    "route": "8系統",
    "destination": "横浜駅前行",
    "direction": "up"
},

{
    "courseId": "0001600987",
    "route": "8系統",
    "destination": "三渓園入口経由 横浜駅前行",
    "direction": "up"
},

]

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "ja-JP,ja;q=0.9"
}

def get_buses(course):
    course_id = course["courseId"]

    url = (
        "https://navi.hamabus.city.yokohama.lg.jp/"
        "koutuu/pc/location/BusOperationResult"
        f"?courseId={course_id}"
    )

    print()
    print("================================")
    print(course["route"])
    print(course["destination"])
    print("courseId:", course_id)
    print("取得中...")
    print("================================")

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=15
        )
        response.raise_for_status()

        html = response.text

        print("HTML取得成功")
        print("文字数:", len(html))

    except Exception as e:
        print("取得エラー:", e)
        return []

    pattern = re.compile(
        r'latlng\s*=\s*new\s+navitime\.geo\.LatLng'
        r'\("([^"]+)",\s*"([^"]+)"\)'
        r'.{0,3000}?'
        r'title:\s*"([^"]+)"',
        re.DOTALL
    )

    matches = pattern.findall(html)
    buses = []

    for latitude, longitude, vehicle_id in matches:
        if not vehicle_id.isdigit():
            continue

        bus = {
            "id": vehicle_id,
            "latitude": float(latitude),
            "longitude": float(longitude),
            "route": course["route"],
            "destination": course["destination"],
            "courseId": course_id,
            "direction": course["direction"]
        }

        buses.append(bus)

        print(
            "バス:",
            vehicle_id,
            latitude,
            longitude
        )

    print("見つかったバス:", len(buses), "台")

    return buses

def update_all_buses():
    all_buses = []

    print()
    print("################################")
    print("横浜市営バス情報を更新します")
    print("################################")

    for course in courses:
        buses = get_buses(course)
        all_buses.extend(buses)
        time.sleep(1)

    data = {
        "updated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "count": len(all_buses),
        "buses": all_buses
    }

    with open(
        "bus_position.json",
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )

    print()
    print("################################")
    print("JSON保存完了")
    print("バスの合計:", len(all_buses), "台")
    print("################################")

print("横浜市営バス 自動更新システム")
print("停止する場合は Ctrl + C")
print()

update_all_buses()
