import chainlit as cl
from crewai import Agent, Task, Crew, LLM
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Gemini LLM using CrewAI's LLM class
llm = LLM(
    model="gemini/gemini-2.5-flash",
    api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.7,
    stream=True
)

# Create Weather Intelligence Agent
weather_agent = Agent(
    role="Weather Intelligence Agent",
    goal="Provide accurate weather analysis and farming recommendations based on weather conditions",
    backstory="""You are an expert meteorologist specializing in agricultural weather patterns. 
    You have deep knowledge of how weather affects farming operations and can provide actionable 
    advice to farmers based on current and forecasted weather conditions.""",
    llm=llm,
    verbose=True,
    allow_delegation=False
)

@cl.on_chat_start
async def start():
    await cl.Message(
        content="🌤️ Welcome to the Agricultural Weather Intelligence Assistant!\n\nI'm your Weather Intelligence Agent, specialized in providing weather-based farming advice.\n\nYou can ask me questions like:\n- 'What's the weather forecast for my wheat crop?'\n- 'Should I irrigate based on upcoming weather?'\n- 'How will next week's temperature affect my crops?'\n\nHow can I help you today?"
    ).send()

@cl.on_message
async def main(message: cl.Message):
    # Show thinking message
    thinking_msg = cl.Message(content="🤔 Analyzing weather conditions and preparing recommendations...")
    await thinking_msg.send()
    
    # Create task for the weather agent
    weather_task = Task(
        description=f"""
        Analyze the following farmer's query and provide weather-based agricultural advice:
        
        Query: {message.content}
        
        Provide:
        1. Current weather assessment
        2. Weather forecast implications for farming
        3. Specific actionable recommendations
        4. Any weather-related risks or opportunities
        
        Be practical and specific in your advice.
        """,
        agent=weather_agent,
        expected_output="Detailed weather analysis with specific farming recommendations"
    )
    
    # Create crew with single agent
    crew = Crew(
        agents=[weather_agent],
        tasks=[weather_task],
        verbose=True
    )
    
    try:
        # Execute the crew
        result = crew.kickoff()
        
        # Update the thinking message with the result
        thinking_msg.content = f"🌤️ **Weather Intelligence Analysis**\n\n{result}"
        await thinking_msg.update()
        
    except Exception as e:
        error_msg = f"❌ Sorry, I encountered an error: {str(e)}\n\nPlease make sure your GOOGLE_API_KEY is set correctly."
        thinking_msg.content = error_msg
        await thinking_msg.update()

if __name__ == "__main__":
    cl.run()