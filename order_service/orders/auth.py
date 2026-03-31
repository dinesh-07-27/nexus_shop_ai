import os
from functools import wraps
from django.http import JsonResponse
from jose import jwt, JWTError

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "NEXUS_SUPER_SECRET_KEY")
ALGORITHM = "HS256"

def require_jwt(view_func):
    """
    Decorator for standard Django views to enforce JWT microservice authentication.
    Injects `request.user_id` and `request.is_admin`.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Unauthorized. Missing or invalid Bearer token.'}, status=401)

        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError as e:
            return JsonResponse({'error': f'Unauthorized. Invalid Token: {str(e)}'}, status=401)

        email = payload.get("sub")
        if not email:
            return JsonResponse({'error': 'Unauthorized. Token missing subject (sub).'}, status=401)

        # Attach custom payload info to request for the view to use
        request.jwt_email = email
        request.user_id = payload.get("user_id")
        request.is_admin = payload.get("is_admin", False)
        
        return view_func(request, *args, **kwargs)

    return _wrapped_view
