# -*- coding: utf-8 -*-

# This project demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.

import ask_sdk_core.utils as ask_utils
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

import requests
import json
import re
import logging
from bs4 import BeautifulSoup

import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

email_slot_key = "EMAIL"
email_slot = "Email"

city_slot_key = "CITY"
city_slot = "City"

def send_email(opp_dict):
    sender_email = secrets.email["address"]
    receiver_email = "<receiveremail>"
    password = secrets.email["password"]

    message = MIMEMultipart("alternative")
    message["Subject"] = "Volunteer Opportunities"
    message["From"] = sender_email
    message["To"] = receiver_email

    plain_links = "\n".join(opp_dict["links"])

    # Create the plain-text and HTML version of your message
    text = """\
    Good day,
    Here are your request links for volunteering opportunities:
    {}
    """.format(plain_links)

    format_links = ["<li><a href='"+x+"'>"+x+"</a></li>" for x in opp_dict["links"]]
    html_links = "\n".join(format_links)

    html = """\
    <html>
    <body>
        <p>Good day,<br>
        Here are your request links for volunteering opportunities:<br>
        <ul>
            {}
        </ul>
        </p>
    </body>
    </html>
    """.format(html_links)

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Welcome, you can tell me the city that you live in, and we will provide you with the first five volunteer opportunities."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class GetCityIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("GetCityIntent")(handler_input)
    
    def handle(self, handler_input):
        """
        Set city.

        type: (HandlerInput) -> Response
        """

        slots = handler_input.request_envelope.request.intent.slots

        city = slots[city_slot].value
        handler_input.attributes_manager.session_attributes[city_slot_key] = city

        base_url = "https://www.volunteermatch.org"
        url_city = city.replace(" ","%20")

        vol_url = "https://www.volunteermatch.org/search?l="+url_city
        "https://www.volunteermatch.org/search/?l=92122"
        page = requests.get(vol_url)
        soup = BeautifulSoup(page.content, 'html.parser')

        title = [x.find('a', class_='link-body-text psr_link').get_text().strip() for x in soup.find_all('span', class_='rwd_listing_wrapper')]
        #address = [x.find('span', class_='street-address').get_text().strip().replace(',', '') for x in soup.find_all('span', class_='rwd_listing_wrapper')]
        #cities = [x.find('span', class_='locality').get_text().strip().replace(',', '') for x in soup.find_all('span', class_='rwd_listing_wrapper')]
        #state = [x.find('span', class_='region').get_text().strip().replace(',', '') for x in soup.find_all('span', class_='rwd_listing_wrapper')]
        #timeframe = [x.get_text().strip().replace("\n",'').replace('  ','') for x in soup.find_all('div', class_='oppdate ym_rwd_show')]
        link = [base_url+x['href'] for x in soup.find_all('a', class_="btn btn--sm read_more psr_link")]
        orgs = [re.sub(r'([^\s\w]|_)+', '', x.find('a', class_='psr_link').get_text()) for x in soup.find_all('span', class_='orgid')]

        handler_input.attributes_manager.session_attributes["opportunities"] = {
            "titles":title,
            "orgs":orgs,
            "links":link
        }

        opp_dict = {}
        visited = []
        counter = 1
        for i in range(len(title)):
            current_title = title[i]
            current_org = orgs[i]
            if current_title not in visited:
                visited.append(current_title)
                opp_dict[counter] = current_title +" hosted by "+ current_org
                counter +=1

        topfive = [opp_dict[i+1] for i in range(5)]
        topfive_statement = ". ".join(topfive)


        speech = ("The stated city is {}. Here are the first five opportunities: {}. Would you like for me to send you an email with the links?".format(city, topfive_statement))
        reprompt = ("Would you like for me to send you a link?")

        handler_input.response_builder.speak(speech).ask(reprompt)
        return handler_input.response_builder.response


class YesIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input)

    def handle(self, handler_input):
        """Handler for Yes Intent, only if the player said yes for
        a new game.
        """
        # type: (HandlerInput) -> Response

        speech_text = "Great! Tell me your email."
        reprompt = "Try saying am email."

        handler_input.response_builder.speak(speech_text).ask(reprompt)
        return handler_input.response_builder.response


class NoIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input)

    def handle(self, handler_input):
        """
        Handler for No Intent, only if the player said no for
        a new game.
        """
        # type: (HandlerInput) -> Response

        speech_text = "Ok. See you next time!!"

        handler_input.response_builder.speak(speech_text)
        return handler_input.response_builder.response


class SetEmailIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("SetEmailIntent")(handler_input)
    
    def handle(self, handler_input):
        """
        Check if color is provided in slot values. If provided, then
        set your favorite color from slot value into session attributes.
        If not, then it asks user to provide the color.
        """
        # type: (HandlerInput) -> Response
        slots = handler_input.request_envelope.request.intent.slots

        email = slots[email_slot].value.lower().replace("at","@").replace(".","").replace(" ","").replace("period",".").replace("dot",".")
        handler_input.attributes_manager.session_attributes[email_slot_key] = email

        opps = handler_input.attributes_manager.session_attributes["opportunities"]
        send_email(opps)

        speech = ("You stated that your email address is {}. An email has been sent. Say another state for more opportunities or you may end the session.".format(email))
        reprompt = ("Would you like for me to send you a link?")

        handler_input.response_builder.speak(speech).ask(reprompt)
        return handler_input.response_builder.response


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """
    The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """
    Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(GetCityIntentHandler())
sb.add_request_handler(SetEmailIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(YesIntentHandler())
sb.add_request_handler(NoIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
#sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()