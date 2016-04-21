import os
import sys
import json
import traceback
import base64
from io import StringIO

from __ALGO__ import __ALGO__

####
# Disable stdout, stderr
old_stdout = sys.stdout
old_stderr = sys.stderr
old_fd_stdout = os.dup(1)
old_fd_stderr = os.dup(2)

# Redirect file descriptors to handle child processes
os.dup2(os.open(os.devnull, os.O_RDWR), 1)
os.dup2(os.open(os.devnull, os.O_RDWR), 2)

captured_stdout = StringIO()

sys.stdout = captured_stdout
sys.stderr = captured_stdout
####

input_object = None

####
#Parse and validate Input
###
try:

    ###
    # Read input from stdin and parse as JSON
    ###
    inputString = sys.stdin.read()
    input_json = json.loads(inputString)

    #input_json: Request
    #    input
    #        body - []
    #            name
    #            filename - option
    #            data
    #            content_type - "void", "text", "json", "binary"
    #            mime_type
    #    modifiers
    #        log_stdout
    #        log_stacktrace

    ###
    #Validate input structure
    ####
    if 'input' not in input_json:
        raise Exception("did not find 'input'")

    if 'modifiers' not in input_json:
        raise Exception("did not find 'modifiers'")

    if 'log_stdout' not in input_json["modifiers"]:
        raise Exception("did not find 'modifiers.log_stdout'")

    if input_json["modifiers"]["log_stdout"] != True and input_json["modifiers"]["log_stdout"] != False:
        raise Exception("'modifiers.log_stdout' is not Boolean")

    if 'log_stacktrace' not in input_json["modifiers"]:
        raise Exception("did not find 'modifiers.log_stacktrace'")

    if input_json["modifiers"]["log_stacktrace"] != True and input_json["modifiers"]["log_stacktrace"] != False:
        raise Exception("'modifiers.log_stacktrace' is not Boolean")

    if 'body' not in input_json["input"]:
        raise Exception("did not find 'input.body'")

    for part in input_json["input"]["body"]:
        if 'name' not in part:
            raise Exception("did not find 'input.body[].name'")
        if 'data' not in part:
            raise Exception("did not find 'input.body[].data'")
        if 'content_type' not in part:
            raise Exception("did not find 'input.body[].content_type'")
        if (part["content_type"] != "void" and part["content_type"] != "text" and part["content_type"] != "json" and part["content_type"] != "binary"):
            raise Exception("'input.body[].content_type' did not parse as valid enum value")
        if 'mime_type' not in part:
            raise Exception("did not find 'input.body[].mime_type'")

    ###
    #Create input_object
    ###
    if len(input_json["input"]["body"]) == 1:
        body_part = input_json["input"]["body"][0]
        input_data = body_part["data"]
        if body_part["content_type"] == "void":
            input_object = None
        elif body_part["content_type"] == "text":
            input_object = input_data
        elif body_part["content_type"] == "json":
            input_object = json.loads(input_data)
        elif body_part["content_type"] == "binary":
            input_object = bytearray(base64.b64decode(input_data))
        else:
            input_object = body_part["data"]
    else:
        input_object = input_json["input"]

except Exception as e:

    ###
    # Protocol Exception
    ###

    # Enable stdout, stderr
    os.dup2(old_fd_stdout, 1)
    os.dup2(old_fd_stderr, 2)
    sys.stdout = old_stdout
    sys.stderr = old_stderr

    #class ProtocolErrorResponse:
    #    error
    #        type - "protocol_error"
    #        message
    #    metadata
    #        stacktrace

    protocol_error_response = {"error":{"type":"protocol_error","message":str(e)},"metadata":{"stacktrace":traceback.format_exc()}}
    print(json.dumps(protocol_error_response))
    sys.exit(0)

try:

    ###
    # Call Algorithm
    ###
    output = __ALGO__.apply(input_object)

    ###
    # Create Algorithm Result
    ###
    result_json = None
    content_type = "void"
    if output is None:
        result_json = None
        content_type = "void"
    elif isinstance(output, str):
        result_json = output
        content_type = "text"
    elif isinstance(output, bytearray):
        result_json = base64.b64encode(output)
        content_type = "binary"
    else:
        result_json = json.dumps(output)
        content_type = "json"

    # Enable stdout, stderr
    os.dup2(old_fd_stdout, 1)
    os.dup2(old_fd_stderr, 2)
    sys.stdout = old_stdout
    sys.stderr = old_stderr

    #class AlgorithmResultResponse:
    #    result
    #        data
    #    metadata
    #        content_type
    #        stdout - option

    if input_json["modifiers"]["log_stdout"] == True:
        algorithm_result_response = {"result":{"data":result_json},"metadata":{"content_type":content_type,"stdout":captured_stdout.getvalue()}}
    else:
        algorithm_result_response = {"result":{"data":result_json},"metadata":{"content_type":content_type}}

    print(json.dumps(algorithm_result_response))
    sys.exit(0)

except Exception as e:

    ###
    # Algorithm Exception
    ###

    # Enable stdout, stderr
    os.dup2(old_fd_stdout, 1)
    os.dup2(old_fd_stderr, 2)
    sys.stdout = old_stdout
    sys.stderr = old_stderr

    #class AlgorithmErrorResponse:
    #    error
    #        type - "algorithm_error"
    #        message
    #    metadata - option
    #        stdout - option
    #        stacktrace - option

    if input_json["modifiers"]["log_stdout"] == True and input_json["modifiers"]["log_stacktrace"] == True:
        algorithm_error_response = {"error":{"type":"algorithm_error","message":str(e)},"metadata":{"stdout":captured_stdout.getvalue(),"stacktrace":traceback.format_exc()}}
    elif input_json["modifiers"]["log_stdout"] == True:
        algorithm_error_response = {"error":{"type":"algorithm_error","message":str(e)},"metadata":{"stdout":captured_stdout.getvalue()}}
    elif input_json["modifiers"]["log_stacktrace"] == True:
        algorithm_error_response = {"error":{"type":"algorithm_error","message":str(e)},"metadata":{"stacktrace":traceback.format_exc()}}
    else:
        algorithm_error_response = {"error":{"type":"algorithm_error","message":str(e)}}

    print(json.dumps(algorithm_error_response))
    sys.exit(0)
