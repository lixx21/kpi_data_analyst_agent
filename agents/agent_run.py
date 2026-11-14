from typing import TypedDict, Any
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from agent_planner import planner
from agent_data import get_data_from_steps
from agent_analyst import analyze_data
from agent_writer import write_analysis_result

llama_model = ChatOllama(model="llama3.2:latest", temperature=0)
coder_model = ChatOllama(model="qwen2.5-coder", temperature=0)

class State(TypedDict):
    question: str
    plan: Any
    sql_data: Any
    analysis: Any
    report: Any

def planner_node(state: State):
    print('planning analysis...')
    plan = planner(llama_model, state['question'])

    return {'plan': plan}

def data_node(state: State):
    print('get data from database...')
    sql_data =  get_data_from_steps(coder_model, state['plan'])

    return {'sql_data': sql_data}

def analyst_node(state: State):
    print('starting analyze data...')
    analysis_result = analyze_data(llama_model, state['question'], state['plan'].model_dump(), state['sql_data'])

    return {'analysis': analysis_result}

def writer_node(state: State):
    print('Write analysis report...')
    report = write_analysis_result(llama_model, state['analysis'])

    return {'report': report}

graph = StateGraph(State)
graph.add_node('planner', planner_node)
graph.add_node('data', data_node)
graph.add_node('analyst', analyst_node)
graph.add_node('writer', writer_node)

graph.add_edge(START, 'planner')
graph.add_edge('planner', 'data')
graph.add_edge('data', 'analyst')
graph.add_edge('analyst', 'writer')
graph.add_edge('writer', END)

app = graph.compile()


question = "Which supplier has the highest defect rate in Raw Materials?"

final_state = app.invoke({'question': question})
print(final_state['report'])


# Generate GRAPH image
# 1. Draw the graph by using this code: print(app.get_graph().draw_mermaid()) 
# 2. Copy and paste the result to mermaid.md