from discord import Member,Interaction
from discord.ext.commands import Context
import bot_globals


def is_user_admin(user: Member) -> bool:
    return user.guild_permissions.administrator

def is_user_director(user: Member) -> bool:
    if user.get_role(bot_globals.ROLEID_DIRECTOR):
        return True
    return False

def is_user_bot_dev(userId : int) -> bool:
    if userId == bot_globals.USERID_AKDENIZ:
        return True
    elif userId == bot_globals.USERID_KHANO:
        return True
    return False

def is_user_approver(user: Member) -> bool:
    if user.get_role(bot_globals.ROLEID_APPROVER):
        return True
    return False

def is_user_member(user: Member) -> bool:
    if user.get_role(bot_globals.ROLEID_MEMBER):
        return True
    return False

def deneme(interaction: Interaction) -> bool:
    return is_user_approver(interaction.user)

def can_user_approve(interaction : Interaction) -> bool:
    if is_user_approver(interaction.user) or is_user_bot_dev(interaction.user) or is_user_admin(interaction.user) or is_user_director(interaction.user):
        return True
    raise 

def can_user_moderate_jams(interaction : Interaction) -> bool:
    if is_user_bot_dev(interaction.user) or is_user_admin(interaction.user) or is_user_director(interaction.user):
        return True
    return False

def can_user_setup_bot(interaction : Interaction) -> bool:
    if is_user_bot_dev(interaction.user) or is_user_director(interaction.user) or is_user_admin(interaction.user):
        return True
    return False