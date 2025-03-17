from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm, LoginForm



import json
import random
import webbrowser
import os
import requests
import datetime
import subprocess
import wikipedia
import speech_recognition as sr
import pywhatkit
import pyaudio
import wave
import math
import threading
import time
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import speedtest
import pyautogui
import platform
import pyttsx3
from translate import Translator
from plyer import notification
import wmi
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import winsound

# Global variables
alarms = []
remembered_items = {}

def login_signup_view(request):
    if request.method == 'POST':
        # Check which form was submitted
        if 'signup-form' in request.POST:
            # Process signup form
            signup_form = SignUpForm(request.POST)
            if signup_form.is_valid():
                user = signup_form.save()
                # Log in the user after signup
                login(request, user)
                return redirect('index')  # Redirect to home page
            login_form = LoginForm()  # Empty login form
        else:
            # Process login form
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                email = login_form.cleaned_data.get('email')
                password = login_form.cleaned_data.get('password')
                remember_me = login_form.cleaned_data.get('remember_me')
                
                # Find user by email
                try:
                    username = User.objects.get(email=email).username
                    user = authenticate(username=username, password=password)
                    if user:
                        login(request, user)
                        # Handle remember me
                        if not remember_me:
                            request.session.set_expiry(0)
                        return redirect('index')  # Redirect to home page
                except User.DoesNotExist:
                    login_form.add_error('email', 'No user found with this email')
            signup_form = SignUpForm()  # Empty signup form
    else:
        login_form = LoginForm()
        signup_form = SignUpForm()
    
    return render(request, 'assistant/login.html', {
        'login_form': login_form, 
        'signup_form': signup_form
    })

def logout_view(request):
    logout(request)
    return redirect('login')


def about_view(request):
    return render(request, 'assistant/about.html')

def service_view(request):
    return render(request, 'assistant/service.html')


def home(request):
    return render(request,"assistant/main.html",locals())


def index(request):
    return render(request, 'assistant/index.html')

