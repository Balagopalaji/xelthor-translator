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

            prefix_map = {
                "1": ["zz'", "ph'", "xa'", "vor'", "mii'"],  # Verbs
                "2": ["xel'"],  # Physical nouns
                "3": ["vor'"],  # Energy concepts
                "4": ["mii'"],  # Abstract concepts
                "5": []  # Connectors
            }

            for row_num, row in enumerate(reader, 1):
                try:
                    if len(row) != 3:
                        errors.append(f"Row {row_num}: Invalid format. Expected 3 columns (english,xelthor,category)")
                        continue

                    english, xelthor, category = [x.strip().lower() for x in row]

                    if not category.isdigit() or category not in prefix_map:
                        errors.append(f"Row {row_num}: Invalid category '{category}'. Must be 1-5")
                        continue

                    if english in dictionary['vocabulary']:
                        errors.append(f"Row {row_num}: Word '{english}' already exists")
                        continue

                    # Validate prefix based on category
                    if category == "5":  # Connectors
                        if len(xelthor) > 4:
                            errors.append(f"Row {row_num}: Connector '{xelthor}' too long (max 4 characters)")
                            continue
                    else:
                        if not any(xelthor.startswith(prefix) for prefix in prefix_map[category]):
                            expected_prefixes = ", ".join(prefix_map[category])
                            errors.append(f"Row {row_num}: Word '{xelthor}' must start with {expected_prefixes}")
                            continue

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