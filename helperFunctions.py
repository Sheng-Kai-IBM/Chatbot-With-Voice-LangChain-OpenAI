import os
import json
import requests
import base64
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.agents import load_tools, initialize_agent, AgentType


# set up API key
RapidAPI_Key = ""
os.environ["OPENAI_API_KEY"] = ""
os.environ["SERPAPI_API_KEY"] = "..."


def openai_set_memory_respond():
    # set up OpenAI GPT3 Api in LangChain
    gpt3 = OpenAI(model_name="gpt-3.5-turbo", temperature=0)

    # set up prompt template
    template = """The following is a friendly conversation between a human and an AI.
    Current conversation:
    {chat_history_lines}
    Human: {input}
    AI:"""
    prompt = PromptTemplate(input_variables=["input", "chat_history_lines"], template=template)

    # define how many previous conversations should be kept as history; k means to keep the previous 7 conversation results
    memory = ConversationBufferWindowMemory(memory_key="chat_history_lines", input_key="input", k=7)
    conversation = ConversationChain(llm=gpt3, verbose=True, memory=memory, prompt=prompt)
    return conversation


def openai_set_no_memory_respond():
    # set up OpenAI GPT3 Api in LangChain
    gpt3 = OpenAI(model_name="gpt-3.5-turbo", temperature=0)
    # set up Serp Api (for Google search) in LangChain
    tools = load_tools(tool_names=["google-search"], llm=gpt3)
    # set up agent to combine LLms and other API to takes in user input
    agent = initialize_agent(tools=tools, llm=gpt3, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True, max_execution_time=3,
                             early_stopping_method="generate")
    return agent


def openai_get_memory_respond(conversation, message):
    try:
        response = conversation.run("Act like a personal assistant, and your name is Mai. You can respond to questions, translate sentences, "
                                    "summarize news, and give recommendations. " + message)
    except ValueError as e:
        response = str(e)
        if not response.startswith("Could not parse LLM output: `"):
            raise e
        response = response.removeprefix("Could not parse LLM output: `").removesuffix("`")
    return response


def openai_get_gpt_review(property_info, user_requirement):
    agent = openai_set_memory_respond()
    try:
        response = agent.run(input="Act like a personal assistant, and your name is Mai. You can respond to questions, translate sentences, "
                                   "summarize news, and give recommendations. Be really critical on reviewing whether the Property Information fits "
                                   "the User Requirement. Based on your discovery, carefully provide a score on an integer scale from 1 to 100 "
                                   "(1 is the lowest, and 100 is the highest. Do not be lazy on calculate the score because each negative review is "
                                   "having a huge reduction on a score (minus 6 on score) and each positive thought is only having a small increment "
                                   "(plus 7 on score).)" + "\n- User Requirement: "
                                   + user_requirement + "\n- Property Information: " + property_info + "\n Your answer cannot use next line "
                                   "command(\n) and can only respond in this format 'Score:&Reason:'")
    except ValueError as e:
        response = str(e)
        if not response.startswith("Could not parse LLM output: `"):
            raise e
        response = response.removeprefix("Could not parse LLM output: `").removesuffix("`")
    return response


def openai_get_google_review(location, community):
    agent = openai_set_no_memory_respond()
    try:
        response = agent.run(input="Detailedly explain in more than 50 words to answer whether the " + location + " " + community
                                   + " community is a good neighborhood or not.")
    except ValueError as e:
        response = str(e)
        if not response.startswith("Could not parse LLM output: `"):
            raise e
        response = response.removeprefix("Could not parse LLM output: `").removesuffix("`")
    return response


