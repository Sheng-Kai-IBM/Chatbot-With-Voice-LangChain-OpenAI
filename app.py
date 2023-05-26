from helperFunctions import *
from flask import Flask, render_template, request, redirect, Response, url_for
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
conversation = openai_set_memory_respond()


@app.route("/", methods=["GET"])
def root():
    return render_template("index.html")


@app.route("/process-message", methods=["POST"])
def process_prompt_route():
    # get user's preferred voice and message from their request
    voice = request.json["voice"]
    user_message = request.json["userMessage"]
    [print(i) for i in [user_message, voice]]

    # call openai_get_memory_respond() function to process the user's message and get a response back
    openai_response_text = openai_get_memory_respond(conversation, user_message)

    # clean the response to remove any empty lines
    openai_response_text = os.linesep.join([s for s in openai_response_text.splitlines() if s])

    # call our text_to_speech function to convert OpenAI API response to speech
    openai_response_speech = text_to_speech(openai_response_text, voice)

    # convert openai_response_speech to base64 string, so it can be sent back in the JSON response
    openai_response_speech = base64.b64encode(openai_response_speech).decode("utf-8")

    # send a JSON response back to the user containing their message's response both in text and speech formats
    response = app.response_class(response=json.dumps({"openaiResponseText": openai_response_text, "openaiResponseSpeech": openai_response_speech}),
                                  status=200,
                                  mimetype="application/json")
    return response


@app.route("/process-requirement", methods=["POST"])
def process_requirement_route():
    # get user message from their request
    location = request.json["location"]
    building_type = request.json["buildingType"]
    beds = request.json["beds"]
    baths = request.json["baths"]
    min_price = request.json["minPrice"]
    max_price = request.json["maxPrice"]
    special_requirement = request.json["specialRequirement"]
    [print("input: ", i) for i in [location, building_type, beds, baths, min_price, max_price, special_requirement]]

    # get the geographic coordinate from relator.ca
    coordinate = api_get_area_geographic_coordinate(location)
    print("Got the city coordinate")

    # get 4 results from relator.ca search
    listing = api_get_residential_properties(coordinate, building_type, beds, baths, min_price, max_price)
    # combine the information into a string for each listing
    listing_string = [', '.join([f'{k}: {v}' for k, v in listing[i].items()]) for i in range(len(listing))]
    print("Got the listing")

    # send a JSON response back to the user containing their message's response both in text and speech formats
    response = app.response_class(response=json.dumps({"listing": listing, "listingString": listing_string}),
                                  status=200,
                                  mimetype="application/json")
    return response


@app.route("/process-openai-review", methods=["POST"])
def process_openai_review_route():
    # get user message from their request
    special_requirement = request.json["specialRequirement"]
    listing = request.json["listing"]
    listing_string = request.json["listingString"]

    # let gpt3 review the listing information and the user requirements to get the top 2 properties
    openai_reviews = openai_get_property_ranking(listing_string, listing, special_requirement)
    print("Got the GPT reviews for top 2 listing")

    # send a JSON response back to the user containing their message's response both in text and speech formats
    response = app.response_class(response=json.dumps({"openaiReviews": openai_reviews}),
                                  status=200,
                                  mimetype="application/json")
    return response


@app.route("/process-google-review", methods=["POST"])
def process_google_review_route():
    # get user message from their request
    location = request.json["location"]
    openai_reviews = request.json["openaiReviews"]

    # get the ranked listing and the Google search
    google_reviews = openai_get_property_google_search(openai_reviews, location)
    print("Got the Google reviews for top 3 listing")

    # combine the final result into a dictionary variable
    combined = {}
    for idx, dictionary in enumerate(google_reviews):
        for key, value in dictionary.items():
            combined["property" + str(idx) + key] = value
    print(combined)

    # send a JSON response back to the user containing their message's response both in text and speech formats
    response = app.response_class(response=json.dumps(combined),
                                  status=200,
                                  mimetype="application/json")
    return response


@app.route('/speech-to-text', methods=['POST'])
def speech_to_text_route():
    # Get the user's speech from their reqeust
    audio = request.data

    # Call speech_to_text function to transcribe the speech
    text = speech_to_text(audio)
    print(text)

    # Return the response back to user in JSON format
    response = app.response_class(response=json.dumps({'text': text}),
                                  status=200,
                                  mimetype='application/json')
    return response


@app.route("/text-to-speech", methods=["POST"])
def text_to_speech_route():
    # get user's preferred voice and formal message
    voice = request.json["voice"]
    user_message = request.json["userMessage"]

    # call our text_to_speech function to convert OpenAI API response to speech
    user_message_speech = text_to_speech(user_message, voice)
    # convert openai_response_speech to base64 string, so it can be sent back in the JSON response
    user_message_speech = base64.b64encode(user_message_speech).decode("utf-8")

    # send a JSON response back to the user containing their message's response both in text and speech formats
    response = app.response_class(response=json.dumps({"messageText": user_message, "messageSpeech": user_message_speech}),
                                  status=200,
                                  mimetype="application/json")
    return response


if __name__ == "__main__":
    app.run(debug=False, use_reloader=True, port=9090, host="0.0.0.0")
