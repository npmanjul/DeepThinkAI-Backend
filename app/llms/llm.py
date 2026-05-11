from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mistralai import ChatMistralAI

load_dotenv()

llm_google = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)
llm_mistral = ChatMistralAI()    
llm=llm_mistral