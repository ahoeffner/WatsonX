import json
import os

from langchain.chains import LLMChain
from typing import Optional, Union
from langchain.tools import tool
from ibm_watsonx_ai import APIClient
from langchain.agents import ZeroShotAgent

from langchain.chains.llm import LLMChain

from langchain.tools.render import render_text_description_and_args

from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder

from langchain_ibm import WatsonxLLM
from langchain.agents import initialize_agent, AgentType, create_react_agent, AgentExecutor
from ibm_cloud_sdk_core import IAMTokenManager

from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain.schema import AgentAction, AgentFinish
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai.foundation_models.utils.enums import ModelTypes, DecodingMethods

class CustomOutputParser(ReActSingleInputOutputParser):
    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        if "Final Answer:" in llm_output:
            return super().parse(llm_output)

        action_match = re.search(r"Action: (\w+)\((.*)\)", llm_output)
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



URL="https://eu-de.ml.cloud.ibm.com"
GENAIKEY = "9uBOD0fWZvED30o9U2y1xXzRUy30zpHtx7rSvICVs9O5"
PROJECTID = "39468945-6088-4d55-86a7-75a07c75f61e"

iam_token_manager = IAMTokenManager(apikey=GENAIKEY)
TOKEN = iam_token_manager.get_token()
os.environ["WATSONX_APIKEY"] = TOKEN

# To display example params enter
GenParams().get_example_values()

generate_params = {
    GenParams.MAX_NEW_TOKENS: 25
}


@tool
def listFlights(query: Optional[str] = None) -> str:
#def listFlights(origin: Optional[str] = None, destination: Optional[str] = None, date: Optional[str] = None) -> str:
	"""Lists available flights based on the departure airport, destination airport, and date."
	Args: A query string that contains the parameters for the flight search.
	Returns:
		str: A message indicating the parameters used for the flight search.
	"""
	print("------------------------------listFlights called with parameters:-----",flush=True)
	return "The flight departure tool was invoked with the following parameters: "


llm = WatsonxLLM(
		model_id="ibm/granite-13b-instruct-v2",
		params=generate_params,
		token=TOKEN,
		url = URL,
		project_id=PROJECTID
	)

credentials = {
	"url": URL,
	"token" :TOKEN,
	"api_key": TOKEN
}

api_client = APIClient(credentials=credentials)
tools = [listFlights]

prompt_template = ZeroShotAgent.create_prompt(
    tools,
    prefix="",
    suffix="",
    input_variables=["input", "agent_scratchpad"],
)

llm_chain = LLMChain(llm=llm, prompt=prompt_template)

# Initialize the ZeroShotAgent with the custom output parser
agent = ZeroShotAgent(llm_chain=llm_chain, prompt=prompt_template, output_parser=CustomOutputParser(), tools=tools)

# Create the AgentExecutor
agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True)

# Run the agent
response = agent_executor.invoke({input:"list flights from New York to London"})
print(response)
