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
#===================================== Helper Functions =================================================#
#======================================================================================================#
def handle_error(response):
    """
    Handle API error responses with detailed messages.

    Args:
        response (requests.Response): The HTTP response object from the API.
    """
    code = response.status_code
    if code == 401:
        print("❌ Unauthorized: Check your API key.")
    elif code == 403:
        print("❌ Forbidden: You don't have access to this service.")
    elif code == 404:
        print("❌ Not Found: The requested resource does not exist.")
    elif code == 429:
        print("❌ Too Many Requests: You exceeded the API request limit.")
    elif code >= 500:
        print("❌ Server Error: Try again later.")
    else:
        print("❌ Unexpected Error:", code)
        print("Response:", response.text)

#======================================================================================================#
def get_symbols():
    """
    Fetch available currency symbols from the API.

    Returns:
        dict: A dictionary where keys are currency codes (e.g., "USD")
              and values are currency names (e.g., "United States Dollar").
              Returns {} if request fails.
    """
    url = f"{BASE_URL}/symbols"
    headers = {"apikey": API_KEY}
    try:
        response = requests.get(url, headers=headers)
    except requests.exceptions.RequestException as e:
        print("❌ Network error while fetching symbols:", e)
        return {}

    if response.status_code != 200:
        handle_error(response)
        return {}

    data = response.json()
    # Some APIs might omit the "success" field, so we check safely
    if not data.get("success", True):
        print("❌ API Error:", data.get("error", data))
        return {}

    return data.get("symbols", {})

#======================================================================================================#
def search_symbols(symbols):
    """
    Let the user search currencies or view all.

    Args:
        symbols (dict): Dictionary of all currency codes and names.

    Returns:
        dict: A filtered dictionary of matches or the full symbols dict.
    """
    while True:
        choice = input("Do you want to search for a currency or view all? (search/all): ").strip().lower()
        if choice in ("search", "all"):
            break
        print("❌ Invalid choice. Please type 'search' or 'all'.")

    if choice == "search":
        keyword = input("Enter part of currency name/code to search: ").strip().lower()
        matches = {c: n for c, n in symbols.items() if keyword in c.lower() or keyword in n.lower()}
        if matches:
            print("\n🔎 Matching Currencies:\n" + "-" * 40)
            for code, name in matches.items():
                print(f"{code} : {name}")
            return matches
        else:
            print("❌ No matches found.")
            # Offer retry or full list
            while True:
                nxt = input("Type 'retry' to search again, or 'all' to view all currencies: ").strip().lower()
                if nxt == "retry":
                    return search_symbols(symbols)   # recursion: try again
                if nxt == "all":
                    break
                print("❌ Invalid. Type 'retry' or 'all'.")

    # If choice is "all" or user chose 'all' after no matches
    print("\nAvailable Currencies:\n" + "-" * 40)
    for code, name in symbols.items():
        print(f"{code} : {name}")
    return symbols

#======================================================================================================#
def choose_currency_from(displayed_dict, prompt):
    """
    Ask user to choose a valid currency code from a given dictionary.

    Args:
        displayed_dict (dict): Dictionary of allowed currencies (shown to user).
        prompt (str): Prompt message asking for input.

    Returns:
        str: The chosen valid currency code.
    """
    allowed = set(displayed_dict.keys())  # using set for faster lookup
    while True:
        cur = input(prompt).strip().upper()
        if cur in allowed:
            return cur
        print("❌ Invalid currency code. Please choose from the list shown.")

#======================================================================================================#
def get_amount():
    """
    Prompt the user for a valid positive numeric amount.

    Returns:
        float: The entered amount.
    """
    while True:
        try:
            amount = float(input("Enter the amount: "))
        except ValueError:
            print("❌ The amount must be a numeric value!")
            continue
        if amount <= 0:
            print("❌ The amount must be greater than 0")
            continue
        return amount

#======================================================================================================#
def convert_currency(from_currency, to_currency, amount):
    """
    Perform currency conversion using the API.

    Args:
        from_currency (str): Source currency code (e.g., "USD").
        to_currency (str): Target currency code (e.g., "EUR").
        amount (float): Amount to convert.

    Returns:
        float | None: The converted amount, or None if failed.
    """
    url = f"{BASE_URL}/convert?to={to_currency}&from={from_currency}&amount={amount}"
    headers = {"apikey": API_KEY}
    try:
        response = requests.get(url, headers=headers)
    except requests.exceptions.RequestException as e:
        print("❌ Network error while converting:", e)
        return None

    if response.status_code != 200:
        handle_error(response)
        return None

    data = response.json()
    if not data.get("success", True):
        print("❌ API Error:", data.get("error", data))
        return None

    return data.get("result")

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

