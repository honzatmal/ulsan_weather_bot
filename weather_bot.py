import requests
import os
from datetime import datetime, timedelta

def get_weather():
    # 1. GitHub Secrets에서 환경 변수 불러오기
    api_key = os.environ.get('WEATHER_API_KEY')
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    # 2. 한국 시간(KST) 계산 (서버 시간 UTC에 9시간 추가)[cite: 2]
    now_utc = datetime.utcnow()
    now_kst = now_utc + timedelta(hours=9)
    formatted_date = now_kst.strftime("%Y년 %m월 %d일 (%a)")
    formatted_time = now_kst.strftime("%H시 %M분")
    
    # 3. WeatherAPI 데이터 호출 (울산 지역 설정)[cite: 2]
    city = "Ulsan"
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}&aqi=yes&lang=ko"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        # 날씨 정보 파싱[cite: 2]
        current = data['current']
        condition = current['condition']['text']
        temp = current['temp_c']
        wind = current['wind_kph']
        precip = current['precip_mm']
        
        # 미세먼지 지수 변환[cite: 2]
        aqi_index = current['air_quality']['us-epa-index']
        aqi_text = {1: "좋음", 2: "보통", 3: "민감군 주의", 4: "나쁨", 5: "매우 나쁨", 6: "위험"}.get(aqi_index, "정보 없음")

        # 4. 메시지 구성 (날짜/시간 포함)[cite: 2]
        message = (
            f"📅 {formatted_date} {formatted_time}\n"
            f"📍 {city} 날씨 리포트\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🌡️ 기온: {temp}°C ({condition})\n"
            f"🌧️ 강수량: {precip}mm\n"
            f"💨 풍속: {wind}km/h\n"
            f"😷 미세먼지: {aqi_text}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"상쾌한 아침 되세요! ☕"
        )
        
        # 5. 텔레그램 메시지 전송[cite: 2]
        send_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message}
        requests.post(send_url, json=payload)
        print(f"{formatted_time}에 성공적으로 메시지를 전송했습니다.")
        
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    get_weather()