def process_voice(request):
    """Process voice input from the frontend"""
    if request.method == 'POST':
        data = json.loads(request.body)
        transcript = data.get('transcript', '').lower()
        
        response = ""
        
        # Hotword detection is handled in JavaScript in the frontend
        
        # 1. Basic conversation responses
        if re.search(r'\b(hey nova|hi nova|hello nova)\b', transcript):
            response = "Hello! I'm Nova, your personal voice assistant. How can I help you today?"
        elif re.search(r'\b(who are you|introduce yourself)\b', transcript):
            response = "I am Nova, your personal AI voice assistant. I can help with searches, play music, set alarms, and much more!"
        elif re.search(r'\b(hello|hi)\b', transcript):
            response = "Hello! How can I assist you today?"
        elif "how are you" in transcript:
            response = "I'm functioning perfectly! How can I help you?"
        elif "i am fine" in transcript or "i'm good" in transcript or "i'm fine" in transcript:
            response = "That's great to hear! What can I help you with today?"
        elif "thank you" in transcript or "thanks" in transcript:
            response = "You're welcome! Is there anything else I can help with?"
        
        # 2. Web search functionality
        elif any(phrase in transcript for phrase in ["find", "google", "look up"]):
            search_query = re.sub(r'\b(find|google|look up)\b', '', transcript).strip()
            if search_query:
                webbrowser.open(f"https://www.google.com/search?q={search_query}")
                response = f"Searching Google for {search_query}"
            else:
                response = "What would you like me to search for?"
        
        # 3. Temperature functionality
        #<---upcoming--->

                
        
        # 4. Time functionality
        elif "time" in transcript:
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            response = f"The current time is {current_time}"
        elif "date" in transcript:
            current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
            response = f"Today is {current_date}"
        
        # 5. Open/Close apps
        elif "open" in transcript:
            app_name = transcript.replace("open", "").strip()
            
            # Dictionary mapping voice commands to application paths
            apps = {
                "notepad": "notepad.exe",
                "calculator": "calc.exe",
                "chrome": "chrome.exe",
                "firefox": "firefox.exe",
                "word": "winword.exe",
                "excel": "excel.exe",
                "spotify": "spotify.exe",
                "outlook": "outlook.exe",
                "powerpoint": "powerpnt.exe",
                "paint": "mspaint.exe",
                "task manager": "taskmgr.exe",
                "file explorer": "explorer.exe",
                "command": "cmd.exe",
                "settings": "ms-settings:",
                "control panel": "control.exe",
            }
            
            # Check if the requested app is in our dictionary
            app_found = False
            for key, value in apps.items():
                if key in app_name:
                    try:
                        os.system(f"start {value}")
                        response = f"Opening {key}"
                        app_found = True
                        break
                    except Exception as e:
                        response = f"Sorry, I couldn't open {key}"
                        app_found = True
            
            if not app_found:
                response = f"I don't know how to open {app_name}"
        
        elif "close" in transcript:
            app_name = transcript.replace("close", "").strip()
            
            # Dictionary mapping voice commands to process names
            apps = {
                "notepad": "notepad.exe",
                "calculator": "calc.exe",
                "chrome": "chrome.exe",
                "firefox": "firefox.exe",
                "word": "winword.exe",
                "excel": "excel.exe",
                "spotify": "spotify.exe",
                "outlook": "outlook.exe",
                "powerpoint": "powerpnt.exe",
                "paint": "mspaint.exe",
                "control panel": "control.exe",
            }
            
            # Check if the requested app is in our dictionary
            app_found = False
            for key, value in apps.items():
                if key in app_name:
                    try:
                        os.system(f"taskkill /f /im {value}")
                        response = f"Closing {key}"
                        app_found = True
                        break
                    except Exception as e:
                        response = f"Sorry, I couldn't close {key}"
                        app_found = True
            
            if not app_found:
                response = f"I don't know how to close {app_name}"
        
        # 6. Alarm functionality
        elif "set alarm" in transcript or "wake me up" in transcript:
            # Extract time from transcript
            time_pattern = r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?"
            matches = re.search(time_pattern, transcript)
            
            if matches:
                hour = int(matches.group(1))
                minute = int(matches.group(2) or 0)
                period = matches.group(3)
                
                # Convert to 24-hour format if needed
                if period and period.lower() == "pm" and hour < 12:
                    hour += 12
                elif period and period.lower() == "am" and hour == 12:
                    hour = 0
                
                # Get current time
                now = datetime.datetime.now()
                alarm_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                # If the time has already passed today, set for tomorrow
                if alarm_time <= now:
                    alarm_time += datetime.timedelta(days=1)
                
                # Store the alarm
                alarm_id = len(alarms)
                alarms.append({
                    "id": alarm_id,
                    "time": alarm_time,
                    "active": True
                })
                
                # Start a thread to handle the alarm
                threading.Thread(target=handle_alarm, args=(alarm_id,), daemon=True).start()
                
                alarm_time_str = alarm_time.strftime("%I:%M %p")
                response = f"Alarm set for {alarm_time_str}"
            else:
                response = "I couldn't understand the time for the alarm. Please try again."
        
        # 7. YouTube functionality
        elif "youtube" in transcript:  
         search = transcript.replace("youtube search", "")
         search = search.replace("youtube", "")
         search = search.replace("jarvis", "")
         web = "https://www.youtube.com/results?search_query=" + search
         webbrowser.open(web)
         pywhatkit.playonyt(search)
         response = "Playing your requested video on YouTube"

        elif "stop" in transcript:
                 pyautogui.press("k")
                 response="video paused"
                
        elif "play" in transcript:
                  pyautogui.press("k")
                  response="video played"
                  
        #20. system control

        elif "mute" in transcript:
                 pyautogui.press("m")
                 response="video muted"

        elif "volume up" in transcript:
                  from .keyboard import volumeup
                  response="Turning volume up,sir"
                  volumeup()

        elif "volume down" in transcript:
                 from .keyboard import volumedown
                 response="Turning volume down, sir"
                 volumedown()
    
        
        # 8. Remember functionality
        elif "remember that" in transcript:
            rememberMessage = transcript.replace("remember that","")
            rememberMessage = transcript.replace("jarvis","")
            response="You told me to remember that"+rememberMessage
            remember = open("Remember.txt","a")
            remember.write(rememberMessage)
            remember.close()
        elif "what do you remember" in transcript:
            remember = open("Remember.txt","r")
            response="You told me to remember that" + remember.read()
        
        # 9. Playing music from playlist/Spotify
        elif "spotify" in transcript or any(keyword in transcript for keyword in ["stream music", "play song", "play track"]):
    # First check if it's a command to open Spotify
            if "open" in transcript and "spotify" in transcript:
                try:
                    os.system("start spotify:") # More reliable way to open Spotify on Windows
                    response = "Opening Spotify"
                except:
                    response = "I couldn't open Spotify"
                    
            elif any(word in transcript for word in ["stop spotify", "close spotify", "quit spotify", "exit spotify"]):
                try:
                    # Use taskkill command to close Spotify properly
                    os.system("taskkill /f /im spotify.exe")
                    response = "Spotify has been closed"
                except:
                    response = "I couldn't close Spotify"
            
            # Handle streaming specific songs
            elif any(pattern in transcript for pattern in ["stream", "play song", "play track"]):
                # Extract the song name - get everything after "stream", "play song", or "play track"
                if "stream" in transcript:
                    music_query = re.sub(r'^.*?stream\s+', '', transcript)
                elif "play song" in transcript:
                    music_query = re.sub(r'^.*?play song\s+', '', transcript)
                elif "play track" in transcript:
                    music_query = re.sub(r'^.*?play track\s+', '', transcript)
                
                # Remove "on spotify" or "spotify" if present at the end
                music_query = re.sub(r'\s+(on spotify|spotify)$', '', music_query).strip()
                
                if music_query:
                    try:
                        # Create properly formatted URI and use proper URL encoding
                        import urllib.parse
                        encoded_query = urllib.parse.quote(music_query)
                        # Use the correct URI format
                        os.system(f'start spotify:search:{encoded_query}')
                        # Give Spotify a moment to process the search
                        time.sleep(2)
                        # Press Enter to play the top result
                        pyautogui.press('space')
                        response = f"Streaming '{music_query}' on Spotify"
                    except Exception as e:
                        response = f"I couldn't stream '{music_query}' on Spotify: {str(e)}"
                else:
                    try:
                        pyautogui.press('playpause')  # Play/Pause shortcut
                        response = "Streaming music"
                    except:
                        response = "I couldn't control music playback"
            

        
        # 10. Calculator functionality
        elif any(op in transcript for op in ["calculate", "plus", "minus", "into", "divided by", "+", "-", "*", "/"]):
            # Convert words to mathematical operations
            calc_text = re.sub(r'\b(calculate|what is|what\'s|equals)\b', '', transcript).strip()
            calc_text = calc_text.replace("plus", "+")
            calc_text = calc_text.replace("minus", "-")
            calc_text = calc_text.replace("into", "*")
            calc_text = calc_text.replace("multiplied by", "*")
            calc_text = calc_text.replace("divided by", "/")
            calc_text = calc_text.replace("x", "*")
            
            # Extract the mathematical expression using regex
            expression = re.findall(r'(\d+(?:\.\d+)?)\s*([+\-*/])\s*(\d+(?:\.\d+)?)', calc_text)
            
            if expression:
                num1 = float(expression[0][0])
                operator = expression[0][1]
                num2 = float(expression[0][2])
                
                result = None
                if operator == '+':
                    result = num1 + num2
                elif operator == '-':
                    result = num1 - num2
                elif operator == '*':
                    result = num1 * num2
                elif operator == '/':
                    if num2 != 0:
                        result = num1 / num2
                    else:
                        response = "I cannot divide by zero."
                
                if result is not None:
                    # Format result to remove trailing zeros if it's a whole number
                    if result.is_integer():
                        result = int(result)
                    response = f"The result is {result}"
            else:
                response = "I couldn't understand the calculation. Please try again."
        
        # 11. News functionality
        #<---upcoming--->
     
                                                        
               
        
        # 12. WhatsApp functionality
        #<---upcoming--->
       

        
        
        # 13. System Shutdown
        elif "shutdown" in transcript or "turn off" in transcript or "power off" in transcript:
            response = "Are you sure you want to shut down your computer? Please say 'yes' to confirm or 'no' to cancel."
            # Store state for follow-up confirmation
            remembered_items["_system_shutdown_pending"] = True
        elif "yes" in transcript and remembered_items.get("_system_shutdown_pending", False):
            # User confirmed shutdown
            remembered_items.pop("_system_shutdown_pending", None)
            try:
                response = "Shutting down your computer now. Goodbye!"
                # Schedule shutdown with a slight delay to allow the response to be sent
                threading.Thread(target=lambda: (time.sleep(5), os.system("shutdown /s /t 1"))).start()
            except:
                response = "I couldn't initiate the shutdown. Please try manually shutting down your computer."
        elif "no" in transcript and remembered_items.get("_system_shutdown_pending", False):
            # User canceled shutdown
            remembered_items.pop("_system_shutdown_pending", None)
            response = "Shutdown canceled. What else can I help you with?"
        
        # 14. Scheduled day
        #<---upcoming--->
        
        
        # 15. Internet speed check
        elif "internet speed" in transcript:
            try:
              wifi = speedtest.Speedtest()
              download_net = wifi.download()/1048576  # Megabyte = 1024*1024 Bytes
              upload_net = wifi.upload()/1048576
        
              download_speed = round(download_net, 2)
              upload_speed = round(upload_net, 2)
        
              response = f"Your download speed is {download_speed} Mbps and upload speed is {upload_speed} Mbps"
            except Exception as e:
              print(f"Speed test error: {e}")
              response = "Sorry, I couldn't check your internet speed"
        
        # 16. Screenshot & Camera
        elif "screenshot" in transcript or "take a screen shot" in transcript:
            try:
                # Generate a filename with timestamp
                screenshot_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = f"screenshots/screenshot_{screenshot_time}.png"
                
                # Ensure directory exists
                os.makedirs("screenshots", exist_ok=True)
                
                # Take screenshot
                screenshot = pyautogui.screenshot()
                screenshot.save(screenshot_path)
                
                response = f"Screenshot taken and saved to {screenshot_path}"
            except:
                response = "I couldn't take a screenshot. Make sure you have the necessary permissions."
        
        elif "camera" in transcript or "take a photo" in transcript or "take a picture" in transcript:
            try:
                # For simplicity, we'll open the camera app
                if os.name == 'nt':  # Windows
                    os.system("start microsoft.windows.camera:")
                else:  # macOS/Linux would need different commands
                    response = "Camera support is currently only available on Windows."
                    return JsonResponse({'response': response})
                    
                response = "Opening the camera app"
            except:
                response = "I couldn't open the camera app."
        
        # 17. Focus Mode
        elif "focus mode" in transcript or "do not disturb" in transcript:
            if "activate" in transcript or "turn on" in transcript or "start" in transcript:
                try:
                    # Turn on do not disturb (Windows)
                    os.system("powershell -command \"(New-Object -ComObject Shell.Application).ToggleDesktop()\"")
                    
                    # Set focus_mode_active flag
                    global focus_mode_active
                    focus_mode_active = True
                    
                    # Calculate end time (30 minutes by default)
                    focus_duration = 30
                    if re.search(r'(\d+)\s*minutes?', transcript):
                        duration_match = re.search(r'(\d+)\s*minutes?', transcript)
                        focus_duration = int(duration_match.group(1))
                    
                    focus_end_time = datetime.datetime.now() + datetime.timedelta(minutes=focus_duration)
                    remembered_items["_focus_end_time"] = focus_end_time
                    
                    # Start a thread to end focus mode
                    threading.Thread(target=end_focus_mode, args=(focus_duration,), daemon=True).start()
                    
                    response = f"Focus mode activated for {focus_duration} minutes. I'll minimize distractions."
                except:
                    response = "I couldn't activate focus mode."
            elif "deactivate" in transcript or "turn off" in transcript or "stop" in transcript:
                try:
                    # Turn off focus mode
                    os.system("powershell -command \"(New-Object -ComObject Shell.Application).ToggleDesktop()\"")
                    focus_mode_active = False
                    remembered_items.pop("_focus_end_time", None)
                    
                    response = "Focus mode deactivated. Welcome back!"
                except:
                    response = "I couldn't deactivate focus mode."
            else:
                if focus_mode_active:
                    # Get remaining time
                    if "_focus_end_time" in remembered_items:
                        remaining = remembered_items["_focus_end_time"] - datetime.datetime.now()
                        remaining_minutes = max(0, int(remaining.total_seconds() / 60))
                        response = f"Focus mode is active. {remaining_minutes} minutes remaining."
                    else:
                        response = "Focus mode is currently active."
                else:
                    response = "Would you like me to activate focus mode? Say 'activate focus mode' to start."
        
        # 18. Google Translator
        #<---upcoming--->
             
        
        # 19. Mail functionality
        #<---upcoming--->
           
    
       # Wikipedia functionality
        elif "wiki" in transcript or "wikipedia" in transcript:
            search_term = re.sub(r'\b(wiki|wikipedia|what is|who is|tell me about)\b', '', transcript).strip()
            
            if search_term:
                try:
                    wiki_summary = wikipedia.summary(search_term, sentences=2)
                    response = f"According to Wikipedia: {wiki_summary}"
                except Exception as e:
                    response = f"Sorry, I couldn't find information about {search_term} on Wikipedia."
            else:
                response = "What would you like me to search on Wikipedia?"
        
        # Handle unknown commands
        else:
            response = "I'm not sure how to help with that. Could you please try another command or phrase it differently?"
        
        return JsonResponse({'response': response})
    
    return JsonResponse({'error': 'Invalid request method'})

