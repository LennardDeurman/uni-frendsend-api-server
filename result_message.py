from flask import jsonify
import simplejson as json

'''

This file creates the response json to the server

'''


class ResultMessage:


    class StatusCodes:
        SERVER_ERROR = 500
        BAD_REQUEST = 400
        NO_ACCESS = 403
        OK = 200

    class StatusMessages:
        OK = "Request was successfull"
        SERVER_ERROR = "Unknown error found"
        NO_ACCESS = "No access"


    class Keys:
        RESULTS = "results"
        RESULTS = "results"
        OBJECT = "object"
        SUCCESS = "success"
        STATUS = "status"
        STATUS_CODE = "status_code"
        STATUS_MESSAGE = "status_message"
        ERROR_CODE = "error_code"
        ERROR_MESSAGE = "error_message"


    @staticmethod
    def ok():
        return ResultMessage.make_response_message(True, ResultMessage.StatusCodes.OK, ResultMessage.StatusMessages.OK)

    
    @staticmethod
    def ok_with_object(response_object):
        return ResultMessage.make_response_message(True, ResultMessage.StatusCodes.OK, ResultMessage.StatusMessages.OK, response_object)


    @staticmethod
    def make_response_message(success, status_code = None, message = None, object = None):
        if status_code == None:
            status_code = ResultMessage.StatusCodes.OK
        if message == None:
            message = ResultMessage.StatusMessages.OK 
        resp_dict = {
            ResultMessage.Keys.OBJECT: object,
            ResultMessage.Keys.SUCCESS: success,
            ResultMessage.Keys.STATUS: {
                ResultMessage.Keys.STATUS_CODE: status_code,
                ResultMessage.Keys.STATUS_MESSAGE: message,
            }
        }
        response = jsonify(resp_dict) 
        response.status_code = status_code
        return response
    
    @staticmethod
    def fail_with_object(status_code, exception):
        obj = {
            ResultMessage.Keys.ERROR_MESSAGE: str(exception)
        }
        response = ResultMessage.make_response_message(False, status_code, obj)
        return response


    
