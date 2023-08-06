from emotional_coefficient import EmotionalCoefficientPrompt

from langchains import GPT3LangChain
from langchains.prompts import (
    ChatPromptTemplate,
    PromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchains.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)


class ChatBot:
    def __init__(self):
        self.system_prompt = []
        self.conversation_message = []

    def input_data_parser(self, request):
        chat_prompt = ChatPromptTemplate.from_messages([])

        # Add System Message Prompt
        chat_prompt.add(self.generate_system_prompt(
            request.user_emotional_settings))

        # Add Previous Conversation Messages
        chat_prompt.add(self.generate_conversation_prompt(
            request.past_conversation))

        # Add Current Question Message
        chat_prompt.add(self.generate_question_prompt(request.current_query))

        prompt = request['question']
        last_10_messages = request['last_10_messages']
        user_profile = request['user_profile']
        emotional_coefficient = request['emotional_coefficient']

        # Count the characters in the prompt
        char_count = self.char_counter(prompt)

        # Generate the system prompt based on user's emotional settings
        self.generate_system_prompt(request.get('user_emotional_settings'))

        # Modify the system role
        prompt = self.system_role_modified(prompt, emotional_coefficient)

        # Apply situation awareness
        prompt = self.situation_awareness(prompt, last_10_messages)

        # Apply personal profile modification
        prompt = self.personal_profile(prompt, user_profile)

        return {
            'prompt': prompt,
            'char_count': char_count,
            'chat_prompt': self.chat_prompt
        }

    def char_counter(self, prompt):
        return len(prompt)

    def generate_system_prompt(self, user_emotional_settings):
        emotional_coefficient_prompt = self.emotional_coefficient_prompt(
            user_emotional_settings)
        # situation_awareness_prompt
        # personal_profile_prompt

        self.system_prompt.append(emotional_coefficient_prompt)
        # self.system_prompt.append(situation_awareness_prompt)
        # self.system_prompt.append(personal_profile_prompt)

    def emotional_coefficient_prompt(user_emotional_settings):
        if user_emotional_settings:
            # Get the emotional settings from the user input, e.g. a JSON object.
            user_emotional_settings = user_emotional_settings

            # Instantiate an EmotionalCoefficientPrompt object with the user-defined settings.
            prompt = EmotionalCoefficientPrompt(
                happiness_setting=user_emotional_settings.get('happiness'),
                humor_setting=user_emotional_settings.get('humor'),
                honesty_setting=user_emotional_settings.get('honesty'),
                trust_setting=user_emotional_settings.get('trust'),
                sad_setting=user_emotional_settings.get('sad'),
                confidence_setting=user_emotional_settings.get('confidence')
            )

            # Generate a prompt based on the user-defined settings.
            system_message_prompt = prompt.generate_emotional_coefficient_prompt()

        else:
            prompt = EmotionalCoefficientPrompt()
            emotional_coefficient_prompt = prompt.generate_emotional_coefficient_prompt
        return emotional_coefficient_prompt

    def situation_awareness(self, prompt, context_messages):
        # Combine prompt with the context messages to create situation awareness
        context = " ".join(context_messages[-10:])
        return context + " " + prompt

    def personal_profile(self, prompt, user_profile):
        # Modify the prompt based on the user's personal profile
        # You can define your logic here, e.g., using user_profile['name'], user_profile['age'], etc.
        return prompt
