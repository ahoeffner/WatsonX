
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

		print("listFlights called with parameters:")

		return "Final answer: The flight departure tool was invoked with the following parameters: " \
			+ f"Origin: {origin}, Destination: {destination}, Date: {date}"


	def tools() -> list[Tool]:
		return [Functions.listFlights]
