import Algorithmia

# This module defines your algorithm, and its input/output.
# You must define an apply function that takes exactly one input.
# The input and output of apply() automatically turns into JSON.
#
# Examples:
#   def apply(array):
#   def apply(str):
#   def apply(x):

def apply(input):
    return 'Hello ' + str(input)
