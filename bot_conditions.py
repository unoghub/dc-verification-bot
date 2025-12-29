from discord import Member
import bot_globals


def is_user_admin(user: Member):
    if is_bot_dev(user.id):
        return True
    return user.guild_permissions.administrator

def is_bot_dev(userId : int):
    if userId == bot_globals.USERID_AKDENIZ or userId == bot_globals.USERID_KHANO:
        return True
    return False

def is_user_approver(user: Member):
    if is_bot_dev(user.id):
        return True
    if user.get_role(bot_globals.ROLEID_APPROVER):
        return True
    return False