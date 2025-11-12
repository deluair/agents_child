"""
Data processing components for the AI agent
"""

# Lazy imports to avoid loading heavy dependencies on module import
def __getattr__(name):
    if name == "TextProcessor":
        from .text_processor import TextProcessor
        return TextProcessor
    elif name == "EmotionProcessor":
        from .emotion_processor import EmotionProcessor
        return EmotionProcessor
    elif name == "ContextProcessor":
        from .context_processor import ContextProcessor
        return ContextProcessor
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ["TextProcessor", "EmotionProcessor", "ContextProcessor"]
