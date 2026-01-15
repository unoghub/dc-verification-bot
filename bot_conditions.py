from discord import Member,Interaction
from bot_exceptions import JamAlreadyPresent, UserAlreadyVerified, UserNotInJam,UserNotVerified,UserNotBotDev,UserNotHasTopAccess,UserNotJamMod,JamNotPresent,JamNotParticipating,UserAlreadyInJamTeam,UserNotApprover,UserAlreadyInJam
from tinydb import Query
from tinydb.table import Document
import bot_globals

#region conditions

def is_user_director(user: Member) -> bool:
    director_role = user.get_role(bot_globals.ROLEID_DIRECTOR)
    botdev_role = user.get_role(bot_globals.ROLEID_BOTDEV)

    return any([
        director_role,
        botdev_role,
        user.guild_permissions.administrator
    ])

def is_user_bot_dev(user : Member) -> bool:
    if user.get_role(bot_globals.ROLEID_BOTDEV):
        return True
    return False

def is_user_jam_mod(user : Member) -> bool:
    director_role = user.get_role(bot_globals.ROLEID_DIRECTOR)
    botdev_role = user.get_role(bot_globals.ROLEID_BOTDEV)
    jammod_role = user.get_role(bot_globals.ROLEID_JAM_MOD)
    return any([
        director_role,
        botdev_role,
        jammod_role,
        user.guild_permissions.administrator
    ])

def is_user_approver(user: Member) -> bool:
    director_role = user.get_role(bot_globals.ROLEID_DIRECTOR)
    approver_role = user.get_role(bot_globals.ROLEID_APPROVER)
    botdev_role = user.get_role(bot_globals.ROLEID_BOTDEV)
    return any([
        director_role,
        approver_role,
        botdev_role,
        user.guild_permissions.administrator
    ])

def is_user_member(user: Member) -> bool:
    member_role = user.get_role(bot_globals.ROLEID_MEMBER)
    director_role = user.get_role(bot_globals.ROLEID_DIRECTOR)
    approver_role = user.get_role(bot_globals.ROLEID_APPROVER)
    botdev_role = user.get_role(bot_globals.ROLEID_BOTDEV)
    jammod_role = user.get_role(bot_globals.ROLEID_JAM_MOD)

    return any([
        member_role,
        director_role,
        approver_role,
        botdev_role,
        jammod_role,
        user.guild_permissions.administrator
    ])

def is_user_have_top_access(user: Member) -> bool:

    director_role = user.get_role(bot_globals.ROLEID_DIRECTOR)
    botdev_role = user.get_role(bot_globals.ROLEID_BOTDEV)

    return any([
        director_role,
        botdev_role,
        user.guild_permissions.administrator
    ])

def is_jam_present():
    return bot_globals.TABLE_JAM_CURRENT.get(Query()._type == "meta")

def is_user_in_jam(user: Member):
    return bot_globals.TABLE_JAM_CURRENT_PARTICIPANTS.get(Query().discordID == user.id)
    
def is_user_in_jam_team(user: Member) -> bool:
    Team = Query()
    participant : Document = is_user_in_jam(user)
    if participant:
        return bot_globals.TABLE_JAM_CURRENT_TEAMS.get((Team.members.any(Query().value == participant.doc_id)) |
            (Team.leader == participant.doc_id))
    return None

#endregion

#region checks

def check_is_approver(interaction : Interaction) -> bool:
    if is_user_approver(interaction.user):
        return True
    raise UserNotApprover()

def check_is_jam_mod(interaction : Interaction) -> bool:
    if is_user_jam_mod(interaction.user):
        return True
    raise UserNotJamMod()

def check_is_botdev(interaction : Interaction) -> bool:
    if is_user_bot_dev(interaction.user):
        return True
    raise UserNotBotDev()

def check_is_member(interaction : Interaction) -> bool:
    if is_user_member(interaction.user):
        return True
    raise UserNotVerified()

def check_has_top_access(interaction : Interaction) -> bool:
    if is_user_have_top_access(interaction.user):
        return True
    raise UserNotHasTopAccess()

def check_can_create_jam_team(interaction : Interaction) -> bool:
    presentJam = is_jam_present()
    jamParticipant = is_user_in_jam(interaction.user)
    participantTeam = is_user_in_jam_team(interaction.user)

    if presentJam:
        if jamParticipant:
            if not participantTeam:
                return True
            else:
                UserAlreadyInJamTeam()
        else:
            raise UserNotInJam()
    else:
        raise JamNotPresent()

def check_is_jam_present(interaction : Interaction) -> bool:
    if is_jam_present():
        return True
    else:
        raise JamNotPresent()
    
def check_is_no_jam_present(interaction : Interaction) -> bool:
    if not is_jam_present():
        return True
    else:
        raise JamAlreadyPresent()

def check_is_member_not_in_jam(interaction : Interaction) -> bool:
    presentJam = is_jam_present()
    jamParticipant = is_user_in_jam(interaction.user)

    if presentJam:
        if not jamParticipant:
            return True
        else:
            raise UserAlreadyInJam()
    else:
        return True

def check_is_member_in_jam(interaction : Interaction) -> bool:
    presentJam = is_jam_present()
    jamParticipant = is_user_in_jam(interaction.user)

    if presentJam:
        if jamParticipant:
            return True
        else:
            raise UserAlreadyInJam()
    else:
        raise JamNotPresent()
    
def check_is_member_in_jam_team(interaction : Interaction) -> bool:
    if check_is_member_in_jam(None):
        partipantData = bot_globals.TABLE_JAM_CURRENT_PARTICIPANTS.get(Query().discordID == interaction.user.id)
        if partipantData:
            return True
        raise JamNotParticipating()

def check_can_user_join_jam(interaction : Interaction) -> bool:
    if is_jam_present():
        if is_user_in_jam(interaction.user):
            raise UserAlreadyInJam()
        else:
            return True
    else:
        raise JamNotPresent()

def check_can_user_create_jam_team(interaction : Interaction) -> bool:
    if is_jam_present():
        if is_user_in_jam(interaction.user):
            if is_user_in_jam_team(interaction.user):
                raise UserAlreadyInJamTeam()
            else:
                return True
        else:
            raise UserNotInJam()
    else:
        raise JamNotPresent()
#endregion