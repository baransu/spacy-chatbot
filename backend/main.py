from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_cors import CORS
import spacy
import requests

nlp = spacy.load("pl_core_news_md")

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app, cors_allowed_origins="*")

if __name__ == '__main__':
    socketio.run(app)

greeting_intent = [
    "Cześć",
    "Co tam u Ciebie",
    "Jak sie masz",
    "Dzień dobry"
]

pollution_intent = [
    "Jaki jest smog",
    "Jakie jest zanieczyszczenie",
    "Stan powietrza",
    "Smog",
    "Zanieczyszczenie"
]

@socketio.event
def new_message(message):
    print('Message: ' + message)
    sentence = nlp(message)

    if(is_similar(sentence, greeting_intent)):
        handle_greeting(sentence)    
        return
    
    if(is_similar(sentence, pollution_intent)):
        handle_pollution(sentence)
        return

    handle_unknown(sentence)

def handle_greeting(sentence):
    socketio.emit("message", "Cześć!")            

def handle_pollution(sentence):
    for ent in sentence.ents:
        if(ent.label_ == "placeName"):
            city = ent.lemma_ 
            location = get_location(city)
            results = airly(location['lat'], location['lng'])

            standards = []
            for r in results:
                standards.append(r['pollutant'] + " " + str(r['percent']) + "%")

            standard = ", ".join(standards) 

            polluted = any(map(lambda r: r['percent'] > 100, results))

            socketio.emit('message', "Wartości dla " + city + ": " + standard)

            sentiment = ""
            if polluted:
                sentiment = "Niestety normy są przekroczone."
            else:
                sentiment = "Jakość powietrza jest super! Korzystaj z niej!"

            socketio.emit('message', sentiment)

def handle_unknown(sentence):
    socketio.emit("message", "Niestety nie rozumiem :(")            


def airly(lat, lng):
    params = {'lat': lat, 'lng': lng, 'maxDistanceKM': 5}
    headers = {
        'Accept-Language': "pl",
        'apikey': "lV0elEcHTtbjm5sFLu7b0qqzHx9q6mm2"
    }

    r = requests.get("https://airapi.airly.eu/v2/measurements/nearest", params = params, headers = headers)
    json = r.json()

    return json['current']['standards']


def get_location(city):
    params = {
        'address': city,
        'key': 'AIzaSyDkfpy75XjGIitLEBztOFrFJtSGxYmE9nE'
    }
    r = requests.get("https://maps.googleapis.com/maps/api/geocode/json", params = params)
    json = r.json()

    return json['results'][0]['geometry']['location']


def is_similar(sentence, intent_sentences, min_similarity = 0.65):
    similarities = []
    
    for intent_sentence in intent_sentences:
        intent_trigger = nlp(intent_sentence)
        trigger_similarity = intent_trigger.similarity(sentence)
        similarities.append(trigger_similarity)
     
    max_similarity = max(similarities)
    print({'intent_sentences': intent_sentences, 'max_similarity': max_similarity})

    return max_similarity >= min_similarity
