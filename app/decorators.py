from django.http import HttpResponse # type: ignore
from django.shortcuts import redirect # type: ignore

def unauthenticated_user(view_func): # type: ignore
    def wrapper_func(request, *args, **kwargs): # type: ignore
        if request.user.is_authenticated: # type: ignore
            return redirect('auctionFront')
        else:
            return view_func(request) # type: ignore

    return wrapper_func # type: ignore