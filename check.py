from backend.app.memory.convolog import ConvoLogger

# Start a session
logger = ConvoLogger(student_id="test_student")
session_id = logger.start_session()

# Log a fake conversation
logger.log_user_message("What is recursion?", topic="recursion")
logger.log_assistant_message("Recursion is a function calling itself.")

logger.log_user_message("Can you give an example?", topic="recursion")
logger.log_assistant_message("Sure! factorial(n) = n * factorial(n-1)")

# End session
logger.end_session()

print(f"Session ID: {session_id}")
print(f"Check file at: data/students/test_student/{session_id}.json")