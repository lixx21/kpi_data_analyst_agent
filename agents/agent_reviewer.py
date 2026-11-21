from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import Literal
from pathlib import Path
import json

class Critique(BaseModel):
    verdict: Literal["PASS", "FAIL"]
    issues: list[str] = Field(description="Specific problems. Empty if none")
    next_action: str = Field(description="One concrete check to do next, or 'none'")


def reviewer(model, analyst):
    data_dictionary = Path("data_dictionary.md").read_text(encoding="utf-8")

    template = """
    You are a strict senior data analyst professional who has 15+ years experiences. 
    Please review the analysis from junior analyst ONLY from the evidence given. Do not invent facts.
    Mark the analysis as FAIL if any of these criterias below is true:
    1. The data does not test the hypothesis
    2. A formula conflicts with the data dictionary
    3. A business rule from the dictionary was ignored
    4. A query returned no rows or errored
    5. The conclusion claims more than the data shows
    6. A query not relevant with the the step goal
    

    Answer:
    1. Please give the detail issues
    2. give the detail next step action if which one of query need to be adjusted or 
    the data need to be adjusted if the issue cause from the data
    3. please check the result to prevent redundant answer

    data dictionary: {data_dictionary}
    question: {question}
    hypothesis: {hypothesis}
    assumptions: {assumptions}
    reasoning: {reasoning}
    supporting data: {supporting_data}
    """

    prompt = ChatPromptTemplate.from_template(template)
    structured_model = model.with_structured_output(Critique)

    chain = prompt | structured_model

    result = chain.invoke({
        "data_dictionary": data_dictionary,
        "question": analyst['question'],
        "hypothesis": analyst['hypothesis'],
        "assumptions": analyst['assumptions'],
        "reasoning": analyst['reasoning'],
        "supporting_data": analyst['data'],
        })
    
    with open("./agent_result/agent_reviewer_results.json", "w", encoding="utf-8") as f:
        json.dump(result.model_dump(), f, ensure_ascii=False, indent=2, default=str)  # Use default=str to handle non-serializable objects like datetime
    
    return result

# with open("./agent_result/agent_analysis_results.json") as f:
#     analysis_result = json.load(f)

# llama_model = ChatOllama(model="llama3.2:latest", temperature=0)
# print(reviewer(llama_model, analysis_result))