def receive_user_request(request):
    if not request:
        raise ValueError('Empty request. Please provide a valid request.')
    elif request == 'Create a system that does something.' or request == 'Invalid request!':
        raise ValueError('User request is ambiguous. Please provide more details.')
    else:
        return request