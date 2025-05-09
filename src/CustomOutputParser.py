import json
from typing import Union
from langchain.schema import AgentAction, AgentFinish
from langchain.agents.output_parsers import ReActSingleInputOutputParser as react

class CustomOutputParser(react):
	def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
		if "Final Answer:" in llm_output:
			return super().parse(llm_output)

		action_match = react.search(r"Action: (\w+)\((.*)\)", llm_output)
		
		if action_match:
			tool = action_match.group(1).strip()
			tool_input_str = action_match.group(2).strip()
			try:
					# Attempt to parse the input string as a dictionary (if it's JSON-like)
					tool_input = json.loads(tool_input_str)
			except json.JSONDecodeError:
					# If not JSON, treat it as a single string input
					tool_input = tool_input_str

			return AgentAction(tool=tool, tool_input=tool_input, log=llm_output)

		return super().parse(llm_output)
