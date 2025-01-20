"""Dictionary management system for the Xel'thor translator."""
import ast

class DictionaryManager:
    def __init__(self, dictionary_file='xelthor_dictionary.py'):
        self.dictionary_file = dictionary_file

    def read_dictionary(self):
        """Read the current dictionary from file."""
        with open(self.dictionary_file, 'r') as file:
            content = file.read()
            # Extract the dictionary part
            try:
                dict_text = content.split('DICTIONARY = ')[1].strip()
                # Use ast.literal_eval for safer evaluation
                return ast.literal_eval(dict_text)
            except Exception as e:
                print(f"Error reading dictionary: {e}")
                # Return a basic dictionary structure if reading fails
                return {
                    "vocabulary": {},
                    "prefixes": {
                        "physical": "xel-",
                        "energy": "vor-",
                        "abstract": "mii-"
                    },
                    "tones": {
                        "present": "",
                        "past": "-pa",
                        "future": "-zi",
                        "eternal": "-th"
                    },
                    "special_phrases": {}
                }

    def write_dictionary(self, dictionary):
        """Write the updated dictionary to file."""
        with open(self.dictionary_file, 'w') as file:
            file.write('"""Dictionary for the Xel\'thor language containing vocabulary and special phrases."""\n\n')
            file.write("DICTIONARY = ")
            # Convert dictionary to a formatted string
            dict_str = str(dictionary)
            # Format with proper indentation
            formatted_dict = dict_str.replace("{", "{\n    ").replace("}", "\n}").replace("': ", "': ").replace(", '", ",\n    '")
            file.write(formatted_dict)

    def add_word(self, english, xelthor, category):
        """Add a new word to the dictionary."""
        try:
            dictionary = self.read_dictionary()

            # Add the new word
            dictionary['vocabulary'][english] = xelthor

            # Write back to file
            self.write_dictionary(dictionary)
            return True
        except Exception as e:
            print(f"Error adding word: {e}")
            return False