def openai_get_property_ranking(listing_string, listing, special_requirement):
    openai_reviews = [openai_get_gpt_review(listing_string[i], special_requirement) for i in range(len(listing_string))]
    print("Got the score and GPT review for each listing")

    # clean the output format once getting gpt3 reviews
    result_dicts = []
    for review in openai_reviews:
        # replace "\nReason" with a placeholder string
        review = review.replace("\nReason", "/nReason")
        # remove all remaining "\n" characters
        review = review.replace("\n", "")
        # split the sentence
        pairs = review.split("/n")
        result_dict = {}
        for key_value in pairs:
            key, value = key_value.split(": ")
            if key.strip() == "Score":
                result_dict[key.strip()] = int(value.strip())
            else:
                result_dict[key.strip()] = value.strip()
        result_dicts.append(result_dict)
    print("Cleaned GPT reviews")

    # extract scores and find the indices of the top 2 scores with property information
    scores = [listing['Score'] for listing in result_dicts]
    sorted_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
    order = sorted_indices[:2]
    new_openai_reviews = [result_dicts[order[i]] for i in range(len(order))]
    top_listing = [listing[order[i]] for i in range(len(order))]
    for i in range(len(top_listing)):
        top_listing[i]["Score"] = new_openai_reviews[i]["Score"]
        top_listing[i]["Reason"] = new_openai_reviews[i]["Reason"]
    return top_listing


def openai_get_property_google_search(property_list, location):
    for i in range(len(property_list)):
        # get the property's community name
        community = api_get_property_community(property_list[i]["Id"], property_list[i]["MlsNumber"])
        print("Got property's community")

        # Google search the community reviews
        search = openai_get_google_review(location, community)
        property_list[i]["GoogleSearch"] = search
    return property_list


def api_get_area_geographic_coordinate(area, culture_id="1"):
    """
    param area: a string type that can be city, ward, street name, etc…
    param culture_id: a string type of number define the language of result 1 - English | 2 - French
    """
    url = "https://realty-in-ca1.p.rapidapi.com/locations/auto-complete"
    querystring = {"Area": area,
                   "CultureId": culture_id}
    headers = {"X-RapidAPI-Key": RapidAPI_Key, "X-RapidAPI-Host": "realty-in-ca1.p.rapidapi.com"}
    response = requests.get(url, headers=headers, params=querystring)

    # get location detail from json result
    output = {"LatitudeMax": 0, "LongitudeMax": 0, "LatitudeMin": 0, "LongitudeMin": 0}
    json_obj = json.loads(response.text)
    results_data = json_obj["SubArea"][0]
    for view_port in results_data["Viewport"]:
        for coordinate in results_data["Viewport"][view_port]:
            if view_port == "NorthEast":
                output.update({coordinate + "Max": results_data["Viewport"][view_port][coordinate]})
            elif view_port == "SouthWest":
                output.update({coordinate + "Min": results_data["Viewport"][view_port][coordinate]})
    return output


def api_get_property_community(property_id, mls):
    """
    param area: a string type that can be city, ward, street name, etc…
    param mls: a string type of the MlsNumber
    """
    url = "https://realty-in-ca1.p.rapidapi.com/properties/detail"
    querystring = {"ReferenceNumber": mls, "PropertyID": property_id, "PreferedMeasurementUnit": "1", "CultureId": "1"}
    headers = {"X-RapidAPI-Key": RapidAPI_Key, "X-RapidAPI-Host": "realty-in-ca1.p.rapidapi.com"}
    response = requests.get(url, headers=headers, params=querystring)

    # get location detail from json result
    json_obj = json.loads(response.text)
    results_data = json_obj["Property"]["Address"]["CommunityName"] + " Neighbourhood"
    return results_data


