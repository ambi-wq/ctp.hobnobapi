from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


def success_response(data, is_array=False):
    if is_array:
        result = data
    else:
        result = [data]
    response = {
        "count": len(result),
        "next": None,
        "previous": None,
        "results": result
    }
    return response

def success_response2(data, is_array=False):
    result = data
    response = {
        "count": len(result),
        "next": None,
        "previous": None,
        "results": result
    }
    return response

def error_response(data):
    response = {"detail": data}
    return response
