import requests
import os
from datetime import datetime, timedelta

def get_weather():
    # 1. 환경 변수 설정
    api_key = os.environ.get('WEATHER_API_KEY')
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    # 2. 한국 시간 계산
    now_utc = datetime.utcnow()
    now_kst = now_utc + timedelta(hours=9)
    formatted_date = now_kst.strftime("%Y년 %m월 %d일 (%a)")
    formatted_time = now_kst.strftime("%H시 %M분")
    
    city = "Ulsan"
    # 예보 데이터를 포함하여 호출[cite: 2]
    url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={city}&days=1&aqi=yes&lang=ko"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        # 현재 및 예보 데이터 파싱[cite: 2]
        current = data['current']
        condition = current['condition']['text']
        temp_now = current['temp_c']
        
        # 오늘의 최저/최고 기온[cite: 2]
        day_data = data['forecast']['forecastday'][0]['day']
        temp_max = day_data['maxtemp_c']
        temp_min = day_data['mintemp_c']
        
        # 강수 시간대 확인[cite: 2]
        forecast_hours = data['forecast']['forecastday'][0]['hour']
        rain_times = []
        for hour_data in forecast_hours:
            hour_time = datetime.strptime(hour_data['time'], '%Y-%m-%d %H:%M')
            if hour_time > now_kst:
                if hour_data['will_it_rain'] or hour_data['will_it_snow']:
                    rain_times.append(hour_time.strftime("%H시"))
        
        if rain_times:
            rain_info = f"☔ 강수 예보: {', '.join(rain_times[:5])} 내외"
        else:
            rain_info = "☀️ 오늘은 비 소식이 없습니다."

        # 미세먼지[cite: 2]
        aqi_index = current['air_quality']['us-epa-index']
        aqi_text = {1: "좋음", 2: "보통", 3: "민감군 주의", 4: "나쁨", 5: "매우 나쁨", 6: "위험"}.get(aqi_index, "정보 없음")

        # 3. 메시지 구성 (최고/최저 기온 추가)[cite: 2]
        message = (
            f"📅 {formatted_date} {formatted_time}\n"
            f"📍 {city} 날씨 리포트\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🌡️ 현재: {temp_now}°C ({condition})\n"
            f"📈 최고: {temp_max}°C / 📉 최저: {temp_min}°C\n"
            f"😷 미세먼지: {aqi_text}\n"
            f"📢 {rain_info}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"오늘도 건강한 하루 되세요! 💪"
        )
        
        # 4. 텔레그램 전송[cite: 2]
        send_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message}
        requests.post(send_url, json=payload)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_weather()
