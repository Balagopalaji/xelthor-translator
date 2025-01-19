"""Xel'thor language translator implementation."""
from vocabulary import VocabularyManager

class XelthorTranslator:
    """Handles translation between English and Xel'thor languages."""

    def __init__(self):
        """Initialize the translator with vocabulary and grammar rules."""
        vocab_manager = VocabularyManager()
        self.eng_to_xel = vocab_manager.get_eng_to_xel()
        self.xel_to_eng = vocab_manager.get_xel_to_eng()

        # Prefixes for states of existence
        self.prefixes = {
            "physical": "xel-",
            "energy": "vor-",
            "abstract": "mii-"
        }

        # Tonal indicators (added as suffixes)
        self.tones = {
            "present": "",  # neutral tone
            "past": "-pa",  # descending tone
            "future": "-zi",  # ascending tone
            "eternal": "-th"  # harmonic tone
        }

    def apply_grammar_rules(self, words, to_xelthor=True):
        """Apply Xel'thor grammar rules (Verb-Object-Subject order)."""
        if len(words) < 3:
            return words

        # Identify the verb (basic implementation)
        verb_index = None
        for i, word in enumerate(words):
            if to_xelthor:
                if word in self.eng_to_xel:
                    xel_word = self.eng_to_xel[word]
                    if any(xel_word.startswith(p) for p in ["zz'", "ph'", "xa'", "vor'", "mii'"]):
                        verb_index = i
                        break
            else:
                if word in self.xel_to_eng:
                    if any(word.startswith(p) for p in ["zz'", "ph'", "xa'", "vor'", "mii'"]):
                        verb_index = i
                        break

        if verb_index is not None:
            if to_xelthor:
                # Move verb to front, object next, subject last
                result = ([words[verb_index]] + 
                         [w for i, w in enumerate(words) if i != verb_index and i > verb_index] +
                         [w for i, w in enumerate(words) if i != verb_index and i < verb_index])
                return result
            else:
                # Reverse VOS to SVO for English
                result = ([w for i, w in enumerate(words) if i != verb_index and i > verb_index] +
                         [words[verb_index]] +
                         [w for i, w in enumerate(words) if i != verb_index and i < verb_index])
                return result

        return words

    def apply_tense(self, xelthor_word, tense="present"):
        """Apply tonal suffix for tense."""
        if tense in self.tones:
            return xelthor_word + self.tones[tense]
        return xelthor_word

    def translate_to_xelthor(self, english_text, tense="present"):
        """
        Translate English text to Xel'thor with tense support.

        Args:
            english_text (str): Text to translate
            tense (str): Desired tense (present, past, future, eternal)

        Returns:
            str: Translated text with tense markers
        """
        if not english_text:
            return ""

        try:
            words = english_text.lower().strip().split()
            xelthor_words = []

            # First pass: basic translation
            for word in words:
                clean_word = word.strip('.,!?')
                if clean_word in self.eng_to_xel:
                    xelthor_words.append(self.eng_to_xel[clean_word])
                else:
                    xelthor_words.append(f"[{clean_word}]")

            # Apply grammar rules
            xelthor_words = self.apply_grammar_rules(xelthor_words, to_xelthor=True)

            # Apply tense to verbs
            final_words = []
            for word in xelthor_words:
                if any(word.startswith(p) for p in ["zz'", "ph'", "xa'", "vor'", "mii'"]):
                    word = self.apply_tense(word, tense)
                final_words.append(word)

            return " ".join(final_words)
        except Exception as e:
            return f"Translation error: {str(e)}"

    def translate_to_english(self, xelthor_text):
        """
        Translate Xel'thor text to English with tense interpretation.

        Args:
            xelthor_text (str): Text to translate

        Returns:
            str: Translated text with proper English tense
        """
        if not xelthor_text:
            return ""

        try:
            words = xelthor_text.strip().split()
            english_words = []

            # Remove tense markers and translate
            for word in words:
                base_word = word
                tense = "present"

                # Check for tense markers
                for t, marker in self.tones.items():
                    if marker and word.endswith(marker):
                        base_word = word[:-len(marker)]
                        tense = t
                        break

                if base_word in self.xel_to_eng:
                    translated = self.xel_to_eng[base_word]
                    # Add tense context if not present
                    if tense != "present":
                        if english_words and english_words[0] != "will" and tense == "future":
                            english_words.insert(0, "will")
                        elif english_words and not any(w in english_words for w in ["had", "was"]) and tense == "past":
                            translated = f"{'was' if translated.endswith('ing') else 'did'} {translated}"
                else:
                    if base_word.startswith('[') and base_word.endswith(']'):
                        translated = base_word.strip('[]')
                    else:
                        translated = base_word

                english_words.append(translated)

            # Apply English grammar rules
            english_words = self.apply_grammar_rules(english_words, to_xelthor=False)

            return " ".join(english_words)
        except Exception as e:
            return f"Translation error: {str(e)}"

    def get_vocabulary(self):
        """Return the current vocabulary as a sorted list of tuples."""
        vocab_manager = VocabularyManager()
        return vocab_manager.get_sorted_vocabulary()