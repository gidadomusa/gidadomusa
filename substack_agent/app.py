from openai import OpenAI


client = OpenAI()
response = client.responses.create(
model="gpt-5",
input="Create a Substack post about AI agents for creators.")

print(response.output_text)