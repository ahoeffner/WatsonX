import requests
from ibm_cloud_sdk_core import IAMTokenManager
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator, BearerTokenAuthenticator

GENAI_KEY = "9uBOD0fWZvED30o9U2y1xXzRUy30zpHtx7rSvICVs9O5"
PROJECT_ID = "39468945-6088-4d55-86a7-75a07c75f61e"

iam_token_manager = IAMTokenManager(apikey=GENAI_KEY)
MY_TOKEN = iam_token_manager.get_token()


url = "https://eu-de.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"

body = {
	"input": "What is a car?",
	"parameters": {
		"decoding_method": "greedy",
		"max_new_tokens": 200,
		"repetition_penalty": 1
	},
	"model_id": "ibm/granite-13b-instruct-v2",
	"project_id": PROJECT_ID,
	"moderations": {
		"hap": {
			"input": {
				"enabled": True,
				"threshold": 0.5,
				"mask": {
					"remove_entity_value": True
				}
			},
			"output": {
				"enabled": True,
				"threshold": 0.5,
				"mask": {
					"remove_entity_value": True
				}
			}
		}
	}
}

headers = {
	"Accept": "application/json",
	"Content-Type": "application/json",
	"Authorization": "Bearer " + MY_TOKEN
}

response = requests.post(
	url,
	headers=headers,
	json=body
)

if response.status_code != 200:
	raise Exception("Non-200 response: " + str(response.text))

data = response.json()
print(data)