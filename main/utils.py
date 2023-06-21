import random
import string

# function for generating booking_id
# length- parameter
#contains digits and letters
def generate_random_string(length):
    # Define the pool of characters
    characters = string.digits + string.ascii_letters

    # Generate a random string of specified length
    random_string = ''.join(random.choice(characters) for _ in range(length))
    
    return random_string