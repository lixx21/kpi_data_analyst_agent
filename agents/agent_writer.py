from langchain_core.prompts import ChatPromptTemplate
from pathlib import Path

def write_analysis_result(model, analysis):

    prompt = """
    You are a senior data analyst / business analyst who always write down your analysis
    into analysis paper / analysis documentation for business team / stakeholders.

    Write the analysis paper / documentation to MD file from analysis result below:
    ```
    {analysis_result}
    ```

    output format:
    - MD file format
    - make it easier to be understand by business stakeholder
    - remove the technical explanation or convert it into business explanation
    """

    chat_prompt_template = ChatPromptTemplate.from_template(prompt)
    chain = chat_prompt_template | model

    result = chain.invoke({
        "analysis_result": analysis
    })

    path = "./agent_result/analysis_report.md"
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(result.content, encoding="utf-8")

    return "The analysis report has been created"
    