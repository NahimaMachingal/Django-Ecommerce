def is_ajax(request):
    return request.headers.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
