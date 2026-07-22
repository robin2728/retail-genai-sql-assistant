from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm_router = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0
)

prompt = ChatPromptTemplate.from_template(
"""
You are an AI Request Router.

Your job is ONLY to classify the user's request.

Possible categories:

DATABASE
- Questions about sales
- Revenue
- Customers
- Orders
- Products
- SQL
- Analytics
- Retail Data

CONVERSATION
- Greetings
- Introductions
- Small talk
- Thank you
- Goodbye

GENERAL
- Programming
- AI
- FastAPI
- JWT
- Redis
- Python
- General knowledge

Return ONLY one word.

Question:

{question}
"""
)

chain = prompt | llm_router | StrOutputParser()

async def classify_intent(question: str):
    intent = await chain.ainvoke(
    {
        "question": question
    })
    return intent.strip().upper()