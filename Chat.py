import streamlit as st
import openai
import os
from datetime import datetime

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")  # or set your key directly

# Initialize session state
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

# Function to generate technical questions
def generate_technical_questions(tech_stack, position, experience):
    prompt = f"""
    Generate 5 technical interview questions to assess a candidate's proficiency for a {position} position.
    The candidate has {experience} years of experience and lists the following technologies: {tech_stack}.
    Provide questions that range from basic to advanced based on their experience level.
    Format the questions as a numbered list with clear, specific questions.
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        st.error(f"Error generating questions: {e}")
        return "Could not generate questions at this time."

# Function to save candidate data
def save_candidate_data(data):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.conversation_history.append({
        "timestamp": timestamp,
        "data": data,
        "questions": generate_technical_questions(
            data['tech_stack'], 
            data['desired_position'],
            data['years_experience']
        )
    })
    st.session_state.submitted = True

# Streamlit UI
st.title("🚀 TalentScout Hiring Assistant")
st.write("Welcome to the TalentScout Hiring Assistant! Let's collect some information to assess your fit for the role.")

# Sidebar
with st.sidebar:
    st.header("About")
    st.write("This tool helps recruiters assess technical candidates by generating relevant interview questions.")
    
    if st.session_state.conversation_history:
        st.header("Previous Submissions")
        for idx, entry in enumerate(st.session_state.conversation_history):
            st.write(f"{idx+1}. {entry['timestamp']} - {entry['data']['full_name']}")

# Main form
if not st.session_state.submitted:
    with st.form(key='candidate_info'):
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input("Full Name*", help="Please enter your full name")
            email = st.text_input("Email Address*", help="We'll contact you at this address")
            years_experience = st.number_input("Years of Experience*", 
                                             min_value=0, 
                                             max_value=50,
                                             help="Total years in professional roles")
        
        with col2:
            phone = st.text_input("Phone Number", help="Optional contact number")
            desired_position = st.text_input("Desired Position(s)*", 
                                           help="E.g., 'Senior Python Developer', 'DevOps Engineer'")
            current_location = st.text_input("Current Location", help="City and country")
        
        tech_stack = st.text_area("Tech Stack*", 
                                help="List all relevant technologies, frameworks, and tools (comma separated)")
        
        submitted = st.form_submit_button("Submit Application")
        if submitted:
            required_fields = [full_name, email, years_experience, desired_position, tech_stack]
            if not all(required_fields):
                st.error("Please fill in all required fields (marked with *)")
            else:
                candidate_data = {
                    "full_name": full_name,
                    "email": email,
                    "phone": phone,
                    "years_experience": years_experience,
                    "desired_position": desired_position,
                    "current_location": current_location,
                    "tech_stack": tech_stack
                }
                save_candidate_data(candidate_data)
                st.rerun()

else:
    # After submission
    latest_entry = st.session_state.conversation_history[-1]
    data = latest_entry['data']
    
    st.success("✅ Thank you for your submission!")
    
    with st.expander("Review Your Information"):
        st.subheader("Candidate Details")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Name:** {data['full_name']}")
            st.write(f"**Email:** {data['email']}")
            st.write(f"**Phone:** {data['phone'] or 'Not provided'}")
        
        with col2:
            st.write(f"**Experience:** {data['years_experience']} years")
            st.write(f"**Position:** {data['desired_position']}")
            st.write(f"**Location:** {data['current_location'] or 'Not provided'}")
    
    st.subheader("Technical Assessment Questions")
    st.markdown(latest_entry['questions'])
    
    st.download_button(
        label="Download Questions",
        data=latest_entry['questions'],
        file_name=f"technical_questions_{data['full_name']}.txt",
        mime="text/plain"
    )
    
    if st.button("Start New Application"):
        st.session_state.submitted = False
        st.rerun()
