"""Main application for the Xel'thor Translator."""
import os
import getpass
import shutil
from translator import XelthorTranslator
from auth_manager import AuthManager
from dictionary_manager import DictionaryManager
import time

def clear_screen():
    """Clear the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')
    # Add a small delay to ensure the screen is cleared
    time.sleep(0.1)

def get_terminal_size():
    """Get the terminal size or default to 80x24."""
    try:
        columns, _ = shutil.get_terminal_size()
        return max(60, min(columns, 100))  # Keep width between 60 and 100
    except:
        return 80

def pause_and_continue():
    """Wait for user input before continuing."""
    input("\nPress Enter to continue...")
    time.sleep(0.1)  # Ensure input buffer is cleared

class XelthorInterface:
    def __init__(self):
        self.translator = XelthorTranslator()
        self.auth_manager = AuthManager()
        self.dictionary_manager = DictionaryManager()
        self.current_user = None
        self.screen_width = get_terminal_size()
        self.status_message = ""

    def set_status(self, message):
        """Set a status message to display at the bottom of the screen."""
        self.status_message = message
        time.sleep(0.1)  # Small delay to ensure status is displayed

    def display_header(self, title):
        """Display a formatted header."""
        clear_screen()
        print("\n" + "="*self.screen_width)
        print(f"{title:^{self.screen_width}}")
        print("="*self.screen_width + "\n")

    def display_footer(self):
        """Display the status bar and navigation hints."""
        print("\n" + "-"*self.screen_width)
        if self.status_message:
            print(f"Status: {self.status_message}")
        if self.current_user:
            print(f"Logged in as: {self.current_user}")
        print("Navigation: [Enter] Continue | [0] Back/Exit | [Numbers] Select Option")
        print("-"*self.screen_width)

    def get_user_input(self, prompt):
        """Get user input with proper buffer handling."""
        print(prompt, end='', flush=True)
        try:
            return input().strip()
        except EOFError:
            return ''
        finally:
            time.sleep(0.1)  # Ensure input buffer is cleared

    def paginate_list(self, items, page_size=10):
        """Display a paginated list of items."""
        total_pages = (len(items) + page_size - 1) // page_size
        current_page = 1

        while True:
            start_idx = (current_page - 1) * page_size
            end_idx = min(start_idx + page_size, len(items))

            self.display_header(f"Page {current_page} of {total_pages}")

            # Display items with proper formatting
            for idx, item in enumerate(items[start_idx:end_idx], start=start_idx + 1):
                if isinstance(item, tuple):
                    eng, xel = item
                    print(f"{idx:3d}. {eng:20} = {xel}")
                else:
                    print(f"{idx:3d}. {item}")

            print("\nNavigation:")
            print("1-9 - Jump to item")
            print("n   - Next page")
            print("p   - Previous page")
            print("0   - Return to menu")

            self.display_footer()

            choice = self.get_user_input("\nEnter choice: ").lower()
            if choice in ['n', 'next'] and current_page < total_pages:
                current_page += 1
            elif choice in ['p', 'prev', 'previous'] and current_page > 1:
                current_page -= 1
            elif choice == '0':
                break
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(items):
                    # Handle item selection if needed
                    pass

    def login(self):
        """Handle user login."""
        self.display_header("Login")
        username = self.get_user_input("Username: ")
        if username.lower() == 'cancel':
            return False
        password = getpass.getpass("Password: ")

        if self.auth_manager.verify_credentials(username, password):
            self.current_user = username
            self.set_status(f"Logged in as {username}")
            return True

        self.set_status("Authentication failed")
        print("\nInvalid username or password.")
        pause_and_continue()
        return False

    def logout(self):
        """Handle user logout."""
        if self.current_user:
            self.current_user = None
            self.set_status("Logged out successfully")
            print("\nYou have been logged out.")
            pause_and_continue()

    @staticmethod
    def require_auth(func):
        """Decorator to require authentication for certain functions."""
        from functools import wraps

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            attempts = 3
            while attempts > 0 and self.current_user is None:
                self.display_header("Authorization Required")
                print("This feature requires authentication.")
                print(f"You have {attempts} login attempts remaining.")
                print("\nEnter 'cancel' as username to go back to main menu.")

                if not self.login():
                    attempts -= 1
                    if attempts > 0:
                        print(f"\nAuthentication failed. {attempts} attempts remaining.")
                    else:
                        print("\nToo many failed attempts. Access denied.")
                        pause_and_continue()
                        return None
                    continue
                break

            if self.current_user is None:
                return None

            return func(self, *args, **kwargs)
        return wrapper

    @require_auth
    def handle_dictionary_management(self):
        """Handle dictionary management operations."""
        while True:
            self.display_header("Dictionary Management")
            menu_items = [
                "Add new word",
                "Edit existing word",
                "Remove word",
                "Add special phrase",
                "Remove special phrase",
                "Batch import/edit words",
                "Batch import/edit special phrases",
                "Back to main menu"
            ]
            for idx, item in enumerate(menu_items, 1):
                print(f"{idx}. {item}")
            print("\n" + "="*self.screen_width)

            choice = self.get_user_input("\nEnter your choice (1-8): ")

            if choice == "1":
                self.add_new_word()
            elif choice == "2":
                self.edit_word()
            elif choice == "3":
                self.remove_word()
            elif choice == "4":
                self.add_special_phrase()
            elif choice == "5":
                self.remove_special_phrase()
            elif choice == "6":
                self.batch_manage_words()
            elif choice == "7":
                self.batch_manage_special_phrases()
            elif choice == "8":
                break
            else:
                print("\nInvalid choice. Please try again.")
                self.display_footer()
                pause_and_continue()

    def batch_manage_words(self):
        """Handle batch import/export of words."""
        while True:
            self.display_header("Batch Word Management")
            print("1. Import words from CSV")
            print("2. Export current words to CSV")
            print("3. Back to dictionary management")
            print("\nCSV Format for import: english,xelthor,category")
            print("\nCategories:")
            print("1 = Verbs (must start with: zz', ph', xa', vor', or mii')")
            print("2 = Physical nouns (must start with: xel')")
            print("3 = Energy concepts (must start with: vor')")
            print("4 = Abstract concepts (must start with: mii')")
            print("5 = Connectors (max 4 characters, no prefix required)")
            print("\nExamples:")
            print("dance,zz'phi,1          # Verb")
            print("star,xel'nova,2         # Physical noun")
            print("energy,vor'shiba,3      # Energy concept")
            print("freedom,mii'lindzz'je,4 # Abstract concept")
            print("and,je,5                # Connector")
            print("\n" + "="*self.screen_width)

            choice = self.get_user_input("\nEnter your choice (1-3): ")

            if choice == "1":
                self.display_header("Import Words")
                print("Enter CSV data (one word per line, empty line to finish):")
                print("Format: english,xelthor,category")
                print("\nCategories and prefix requirements:")
                print("1. Verbs: Must start with zz', ph', xa', vor', or mii'")
                print("2. Physical nouns: Must start with xel'")
                print("3. Energy concepts: Must start with vor'")
                print("4. Abstract concepts: Must start with mii'")
                print("5. Connectors: Max 4 characters, no prefix required")
                print("\nExamples:")
                print("dance,zz'phi,1")
                print("star,xel'nova,2")
                print("energy,vor'shiba,3")
                print("freedom,mii'lindzz'je,4")
                print("and,je,5")
                print("\n" + "="*self.screen_width + "\n")

                lines = []
                while True:
                    line = self.get_user_input("")
                    if not line:
                        break
                    lines.append(line)

                if lines:
                    csv_content = "\n".join(lines)
                    success_count, errors = self.dictionary_manager.batch_add_words(csv_content)

                    self.display_header("Import Results")
                    print(f"Successfully added {success_count} words")
                    if errors:
                        print("\nErrors:")
                        for error in errors:
                            print(f"- {error}")

                    if success_count > 0:
                        self.translator.reload_dictionary()

                pause_and_continue()

            elif choice == "2":
                self.display_header("Export Words")
                csv_content = self.dictionary_manager.export_words_to_csv()
                print("Current words in CSV format:")
                print("\n" + "="*self.screen_width + "\n")
                print(csv_content)
                pause_and_continue()

            elif choice == "3":
                break

    def batch_manage_special_phrases(self):
        """Handle batch import/export of special phrases."""
        while True:
            self.display_header("Batch Special Phrase Management")
            print("1. Import special phrases from CSV")
            print("2. Export current special phrases to CSV")
            print("3. Back to dictionary management")
            print("\nCSV Format for import: english,xelthor")
            print("\n" + "="*self.screen_width)

            choice = self.get_user_input("\nEnter your choice (1-3): ")

            if choice == "1":
                self.display_header("Import Special Phrases")
                print("Enter CSV data (one phrase per line, empty line to finish):")
                print("Format: english,xelthor")
                print("Example: may the force be with you,vor'thala mii'keth")
                print("\n" + "="*self.screen_width + "\n")

                lines = []
                while True:
                    line = self.get_user_input("")
                    if not line:
                        break
                    lines.append(line)

                if lines:
                    csv_content = "\n".join(lines)
                    success_count, errors = self.dictionary_manager.batch_add_special_phrases(csv_content)

                    self.display_header("Import Results")
                    print(f"Successfully added {success_count} special phrases")
                    if errors:
                        print("\nErrors:")
                        for error in errors:
                            print(f"- {error}")

                    if success_count > 0:
                        self.translator.reload_dictionary()

                pause_and_continue()

            elif choice == "2":
                self.display_header("Export Special Phrases")
                csv_content = self.dictionary_manager.export_special_phrases_to_csv()
                print("Current special phrases in CSV format:")
                print("\n" + "="*self.screen_width + "\n")
                print(csv_content)
                pause_and_continue()

            elif choice == "3":
                break

    @require_auth
    def handle_backup_management(self):
        """Handle backup management operations."""
        while True:
            self.display_header("Backup Management")
            menu_items = [
                "Create backup",
                "List backups",
                "Restore from backup",
                "Back to main menu"
            ]
            for idx, item in enumerate(menu_items, 1):
                print(f"{idx}. {item}")
            print("\n" + "="*self.screen_width)

            choice = self.get_user_input("\nEnter your choice (1-4): ")

            if choice == "1":
                self.set_status("Creating backup...")
                backup_file = self.dictionary_manager.create_backup()
                if backup_file:
                    self.set_status("Backup created successfully")
                    print(f"\nBackup created: {backup_file}")
                else:
                    self.set_status("Failed to create backup")
                    print("\nFailed to create backup.")
            elif choice == "2":
                backups = self.dictionary_manager.list_backups()
                if backups:
                    self.paginate_list(backups)
                else:
                    print("\nNo backups available.")
            elif choice == "3":
                self.handle_backup_restore()
            elif choice == "4":
                break

            self.display_footer()
            pause_and_continue()

    def print_menu(self):
        """Display the main menu options."""
        self.display_header("Xel'thor Translator")
        menu_items = [
            "English to Xel'thor",
            "Xel'thor to English",
            "View vocabulary",
            "View grammar rules",
            "View special phrases",
            "Dictionary Management (Auth Required)",
            "Backup Management (Auth Required)",
            "Logout",
            "Exit"
        ]
        for idx, item in enumerate(menu_items, 1):
            print(f"{idx:2d}. {item}")

        self.display_footer()

    def handle_translation(self, direction='to_xelthor'):
        """Handle translation in either direction."""
        self.display_header("Translation")
        if direction == 'to_xelthor':
            text = self.get_user_input("Enter English text: ")
            print("\nSelect tense:")
            print("1. Present")
            print("2. Past")
            print("3. Future")
            print("4. Eternal")
            tense_choice = self.get_user_input("\nEnter tense (1-4): ")

            tense_map = {"1": "present", "2": "past", "3": "future", "4": "eternal"}
            tense = tense_map.get(tense_choice, "present")

            self.display_header("Translation Result")
            self.set_status("Translating...") #Simulate loading
            time.sleep(1) #Simulate a delay
            result = self.translator.translate_to_xelthor(text, tense)
            self.set_status("") #Clear loading message
            print("Xel'thor translation:")
        else:
            text = self.get_user_input("Enter Xel'thor text: ")
            self.display_header("Translation Result")
            self.set_status("Translating...") #Simulate loading
            time.sleep(1) #Simulate a delay
            result = self.translator.translate_to_english(text)
            self.set_status("") #Clear loading message
            print("English translation:")

        print("-" * self.screen_width)
        print(result)
        print("-" * self.screen_width)
        self.display_footer()
        pause_and_continue()

    def view_vocabulary(self):
        """Display the current vocabulary."""
        categories = {
            "Verbs": lambda x: any(x.startswith(p) for p in ["zz'", "ph'", "xa'", "vor'", "mii'"]),
            "Physical Nouns (xel-)": lambda x: x.startswith("xel'"),
            "Energy Nouns (vor-)": lambda x: x.startswith("vor'") and len(x) > 4,
            "Abstract Nouns (mii-)": lambda x: x.startswith("mii'"),
            "Connectors": lambda x: len(x) <= 4
        }

        for category, check_func in categories.items():
            self.display_header(f"Vocabulary - {category}")
            words = [(eng, xel) for eng, xel in sorted(self.translator.eng_to_xel.items()) 
                    if check_func(xel)]

            if words:
                self.paginate_list(words)
            else:
                print("(No words in this category)")

            self.display_footer()
            pause_and_continue()

    def handle_backup_restore(self):
        """Handle the backup restoration process."""
        backups = self.dictionary_manager.list_backups()
        if not backups:
            print("\nNo backups available.")
            return

        self.display_header("Restore Backup")
        print("Available backups:")
        for i, backup in enumerate(backups, 1):
            print(f"{i}. {backup}")
        print("\n" + "="*self.screen_width)

        try:
            idx = int(self.get_user_input("\nEnter backup number to restore (or 0 to cancel): ")) - 1
            if idx == -1:
                return
            if 0 <= idx < len(backups):
                backup_file = os.path.join(self.dictionary_manager.backup_dir, backups[idx])
                self.set_status("Restoring backup...")
                if self.dictionary_manager.restore_backup(backup_file):
                    self.translator.reload_dictionary()
                    self.set_status("Backup restored successfully")
                    print("\nBackup restored successfully.")
                else:
                    self.set_status("Failed to restore backup")
                    print("\nFailed to restore backup.")
            else:
                print("\nInvalid backup number.")
        except ValueError:
            print("\nInvalid input.")
        self.display_footer()
        pause_and_continue()

    def add_new_word(self):
        """Add a new word to the dictionary."""
        self.display_header("Add New Word")

        english = self.get_user_input("Enter English word (or 'cancel' to abort): ").lower().strip()
        if english == 'cancel':
            return

        if english in self.translator.eng_to_xel:
            print(f"\nWord '{english}' already exists with translation: {self.translator.eng_to_xel[english]}")
            self.display_footer()
            pause_and_continue()
            return

        self.display_header("Word Category")
        categories = [
            "Verb",
            "Physical noun (xel-)",
            "Energy concept (vor-)",
            "Abstract concept (mii-)",
            "Connector/Preposition"
        ]
        for idx, category in enumerate(categories, 1):
            print(f"{idx}. {category}")
        print("\n" + "="*self.screen_width)

        category = self.get_user_input("\nEnter category (1-5 or 'cancel'): ")
        if category == 'cancel':
            return

        if category not in ["1", "2", "3", "4", "5"]:
            print("\nInvalid category.")
            self.display_footer()
            pause_and_continue()
            return

        self.display_header("Xel'thor Translation")
        prefix_map = {
            "1": ["zz'", "ph'", "xa'", "vor'", "mii'"],
            "2": ["xel'"],
            "3": ["vor'"],
            "4": ["mii'"],
            "5": []
        }

        print("Prefix guidelines:")
        if category == "1":
            print("Verbs should start with: zz', ph', xa', vor', or mii'")
        elif category == "2":
            print("Physical nouns should start with: xel'")
        elif category == "3":
            print("Energy concepts should start with: vor'")
        elif category == "4":
            print("Abstract concepts should start with: mii'")
        else:
            print("Connectors should be short (1-4 characters)")
        print("\n" + "="*self.screen_width)

        while True:
            xelthor = self.get_user_input("\nEnter Xel'thor translation (or 'cancel' to abort): ").lower().strip()

            if xelthor == 'cancel':
                return

            if category == "5":
                if len(xelthor) <= 4:
                    break
            else:
                if any(xelthor.startswith(prefix) for prefix in prefix_map[category]):
                    break
            print("\nInvalid format! Please follow the prefix guidelines.")

        self.display_header("Result")
        self.set_status("Adding new word...")
        if self.translator.add_new_word(english, xelthor, category):
            self.set_status("Word added successfully")
            print(f"Successfully added: {english} = {xelthor}")
        else:
            self.set_status("Failed to add word")
            print("Failed to add word. Please try again.")
        self.display_footer()
        pause_and_continue()

    def edit_word(self):
        """Edit an existing word in the dictionary."""
        self.display_header("Edit Word")

        # Display current vocabulary for reference
        print("Current vocabulary:")
        words = sorted(self.translator.eng_to_xel.items())
        for idx, (eng, xel) in enumerate(words, 1):
            print(f"{idx:3d}. {eng:20} = {xel}")

        print("\n" + "="*self.screen_width)
        english = self.get_user_input("\nEnter English word to edit (or 'cancel' to abort): ").lower().strip()

        if english == 'cancel':
            return

        if english not in self.translator.eng_to_xel:
            print(f"\nWord '{english}' not found in dictionary.")
            self.display_footer()
            pause_and_continue()
            return

        current_xelthor = self.translator.eng_to_xel[english]
        print(f"\nCurrent translation: {current_xelthor}")

        new_xelthor = self.get_user_input("\nEnter new Xel'thor translation (or 'cancel' to abort): ").lower().strip()
        if new_xelthor == 'cancel':
            return

        self.set_status("Updating word...")
        if self.dictionary_manager.edit_word(english, new_xelthor):
            self.translator.reload_dictionary()
            self.set_status("Word updated successfully")
            print(f"\nSuccessfully updated: {english} = {new_xelthor}")
        else:
            self.set_status("Failed to update word")
            print("\nFailed to update word. Please try again.")

        self.display_footer()
        pause_and_continue()

    def get_similar_word(self, word, words, threshold=0.6):
        """Find a similar word in the dictionary using string similarity."""
        def levenshtein_distance(s1, s2):
            if len(s1) < len(s2):
                return levenshtein_distance(s2, s1)
            if len(s2) == 0:
                return len(s1)
            previous_row = range(len(s2) + 1)
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            return previous_row[-1]

        def similarity(s1, s2):
            distance = levenshtein_distance(s1, s2)
            max_len = max(len(s1), len(s2))
            return 1 - (distance / max_len)

        best_match = None
        best_similarity = 0

        for candidate in words:
            sim = similarity(word, candidate)
            if sim > threshold and sim > best_similarity:
                best_similarity = sim
                best_match = candidate

        return best_match

    def remove_word(self):
        """Remove a word from the dictionary."""
        while True:
            self.display_header("Remove Word")

            # Display current vocabulary for reference
            print("Current vocabulary:")
            words = sorted(self.translator.eng_to_xel.items())
            for idx, (eng, xel) in enumerate(words, 1):
                print(f"{idx:3d}. {eng:20} = {xel}")

            print("\n" + "="*self.screen_width)
            english = self.get_user_input("\nEnter English word to remove (or '0' to go back): ").lower().strip()

            if english == '0':
                return

            if english not in self.translator.eng_to_xel:
                similar_word = self.get_similar_word(english, self.translator.eng_to_xel.keys())
                if similar_word:
                    print(f"\nWord '{english}' not found. Did you mean '{similar_word}'?")
                    choice = self.get_user_input("Enter 'y' to remove this word, or any other key to try again: ").lower()
                    if choice == 'y':
                        english = similar_word
                    else:
                        self.display_footer()
                        pause_and_continue()
                        continue
                else:
                    self.set_status("Word not found")
                    print(f"\nWord '{english}' not found in dictionary.")
                    self.display_footer()
                    pause_and_continue()
                    continue

            confirm = self.get_user_input(f"\nAre you sure you want to remove '{english}' = '{self.translator.eng_to_xel[english]}'? (yes/no): ").lower()
            if confirm != 'yes':
                self.set_status("Operation cancelled")
                print("\nOperation cancelled.")
                self.display_footer()
                pause_and_continue()
                continue

            self.set_status("Removing word...")
            if self.dictionary_manager.remove_word(english):
                self.translator.reload_dictionary()
                self.set_status("Word removed successfully")
                print(f"\nSuccessfully removed: {english}")
            else:
                self.set_status("Failed to remove word")
                print("\nFailed to remove word. Please try again.")

            self.display_footer()
            choice = self.get_user_input("\nPress Enter to remove another word, or '0' to go back: ")
            if choice == '0':
                break

    def add_special_phrase(self):
        """Add a new special phrase to the dictionary."""
        self.display_header("Add Special Phrase")

        english = self.get_user_input("Enter English phrase (or 'cancel' to abort): ").lower().strip()
        if english == 'cancel':
            return

        if english in self.translator.special_phrases:
            print(f"\nPhrase '{english}' already exists with translation: {self.translator.special_phrases[english]}")
            self.display_footer()
            pause_and_continue()
            return

        xelthor = self.get_user_input("\nEnter Xel'thor translation (or 'cancel' to abort): ").strip()
        if xelthor == 'cancel':
            return

        self.set_status("Adding special phrase...")
        if self.dictionary_manager.add_special_phrase(english, xelthor):
            self.translator.reload_dictionary()
            self.set_status("Special phrase added successfully")
            print(f"\nSuccessfully added special phrase: {english} = {xelthor}")
        else:
            self.set_status("Failed to add special phrase")
            print("\nFailed to add special phrase. Please try again.")

        self.display_footer()
        pause_and_continue()

    def remove_special_phrase(self):
        """Remove a special phrase from the dictionary."""
        self.display_header("Remove Special Phrase")

        # Display current special phrases for reference
        print("Current special phrases:")
        phrases = sorted(self.translator.special_phrases.items())
        for idx, (eng, xel) in enumerate(phrases, 1):
            print(f"{idx:3d}. {eng:20} = {xel}")

        if not phrases:
            print("\nNo special phrases found in dictionary.")
            self.display_footer()
            pause_and_continue()
            return

        print("\n" + "="*self.screen_width)
        english = self.get_user_input("\nEnter English phrase to remove (or 'cancel' to abort): ").lower().strip()

        if english == 'cancel':
            return

        if english not in self.translator.special_phrases:
            print(f"\nPhrase '{english}' not found in dictionary.")
            self.display_footer()
            pause_and_continue()
            return

        confirm = self.get_user_input(f"\nAre you sure you want to remove '{english}' = '{self.translator.special_phrases[english]}'? (yes/no): ").lower()
        if confirm != 'yes':
            print("\nOperation cancelled.")
            self.display_footer()
            pause_and_continue()
            return

        self.set_status("Removing special phrase...")
        if self.dictionary_manager.remove_special_phrase(english):
            self.translator.reload_dictionary()
            self.set_status("Special phrase removed successfully")
            print(f"\nSuccessfully removed: {english}")
        else:
            self.set_status("Failed to remove special phrase")
            print("\nFailed to remove special phrase. Please try again.")

        self.display_footer()
        pause_and_continue()

    def run(self):
        """Main application loop."""
        while True:
            try:
                self.print_menu()
                choice = self.get_user_input("\nEnter your choice (1-9 or 0 to exit): ")

                if choice == "0":
                    self.display_header("Farewell")
                    print("Farewell, star wanderer!")
                    break
                elif choice == "1":
                    self.handle_translation('to_xelthor')
                elif choice == "2":
                    self.handle_translation('from_xelthor')
                elif choice == "3":
                    self.view_vocabulary()
                elif choice == "4":
                    self.display_header("Grammar Rules")
                    print("1. Sentence Structure: Verb-Object-Subject (VOS)")
                    print("2. Prefixes:")
                    print("   - xel- : physical objects")
                    print("   - vor- : energy concepts")
                    print("   - mii- : abstract concepts")
                    print("3. Tense Markers:")
                    print("   - Present: no marker")
                    print("   - Past: -pa (descending tone)")
                    print("   - Future: -zi (ascending tone)")
                    print("   - Eternal: -th (harmonic tone)")
                    pause_and_continue()
                elif choice == "5":
                    self.display_header("Special Phrases")
                    phrases = self.translator.special_phrases
                    if phrases:
                        for eng, xel in phrases.items():
                            print(f"{eng:20} = {xel}")
                    else:
                        print("No special phrases defined yet.")
                    pause_and_continue()
                elif choice == "6":
                    self.handle_dictionary_management()
                elif choice == "7":
                    self.handle_backup_management()
                elif choice == "8":
                    if self.current_user:
                        self.logout()
                    else:
                        self.login()
                elif choice == "9":
                    self.display_header("Farewell")
                    print("Farewell, star wanderer!")
                    break
                else:
                    print("\nInvalid choice. Please enter a number between 1 and 9.")
                    pause_and_continue()

            except KeyboardInterrupt:
                self.display_header("Exit")
                print("Program terminated. Farewell!")
                break
            except Exception as e:
                print(f"\nAn error occurred: {str(e)}")
                pause_and_continue()
                if self.get_user_input("Enter 0 to exit or any key to continue: ") == "0":
                    break

if __name__ == "__main__":
    interface = XelthorInterface()
    interface.run()