"""Main application for the Xel'thor Translator."""
import os
import getpass
from translator import XelthorTranslator
from auth_manager import AuthManager
from dictionary_manager import DictionaryManager

def clear_screen():
    """Clear the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

class XelthorInterface:
    def __init__(self):
        self.translator = XelthorTranslator()
        self.auth_manager = AuthManager()
        self.dictionary_manager = DictionaryManager()
        self.current_user = None

    def login(self):
        """Handle user login."""
        print("\n=== Login ===")
        username = input("Username: ")
        password = getpass.getpass("Password: ")

        if self.auth_manager.verify_credentials(username, password):
            self.current_user = username
            return True
        return False

    def print_menu(self):
        """Display the main menu options."""
        clear_screen()
        print("\n=== Xel'thor Translator ===")
        print("1. English to Xel'thor")
        print("2. Xel'thor to English")
        print("3. View vocabulary")
        print("4. View grammar rules")
        print("5. View special phrases")
        print("6. Dictionary Management (Auth Required)")
        print("7. Backup Management (Auth Required)")
        print("8. Exit")
        print("========================")

    def require_auth(self, func):
        """Decorator to require authentication for certain functions."""
        def wrapper(*args, **kwargs):
            if self.current_user is None:
                print("\nAuthorization required. Please login first.")
                if not self.login():
                    print("Authentication failed.")
                    return
            return func(*args, **kwargs)
        return wrapper

    def handle_translation(self, direction='to_xelthor'):
        """Handle translation in either direction."""
        if direction == 'to_xelthor':
            text = input("\nEnter English text: ")
            print("\nSelect tense:")
            print("1. Present")
            print("2. Past")
            print("3. Future")
            print("4. Eternal")
            tense_choice = input("Enter tense (1-4): ")

            tense_map = {"1": "present", "2": "past", "3": "future", "4": "eternal"}
            tense = tense_map.get(tense_choice, "present")

            result = self.translator.translate_to_xelthor(text, tense)
        else:
            text = input("\nEnter Xel'thor text: ")
            result = self.translator.translate_to_english(text)

        print(f"\n{'English' if direction == 'from_xelthor' else 'Xel\'thor'} translation:")
        print(result)

    def view_vocabulary(self):
        """Display the current vocabulary."""
        print("\nCurrent vocabulary:")
        categories = {
            "Verbs": lambda x: any(x.startswith(p) for p in ["zz'", "ph'", "xa'", "vor'", "mii'"]),
            "Physical Nouns (xel-)": lambda x: x.startswith("xel'"),
            "Energy Nouns (vor-)": lambda x: x.startswith("vor'") and len(x) > 4,
            "Abstract Nouns (mii-)": lambda x: x.startswith("mii'"),
            "Connectors": lambda x: len(x) <= 4
        }

        for category, check_func in categories.items():
            print(f"\n{category}:")
            for eng, xel in sorted(self.translator.eng_to_xel.items()):
                if check_func(xel):
                    print(f"{eng:15} = {xel}")

    def handle_dictionary_management(self):
        """Handle dictionary management operations."""
        self.require_auth(lambda: None)()

        while True:
            print("\n=== Dictionary Management ===")
            print("1. Add new word")
            print("2. Edit existing word")
            print("3. Remove word")
            print("4. Add special phrase")
            print("5. Remove special phrase")
            print("6. Back to main menu")

            choice = input("\nEnter your choice (1-6): ")

            if choice == "1":
                self.add_new_word()
            elif choice == "6":
                break
            else:
                print("\nFeature coming soon!")

    def handle_backup_management(self):
        """Handle backup management operations."""
        self.require_auth(lambda: None)()

        while True:
            print("\n=== Backup Management ===")
            print("1. Create backup")
            print("2. List backups")
            print("3. Restore from backup")
            print("4. Back to main menu")

            choice = input("\nEnter your choice (1-4): ")

            if choice == "1":
                backup_file = self.dictionary_manager.create_backup()
                if backup_file:
                    print(f"\nBackup created: {backup_file}")
                else:
                    print("\nFailed to create backup.")
            elif choice == "2":
                backups = self.dictionary_manager.list_backups()
                if backups:
                    print("\nAvailable backups:")
                    for i, backup in enumerate(backups, 1):
                        print(f"{i}. {backup}")
                else:
                    print("\nNo backups available.")
            elif choice == "3":
                backups = self.dictionary_manager.list_backups()
                if not backups:
                    print("\nNo backups available.")
                    continue

                print("\nAvailable backups:")
                for i, backup in enumerate(backups, 1):
                    print(f"{i}. {backup}")

                try:
                    idx = int(input("\nEnter backup number to restore: ")) - 1
                    if 0 <= idx < len(backups):
                        backup_file = os.path.join(self.dictionary_manager.backup_dir, backups[idx])
                        if self.dictionary_manager.restore_backup(backup_file):
                            self.translator.reload_dictionary()
                            print("\nBackup restored successfully.")
                        else:
                            print("\nFailed to restore backup.")
                    else:
                        print("\nInvalid backup number.")
                except ValueError:
                    print("\nInvalid input.")
            elif choice == "4":
                break

    def add_new_word(self):
        """Add a new word to the dictionary."""
        print("\n=== Add New Word ===")

        english = input("\nEnter English word: ").lower().strip()
        if english in self.translator.eng_to_xel:
            print(f"\nWord '{english}' already exists with translation: {self.translator.eng_to_xel[english]}")
            return

        print("\nSelect word category:")
        print("1. Verb")
        print("2. Physical noun (xel-)")
        print("3. Energy concept (vor-)")
        print("4. Abstract concept (mii-)")
        print("5. Connector/Preposition")

        category = input("Enter category (1-5): ")
        if category not in ["1", "2", "3", "4", "5"]:
            print("\nInvalid category.")
            return

        prefix_map = {
            "1": ["zz'", "ph'", "xa'", "vor'", "mii'"],
            "2": ["xel'"],
            "3": ["vor'"],
            "4": ["mii'"],
            "5": []
        }

        print("\nPrefix guidelines:")
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

        while True:
            xelthor = input("\nEnter Xel'thor translation: ").lower().strip()

            if category == "5":
                if len(xelthor) <= 4:
                    break
            else:
                if any(xelthor.startswith(prefix) for prefix in prefix_map[category]):
                    break
            print("Invalid format! Please follow the prefix guidelines.")

        if self.translator.add_new_word(english, xelthor, category):
            print(f"\nSuccessfully added: {english} = {xelthor}")
        else:
            print("\nFailed to add word. Please try again.")

    def run(self):
        """Main application loop."""
        while True:
            try:
                self.print_menu()
                choice = input("\nEnter your choice (1-8): ")

                if choice == "1":
                    self.handle_translation('to_xelthor')
                elif choice == "2":
                    self.handle_translation('from_xelthor')
                elif choice == "3":
                    self.view_vocabulary()
                elif choice == "4":
                    print("\nXel'thor Grammar Rules:")
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
                elif choice == "5":
                    print("\nXel'thor Special Phrases:")
                    for eng, xel in self.translator.special_phrases.items():
                        print(f"{eng:20} = {xel}")
                elif choice == "6":
                    self.handle_dictionary_management()
                elif choice == "7":
                    self.handle_backup_management()
                elif choice == "8":
                    print("\nFarewell, star wanderer!")
                    break
                else:
                    print("\nInvalid choice. Please try again.")

                input("\nPress Enter to continue...")

            except KeyboardInterrupt:
                print("\nProgram terminated by user. Farewell!")
                break
            except Exception as e:
                print(f"\nAn error occurred: {str(e)}")
                input("\nPress Enter to continue...")

if __name__ == "__main__":
    interface = XelthorInterface()
    interface.run()