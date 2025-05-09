# Garbage Classification App

## Overview
A web application for classifying waste images into 12 categories using a Django backend with TensorFlow. Users can upload images, and the app returns the waste type.

## Features
- **Image Upload**: Upload waste images via a web interface.
- **Classification**: Classifies images into:
  - Metal, White-glass, Biological, Paper, Brown-glass, Battery, Trash, Cardboard, Shoes, Clothes, Plastic, Green-glass
- **Results**: Displays classification results to users.
- **Backend**: Django with TensorFlow (MobileNet and VGG16 models).
- **Authentication**: Google login/signup via django-allauth.

## Technologies
- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python, Django, TensorFlow, MobileNet, VGG16, django-allauth, uv
- **Models**: Hosted on [Google Drive](https://drive.google.com/drive/folders/1GslR2Hw9k7YF1Y6zhIgcd0adAcmAM85A?usp=drive_link)
- **Kaggle Notebook**: [Garbage Classifier](https://www.kaggle.com/code/mrthapa4/gragbage-classifier/edit)

## Dataset
Trained on a dataset of 15,515 images:
- Metal: 769, White-glass: 775, Biological: 985, Paper: 1050, Brown-glass: 607, Battery: 945, Trash: 697, Cardboard: 891, Shoes: 1977, Clothes: 5325, Plastic: 865, Green-glass: 629

## Setup
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/mrthapa4/garbage_classifier_Project.git
   cd Garbage-Classifier-
