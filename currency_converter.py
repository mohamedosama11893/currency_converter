"""
Currency Converter Tool
===========================

This program allows users to convert between currencies using the Fixer API (Apilayer).
It provides the following features:
- Fetches live currency symbols from the API.
- Lets the user search currencies by code or name (or display all).
- Ensures user selects valid currency codes from displayed results.
- Handles input validation for currency codes and amounts.
- Performs live currency conversion using the API.
- Includes error handling for network/API issues.

Requirements:
- requests library
- A valid API key from https://apilayer.com

"""

import requests

API_KEY = "Put_Your_Api_Key_Here"
BASE_URL = "https://api.apilayer.com/fixer"



#======================================================================================================#
#==================================== Main program flow================================================#
#======================================================================================================#
def main():
    """
    Main program flow:
    - Fetch symbols
    - Display/search currencies
    - Prompt user to select from-currency and to-currency
    - Ask for amount
    - Convert and display result
    """
    symbols = get_symbols()
    if not symbols:
        return

    print("\n=== Currency Converter ===")
    # Step 1: Search or view all currencies
    displayed = search_symbols(symbols)

    # Step 2: Choose FROM currency
    if displayed is not symbols:
        use_displayed = input("Pick from the displayed results only? (y/n): ").strip().lower()
        if use_displayed == "y":
            from_currency = choose_currency_from(displayed, "\nEnter the currency you want to convert from (e.g. USD): ")
        else:
            print("\nShowing all currencies now:\n" + "-" * 30)
            for code, name in symbols.items():
                print(f"{code} : {name}")
            from_currency = choose_currency_from(symbols, "\nEnter the currency you want to convert from (e.g. USD): ")
    else:
        from_currency = choose_currency_from(symbols, "\nEnter the currency you want to convert from (e.g. USD): ")

    # Step 3: Choose TO currency (search again if needed)
    print("\nYou selected:", from_currency)
    print("\nNow choose the currency to convert TO.")
    displayed2 = search_symbols(symbols)
    if displayed2 is not symbols:
        use_displayed2 = input("Pick from the displayed results only? (y/n): ").strip().lower()
        if use_displayed2 == "y":
            to_currency = choose_currency_from(displayed2, "Enter the currency you want to convert to (e.g. EGP): ")
        else:
            print("\nShowing all currencies now:\n" + "-" * 30)
            for code, name in symbols.items():
                print(f"{code} : {name}")
            to_currency = choose_currency_from(symbols, "Enter the currency you want to convert to (e.g. EGP): ")
    else:
        to_currency = choose_currency_from(symbols, "Enter the currency you want to convert to (e.g. EGP): ")

    # Step 4: Amount and conversion
    amount = get_amount()
    result = convert_currency(from_currency, to_currency, amount)
    if result is not None:
        print(f"\n✅ {amount:,.2f} {from_currency} = {result:,.2f} {to_currency}")


if __name__ == "__main__":
    """
    Entry point of the script.
    Runs the converter in a loop until the user decides to exit.
    """
    while True:
        main()
        again = input("\nDo you want to convert another amount? (y/n): ").strip().lower()
        if again != "y":
            print("Goodbye 👋")
            break

