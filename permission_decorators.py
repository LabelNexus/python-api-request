from flask import g, request
from lumavate_exceptions import InvalidOperationException
from functools import wraps

def has_permission(permission_name, methods=['*']):
  def decorator(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
      if not '*' in methods and not request.method in methods:
        return f(*args, **kwargs)
      
      if not hasattr(g, 'user'):
        raise InvalidOperationException('Not authorized')
      if g.user.get('isServiceUser', False):
        return f(*args, **kwargs)

      if permission_name and not permission_name.value in g.user['rolePermissions']:
        raise InvalidOperationException('Not authorized')
      return f(*args, **kwargs)
    return decorated_func
  return decorator