


# importing the pyttsx library
import pyttsx3
  
# initialisation
engine = pyttsx3.init()
  
# testing
engine.setProperty("rate", 100)
engine.say("ADSM Analyzer not working, please check ASAP")
engine.runAndWait()

