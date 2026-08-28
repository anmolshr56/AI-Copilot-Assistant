from crewai import Agent, Task, Crew, Process
from backend.llm_config import get_llm


def run_crew_task(topic):

    # Research Agent
    researcher = Agent(
        role='Researcher',
        goal=f'Find 3 groundbreaking facts about {topic}',
        backstory='You are an elite researcher who finds the truth no matter what.',
        llm=get_llm(use_cloud=True),
        verbose=True
    )

    # Writer Agent
    writer = Agent(
        role='Content Creator',
        goal=f'Write a viral Gen-Z style LinkedIn post about {topic}',
        backstory='You turn boring data into viral content using emojis and slang.',
        llm=get_llm(use_cloud=True),
        verbose=True
    )

    # Tasks
    task1 = Task(
        description=f'''
        Research the topic: {topic}

        Find:
        1. Three important facts
        2. Recent developments
        3. Why it matters

        Give a concise research summary.
        ''',
        agent=researcher,
        expected_output="Research summary with 3 facts"
    )

    task2 = Task(
        description=f'''
        Using the research summary,
        create a professional LinkedIn post about {topic}.

        Make it engaging and easy to read.
        ''',
        agent=writer,
        expected_output="LinkedIn post"
    )

    # Crew
    crew = Crew(
        agents=[researcher, writer],
        tasks=[task1, task2],
        process=Process.sequential,
        verbose=True
    )

    result = crew.kickoff()

    return str(result)