from lumavate_exceptions import ApiException
import requests
import json

class ApiRequest:
  def __init__(self):
    pass

  def get(self, path, headers=None, raw=False):
    return self.make_request('get', path, headers=headers, raw=raw)

  def post(self, path, payload, headers=None, files=None, raw=False):
    return self.make_request('post', path, payload=payload, headers=headers, files=files, raw=raw)

  def put(self, path, payload, headers=None, raw=False):
    return self.make_request('put', path, payload=payload, headers=headers, raw=raw)

  def delete(self, path, headers=None, raw=False):
    return self.make_request('delete', path, headers=headers, raw=raw)

  def sign_url(self, method, path, payload, headers):
    return path

  def make_request(self, method, path, headers=None, payload=None, files=None, raw=False):
    response_content = None
    results = {}

    if headers is None:
      headers = {}

    if 'Authorization' not in headers:
      headers['Authorization'] = self.get_auth_token()

    if 'Content-Type' not in headers:
      headers['Content-Type'] = 'application/json'

    if path.startswith('/'):
      path = self.get_base_url() + path

    if payload is not None:
      payload = json.dumps(payload)

    headers['Connection'] = 'close'

    with requests.Session() as s:
      url = self.sign_url(method, path, payload, headers)
      res = getattr(s, method.lower())(url, headers=headers, data=payload, stream=True, timeout=None, files=files)
      res.encoding = 'utf-8' if not(res.encoding) else res.encoding

      for chunk in res.iter_content(chunk_size=524288, decode_unicode=not raw):
        if chunk:
          if response_content is None:
            response_content = chunk
          else:
            response_content += chunk

      if(res.status_code == 200):
        if raw:
          results = response_content
        else:
          results = json.loads(response_content)

    return self.handle_response(res, results, raw=raw)

  def handle_response(self, res, data = None, raw=False):
    response_data = data

    if res.status_code == 200:
      if not raw and 'payload' in response_data:
        return response_data['payload']['data']
      else:
        return response_data

    else:
      self.raise_exception(res)

  def raise_exception(self, res):
    raise ApiException(res.status_code, 'Error making request ' + res.url + ':' + res.request.method + ' - ' + str(res.status_code))