def api_get_residential_properties(coordinate, building_type, bed, bath, price_min, price_max):
    """
    param coordinate: a dictionary type that define geographic coordinate
    param building_type: a string type that define the building type like House, Townhouse, or Apartment
    param bed: an integer type that define the number of bedroom
    param bath: an integer type that define the number of bathroom
    param price_min: an integer type that define the min target price
    param price_max: an integer type that define the max target price
    """
    bt = {"House": "1", "Townhouse": "16", "Apartment": "17"}

    url = "https://realty-in-ca1.p.rapidapi.com/properties/list-residential"
    querystring = {"LatitudeMax": coordinate["LatitudeMax"],
                   "LatitudeMin": coordinate["LatitudeMin"],
                   "LongitudeMax": coordinate["LongitudeMax"],
                   "LongitudeMin": coordinate["LongitudeMin"],
                   "CurrentPage": "1",
                   "RecordsPerPage": "4",
                   "SortOrder": "A",
                   "SortBy": "1",
                   "CultureId": "1",
                   "NumberOfDays": "0",
                   "BedRange": str(bed) + "-0",
                   "BathRange": str(bath) + "-0",
                   "PriceMin": str(price_min),
                   "PriceMax": str(price_max),
                   "BuildingTypeId": bt[building_type],
                   "TransactionTypeId": "2"}
    headers = {"X-RapidAPI-Key": RapidAPI_Key, "X-RapidAPI-Host": "realty-in-ca1.p.rapidapi.com"}
    response = requests.get(url, headers=headers, params=querystring)

    output = []
    json_obj = json.loads(response.text)
    results_data = json_obj["Results"]
    for listing in range(len(results_data)):
        data = results_data[listing]
        info = {"Id": "", "MlsNumber": "", "PublicRemarks": "", "AddressText": "", "Price": "", "Type": "", "Bedrooms": "", "Bathrooms": "",
                "ParkingType": "", "ParkingSpaceTotal": "", "Ammenities": "", "AmmenitiesNearBy": "", "Photo": "", "RelativeDetailsURL": ""}
        info.update({"Id": data["Id"]})
        info.update({"MlsNumber": data["MlsNumber"]})
        info.update({"PublicRemarks": data["PublicRemarks"]})
        info.update({"RelativeDetailsURL": "https://www.realtor.ca" + data["RelativeDetailsURL"]})
        info.update({"Bathrooms": data["Building"]["BathroomTotal"]})
        info.update({"Bedrooms": data["Building"]["Bedrooms"]})
        info.update({"Type": data["Building"]["Type"]})
        info.update({"Ammenities": data["Building"].get("Ammenities")})
        info.update({"Price": data["Property"]["Price"]})
        info.update({"AddressText": data["Property"]["Address"]["AddressText"]})
        info.update({"Photo": data["Property"]["Photo"][0].get("HighResPath") if "Photo" in data["Property"] else None})
        info.update({"ParkingType": data["Property"]["Parking"][0].get("Name") if "Parking" in data["Property"] else None})
        info.update({"ParkingSpaceTotal": data["Property"].get("ParkingSpaceTotal")})
        info.update({"AmmenitiesNearBy": data["Property"].get("AmmenitiesNearBy")})
        output.append(info)
    return output


def speech_to_text(audio):
    # speech url
    speech_to_text_url = "https://sn-watson-stt.labs.skills.network/speech-to-text/api/v1/recognize"
    # set up the headers for audio format
    headers = {"Content-Type": "audio/wav"}
    # set up parameters
    params = {"model": "en-US_Multimedia", "background_audio_suppression": "0.7"}
    # method to get the Voice data from the text service
    response = requests.post(speech_to_text_url, headers=headers, params=params, data=audio).json()

    # Parse the response to get our transcribed text
    transcript = "null"
    while bool(response.get("results")):
        print("speech to text response:", response)
        transcript = response.get("results").pop().get("alternatives").pop().get("transcript")
        print("recognised text: ", transcript)
    return transcript


def text_to_speech(texts, voice=""):
    # text url
    text_to_speech_url = "https://sn-watson-tts.labs.skills.network/text-to-speech/api/v1/synthesize?output=output_text.wav"
    # Adding voice parameter in api_url if the user has selected a preferred voice
    if voice != "" and voice != "default":
        text_to_speech_url += "&voice=" + voice
    # set up the headers for post request to service
    headers = {"Content-Type": "application/json", "Accept": "audio/wav"}
    # set up parameters
    params = {"rate_percentage": -2, "pitch_percentagequery": 0}
    # Set the body of our HTTP request
    json_data = {'text': texts}
    # method to get the Voice data from the text service
    response = requests.post(text_to_speech_url, headers=headers, params=params, json=json_data)

    print('text to speech response:', response)
    return response.content