def handle_alarm(alarm_id):
    """Background function to handle alarms"""
    alarm = next((a for a in alarms if a["id"] == alarm_id), None)
    if not alarm:
        return
        
    # Calculate seconds until alarm
    now = datetime.datetime.now()
    seconds_until_alarm = (alarm["time"] - now).total_seconds()
    
    if seconds_until_alarm > 0:
        time.sleep(seconds_until_alarm)
        
    # Check if alarm is still active
    alarm = next((a for a in alarms if a["id"] == alarm_id), None)
    if alarm and alarm["active"]:
        # Play alarm sound and show notification
        try:
            # Play sound
            frequency = 2500  # Hz
            duration = 1000  # ms
            winsound.Beep(frequency, duration)
            
            # Show notification
            notification.notify(
                title="Alarm",
                message=f"Your alarm for {alarm['time'].strftime('%H:%M')} is ringing!",
                app_name="Alarm App",
                timeout=10
            )
        except Exception as e:
            print(f"Error triggering alarm: {e}")

def process_transcript(transcript):
    """Process the speech transcript and perform the appropriate action"""
    global scheduled_tasks
    
    # Convert transcript to lowercase for easier matching
    transcript = transcript.lower()
    
    # Initialize the response
    response = ""
    
    # Handle different commands based on transcript content
    if "tomorrow" in transcript and any(word in transcript for word in ["plan", "schedule", "task", "agenda", "to do"]):
        # Extract the task for tomorrow
        task_match = re.search(r'(?:is|are|have)\s+(.*?)(?:\.|$)', transcript) or re.search(r'(?:tomorrow[\'s]*)\s+(.*?)(?:\.|$)', transcript)
        
        if task_match:
            task = task_match.group(1).strip()
            # Calculate tomorrow's date
            tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            
            # Store the scheduled task
            if tomorrow not in scheduled_tasks:
                scheduled_tasks[tomorrow] = []
            scheduled_tasks[tomorrow].append(task)
            
            response = f"I've scheduled this for tomorrow: {task}"
        else:
            response = "What would you like me to schedule for tomorrow?"
    
    elif any(phrase in transcript for phrase in ["today's schedule", "what do i have today", "today's tasks", "today's agenda"]):
        # Get today's date
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        
        if today in scheduled_tasks and scheduled_tasks[today]:
            tasks = scheduled_tasks[today]
            
            # Send system notification
            try:
                notification_text = "Today's agenda: " + ", ".join(tasks)
                notification.notify(
                    title="Today's Schedule",
                    message=notification_text,
                    timeout=10
                )
                response = f"Here's what you have scheduled for today: {', '.join(tasks)}"
            except Exception as e:
                print(f"Error showing notification: {e}")
                response = f"Your schedule for today: {', '.join(tasks)}"
        else:
            response = "You don't have anything scheduled for today."
    
    elif "set alarm" in transcript or "wake me up" in transcript:
        # Extract time from transcript
        time_match = re.search(r'(\d{1,2}):?(\d{2})?\s*(am|pm)?', transcript)
        
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2) or 0)
            period = time_match.group(3)
            
            # Adjust hour for PM
            if period == "pm" and hour < 12:
                hour += 12
            # Adjust for 12 AM
            elif period == "am" and hour == 12:
                hour = 0
                
            # Set the alarm time
            now = datetime.datetime.now()
            alarm_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # If the time has already passed for today, set it for tomorrow
            if alarm_time <= now:
                alarm_time += datetime.timedelta(days=1)
                
            # Create and store alarm
            alarm_id = str(uuid.uuid4())
            alarm = {
                "id": alarm_id,
                "time": alarm_time,
                "active": True
            }
            alarms.append(alarm)
            
            # Start a thread to handle the alarm
            alarm_thread = threading.Thread(target=handle_alarm, args=(alarm_id,))
            alarm_thread.daemon = True
            alarm_thread.start()
            
            response = f"Alarm set for {alarm_time.strftime('%I:%M %p')}"
        else:
            response = "I didn't understand when to set the alarm. Please specify a time."
    
    else:
        response = "I'm not sure how to help with that. You can schedule tasks or set alarms."
        
    return response

