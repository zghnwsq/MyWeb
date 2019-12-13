

def get_personal(request, context):
    user_name = request.session['user_name']
    user_group = request.session['user_group']
    context['user_name'] = user_name
    context['user_group'] = user_group
    return context
