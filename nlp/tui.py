def display(text):
    '''
    Display one line of text on the screen

    text is a string
    '''
    print(text)

def prompt(prompt):
    '''
    Prompts the user for a value

    prompt is a string
    '''
    return raw_input(prompt)


def choice(options):
    '''
    Display a list of options of what the user can do and let the user pick one

    options is a list of strings (each one is an option the user can choose)
    '''
    print("What would you like to do?")
    for index, option in enumerate(options):
        human_index = index + 1
        print("    {}. {}".format(human_index, option))

    # ask the user for choices
    number = None
    while number is None:
        try:
            user_input = input("Type the number or the option: ")
            try:
                number = int(user_input)
            except ValueError:
                simple_user_input = user_input.strip().lower()
                for index, option in enumerate(options):
                    simple_option = option.strip().lower()
                    if simple_user_input == simple_option:
                        number = index + 1
            number -= 1
            if number < 0 or len(options) <= number:
                raise ValueError("Invalid number")

        except Exception:
            print("Sorry, please enter a number between 1 and {}".format(len(options)))
            number = None
    return number