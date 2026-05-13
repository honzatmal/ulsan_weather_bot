import requests
import os
from datetime import datetime, timedelta

def get_weather():
    # 1. 환경 변수 설정
    api_key = os.environ.get('WEATHER_API_KEY')
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    # 2. 날짜 계산 (오늘 및 어제)
    now_utc = datetime.utcnow()
    now_kst = now_utc + timedelta(hours=9)
    yesterday_kst = now_kst - timedelta(days=1)
    
    formatted_date = now_kst.strftime("%Y년 %m월 %d일 (%a)")
    formatted_time = now_kst.strftime("%H시 %M분")
    yesterday_str = yesterday_kst.strftime("%Y-%m-%d")
    
    city = "Ulsan"
    
    try:
        # 오늘 예보 및 현재 날씨 데이터
        url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={city}&days=1&aqi=yes&lang=ko"
        response = requests.get(url).json()
        
        current = response['current']
        temp_now = current['temp_c']
        condition = current['condition']['text']
        
        # 오늘의 최저/최고 기온[cite: 2]
        day_data = response['forecast']['forecastday'][0]['day']
        temp_max = day_data['maxtemp_c']
        temp_min = day_data['mintemp_c']
        
        # 3. 어제의 동일 시간대 기온 가져오기[cite: 2]
        history_url = f"http://api.weatherapi.com/v1/history.json?key={api_key}&q={city}&dt={yesterday_str}&lang=ko"
        history_response = requests.get(history_url).json()
        # 어제 같은 시간(정시 기준)의 기온 추출[cite: 2]
        temp_yesterday = history_response['forecast']['forecastday'][0]['hour'][now_kst.hour]['temp_c']
        
        # 기온 차이 계산[cite: 2]
        temp_diff = round(temp_now - temp_yesterday, 1)
        if temp_diff > 0:
            diff_text = f"어제보다 {temp_diff}도 높아요 📈"
        elif temp_diff < 0:
            diff_text = f"어제보다 {abs(temp_diff)}도 낮아요 📉"
        else:
            diff_text = "어제와 기온이 같아요 ↔️"

        # 4. 강수 예보 확인[cite: 2]
        forecast_hours = response['forecast']['forecastday'][0]['hour']
        rain_times = [datetime.strptime(h['time'], '%Y-%m-%d %H:%M').strftime("%H시") 
                      for h in forecast_hours if datetime.strptime(h['time'], '%Y-%m-%d %H:%M') > now_kst 
                      and (h['will_it_rain'] or h['will_it_snow'])]
        
        rain_info = f"☔ 강수 예보: {', '.join(rain_times[:5])} 내외" if rain_times else "☀️ 오늘은 비 소식이 없습니다."

        # 미세먼지[cite: 2]
        aqi_index = current['air_quality']['us-epa-index']
        aqi_text = {1: "좋음", 2: "보통", 3: "민감군 주의", 4: "나쁨", 5: "매우 나쁨", 6: "위험"}.get(aqi_index, "정보 없음")

        # 5. 메시지 구성[cite: 2]
        message = (
            f"📅 {formatted_date} {formatted_time}\n"
            f"📍 {city} 날씨 리포트\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🌡️ 현재 기온: {temp_now}°C ({condition})\n"
            f"🌡️ {diff_text}\n"
            f"📈 최고: {temp_max}°C / 📉 최저: {temp_min}°C\n"
            f"😷 미세먼지: {aqi_text}\n"
            f"📢 {rain_info}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"오늘도 힘찬 하루 되세요! 💪"
        )
        
        send_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        requests.post(send_url, json={"chat_id": chat_id, "text": message})
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_weather()
