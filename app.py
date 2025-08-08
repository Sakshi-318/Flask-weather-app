from flask import Flask, render_template, request, flash
import requests
import os
from dotenv import load_dotenv
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'myweatherapp2024!@#randomsecret$%^key&*()'
load_dotenv()  # Load .env file
API_KEY = os.getenv('API_KEY')  
BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'

def get_weather_data(city):
    """
    Fetch weather data from OpenWeatherMap API
    """
    try:
        params = {
            'q': city,
            'appid': API_KEY,
            'units': 'metric'  
        }

        response = requests.get(BASE_URL, params=params, timeout=5)

        if response.status_code == 200:
            data = response.json()

            weather_info = {
                'city': data['name'],
                'country': data['sys']['country'],
                'temperature': round(data['main']['temp']),
                'description': data['weather'][0]['description'].title(),
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'wind_speed': data.get('wind', {}).get('speed', 0),
                'icon': data['weather'][0]['icon'],
                'main': data['weather'][0]['main'].lower()
            }
            return weather_info
        
        elif response.status_code == 404:
            return {'error': 'City not found. Please check the spelling and try again.'}
        else:
            return {'error': 'Unable to fetch weather data. Please try again later.'}
            
    except requests.exceptions.Timeout:
        return {'error': 'Request timeout. Please try again.'}
    except requests.exceptions.ConnectionError:
        return {'error': 'Connection error. Please check your internet connection.'}
    except Exception as e:
        return {'error': 'An unexpected error occurred. Please try again.'}

def get_background_class(weather_main):
    """
    Return CSS class based on weather condition
    """
    weather_backgrounds = {
        'clear': 'sunny',
        'clouds': 'cloudy',
        'rain': 'rainy',
        'drizzle': 'rainy',
        'thunderstorm': 'stormy',
        'snow': 'snowy',
        'mist': 'misty',
        'fog': 'misty',
        'haze': 'misty'
    }
    return weather_backgrounds.get(weather_main, 'default')

@app.route('/', methods=['GET', 'POST'])
def index():
    weather_data = None
    background_class = 'default'
    
    if request.method == 'POST':
        city = request.form.get('city', '').strip()
        
        if not city:
            flash('Please enter a city name.', 'error')
        else:
            weather_data = get_weather_data(city)
            
            if 'error' in weather_data:
                flash(weather_data['error'], 'error')
                weather_data = None
            else:
                background_class = get_background_class(weather_data['main'])
    
    return render_template('index.html', 
                         weather=weather_data, 
                         background_class=background_class,
                         current_time=datetime.now().strftime('%Y-%m-%d %H:%M'))

@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    flash('An internal error occurred. Please try again later.', 'error')
    return render_template('index.html'), 500

if __name__ == '__main__':
    app.run(debug=True)