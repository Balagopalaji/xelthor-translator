"""Vocabulary management for the Xel'thor translator."""

class VocabularyManager:
    """Manages the vocabulary dictionary for the Xel'thor language."""

    def __init__(self):
        """Initialize the expanded vocabulary."""
        self.vocabulary = {
            # Basic verbs
            "travel": "zz'rix",
            "communicate": "ph'sor",
            "see": "xa'lor",
            "think": "mii'sor",
            "share": "ph'sor",
            "create": "vor'tix",
            "learn": "mii'zar",
            "speak": "ph'lor",

            # Nouns - Physical objects (xel- prefix)
            "traveler": "xel'thor",
            "star": "xel'ka",
            "ship": "xel'vor",
            "world": "xel'thal",
            "body": "xel'phi",

            # Nouns - Energy concepts (vor- prefix)
            "light": "vor'kaan",
            "energy": "vor'thi",
            "power": "vor'zix",
            "space": "vor'thal",
            "time": "vor'phi",

            # Nouns - Abstract concepts (mii- prefix)
            "wisdom": "mii'path",
            "knowledge": "mii'path",
            "truth": "mii'kan",
            "thought": "mii'lor",
            "unity": "mii'zol",

            # Connectors and prepositions
            "through": "vor",
            "between": "zz",
            "with": "phi",
            "in": "ka",
            "to": "th",
            "from": "rx"
        }

    def get_eng_to_xel(self):
        """Return the English to Xel'thor dictionary."""
        return self.vocabulary.copy()

    def get_xel_to_eng(self):
        """Return the Xel'thor to English dictionary."""
        return {v: k for k, v in self.vocabulary.items()}

    def get_sorted_vocabulary(self):
        """Return vocabulary sorted alphabetically by English words."""
        return sorted(self.vocabulary.items())