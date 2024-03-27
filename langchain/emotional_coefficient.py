from langchain.prompts import SystemMessagePromptTemplate
from prompt_constants import DEFAULT_EMOTIONAL_COEFFICIENT_SETTINGS
from template_store import EMOTIONAL_COEFFICIENT_TEMPLATE


class EmotionalCoefficientPrompt:
    def __init__(self, happiness_setting, humor_setting, honesty_setting, trust_setting, saddness_setting, confidence_setting, **kwargs):
        self.happiness_setting = happiness_setting or DEFAULT_EMOTIONAL_COEFFICIENT_SETTINGS.get(
            'happiness_setting')
        self.humor_setting = humor_setting or DEFAULT_EMOTIONAL_COEFFICIENT_SETTINGS.get(
            'humor_setting')
        self.honesty_setting = honesty_setting or DEFAULT_EMOTIONAL_COEFFICIENT_SETTINGS.get(
            'honesty_setting')
        self.trust_setting = trust_setting or DEFAULT_EMOTIONAL_COEFFICIENT_SETTINGS.get(
            'trust_setting')
        self.sad_setting = saddness_setting or DEFAULT_EMOTIONAL_COEFFICIENT_SETTINGS.get(
            'sad_setting')
        self.confidence_setting = confidence_setting or DEFAULT_EMOTIONAL_COEFFICIENT_SETTINGS.get(
            'confidence_setting')
        self._additional_settings = kwargs

    def generate_emotional_coefficient_prompt(self):
        # Load EMOTIONAL_COEFFICIENT_TEMPLATE from the template_store.
        template = EMOTIONAL_COEFFICIENT_TEMPLATE

        # You may include additional settings if they are passed.
        for key, value in self._additional_settings.items():
            template += f" {key.capitalize()}: {{{key}}}"

        # Now, use the SystemMessagePromptTemplate's from_template method to create the prompt.
        system_emotional_coefficient_prompt = SystemMessagePromptTemplate.from_template(
            template,
            happiness_setting=self._happiness_setting,
            humor_setting=self._humor_setting,
            honesty_setting=self._honesty_setting,
            trust_setting=self._trust_setting,
            sad_setting=self._sad_setting,
            **self._additional_settings
        )

        return system_emotional_coefficient_prompt

    @property
    def happiness_setting(self):
        return self._happiness_setting

    @happiness_setting.setter
    def happiness_setting(self, new_setting):
        self._happiness_setting = new_setting

    @property
    def humor_setting(self):
        return self._humor_setting

    @humor_setting.setter
    def humor_setting(self, new_setting):
        self._humor_setting = new_setting

    @property
    def honesty_setting(self):
        return self._honesty_setting

    @honesty_setting.setter
    def honesty_setting(self, new_setting):
        self._honesty_setting = new_setting

    @property
    def trust_setting(self):
        return self._trust_setting

    @trust_setting.setter
    def trust_setting(self, new_setting):
        self._trust_setting = new_setting

    @property
    def sad_setting(self):
        return self._sad_setting

    @sad_setting.setter
    def sad_setting(self, new_setting):
        self._sad_setting = new_setting
