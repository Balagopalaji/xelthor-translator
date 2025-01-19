"""Xel'thor language translator implementation."""
from vocabulary import VocabularyManager

class XelthorTranslator:
    """Handles translation between English and Xel'thor languages."""
    
    def __init__(self):
        """Initialize the translator with vocabulary."""
        vocab_manager = VocabularyManager()
        self.eng_to_xel = vocab_manager.get_eng_to_xel()
        self.xel_to_eng = vocab_manager.get_xel_to_eng()
        
    def translate_to_xelthor(self, english_text):
        """
        Translate English text to Xel'thor.
        
        Args:
            english_text (str): Text to translate
            
        Returns:
            str: Translated text with unknown words in brackets
        """
        if not english_text:
            return ""
            
        try:
            words = english_text.lower().strip().split()
            xelthor_words = []
            
            for word in words:
                # Remove basic punctuation for translation
                clean_word = word.strip('.,!?')
                if clean_word in self.eng_to_xel:
                    xelthor_words.append(self.eng_to_xel[clean_word])
                else:
                    xelthor_words.append(f"[{clean_word}]")
                    
            return " ".join(xelthor_words)
        except Exception as e:
            return f"Translation error: {str(e)}"
    
    def translate_to_english(self, xelthor_text):
        """
        Translate Xel'thor text to English.
        
        Args:
            xelthor_text (str): Text to translate
            
        Returns:
            str: Translated text with unknown words preserved
        """
        if not xelthor_text:
            return ""
            
        try:
            words = xelthor_text.strip().split()
            english_words = []
            
            for word in words:
                # Handle bracketed unknown words
                if word.startswith('[') and word.endswith(']'):
                    english_words.append(word.strip('[]'))
                else:
                    clean_word = word.strip('.,!?')
                    if clean_word in self.xel_to_eng:
                        english_words.append(self.xel_to_eng[clean_word])
                    else:
                        english_words.append(clean_word)
                    
            return " ".join(english_words)
        except Exception as e:
            return f"Translation error: {str(e)}"
            
    def get_vocabulary(self):
        """Return the current vocabulary as a sorted list of tuples."""
        vocab_manager = VocabularyManager()
        return vocab_manager.get_sorted_vocabulary()
