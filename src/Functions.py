
import json
from typing import Optional
from langchain.agents import Tool
from langchain_core.tools import tool

class Functions :
	@tool
	def listFlights(origin: Optional[str] = None, destination: Optional[str] = None, date: Optional[str] = None) -> str:
		"""
		Flight departure tool to list flights based on origin, destination, and date.
		Args:
			origin (str): The origin city or airport code.
			destination (str): The destination city or airport code.
			date (str): The date of travel in YYYY-MM-DD format.
		Returns:
			str: A message indicating the flight details.
		"""

		print("****************** listFlights called ******************")

		response = {
			"Observation": "action result",
			"Thought": "I know what to respond",
			"Action": {
				"action": "Final Answer",
				"action_input": "We have found the following flights: SK0263, SK0264, SK0265"
			}
		}

		response = json.dumps(response, indent=4)
		return response



	def tools() -> list[Tool]:
		return [Functions.listFlights]
