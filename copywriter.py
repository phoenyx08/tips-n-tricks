from langchain.agents import Tool
from pydantic import BaseModel
from src.tools import markdown_to_html, render_html, save_article_file
from langchain.agents import AgentExecutor
from langchain.agents.openai_functions_agent.base import create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

# Prompt user for the title
title = input("Enter the title of your article: ")

# Tool input schema
class MarkdownInput(BaseModel):
    markdown_text: str

# Tool function
def convert_markdown_tool(markdown_text: str) -> str:
    html_body = markdown_to_html(markdown_text)
    title_line = markdown_text.splitlines()[0]
    title = title_line.replace("#", "").strip() if title_line.startswith("#") else "Untitled"
    full_html = render_html(title, html_body)
    file_path, slug = save_article_file(title, full_html)
    return f"✅ Article saved to: {file_path} (slug: {slug})"

# Define tool
markdown_to_html_tool = Tool(
    name="MarkdownToHTML",
    func=convert_markdown_tool,
    description="Use this tool to convert a markdown-formatted article into styled HTML and save it as a file.",
    args_schema=MarkdownInput
)

# Create agent
llm = ChatOpenAI(model="gpt-4.1", temperature=0.7)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are helpful writer of howto articles on programming topics."),
    MessagesPlaceholder("chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder("agent_scratchpad")
])

agent_runnable = create_openai_functions_agent(llm, [markdown_to_html_tool], prompt)
agent_executor = AgentExecutor(
    agent=agent_runnable,
    tools=[markdown_to_html_tool],
    verbose=True
)

# Prompt to agent
instruction = (
    f"Write a how-to article on '{title}'. "
    "Format it in markdown. Then use the MarkdownToHTML tool to convert and save the article."
)

# Run
agent_executor.invoke({"input": instruction})
