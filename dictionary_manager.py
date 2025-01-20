"""Dictionary management system for the Xel'thor translator."""
import ast
import os
import shutil
import csv
from datetime import datetime
from io import StringIO

class DictionaryManager:
    def __init__(self, dictionary_file='xelthor_dictionary.py', backup_dir='dictionary_backups'):
        self.dictionary_file = dictionary_file
        self.backup_dir = backup_dir
        self.prefix_map = {
            "1": ["zz'", "ph'", "xa'", "vor'", "mii'"],  # Verbs
            "2": ["xel'"],  # Physical nouns
            "3": ["vor'"],  # Energy concepts
            "4": ["mii'"],  # Abstract concepts
            "5": []  # Connectors
        }
        # Valid consonant combinations based on phonology rules
        self.valid_consonants = ['x', 'th', "k'", 'zz', 'ph', "r'"]
        # Harmonized vowel pairs
        self.harmonized_vowels = ['aa', 'ee', 'ii', 'oo', 'uu']
        # Default prefixes for each category
        self.default_prefix = {
            "1": "zz'",  # Default verb prefix
            "2": "xel'", # Default physical prefix
            "3": "vor'", # Default energy prefix
            "4": "mii'", # Default abstract prefix
            "5": ""      # No prefix for connectors
        }
        self.ensure_backup_dir()

    def validate_phonology(self, word):
        """Validate word phonology according to language rules."""
        # Check for valid consonant combinations
        has_valid_consonant = any(cons in word for cons in self.valid_consonants)
        if not has_valid_consonant:
            return False, "Word must contain at least one valid consonant combination (x, th, k', zz, ph, r')"

        # Check for harmonized vowels
        for vowel_pair in self.harmonized_vowels:
            if vowel_pair in word:
                return True, None

        return True, None  # Allow words without harmonized vowels for flexibility

    def validate_word(self, xelthor, category):
        """Validate a Xel'thor word according to language rules."""
        # First check phonology rules
        is_valid_phon, phon_error = self.validate_phonology(xelthor)
        if not is_valid_phon:
            return False, phon_error

        if category == "5":  # Connectors
            if len(xelthor) > 4:
                return False, "Connector words must be 4 characters or less"
            return True, None

        # Check if word has a valid prefix for its category
        valid_prefixes = self.prefix_map[category]
        if not any(xelthor.startswith(prefix) for prefix in valid_prefixes):
            expected_prefixes = ", ".join(valid_prefixes)
            return False, f"Word must start with one of these prefixes: {expected_prefixes}"

        return True, None

    def add_word(self, english, xelthor, category):
        """Add a new word to the dictionary with validation."""
        try:
            # Validate the word format
            is_valid, error_msg = self.validate_word(xelthor, category)
            if not is_valid:
                print(f"Validation error: {error_msg}")
                return False

            dictionary = self.read_dictionary()

            # Check for duplicate
            if english in dictionary['vocabulary']:
                print(f"Word '{english}' already exists")
                return False

            dictionary['vocabulary'][english] = xelthor
            return self.write_dictionary(dictionary)
        except Exception as e:
            print(f"Error adding word: {str(e)}")
            return False

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

    def batch_add_words(self, csv_content):
        """Add multiple words from CSV content.
        Expected format: english,xelthor,category
        Category should be 1-5 corresponding to the word types
        Returns tuple: (success_count, error_list)
        """
        try:
            dictionary = self.read_dictionary()
            success_count = 0
            errors = []

            csv_file = StringIO(csv_content)
            reader = csv.reader(csv_file)

            for row_num, row in enumerate(reader, 1):
                try:
                    if len(row) != 3:
                        errors.append(f"Row {row_num}: Invalid format. Expected 3 columns (english,xelthor,category)")
                        continue

                    english, xelthor, category = [x.strip().lower() for x in row]

                    if not category.isdigit() or category not in self.prefix_map:
                        errors.append(f"Row {row_num}: Invalid category '{category}'. Must be 1-5")
                        continue

                    if english in dictionary['vocabulary']:
                        errors.append(f"Row {row_num}: Word '{english}' already exists")
                        continue

                    # Handle prefixes automatically
                    if category == "5":  # Connectors
                        if len(xelthor) > 4:
                            errors.append(f"Row {row_num}: Connector '{xelthor}' too long (max 4 characters)")
                            continue
                    else:
                        # Check if word already has a valid prefix
                        has_valid_prefix = any(xelthor.startswith(prefix) for prefix in self.prefix_map[category])

                        if not has_valid_prefix:
                            # Add the default prefix for this category
                            xelthor = self.default_prefix[category] + xelthor
                            print(f"Row {row_num}: Added prefix {self.default_prefix[category]} to '{english}' -> '{xelthor}'")

                    dictionary['vocabulary'][english] = xelthor
                    success_count += 1

                except Exception as e:
                    errors.append(f"Row {row_num}: Error processing row: {str(e)}")

            if success_count > 0:
                self.write_dictionary(dictionary)

            return success_count, errors

        except Exception as e:
            return 0, [f"Error processing CSV: {str(e)}"]

    def batch_add_special_phrases(self, csv_content):
        """Add multiple special phrases from CSV content.
        Expected format: english,xelthor
        Returns tuple: (success_count, error_list)
        """
        try:
            dictionary = self.read_dictionary()
            success_count = 0
            errors = []

            csv_file = StringIO(csv_content)
            reader = csv.reader(csv_file)

            for row_num, row in enumerate(reader, 1):
                try:
                    if len(row) != 2:
                        errors.append(f"Row {row_num}: Invalid format. Expected 2 columns (english,xelthor)")
                        continue

                    english, xelthor = [x.strip().lower() for x in row]

                    if english in dictionary['special_phrases']:
                        errors.append(f"Row {row_num}: Phrase '{english}' already exists")
                        continue

                    dictionary['special_phrases'][english] = xelthor
                    success_count += 1

                except Exception as e:
                    errors.append(f"Row {row_num}: Error processing row: {str(e)}")

            if success_count > 0:
                self.write_dictionary(dictionary)

            return success_count, errors

        except Exception as e:
            return 0, [f"Error processing CSV: {str(e)}"]

    def export_words_to_csv(self):
        """Export all words to CSV format string."""
        dictionary = self.read_dictionary()
        output = StringIO()
        writer = csv.writer(output)

        # Determine categories based on prefixes
        for english, xelthor in sorted(dictionary['vocabulary'].items()):
            category = "5"  # Default to connector
            if any(xelthor.startswith(p) for p in ["zz'", "ph'", "xa'", "vor'", "mii'"]):
                category = "1"  # Verb
            elif xelthor.startswith("xel'"):
                category = "2"  # Physical noun
            elif xelthor.startswith("vor'"):
                category = "3"  # Energy concept
            elif xelthor.startswith("mii'"):
                category = "4"  # Abstract concept

            writer.writerow([english, xelthor, category])

        return output.getvalue()

    def export_special_phrases_to_csv(self):
        """Export all special phrases to CSV format string."""
        dictionary = self.read_dictionary()
        output = StringIO()
        writer = csv.writer(output)

        for english, xelthor in sorted(dictionary['special_phrases'].items()):
            writer.writerow([english, xelthor])

        return output.getvalue()

    def ensure_backup_dir(self):
        """Create backup directory if it doesn't exist."""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)