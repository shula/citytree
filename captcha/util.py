# Copyright (c) 2007 Brandon Low
# Licensed under the GPL v2
#from settings import ALLOWED_CHARACTERS
#import random

from captcha.generator.Words import WordList
from settings import MIN_LENGTH, MAX_LENGTH

# врахувати довжину потім
def get_string():
    return defaultWordList.pick()

defaultWordList = WordList("basic-english", minLength=MIN_LENGTH, maxLength=MAX_LENGTH)