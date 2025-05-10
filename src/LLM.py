import os
import warnings
from dotenv import load_dotenv
from Functions import Functions
from langchain.agents import Tool
from langchain_ibm import WatsonxLLM
from langchain.agents import AgentExecutor
from langchain.prompts import PromptTemplate
from ibm_cloud_sdk_core import IAMTokenManager
from langchain_core.runnables import RunnablePassthrough
from langchain.memory import ConversationBufferWindowMemory
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.agents.output_parsers import JSONAgentOutputParser
from langchain.tools.render import render_text_description_and_args
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


# Load environment variables from .env file

load_dotenv()

URL = os.getenv("URL")
MODEL = os.getenv("MODEL")
APIKEY = os.getenv("APIKEY")
PROJECTID = os.getenv("PROJECTID")

tknmgr = IAMTokenManager(apikey=APIKEY)
TOKEN = tknmgr.get_token()

# Define the prompt templates
PROMPT = """{input} {agent_scratchpad} (reminder to always respond in a JSON blob)"""

SYSTEM = """ You are a personal assistant. Do your best to answer as concisely as possible. " \
				 For travel-related questions, you should use the tools available for providing up tp date information.
				 Based on the given instructions, answer the following question {question}."""

AGENT = """ Respond to the human as helpfully and accurately as possible. You have access to the following tools: {tools}
				Use a json blob to specify a tool by providing an action key (tool name) and an action_input key (tool input).
				Valid "action" values: "Final Answer" or {tool_names}
				Provide only ONE action per $JSON_BLOB, as shown:"
				```
				{{
					"action": $TOOL_NAME,
					"action_input": $INPUT
				}}
				```
				The tool response is always a simple string representing the final response."""


class LLM:
	def __init__(self,tools:list[Tool] = None):
		self.history = []
		self.tools = tools

		parameters = {
			"decoding_method": "greedy",
			"temperature": 0,
			"min_new_tokens": 5,
			"max_new_tokens": 250,
			"stop_sequences":['\nObservation', '\n\n']
		}

		self.llm = WatsonxLLM(
			url = URL,
			token=TOKEN,
			model_id=MODEL,
			params=parameters,
			project_id=PROJECTID
		)


	def chat(self, question:str):
		if not self.tools:
			prompt = PromptTemplate.from_template(SYSTEM)
			chain = prompt | self.llm

			response = chain.invoke({"question": question})
			return response
		else:
			return self.agent(question)


	def agent(self, question:str):
		prompt = ChatPromptTemplate.from_messages(
		[
			("system", AGENT),
			MessagesPlaceholder("chat_history", optional=True),
			("human", PROMPT),
		]
		)

		tools_prompt = prompt.partial(
		tools=render_text_description_and_args(list(self.tools)),
		tool_names=", ".join([t.name for t in self.tools]),
		)

		warnings.filterwarnings("ignore")
		memory = ConversationBufferWindowMemory(k=5)

		agent_chain = ( RunnablePassthrough.assign(
			agent_scratchpad=lambda x: format_log_to_str(x["intermediate_steps"]),
			chat_history=lambda x: memory.chat_memory.messages,
			) | tools_prompt | self.llm | JSONAgentOutputParser()
		)

		executor = AgentExecutor(agent=agent_chain, tools=self.tools, handle_parsing_errors=True, verbose=False, memory=memory)

		response = executor.invoke({"input":question})
		print(f"Response: {response}")
		return response


def main():
	llm = LLM(Functions.tools())
	llm.chat("find me a flight from London to Paris on 2023-10-01")

if __name__ == "__main__":
    main()