from typing import TypedDict, Any
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from agent_planner import planner
from agent_data import get_data_from_steps
from agent_analyst import analyze_data
from agent_writer import write_analysis_result
from agent_reviewer import reviewer
import streamlit as st
import os

def graph_agent():
    OLLAMA_URL= os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    # OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434") #for docker. (for non-docker use http://localhost:11434)
    llama_model = ChatOllama(model="llama3.2:latest", temperature=0, base_url=OLLAMA_URL)
    coder_model = ChatOllama(model="qwen2.5-coder", temperature=0, base_url=OLLAMA_URL)

    class State(TypedDict):
        question: str
        plan: Any
        sql_data: Any
        analysis: Any
        review: Any
        feedback: str
        loop_count: int 
        report: Any

    def planner_node(state: State):
        print('planning analysis...')
        q = state['question']
        if state.get("feedback"):
            q += f"\n\nPrevious attempt feedback: {state['feedback']}"
        plan = planner(llama_model, q)

        return {'plan': plan}

    def data_node(state: State):
        print('get data from database...')
        sql_data =  get_data_from_steps(coder_model, state['plan'])

        return {'sql_data': sql_data}

    def analyst_node(state: State):
        print('starting analyze data...')
        analysis_result = analyze_data(llama_model, state['question'], state['plan'].model_dump(), state['sql_data'])

        return {'analysis': analysis_result}

    def critic_node(state: State):
        review = reviewer(llama_model, state['analysis'])
        feedback = ""
        if review.verdict == "FAIL":
            feedback = (f"A reviewer found these problems: {review.issues}. "
                        f"Fix this: {review.next_action}")
        return {
            "review": review,
            "feedback": feedback,
            "loop_count": state.get("loop_count", 0) + 1
        }

    def route_after_critic(state: State):
        if state["review"].verdict == "PASS" or state["loop_count"] >= 3:
            return "writer"
        return "planner" 

    def writer_node(state: State):
        print('Write analysis report...')
        report = write_analysis_result(llama_model, state['analysis']['analysis_result'])

        return {'report': report}

    graph = StateGraph(State)
    graph.add_node('planner', planner_node)
    graph.add_node('data', data_node)
    graph.add_node('analyst', analyst_node)
    graph.add_node('critic', critic_node)
    graph.add_node('writer', writer_node)

    graph.add_edge(START, 'planner')
    graph.add_edge('planner', 'data')
    graph.add_edge('data', 'analyst')
    graph.add_edge("analyst", "critic")            # replaces analyst -> writer
    graph.add_conditional_edges(
        "critic", route_after_critic,
        {"writer": "writer", "planner": "planner"},
    )
    graph.add_edge('writer', END)

    agent_app = graph.compile()

    return agent_app

def main(agent_app):

    st.set_page_config(
        page_title='KPI Analysis Agent'
    )

    st.title("KPI Analyst Agent")
    question = st.text_input("question")
    
    if st.button("Ask"):
        final_state = {"question": question}
    # question = "Which supplier has the highest defect rate in Raw Materials?"
        with st.status("⏳Analyzing data...", expanded=True) as status:

            for event in agent_app.stream({"question": question}):

                for node_name, state in event.items():
                    st.write(f"Agent {node_name} done ✅")
                    if node_name == 'critic':
                        review = state['review']
                        st.write(f"Verdict: {review.verdict} | Issues: {review.issues}")
                    final_state.update(state)

            status.update(label="Analysis complete", state="complete", expanded=False)
    # final_state = app.invoke({'question': question})
        st.subheader('Analysis Report:')
        st.markdown(final_state['report'])
    # Generate GRAPH image
    # 1. Draw the graph by using this code: print(app.get_graph().draw_mermaid()) 
    # 2. Copy and paste the result to mermaid.md
if __name__== "__main__":
    agent_app = graph_agent()
    main(agent_app)