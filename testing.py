import openai

def generate_response(prompt):
    try:
        # Primary method: Try OpenAI API
        response = openai.ChatCompletion.create(
            api_key=OPENAI_API_KEY,
            model="gpt-3.5-turbo", 
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
        
    except Exception as e:
        # Fallback method: Use simple rule-based responses
        if "hello" in prompt.lower():
            return "Hi there! I'm currently in fallback mode."
        else:
            return "I'd love to help, but my AI service is unavailable right now."