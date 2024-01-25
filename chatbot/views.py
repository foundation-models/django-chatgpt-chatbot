from django.shortcuts import render,redirect
from django.http import JsonResponse
import openai

from django.contrib import auth
from django.contrib.auth.models import User
from .models import Chat

from django.utils import timezone
import os
import string
from openai import OpenAI

openai_api_key = 'YOUR_API_KEY' # Replace YOUR_API_KEY with your openai apikey 
openai.api_key = openai_api_key
 
openai.api_type = "open_ai"
openai_api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
model_name = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
instruction = os.getenv("INSTRUCTION")

client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key=openai_api_key,
    base_url=openai_api_base,
)

def ask_openai(message):
    if instruction:
        template = string.Template(instruction)
        record = {'input': message }
        message = template.substitute(record)
    completion = client.completions.create(
        model = model_name,
        prompt = message,
        # max_tokens=150,
        # n=1,
        # stop='xxx',
        # temperature=0.7,
        # stream=True,
        # messages=[
        #     {"role": "system", "content": "You are an helpful assistant."},
        #     {"role": "user", "content": message},
        # ]
    )
    answer = completion.choices[0].text
    return answer

# Create your views here.

def chatbot(request):
    chats = Chat.objects.filter(user=request.user)


    if request.method == 'POST':
        message = request.POST.get('message')
        response = ask_openai(message)

        chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now)
        chat.save()
        return JsonResponse({'message': message, 'response': response})
    return render(request, 'chatbot.html', {'chats': chats})


def login(request):
    if request.method=='POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('chatbot')
        else:
            error_message = 'Invalid username or password'
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1==password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                auth.login(request, user)
                return redirect('chatbot')
            except:
                error_message = 'Error creating account'
            return render(request, 'register.html', {'error_message': error_message})
        else:
            error_message = "Password don't match" 
            return render(request, 'register.html', {'error_message': error_message})
    return render(request, 'register.html')

def logout(request):
    auth.logout(request)
    return redirect('login')