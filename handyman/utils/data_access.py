from ..models import Handyman, CustomUser

def get_handyman_user_info(handyman_id):
    try:
        handyman = Handyman.objects.get(id=handyman_id)
        user = handyman.user  
        return handyman, user
    except Handyman.DoesNotExist:
        return None, None
