from django.contrib import messages

class CurrentViewApplicationName(object):

    def process_view(self, request, view_func, view_args, view_kwargs):

        func_name = view_func.func_name.lower()
        if func_name.startswith('slice'):
            request.current_app = 'slice'
        elif func_name.startswith('island') or func_name.startswith('node'):
            request.current_app = 'node'
        else:
            mod_parts = view_func.__module__.split('.')
            if len(mod_parts) >= 2:
                request.current_app = mod_parts[0].lower()
            else:
                # default app name if no app name is available
                request.current_app = 'project'

class ExceptionAsMessageForAdmin(object):

    def process_exception(self, request, exception):
        if request.user.is_authenticated() and request.user.is_superuser:
            messages.error(request, exception)


