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
    print("6. Exit")
    print("-" * 40)

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

def display_translation(original, translated, direction):
    """Display the translation results."""
    print(f"\n{direction} Translation")
    print("-" * 40)
    print(f"Original text: {original}")
    print(f"Translated text: {translated}")

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

def get_tense_choice():
    """Get the desired tense for translation."""
    print("\nSelect tense:")
    print("1. Present")
    print("2. Past")
    print("3. Future")
    print("4. Eternal")

    tense_map = {"1": "present", "2": "past", "3": "future", "4": "eternal"}
    choice = get_valid_choice(4)
    return tense_map.get(choice, "present")

def main():
    """Main application loop."""
    translator = XelthorTranslator()

    while True:
        clear_screen()
        print_header()
        print_menu()

        choice = get_valid_choice(6)

        if choice == '1':
            text = input("\nEnter English text to translate: ").strip()
            if text:
                tense = get_tense_choice()
                result = translator.translate_to_xelthor(text, tense)
                display_translation(text, result, "English to Xel'thor")

        elif choice == '2':
            text = input("\nEnter Xel'thor text to translate: ").strip()
            if text:
                result = translator.translate_to_english(text)
                display_translation(text, result, "Xel'thor to English")

        elif choice == '3':
            display_vocabulary(translator)

        elif choice == '4':
            print_grammar_rules()

        elif choice == '5':
            print_special_phrases(translator)

        elif choice == '6':
            print("\nFarewell, xel'thor! May the vor'kaan guide your path.")
            print("\n" + "="*40 + "\n")
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