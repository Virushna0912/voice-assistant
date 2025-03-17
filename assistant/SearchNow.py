import speech_recognition
import pyttsx3
import pywhatkit
import wikipedia
import webbrowser


def searchYoutube(transcript):
    if "youtube" in transcript:
        response = "This is what I found for your search!"
        transcript = transcript.replace("youtube search","")
        transcript = transcript.replace("youtube","")
        transcript = transcript.replace("jarvis","")
        web  = "https://www.youtube.com/results?search_transcript=" + transcript
        webbrowser.open(web)
        pywhatkit.playonyt(transcript)
        response = "Done, Sir"