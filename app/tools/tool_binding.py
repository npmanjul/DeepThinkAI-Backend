from app.tools.tools import tavily_search, gemini_generate_image_bytes, today_date

from app.llms.llm import llm_mistral, llm_google, llm

tools = [tavily_search, gemini_generate_image_bytes,today_date]

llm_mistral_with_tools = llm_mistral.bind_tools(tools)
llm_google_with_tools = llm_google.bind_tools(tools) 