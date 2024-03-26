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
  ProductsFullAccess = 'products:full_access'
  LocationsFullAccess = 'locations:full_access'
  ExperiencesEdit = 'experiences:edit'
  ExperiencesPublish = 'experiences:publish'
  LanguagesFullAccess = 'languages:full_access'
  AuthenticationFullAccess = 'authentication:full_access'
  MessagingAdminFullAccess = 'messaging_admin:full_access'
  AudiencesFullAccess = 'audiences:full_access'
  ActivationsFullAccess = 'activations:full_access'


  @classmethod
  def get_version(cls):
    hashable = {j.name: j.value for j in cls}
    return hashlib.md5(json.dumps(hashable, sort_keys=True).encode('utf-8')).hexdigest()