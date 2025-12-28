# pip install google-genai

import base64
import os
from google import genai
from google.genai import types
import json
from google.colab import userdata


from api_key import API_KEY
# API_KEY = userdata.get('API_KEY')

example_response = """An airliner features a long, cylindrical fuselage designed to transport many passengers.
Fixed wings are attached to the midsection of an airliner to provide lift.
Most modern airliner designs include jet engines mounted under the wings.
A vertical stabilizer and horizontal stabilizers are located at the rear of an airliner.
An airliner often has rows of small windows along both sides of the fuselage.
The exterior of an airliner is typically painted with a specific airline's livery.
Retractable landing gear is positioned underneath an airliner for takeoff and landing.
A cockpit with large glass windows is situated at the front of an airliner.
Smooth, aerodynamic surfaces cover the entire body of an airliner to reduce drag.
An airliner possesses a distinctive tail section that aids in flight stability.

You can identify an airliner by its massive size compared to private planes.
Multiple rows of passenger windows along the fuselage help distinguish an airliner.
An airliner is recognizable by the specific logo and colors of a commercial airline.
Large jet engines producing a steady hum are a key feature of an airliner.
Observing an airliner at a major commercial airport confirms its primary function.
The presence of many emergency exits indicates that the aircraft is an airliner.
An airliner is characterized by its ability to carry hundreds of people at once.
You can spot an airliner by its high-altitude contrails during long-distance flights.
A tricycle landing gear configuration is common for a modern jet airliner.
Heavy cargo doors and passenger boarding gates are hallmarks of an airliner.

An airliner resembles a giant, metal tube with sweeping wings on each side.
The nose of an airliner is usually rounded to improve its aerodynamic profile.
On the ground, an airliner looks like a towering structure supported by wheels.
An airliner appears as a bright white or metallic object against the sky.
Winglets are often seen at the tips of the wings on a modern airliner.
The belly of an airliner is curved and contains various storage compartments.
Navigational lights blink at the wingtips and tail of a flying airliner.
An airliner has a wide wingspan that often exceeds the length of its fuselage.
Inside the cabin, an airliner looks like a long hallway filled with seats.
From a distance, an airliner looks like a sleek silver bird gliding through clouds.

A high-resolution photo shows an airliner cruising above a thick layer of clouds.
One popular image depicts an airliner parked at a gate with a jet bridge.
An airliner is captured mid-takeoff with its landing gear beginning to retract.
A sunset silhouette highlights the iconic shape of a departing airliner.
An airliner appears in a top-down view while flying over a vast ocean.
A close-up shot focuses on the powerful turbine of a stationary airliner.
An airliner is shown being refueled on a busy airport tarmac.
Lightning strikes near an airliner in a dramatic weather-themed photograph.
A vintage photo displays a classic propeller-driven airliner from the mid-twentieth century.
An airliner is pictured landing on a runway with smoke rising from its tires.

A commercial airliner soars gracefully through the clear blue sky at high altitude.
This airliner waits patiently on the taxiway for clearance from the tower.
Sunlight reflects off the polished aluminum skin of a classic airliner.
A modern airliner prepares for a long-haul flight across the Atlantic Ocean.
Passengers board the airliner through a mobile staircase on a sunny morning.
The massive wingspan of the airliner dominates the frame of this aerial photograph.
Maintenance crews perform a final safety check on the airliner before departure.
An airliner leaves white vapor trails behind as it reaches cruising speed.
City lights glow beneath a descending airliner during a night approach.
This wide-body airliner is designed to transport over three hundred travelers safely.
"""

def extract_sentences(response_text):
    sentences = []
    lines = response_text.split('\n')
    for line in lines:
        line = line.strip()
        if line:
            sentences.append(line)
    return sentences

def generate(classes):

    prompt = """You're an expert writing objective and general descriptions for things in English. Write short sentence less than 40 words to answer each of these questions in english. exactly 10 sentences for each question. 1 sentence on 1 line. the english name of the main subject must appear in every sentence. you must translate the name to english. do not reiterate the questions. do not provide sources."""

    # Load các lớp đã tồn tại từ file JSON
    with open("class_dict.json", "r", encoding="utf-8") as json_file:
        try:
            data = json.load(json_file)
        except json.JSONDecodeError:
            data = {}

    existed_classes = list(data.keys())

    # Lọc các lớp đã tồn tại và tạo prompt
    with open("previous_prompt.txt", "a", encoding="utf-8") as prompt_file:
        for cls in classes:
            cls = cls.strip()
            if cls not in existed_classes:
                class_prompt = prompt
                class_prompt += f'\nDescribe what a {cls} looks like.'
                class_prompt += f'\nHow can you identify a {cls} by appearances?'
                class_prompt += f'\nWhat does a {cls} look like?'
                class_prompt += f'\nDescribe an image from the internet of a {cls}.'
                class_prompt += f'\nA caption of an image of a {cls}:'

                prompt_file.write(class_prompt + "\n\n")
            else:
                # print(f"{cls} already exists in class_dict.json, skipping...")
                continue

            client = genai.Client(
                api_key=API_KEY,
            )

            model = "gemini-2.5-flash"
            contents = [
                genai.types.Content(
                    role="user",
                    parts=[
                        genai.types.Part.from_text(text=class_prompt),
                    ],
                ),
            ]
            tools = [
                genai.types.Tool(googleSearch=genai.types.GoogleSearch(
                )),
            ]
            generate_content_config = genai.types.GenerateContentConfig(
                temperature=0.99,
                thinking_config=genai.types.ThinkingConfig(
                    thinking_budget=-1,
                ),
                tools=tools,
            )

            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=generate_content_config,
            )

            print("Response received.\n")
            print(response.text)

            with open(f'response_{cls}.txt', "w", encoding="utf-8") as resp_file:
                resp_file.write(response.text)
                # resp_file.write(example_response)
            resp_file.close()

            extracted_sentences = extract_sentences(response.text)
            # extracted_sentences = extract_sentences(example_response)
            data[cls] = extracted_sentences

    prompt_file.close()

    with open("class_dict.json", "w") as json_file:
        # data["acoustic"] = ["whiskers", "sharp_claws", "retractable_claws", "purring", "tail"]
        json.dump(data, json_file, indent=2)
    json_file.close()

classes = []
classes = ['mèo', 'airliner', 'albatross']
generate(classes)
