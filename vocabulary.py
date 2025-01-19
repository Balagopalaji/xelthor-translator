"""Vocabulary management for the Xel'thor translator."""

class VocabularyManager:
    """Manages the vocabulary dictionary for the Xel'thor language."""
    
    def __init__(self):
        """Initialize the basic vocabulary."""
        self.vocabulary = {
            "traveler": "xel'thor",
            "light": "vor'kaan",
            "wisdom": "mii'path",
            "travel": "zz'rix",
            "homeworld": "k'thal",
            "communicate": "ph'sor",
            "through": "vor",
            "between": "zz",
            "share": "ph'sor",
            "knowledge": "mii'path",
            "star": "xel'ka",
            "space": "vor'thal",
            "think": "mii'sor",
            # Additional vocabulary
            "galaxy": "vor'ka",
            "time": "mii'thal",
            "journey": "zz'thor",
            "learn": "mii'vor",
            "universe": "xel'thal"
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
