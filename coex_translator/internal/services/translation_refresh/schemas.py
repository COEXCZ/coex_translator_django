import dataclasses


@dataclasses.dataclass(kw_only=True)
class Translation:
    message: str  # key of the message
    translation: str  # translated text
    language: str  # language code
