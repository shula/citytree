import sha
import random

def make_random_hash():
    return sha.new(hex((random.randint(0,65536)<<16)+random.randint(0,65536))[2:]).hexdigest()

