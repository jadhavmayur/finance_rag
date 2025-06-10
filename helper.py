from langchain.schema.runnable import RunnablePassthrough,RunnableLambda
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage


### Document parser
def parse_docs(docs):
    """Split base64-encoded images and texts"""
    text = []
    for doc in docs:
        # print("doc: ",doc)
        text.append(doc)
    return {"texts":text}

### Prompt
def build_prompt(kwargs):
    # print(kwargs)
    docs_by_type = kwargs["context"]
    user_question = kwargs["question"]
    context_text = ""
    
    if len(docs_by_type["texts"]) > 0:
        for text_element in docs_by_type["texts"]:
            # print("text_element: ",text_element.page_content)
            # print("---"*50)
            context_text += text_element.page_content
            
    prompt_template = f"""Role: You are a financial advisor who give answer to user's query.
                         Responsibility: 
                         1. Compare spending of user of last six months.
                         2. Tell the what is user recurring exapnses and how he can reduce it.
                         3. Foracsting the next six month expanses.
                         Note: As per query generate answer
                        Context: {context_text}
                        Question: {user_question}
                        """
    # print("docs_by_type: ", docs_by_type)
    prompt_content = [{"type": "text", "text": prompt_template}]
    return ChatPromptTemplate.from_messages(
        [
            HumanMessage(content=prompt_content),
        ]
    )

