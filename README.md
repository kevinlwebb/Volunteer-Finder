Build An Alexa Volunteer Finder Skill using ASK Python SDK
=========================================

This Alexa skill finds volunteer opportunities in your area and sends you an email with links. 


Concepts
--------

The volunteer finder skill is a skill where alexa asks you to pick a city and sends you an email after giving it permission and your email address. This Alexa Skill is written in Python and demonstrates 
the use of session attributes, slots, and intents.

Setup
-----

To run this example skill you need to do two things. The first is to
deploy the example code in lambda, and the second is to configure the
Alexa skill to use Lambda. 

[![Get Started](https://camo.githubusercontent.com/db9b9ce26327ad3bac57ec4daf0961a382d75790/68747470733a2f2f6d2e6d656469612d616d617a6f6e2e636f6d2f696d616765732f472f30312f6d6f62696c652d617070732f6465782f616c6578612f616c6578612d736b696c6c732d6b69742f7475746f7269616c732f67656e6572616c2f627574746f6e732f627574746f6e5f6765745f737461727465642e5f5454485f2e706e67)](https://developer.amazon.com/en-US/alexa/alexa-skills-kit/get-deeper/tutorials-code-samples/alexa-skill-python-tutorial)

### Usage

```text
Alexa, open volunteer finder
	>> Welcome, you can tell me the city that you live in, and we will provide you with the first five volunteer opportunities.
San Diego
	>> The stated city is {}. Here are the first five opportunities: ...      
...
```

### Repository Contents	 
* `/lambda` - Back-End Logic for the Alexa Skill hosted on [AWS Lambda](https://aws.amazon.com/lambda/)
* `/models` - Voice User Interface and Language Specific Interaction Models