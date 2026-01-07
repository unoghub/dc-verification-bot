from discord import Member,Interaction
from discord.ext.commands import Context
from bot_exceptions import UserNotApproved,UserNotBotDev,UserNotHasTopAccess,UserNotJamMod,NoJamPresent,JamNotParticipating,UserAlreadyInATeam,UserNotApprover
from tinydb import Query
import bot_globals


def is_user_admin(user: Member) -> bool:
    return user.guild_permissions.administrator

def is_user_director(user: Member) -> bool:
    if user.get_role(bot_globals.ROLEID_DIRECTOR):
        return True
    return False

def is_user_bot_dev(user : Member) -> bool:
    if user.get_role(bot_globals.ROLEID_BOTDEV):
        return True
    return False

def is_user_jam_mod(user : Member) -> bool:
    if user.get_role(bot_globals.ROLEID_JAM_MOD):
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

def check_is_approver(interaction : Interaction) -> bool:
    if is_user_approver(interaction.user) or is_user_bot_dev(interaction.user) or is_user_admin(interaction.user) or is_user_director(interaction.user):
        return True
    raise UserNotApprover()

def check_is_jam_mod(interaction : Interaction) -> bool:
    if is_user_jam_mod(interaction.user) or is_user_bot_dev(interaction.user) or is_user_admin(interaction.user) or is_user_director(interaction.user):
        return True
    raise UserNotJamMod()

def check_is_botdev(interaction : Interaction) -> bool:
    if is_user_bot_dev(interaction.user):
        return True
    raise UserNotBotDev()

def check_is_member(interaction : Interaction) -> bool:
    member = interaction.user.get_role(bot_globals.ROLEID_MEMBER)
    director = interaction.user.get_role(bot_globals.ROLEID_DIRECTOR)
    approver = interaction.user.get_role(bot_globals.ROLEID_APPROVER)
    botdev = interaction.user.get_role(bot_globals.ROLEID_BOTDEV)
    jammod = interaction.user.get_role(bot_globals.ROLEID_JAM_MOD)
    if member or director or approver or botdev or jammod or is_user_admin(interaction.user):
        return True
    raise UserNotApproved()

def check_has_top_access(interaction : Interaction) -> bool:
    if is_user_director(interaction.user) or is_user_bot_dev(interaction.user) or is_user_admin(interaction.user):
        return True
    raise UserNotHasTopAccess()

def check_can_create_jam_team(interaction : Interaction) -> bool:
    jamData = bot_globals.TABLE_JAM_CURRENT.get(Query()._type == "meta")
    participantData = bot_globals.TABLE_JAM_CURRENT_PARTICIPANTS.get(Query().discordID == interaction.user.id)
    
    if not jamData:
        raise NoJamPresent()
    elif not participantData:
        raise JamNotParticipating()
    elif participantData.teamID != -1:
        raise UserAlreadyInATeam()
    
    return True
