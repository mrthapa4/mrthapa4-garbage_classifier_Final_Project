from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import UserProfile
import tensorflow as tf
from tensorflow.keras.models import load_model
from PIL import Image
import numpy as np
from django.conf import settings
import os
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import requests
from django.utils.text import get_valid_filename
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import uuid

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(base_dir, 'garbage_dashboard', 'models', 'new_grabage_model.keras')


if not os.path.exists(model_path):
    print(f"Model file not found at: {model_path}")
    model = None
    CLASS_NAMES = []
else:
    try:
        model = load_model(model_path) 
        CLASS_NAMES = ['battery', 'biological', 'brown-glass', 'cardboard', 'clothes', 'green-glass', 'metal', 'paper', 'plastic', 'shoes', 'trash', 'white-glass']
    except Exception as e:
        print(f"Error loading model: {e}")
        model = None
        CLASS_NAMES = []
print('class names:', CLASS_NAMES)
def index(request):
   
    user_ip = request.META.get('HTTP_X_FORWARDED_FOR')
    if user_ip:
        user_ip = user_ip.split(',')[0] 
    else:
        user_ip = request.META.get('REMOTE_ADDR', '127.0.0.1')

   
    try:
        ip_response = requests.get(f'https://ipapi.co/{user_ip}/json/')
        ip_response.raise_for_status()
        location_data = ip_response.json()
        lat = location_data.get('latitude', '27.7172')  
        lon = location_data.get('longitude', '85.3240')
        city = location_data.get('city', 'Kathmandu')
        country = location_data.get('country_name', 'Nepal')
    except requests.exceptions.RequestException as e:
        print(f"Error fetching user location: {e}")
        lat, lon, city, country = '27.7172', '85.3240', 'Kathmandu', 'Nepal' 

    
    api_key = "cbaf362016e829407370f3254c7c951e"  
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        air_quality_data = response.json()

        # Extract AQI and pollutant components
        aqi = air_quality_data['list'][0]['main']['aqi']  
        components = air_quality_data['list'][0]['components']
        pm25 = components.get('pm2_5', 'N/A')  # PM2.5 concentration
        pm10 = components.get('pm10', 'N/A')  # PM10 concentration
        o3 = components.get('o3', 'N/A')  # Ozone concentration
        no2 = components.get('no2', 'N/A')  # Nitrogen Dioxide concentration
        so2 = components.get('so2', 'N/A')  # Sulfur Dioxide concentration
        co = components.get('co', 'N/A')  # Carbon Monoxide concentration

        
        aqi_levels = {
            1: "Good",
            2: "Fair",
            3: "Moderate",
            4: "Poor",
            5: "Very Poor"
        }
        aqi_description = aqi_levels.get(aqi, "Unknown")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching air quality data: {e}")
        aqi_description = "Error"
        pm25 = pm10 = o3 = no2 = so2 = co = "N/A"

    
    return render(request, 'index.html', {
        'location': f"{city}, {country}",
        'aqi_description': aqi_description,
        'pm25': pm25,
        'pm10': pm10,
        'o3': o3,
        'no2': no2,
        'so2': so2,
        'co': co,
    })

# @login_required
# def upload_file(request):
#     if request.method == 'POST':
#         file = request.FILES.get('file')
#         if file:
#             try:
#                 img = Image.open(file)
#                 if img.mode in ('RGBA', 'LA'):
#                     img = img.convert('RGB')
#                 img = img.resize((224, 224))
#                 img_array = np.expand_dims(np.array(img) / 255.0, axis=0)

#                 if model:
#                     user_profile = request.user.profile
#                     if not user_profile.deduct_tokens(amount=3):
#                         return render(request, 'upload.html', {
#                             'error': 'Insufficient tokens to classify image. You need at least 3 tokens.',
#                             'tokens': user_profile.tokens,
#                         })

                   
#                     safe_filename = get_valid_filename(file.name)
#                     file_path = default_storage.save(safe_filename, ContentFile(file.read()))

