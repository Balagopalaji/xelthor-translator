"""Dictionary management system for the Xel'thor translator."""
import ast
import os
import shutil
from datetime import datetime

class DictionaryManager:
    def __init__(self, dictionary_file='xelthor_dictionary.py', backup_dir='dictionary_backups'):
        self.dictionary_file = dictionary_file
        self.backup_dir = backup_dir
        self.ensure_backup_dir()

    def ensure_backup_dir(self):
        """Create backup directory if it doesn't exist."""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

    def read_dictionary(self):
        """Read the current dictionary from file."""
        try:
            with open(self.dictionary_file, 'r') as file:
                content = file.read()
                dict_text = content.split('DICTIONARY = ')[1].strip()
                # Use ast.literal_eval for safer evaluation
                return ast.literal_eval(dict_text)
        except Exception as e:
            print(f"Error reading dictionary: {str(e)}")
            return {
                'vocabulary': {},
                'prefixes': {
                    'physical': 'xel-',
                    'energy': 'vor-',
                    'abstract': 'mii-'
                },
                'tones': {
                    'present': '',
                    'past': '-pa',
                    'future': '-zi',
                    'eternal': '-th'
                },
                'special_phrases': {}
            }

    def write_dictionary(self, dictionary):
        """Write the updated dictionary to file."""
        try:
            # Create backup before writing
            self.create_backup()

            with open(self.dictionary_file, 'w') as file:
                file.write('"""Dictionary for the Xel\'thor language containing vocabulary and special phrases."""\n\n')
                file.write("DICTIONARY = ")
                # Format with proper indentation
                dict_str = str(dictionary)
                formatted_dict = dict_str.replace("{", "{\n    ").replace("}", "\n}").replace("': ", "': ").replace(", '", ",\n    '")
                file.write(formatted_dict)
            return True
        except Exception as e:
            print(f"Error writing dictionary: {str(e)}")
            return False

    def create_backup(self):
        """Create a backup of the current dictionary."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"{self.backup_dir}/xelthor_dictionary_{timestamp}.py"
        try:
            shutil.copy2(self.dictionary_file, backup_file)
            return backup_file
        except Exception as e:
            print(f"Error creating backup: {str(e)}")
            return None

    def restore_backup(self, backup_file):
        """Restore dictionary from a backup file."""
        try:
            if os.path.exists(backup_file):
                shutil.copy2(backup_file, self.dictionary_file)
                return True
        except Exception as e:
            print(f"Error restoring backup: {str(e)}")
        return False

    def list_backups(self):
        """List all available backups."""
        try:
            return sorted([f for f in os.listdir(self.backup_dir) 
                       if f.startswith('xelthor_dictionary_')])
        except Exception as e:
            print(f"Error listing backups: {str(e)}")
            return []

    def add_word(self, english, xelthor, category):
        """Add a new word to the dictionary."""
        dictionary = self.read_dictionary()
        dictionary['vocabulary'][english] = xelthor
        return self.write_dictionary(dictionary)

    def edit_word(self, english, new_xelthor):
        """Edit an existing word in the dictionary."""
        try:
            dictionary = self.read_dictionary()
            if english in dictionary['vocabulary']:
                dictionary['vocabulary'][english] = new_xelthor
                return self.write_dictionary(dictionary)
            return False
        except Exception as e:
            print(f"Error editing word: {str(e)}")
            return False

    def remove_word(self, english):
        """Remove a word from the dictionary."""
        try:
            dictionary = self.read_dictionary()
            if english in dictionary['vocabulary']:
                del dictionary['vocabulary'][english]
                return self.write_dictionary(dictionary)
            return False
        except Exception as e:
            print(f"Error removing word: {str(e)}")
            return False

    def add_special_phrase(self, english, xelthor):
        """Add a new special phrase to the dictionary."""
        try:
            dictionary = self.read_dictionary()
            dictionary['special_phrases'][english] = xelthor
            return self.write_dictionary(dictionary)
        except Exception as e:
            print(f"Error adding special phrase: {str(e)}")
            return False

    def remove_special_phrase(self, english):
        """Remove a special phrase from the dictionary."""
        try:
            dictionary = self.read_dictionary()
            if english in dictionary['special_phrases']:
                del dictionary['special_phrases'][english]
                return self.write_dictionary(dictionary)
            return False
        except Exception as e:
            print(f"Error removing special phrase: {str(e)}")
            return False