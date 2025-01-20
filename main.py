"""Main application for the Xel'thor Translator."""
import os
from translator import XelthorTranslator

def clear_screen():
    """Clear the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the application header."""
    print("\n" + "="*40)
    print("        Xel'thor Translator")
    print("="*40)

def print_menu():
    """Display the main menu options."""
    print("\nChoose an option:")
    print("1. English to Xel'thor")
    print("2. Xel'thor to English")
    print("3. View vocabulary")
    print("4. View grammar rules")
    print("5. View special phrases")
    print("6. Add new word")
    print("7. Exit")
    print("-" * 40)

def get_word_category():
    """Get the category for a new word."""
    print("\nSelect word category:")
    print("1. Verb")
    print("2. Physical noun (xel-)")
    print("3. Energy concept (vor-)")
    print("4. Abstract concept (mii-)")
    print("5. Connector/Preposition")

    while True:
        choice = input("Enter category (1-5): ")
        if choice in ["1", "2", "3", "4", "5"]:
            return choice

def validate_xelthor_word(word, category):
    """Validate that the Xel'thor word follows naming conventions."""
    prefixes = {
        "1": ["zz'", "ph'", "xa'", "vor'", "mii'"],  # verbs
        "2": ["xel'"],  # physical nouns
        "3": ["vor'"],  # energy concepts
        "4": ["mii'"],  # abstract concepts
        "5": []         # connectors (no prefix required)
    }

    if category == "5":
        return len(word) <= 4  # connectors should be short

    valid_prefixes = prefixes[category]
    return any(word.startswith(prefix) for prefix in valid_prefixes)

def add_new_word(translator):
    """Add a new word to the dictionary."""
    print("\n=== Add New Word ===")

    # Get English word
    english = input("\nEnter English word: ").lower().strip()

    # Check if word already exists
    if english in translator.eng_to_xel:
        print(f"\nWord '{english}' already exists with translation: {translator.eng_to_xel[english]}")
        return

    # Get word category
    category = get_word_category()

    # Show prefix guidelines based on category
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

    # Get Xel'thor translation
    while True:
        xelthor = input("\nEnter Xel'thor translation: ").lower().strip()

        if validate_xelthor_word(xelthor, category):
            break
        else:
            print("Invalid format! Please follow the prefix guidelines.")

    # Add word to dictionary
    try:
        translator.add_new_word(english, xelthor, category)
        print(f"\nSuccessfully added: {english} = {xelthor}")
    except Exception as e:
        print(f"\nError adding word: {e}")

def print_grammar_rules():
    """Display the Xel'thor grammar rules."""
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
    print("\nExample: 'zz'rix-pa xel'thor vor'thal'")
    print("Means: 'The traveler traveled through space' (past tense)")

def print_special_phrases(translator):
    """Display special Xel'thor phrases and their meanings."""
    print("\nXel'thor Special Phrases:")
    print("-" * 40)
    for eng, xel in translator.special_phrases.items():
        print(f"{eng:20} = {xel}")

def display_vocabulary(translator):
    """Display the current vocabulary categorized by type."""
    print("\nCurrent Vocabulary:")
    print("-" * 40)

    categories = {
        "Verbs": lambda x: any(x.startswith(p) for p in ["zz'", "ph'", "xa'", "vor'", "mii'"]),
        "Physical Nouns (xel-)": lambda x: x.startswith("xel'"),
        "Energy Nouns (vor-)": lambda x: x.startswith("vor'") and len(x) > 4,
        "Abstract Nouns (mii-)": lambda x: x.startswith("mii'"),
        "Connectors": lambda x: len(x) <= 4
    }

    for category, condition in categories.items():
        print(f"\n{category}:")
        for eng, xel in sorted(translator.eng_to_xel.items()):
            if condition(xel):
                print(f"{eng:15} = {xel}")

def get_valid_choice(max_choice):
    """Get and validate user menu choice."""
    while True:
        choice = input(f"\nEnter your choice (1-{max_choice}): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= max_choice:
            return choice
        print(f"Invalid choice. Please enter a number between 1 and {max_choice}.")

def main():
    """Main application loop."""
    translator = XelthorTranslator()

    while True:
        clear_screen()
        print_header()
        print_menu()

        choice = get_valid_choice(7)

        if choice == "1":
            text = input("\nEnter English text: ")
            print("\nSelect tense:")
            print("1. Present")
            print("2. Past")
            print("3. Future")
            print("4. Eternal")
            tense_choice = input("Enter tense (1-4): ")

            tense_map = {"1": "present", "2": "past", "3": "future", "4": "eternal"}
            tense = tense_map.get(tense_choice, "present")

            result = translator.translate_to_xelthor(text, tense)
            print("\nXel'thor translation:")
            print(result)

        elif choice == "2":
            text = input("\nEnter Xel'thor text: ")
            result = translator.translate_to_english(text)
            print("\nEnglish translation:")
            print(result)

        elif choice == "3":
            display_vocabulary(translator)

        elif choice == "4":
            print_grammar_rules()

        elif choice == "5":
            print_special_phrases(translator)

        elif choice == "6":
            add_new_word(translator)

        elif choice == "7":
            print("\nFarewell, star wanderer!")
            break

        input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        clear_screen()
        print("\nProgram terminated by user. Farewell!")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")
        print("Please restart the application.")