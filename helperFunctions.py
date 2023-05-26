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
RapidAPI_Key = "..."
os.environ["OPENAI_API_KEY"] = "..."
os.environ["SERPAPI_API_KEY"] = "..."


def api_get_area_geographic_coordinate(area, culture_id="1"):
    return None


def api_get_property_community(property_id, mls):
    return None


def api_get_residential_properties(coordinate, building_type, bed, bath, price_min, price_max):
    return None


def openai_set_memory_respond():
    return None


def openai_set_no_memory_respond():
    return None


def openai_get_memory_respond(conversation, message):
    return None


def openai_get_gpt_review(property_info, user_requirement):
    return None


def openai_get_google_review(location, community):
    return None


def openai_get_property_ranking(listing_string, listing, special_requirement):
    return None


def openai_get_property_google_search(property_list, location):
    return None


def speech_to_text(audio):
    return None


def text_to_speech(texts, voice=""):
    return None
