from emotional_coefficient import EmotionalCoefficientPrompt
from prompt_constants import MAX_CONVERSATION_LENGTH, MAX_PROMPT_TOKEN
from constants import OPENAI_MODEL

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

# TODO: Move to exception class


class PromptTokenLengthExceededException(Exception):
    pass


class InvalidCurrentConversationRole(Exception):
    pass


class ChatBot:
    def __init__(self):
        self.conversation_message = []

    # Main function to control prompt behaviour
    def input_data_parser(self, request):
        chat_prompt = ChatPromptTemplate.from_messages([])

        # Add System Message Prompt
        # chat_prompt.add(self.generate_system_prompt(
        #     request.user_emotional_settings))

        # Final System Modified Prompt
        # TODO: Add any final modification and other checks.

        # Add Previous Conversation Messages
        # chat_prompt.add(self.generate_conversation_prompt(
        #     request.past_conversation))

        # Add Current Question Message
        chat_prompt.add(self.generate_current_prompt(
            request.current_conversation))

        # Apply situation awareness
        # prompt = self.situation_awareness(prompt, )

        # Apply personal profile modification
        # user_profile = request['user_profile']
        # prompt = self.personal_profile(prompt, user_profile)

        # Count the characters in the prompt
        # TODO - Try and run only the current_prompt if char_count is large.
        char_count = self.char_counter(chat_prompt)
        if char_count >= MAX_PROMPT_TOKEN[OPENAI_MODEL]:
            raise PromptTokenLengthExceededException(
                'The length of the generated prompt tokens exceeded 1000.')

        return {
            'prompt': chat_prompt,
        }

    def char_counter(self, prompt):
        return len(prompt)

    """
    n is the ascending meaning n with the smallest is the oldest conversation.
    Also, N can be only in even as it contains equal number of user and assistant.
    'past_conversation': {
        "N": 4,
        'conversation':
        [
            {
                "n" = 1, 
                "content": "Hello",
                 "role": "user"
            }
            {
                "n" = 2, 
                "assistant": "Hello! How can I assist you today?",
                 "role": "assistant"
            } 
            {
                "n" = 3, 
                "content": "Who won the world series in 2020?",
                 "role": "user"
            }
            {
                "n" = 4, 
                "content": "The Los Angeles Dodgers won the World Series in 2020.",
                 "role": "assistant"
            }
        ]
    }
    """

    def generate_conversation_prompt(self, past_conversation):
        messages = self.past_conversation_parser(past_conversation)

        # Initialize an empty ChatPromptTemplate
        conversation_prompt = ChatPromptTemplate.from_messages([])

        # Counter for number of messages processed
        message_count = 1

        # Iterate through the past conversation and create prompts based on the role
        for message in messages:
            # Check if we've already processed MAX_CONVERSATION_LENGTH messages
            if message_count >= MAX_CONVERSATION_LENGTH:
                break

            content = message['content']
            role = message['role']

            if role == 'user':
                # Create a HumanMessage object and add it to the conversation prompt
                human_message = HumanMessage(content=content)
                conversation_prompt.add(
                    HumanMessagePromptTemplate.from_message(human_message))
            elif role == 'assistant':
                # Create a AIMessage object and add it to the conversation prompt
                ai_message = AIMessage(content=content)
                conversation_prompt.add(
                    AIMessagePromptTemplate.from_message(ai_message))

             # Increment message count
            message_count += 1

        return conversation_prompt

    def past_conversation_parser(self, past_conversation):
        messages = []
        conversations = past_conversation['conversation']
        for conversation in conversations:
            # Create a message dictionary that combines 'content' and 'assistant'
            message = {
                'index': conversation['n'],
                # TODO: Add a summerizer if the token length is too large
                # (char_counter(conversation.get('content')) >= PAST_CONVERSATION_SUMMERIZER_TRIGGER_LIMIT).
                'content': conversation.get('content'),
                'role': 'system' if 'assistant' in conversation else 'user'
            }
            messages.append(message)

        # Sort the messages by the index
        sorted_messages = sorted(messages, key=lambda x: x['index'])

        return sorted_messages

    """       
    'current_conversation':
        {
            "n" = 1, 
            "content": "Where was it played?",
            "role": "user"
        }        
    """

    def generate_current_prompt(self, current_conversation):
        role = current_conversation.get('role')
        content = current_conversation.get('content')

        if role == 'user':
            prompt_template = HumanMessagePromptTemplate(content=content)
        else:
            raise InvalidCurrentConversationRole('Invalid conversation role')

        return ChatPromptTemplate.from_messages([prompt_template])

    def generate_system_prompt(self, user_emotional_settings):
        emotional_coefficient_prompt = self.emotional_coefficient_prompt(
            user_emotional_settings)
        return emotional_coefficient_prompt

    def emotional_coefficient_prompt(user_emotional_settings):
        if user_emotional_settings:
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
            emotional_coefficient_prompt = prompt.generate_emotional_coefficient_prompt()

        else:
            prompt = EmotionalCoefficientPrompt()
            emotional_coefficient_prompt = prompt.generate_emotional_coefficient_prompt()
        return emotional_coefficient_prompt

    def situation_awareness(self, prompt, context_messages):
        # Combine prompt with the context messages to create situation awareness
        context = " ".join(context_messages[-10:])
        return context + " " + prompt

    def personal_profile(self, prompt, user_profile):
        # Modify the prompt based on the user's personal profile
        # You can define your logic here, e.g., using user_profile['name'], user_profile['age'], etc.
        return prompt
