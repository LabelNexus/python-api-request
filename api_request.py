"""Common Request Module"""
# pylint: disable=too-many-arguments,unused-argument,no-self-use
import json
import requests
from lumavate_exceptions import ApiException
from urllib.parse import quote, urlparse

class ApiRequest:
  """
  Represents all api requests.  This helper will make sure that requests
  will be routed to a common base url if applicable.  Also a standard auth
  bearer token will be placed in the request as needed.  Requests will be
  chunked if the response is large, and connections will NOT be pooled
  """

  def __init__(self):
    pass

  def get_auth_token(self):
    """Return the current auth token, if any"""
    raise Exception('Not Implemented')

  def get_base_url(self):
    """Return the appropriate base url for the api call"""
    raise Exception('Not implemented')

  def get(self, path, headers=None, raw=False, timeout=None, encode_qs=False):
    """Perform a 'GET' REST request with the given parameters"""
    return self.make_request('get', path, headers=headers, raw=raw, timeout=timeout, encode_qs=encode_qs)

  def patch(self, path, payload, headers=None, raw=False, timeout=None, encode_qs=False):
    """Perform a 'PUT' REST request with the given parameters"""
    return self.make_request(
        'patch',
        path,
        payload=payload,
        headers=headers,
        raw=raw,
        timeout=timeout,
        encode_qs=encode_qs)

  def post(self, path, payload, headers=None, files=None, raw=False, timeout=None, encode_qs=False):
    """Perform a 'POST' REST request with the given parameters"""
    return self.make_request(
        'post',
        path,
        payload=payload,
        headers=headers,
        files=files,
        raw=raw,
        timeout=timeout,
        encode_qs=encode_qs)

  def put(self, path, payload, headers=None, raw=False, timeout=None, encode_qs=False):
    """Perform a 'PUT' REST request with the given parameters"""
    return self.make_request(
        'put',
        path,
        payload=payload,
        headers=headers,
        raw=raw,
        timeout=timeout,
        encode_qs=encode_qs)

  def delete(self, path, headers=None, raw=False, timeout=None, encode_qs=False):
    """Perform a 'DELETE' REST request with the given parameters"""
    return self.make_request('delete', path, headers=headers, raw=raw, timeout=timeout, encode_qs=encode_qs)

  def sign_url(self, method, path, payload, headers):
    """With the given request paraemters, calculate a request signature"""
    return path

  def make_request(
      self,
      method,
      path,
      headers=None,
      payload=None,
      files=None,
      raw=False,
      timeout=None,
      encode_qs=False,
      ignore_content_type=False):
    """Make a request with the given method and parameters"""
    response_content = None
    results = {}

    if headers is None:
      headers = {}

    if timeout is None:
      # If timeout is not set, requests library will hang indefinitely
      timeout = 30

    if 'Authorization' not in headers:
      headers['Authorization'] = self.get_auth_token()

    if 'Content-Type' not in headers and not ignore_content_type:
      headers['Content-Type'] = 'application/json'

    if path.startswith('/'):
      path = self.get_base_url() + path

    if payload is not None:
      payload = json.dumps(payload)

    headers['Connection'] = 'close'

    with requests.Session() as session:
      if encode_qs:
        parsed_url = urlparse(path)
        path = f'{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}'
        if parsed_url.query != '':
            path += '?'
            args = parsed_url.query.split('&')
            last_item_idx = len(args) -1
            for idx, arg in enumerate(args):
                key, value = arg.split('=')
                if idx ==  last_item_idx:
                    path += f"{key}={quote(value)}"
                else:
                    path += f"{key}={quote(value)}&"

      url = self.sign_url(method, path, payload, headers)
      func = getattr(session, method.lower())
      try:
        res = func(
            url,
            headers=headers,
            data=payload,
            stream=True,
            timeout=timeout,
            files=files)
      except requests.exceptions.ReadTimeout  as e:
        raise ApiException(408, 'Request Timeout')
      except Exception as e:
        print(e.__dict__)
        raise

      res.encoding = 'utf-8' if not(res.encoding) else res.encoding

      for chunk in res.iter_content(chunk_size=524288, decode_unicode=not raw):
        if chunk:
          if response_content is None:
            response_content = chunk
          else:
            response_content += chunk

      if res.status_code == 200:
        if raw:
          results = response_content
        else:
          results = json.loads(response_content)

    return self.handle_response(res, data=results, raw=raw, response_content=response_content)

  def handle_response(self, res, data=None, raw=False, response_content=None):
    """Given the request outcome, properly respond to the data"""
    response_data = data

    if res.status_code == 200:
      if not raw and 'payload' in response_data:
        return response_data['payload']['data']

      return response_data

    return self.raise_exception(res, response_content)

  def raise_exception(self, res, response_content=None):
    """Raise an appropriate exception, based on the response state and data"""
    raise ApiException(
        res.status_code,
        'Error making request ' + res.url + ':' + res.request.method + ' - ' + str(res.status_code))
