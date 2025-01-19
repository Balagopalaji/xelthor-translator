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
    print("\nAvailable Options:")
    print("1. English to Xel'thor Translation")
    print("2. Xel'thor to English Translation")
    print("3. View Vocabulary")
    print("4. Exit")
    print("\n" + "-"*40)

def display_translation(original, translated, direction):
    """Display the translation results."""
    clear_screen()
    print_header()
    print(f"\n{direction} Translation")
    print("-" * 40)
    print(f"Original text: {original}")
    print(f"Translated text: {translated}")

def display_vocabulary(translator):
    """Display the current vocabulary."""
    clear_screen()
    print_header()
    print("\nCurrent Vocabulary:")
    print("-" * 40)
    
    vocabulary = translator.get_vocabulary()
    max_eng_length = max(len(eng) for eng, _ in vocabulary)
    
    for eng, xel in vocabulary:
        print(f"{eng:<{max_eng_length}} = {xel}")

def get_valid_choice():
    """Get and validate user menu choice."""
    while True:
        choice = input("\nEnter your choice (1-4): ").strip()
        if choice in ['1', '2', '3', '4']:
            return choice
        print("Invalid choice. Please enter a number between 1 and 4.")

def main():
    """Main application loop."""
    translator = XelthorTranslator()
    
    while True:
        clear_screen()
        print_header()
        print_menu()
        
        choice = get_valid_choice()
        
        if choice == '1':
            text = input("\nEnter English text to translate: ").strip()
            if text:
                result = translator.translate_to_xelthor(text)
                display_translation(text, result, "English to Xel'thor")
            
        elif choice == '2':
            text = input("\nEnter Xel'thor text to translate: ").strip()
            if text:
                result = translator.translate_to_english(text)
                display_translation(text, result, "Xel'thor to English")
            
        elif choice == '3':
            display_vocabulary(translator)
            
        elif choice == '4':
            clear_screen()
            print_header()
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