#                     # Classify the image
#                     prediction = model.predict(img_array)[0]
#                     confidence = np.max(prediction) * 100
#                     predicted_class_index = np.argmax(prediction)
#                     predicted_class_name = CLASS_NAMES[predicted_class_index]

                    
#                     result = f'Prediction: {predicted_class_name} (Confidence: {confidence:.2f}%)'
#                     full_image_path = f'{settings.MEDIA_URL}{file_path}'

                    
#                     return render(request, 'upload.html', {
#                         'result': result,
#                         'image_path': full_image_path,
#                         'tokens': user_profile.tokens,
#                         'deducted': True,
#                     })
#                 else:
#                     return render(request, 'upload.html', {'error': 'Model loading failed.', 'tokens': request.user.profile.tokens})

#             except Exception as e:
#                 return render(request, 'upload.html', {'error': f'Error processing image: {e}', 'tokens': request.user.profile.tokens})
#         else:
#             return render(request, 'upload.html', {'error': 'Please upload an image.', 'tokens': request.user.profile.tokens})
#     return render(request, 'upload.html', {'tokens': request.user.profile.tokens})
@login_required
def upload_file(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if file:
            try:
                img = Image.open(file)
                if img.mode in ('RGBA', 'LA'):
                    img = img.convert('RGB')
                img = img.resize((224, 224))
                img_array = np.expand_dims(np.array(img) / 255.0, axis=0)

                if hasattr(request.user, 'profile'):
                    user_profile = request.user.profile
                    if not user_profile.deduct_tokens(amount=3):
                        return render(request, 'upload.html', {
                            'error': 'Insufficient tokens to classify image. You need at least 3 tokens.',
                            'tokens': user_profile.tokens,
                        })

                    # Generate a unique filename for the static file
                    unique_filename = f"{uuid.uuid4().hex}_{get_valid_filename(file.name)}"
                    static_image_path = os.path.join('classified_images', unique_filename)
                    full_static_path = os.path.join(settings.STATIC_ROOT, static_image_path)

                    # Ensure the directory exists
                    os.makedirs(os.path.dirname(full_static_path), exist_ok=True)

                    # Save the processed image to the static directory
                    img.save(full_static_path)

                    # Construct the static URL
                    static_image_url = os.path.join(settings.STATIC_URL, static_image_path)

                    # Classify the image
                    prediction = model.predict(img_array)[0]
                    confidence = np.max(prediction) * 100
                    predicted_class_index = np.argmax(prediction)
                    predicted_class_name = CLASS_NAMES[predicted_class_index]

                    
                    result = f'Prediction: {predicted_class_name} (Confidence: {confidence:.2f}%)'
                    full_image_path = f'{settings.MEDIA_URL}{file_path}'

                    
                    return render(request, 'upload.html', {
                        'result': result,
                        'image_path': full_image_path,
                        'tokens': user_profile.tokens,
                        'deducted': True,
                    })
                else:
                    return render(request, 'upload.html', {'error': 'User profile not found.', 'tokens': 0})

            except Exception as e:
                return render(request, 'upload.html', {'error': f'Error processing image: {e}', 'tokens': request.user.profile.tokens})
        else:
            return render(request, 'upload.html', {'error': 'Please upload an image.', 'tokens': request.user.profile.tokens})
    return render(request, 'upload.html', {'tokens': request.user.profile.tokens})

def result(request):
  
    return render(request, 'result.html', {'result': 'This is a placeholder for the classification result.'})

@login_required
def profile(request):
    tokens = 0
    if hasattr(request.user, 'profile'):
        tokens = request.user.profile.tokens
    return render(request, 'profile.html', {'user': request.user, 'tokens': tokens})

@login_required
def classify_item(request, item_id):
    try:
        user_profile = request.user.profile
    except UserProfile.DoesNotExist:
        return HttpResponse("User profile not found. Please ensure your profile is created.", status=500)
    classification_result = "Successfully classified item {}".format(item_id)
    user_profile.deduct_tokens()
    return render(request, 'classification_result.html',
                  {'result': classification_result, 'tokens': user_profile.tokens, 'deducted': True})