def end_focus_mode(duration_minutes):
    """
    Function to automatically end focus mode after the specified duration.
    
    Args:
        duration_minutes (int): Duration of focus mode in minutes
    """
    # Sleep for the specified duration
    time.sleep(duration_minutes * 60)
    
    # Check if focus mode is still active before ending it
    # (in case it was manually deactivated)
    global focus_mode_active
    if focus_mode_active:
        try:
            # Turn off focus mode
            os.system("powershell -command \"(New-Object -ComObject Shell.Application).ToggleDesktop()\"")
            focus_mode_active = False
            remembered_items.pop("_focus_end_time", None)
            
            # You could add notification functionality here, for example:
            # notify_user("Focus mode has ended")
            
            print("Focus mode automatically ended after scheduled duration")
        except Exception as e:
            print(f"Error ending focus mode: {str(e)}")
            
import uuid  # Add this import at the top of your file

def handle_alarm(alarm_id):
    """
    Function to handle an alarm when it triggers.
    
    Args:
        alarm_id (str): Unique identifier for the alarm
    """
    # Find the alarm with the matching ID
    alarm = None
    for a in alarms:
        if a["id"] == alarm_id:
            alarm = a
            break
    
    if not alarm or not alarm["active"]:
        return
    
    # Calculate time to sleep until alarm
    now = datetime.datetime.now()
    seconds_to_wait = (alarm["time"] - now).total_seconds()
    
    if seconds_to_wait <= 0:
        return
    
    # Sleep until alarm time
    time.sleep(seconds_to_wait)
    
    # Check if alarm is still active before triggering
    if not alarm["active"]:
        return
    
    # Trigger the alarm
    try:
        # Play an alarm sound (Windows example)
        import winsound
        for _ in range(5):  # Play sound 5 times
            winsound.Beep(1000, 500)  # Frequency 1000Hz, duration 500ms
            time.sleep(0.5)
        
        # You could also use a more pleasant sound file if available:
        # winsound.PlaySound("alarm.wav", winsound.SND_FILENAME)
        
        # Mark alarm as inactive after it triggers
        alarm["active"] = False
        
        # Optional: Show a notification or speak a message
        print(f"ALARM! It's {alarm['time'].strftime('%I:%M %p')}")
        
    except Exception as e:
        print(f"Error triggering alarm: {str(e)}")
        
#handling whatsapp

