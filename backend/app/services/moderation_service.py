"""
ModerationService for content filtering - Task 4.1
Requirements: 8
"""
import logging

logger = logging.getLogger(__name__)


class ModerationService:
    """Service for content moderation with profanity filtering"""

    def __init__(self):
        # Initialize profanity filter
        try:
            from better_profanity import profanity
            profanity.load_censor_words()
            self.profanity = profanity
        except ImportError:
            logger.warning("better-profanity not installed, profanity filtering disabled")
            self.profanity = None

    def check_profanity(self, text: str) -> bool:
        """
        Check if text contains profanity

        Returns:
            True if profane content detected, False otherwise
        """
        if not self.profanity or not text:
            return False

        is_flagged = self.profanity.contains_profanity(text)

        if is_flagged:
            logger.warning(f"Profanity detected in text: {text[:50]}...")

        return is_flagged
