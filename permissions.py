from enum import Enum
import hashlib
import json

class Permissions(Enum):
  UsersFullAccess = 'users:full_access'
  AudioFullAccess = 'audio:full_access'
  DocumentsFullAccess = 'documents:full_access'
  ImagesFullAccess = 'images:full_access'
  TextFullAccess = 'text:full_access'
  VideoFullAccess = 'video:full_access'
  FormsFullAccess = 'forms:full_access'

  @classmethod
  def get_version(cls):
    hashable = {j.name: j.value for j in cls}
    return hashlib.md5(json.dumps(hashable, sort_keys=True).encode('utf-8')).hexdigest()