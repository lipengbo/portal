from profiles.models import Profile

class CcfBackend(object):

    def authenticate(**credentials):
        return None

    def has_perm(self, user_obj, perm, obj):
        if isinstance(obj, Profile) and perm == 'can_view':
            return True
        if perm in ["agora.add_forumthread", "agora.add_forumreply"]:
            if user_obj.is_authenticated():
                return True