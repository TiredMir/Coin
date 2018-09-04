#!/usr/bin/env python3
import os
import argparse
import sys
import urllib.request
import json
import subprocess
import shlex
import platform
import signal


# Clear the screen
def clear():
    if os.name == 'nt':
        os.system("cls")
    else:
        os.system("clear")


def signal_handler(sig, frame):
    print("\nCaught SIGINT")
    print("Program terminated")
    exit(1)


# Check connectivity
def connectivity():
    hostname = 'free.currencyconverterapi.com'
    platform_name = platform.system()
    if platform_name == 'Windows':
        # try:
        os.system("ping -n 1 {} | findstr dummy".format(hostname))
        return 0
        # except:

    else:
        command = shlex.split("ping -c1 {}".format(hostname))
        try:
            output_test = subprocess.check_output(command)
            return 0
        except subprocess.CalledProcessError as err:
            print("The server is currently unreachable."
                  "Please try again later.")
            return 3


# Get the JSON values and parse them in memory without writing to disk, and
# finally convert the values
def exchange():
    global amount, base, target, free_url
    base = base.upper()
    target = target.upper()
    free_url = "http://free.currencyconverterapi.com/api/v6/convert?q="
    rounding_digits = 4
    json_exchange = urllib.request.urlopen(
        "{}{}_{}&compact=ultra".format(free_url, base, target)
    )
    parsed_exchange = json.loads(json_exchange.read())
    # Prettify the parsed value
    pparsed_exchange = float(json.dumps(
        parsed_exchange, sort_keys=True,
        separators=(',', ':')).replace("}", "").split(":")[1].rstrip())
    exchange_rate = round(amount * pparsed_exchange, rounding_digits)
    print(amount, base, "is", exchange_rate, target, "\n")


# Get the list of available currency exchange values
def currencylist():
    currencyurl = "https://free.currencyconverterapi.com/api/v6/currencies"
    json_currency = urllib.request.urlopen(currencyurl)
    parsed_currency = json.loads(json_currency.read())
    pparsed_currency = json.dumps(
        parsed_currency, ensure_ascii=False,
        indent=0, sort_keys=True, separators=(',', ':')
    )
    # Write the values to a file called currencylist.txt
    try:
        fcurrencylist = open("currencylist.txt", "w", encoding='utf-8')
        fcurrencylist.write(pparsed_currency)
    finally:
        fcurrencylist.close()


# Ask if the user wants to update the currency list
def write_to_file():
    yes_list = ["Yes", "yes", "Y", "y"]
    no_list = ["No", "no", "N", "n"]
    curr = input(
                "Would you like to refresh the currency list file?\n"
                "Enter yes or no:\n\n"
    )
    while curr not in yes_list or no_list:
        if curr in yes_list:
            print("\nWriting to file...")
            currencylist()
            print("\nDone")
            break
        elif curr in no_list:
            print("\nCurrency list update cancelled.\n")
            break
        else:
            print("Unknown value. Please try again...\n")
            curr = input(
                        "Would you like to refresh the currency list file?\n"
                        "Enter yes or no:\n\n"
            )
    return curr


# Show the available currency list
def show():
    yes_list = ["Yes", "yes", "Y", "y"]
    no_list = ["No", "no", "N", "n"]
    choice = input(
                    "Would you like to see the available currencies?\n"
                    "Enter yes or no:\n\n"
    )
    if choice in yes_list:
        currencylist()
        filepath = './currencylist.txt'
        cat_command = shlex.split("cat {}".format(filepath))
        less_command = shlex.split("less")
        try:
            cat_pipe = subprocess.Popen(cat_command, stdout=subprocess.PIPE)
            less_pipe = subprocess.Popen(
                                        less_command, stdin=cat_pipe.stdout,
                                        stdout=subprocess.PIPE
            )
            cat_pipe.stdout.close()
            stdout = less_pipe.communicate
        except subprocess.CalledProcessError as err:
            print("Oops, something went wrong. Error Code: 2")
            return 2
    elif choice in no_list:
        pass
    else:
        print("Unknown value. Please try again...\n")
        choice = input(
                        "Would you like to see the available currencies?\n"
                        "Enter yes or no:\n\n"
        )


def menu():
    print("What would you like to do? Select an entry number:\n")
    print("1. Convert currencies\n")
    print("2. Update currency list\n")
    print("3. Show the available currencies\n")
    print("4. Check connection to server\n")
    choice_range = [1,2,3,4]
    answer = None
    while answer not in choice_range:
      for retries in range(4):
        try:
            answer = int(input())
        except ValueError:
                print("Value Error. Please choose a valid entry")
                answer = int(input())
                if answer == int:
                    break
        if answer == 1:
            global amount, base, target
            amount = float(input("Enter an amount in the base "
                                 "currency:\n"))
            base = str(input(
                            "Enter a three letter currency "
                            "code(e.g. USD) for the base currency:\n"
                            ))
            target = str(input(
                            "Enter a three letter currency code(e.g. USD) "
                            "for the target currency:\n"
                            ))

            exchange()
            exit (0)
        elif answer == 2:
            currencylist()
            print("Currency list updated.\n")
            exit(0)
        elif answer == 3:
            show()
        elif answer == 4:
            connect = int(connectivity())
            if connect == 0:
                print("Server is up and running.\n")
                exit (0)
            elif connect == 3:
                exit (3)
        else:
            print("Please enter a valid number from the "
                  "list.\n")
            menu()


# Basically clean up, take arguments and call the exchange function
def main():
    clear()
    signal.signal(signal.SIGINT, signal_handler)
    parser = argparse.ArgumentParser(description='A program that exchanges \
    currency units.')
    parser.add_argument('-a', type=float, help='The amount of the base \
    currency unit', default=1.0)
    parser.add_argument('-b', type=str, help='The base currency unit convert \
    from', default='USD')
    parser.add_argument('-t', type=str, help='The target currency unit to \
    convert to', default='EUR')
    if len(sys.argv) <= 1:
        # parser.print_help()
        menu()
        exit(4)
    args = parser.parse_args()
    global amount, base, target, free_url
    amount = args.a
    base = args.b
    target = args.t
    exchange()
    return 0


if __name__ == "__main__":
    connectivity()
    main()
