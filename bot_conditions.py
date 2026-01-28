from discord import Member,Interaction
from bot_exceptions import *
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
    volunteer_role = user.get_role(bot_globals.ROLEID_VOLUNTEER)
    director_role = user.get_role(bot_globals.ROLEID_DIRECTOR)
    approver_role = user.get_role(bot_globals.ROLEID_APPROVER)
    botdev_role = user.get_role(bot_globals.ROLEID_BOTDEV)
    jammod_role = user.get_role(bot_globals.ROLEID_JAM_MOD)

    return any([
        member_role,
        director_role,
        approver_role,
        botdev_role,
        volunteer_role,
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

def is_jam_present() -> Document:
    return bot_globals.TABLE_JAM_CURRENT.get(Query()._type == "meta")

def is_user_in_jam(user: Member) -> Document:
    if is_jam_present():
        return bot_globals.TABLE_JAM_CURRENT_PARTICIPANTS.get(Query().discordID == user.id)
    return None
    
def is_user_in_jam_team(user: Member) -> Document:
    Team = Query()
    participant : Document = is_user_in_jam(user)
    if not participant:
        return None
    if participant.get('teamID') == -1:
        return None
    return bot_globals.TABLE_JAM_CURRENT_TEAMS.get(doc_id=participant.get('teamID'))
    # return bot_globals.TABLE_JAM_CURRENT_TEAMS.get((Team.members.any(Query() == participant.doc_id)) |
    #     (Team.leader == participant.doc_id))
    

def is_user_jam_team_leader(user: Member) -> Document:
    team = is_user_in_jam_team(user)
    participant : Document = is_user_in_jam(user)
    if team and team.get('leader') == participant.doc_id:
        return team
    return None

def is_jam_team_submitted(team_doc : Document):
    if team_doc.get('gameURL') != "":
        return True
    return False

#endregion

#region checks

def check_is_approver(interaction : Interaction) -> bool:
    if is_user_approver(interaction.user):
        return True
    raise YouMustBeApproverException()

def check_is_jam_mod(interaction : Interaction) -> bool:
    if is_user_jam_mod(interaction.user):
        return True
    raise YouMustBeJamModException()

def check_is_botdev(interaction : Interaction) -> bool:
    if is_user_bot_dev(interaction.user):
        return True
    raise YouMustBeBotDevException()

def check_is_member(interaction : Interaction) -> bool:
    if is_user_member(interaction.user):
        return True
    raise YoureNotVerifiedException()

def check_has_top_access(interaction : Interaction) -> bool:
    if is_user_have_top_access(interaction.user):
        return True
    raise YouMustHaveTopAccessException()

def check_can_create_jam_team(interaction : Interaction) -> bool:
    presentJam = is_jam_present()
    jamParticipant = is_user_in_jam(interaction.user)
    participantTeam = is_user_in_jam_team(interaction.user)

    if presentJam:
        if jamParticipant:
            if not participantTeam:
                return True
            else:
                YouMustNotBeInJamTeamException()
        else:
            raise YouMustJoinJamException()
    else:
        raise JamNotPresentException()

def check_is_jam_present(interaction : Interaction) -> bool:
    if is_jam_present():
        return True
    else:
        raise JamNotPresentException()
    
def check_is_no_jam_present(interaction : Interaction) -> bool:
    if not is_jam_present():
        return True
    else:
        raise JamAlreadyPresentException()

def check_is_member_not_in_jam(interaction : Interaction) -> bool:
    presentJam = is_jam_present()
    jamParticipant = is_user_in_jam(interaction.user)

    if presentJam:
        if not jamParticipant:
            return True
        else:
            raise YoureAlreadyInJamException()
    else:
        return True

def check_is_member_in_jam(interaction : Interaction) -> bool:
    presentJam = is_jam_present()
    jamParticipant = is_user_in_jam(interaction.user)

    if presentJam:
        if jamParticipant:
            return True
        else:
            raise YoureAlreadyInJamException()
    else:
        raise JamNotPresentException()
    
def check_can_member_get_jam_info(interaction: Interaction):
    member = is_user_member(interaction.user)
    presentJam = is_jam_present()
    if not member:
        raise YoureNotVerifiedException()
    elif not presentJam:
        raise JamNotPresentException()
    return True

def check_can_member_get_jam_help(interaction: Interaction):
    member = is_user_member(interaction.user)
    if not member:
        raise YoureNotVerifiedException()
    return True

def check_is_member_in_jam_team(interaction : Interaction) -> bool:
    if check_is_member_in_jam(None):
        partipantData = bot_globals.TABLE_JAM_CURRENT_PARTICIPANTS.get(Query().discordID == interaction.user.id)
        if partipantData:
            return True
        raise YouMustJoinJamException()

def check_can_user_join_jam(interaction : Interaction) -> bool:
    member = is_user_member(interaction.user)
    if not member:
        raise YoureNotVerifiedException()
    jam = is_jam_present()
    if not jam:
        raise JamNotPresentException()
    participant = is_user_in_jam(interaction)
    if participant:
        raise YouAlreadyInJamException()
    return True

def check_can_user_create_jam_team(interaction : Interaction) -> bool:
    member = is_user_member(interaction.user)
    jam = is_jam_present()
    participant = is_user_in_jam(interaction.user)
    team = is_user_in_jam_team(interaction.user)
    if not member:
        raise YoureNotVerifiedException()
    elif not jam:
        raise JamNotPresentException()
    elif not participant:
        raise YouMustJoinJamException()
    elif team:
        raise YouMustNotBeInJamTeamException()
    return True

def check_can_user_leave_jam_team(interaction: Interaction) -> bool:
    jam = is_jam_present()
    member = is_user_member(interaction.user)
    participant = is_user_in_jam(interaction.user)
    team = is_user_in_jam_team(interaction.user)
    if not jam:
        raise JamNotPresentException()
    if not member:
        raise YoureNotVerifiedException()
    elif not participant:
        raise YouMustJoinJamException()
    elif not team:
        raise YouMustBeInJamTeamException()
    return True

def check_can_user_send_jam_team_join_request(interaction : Interaction) -> bool:
    jam = is_jam_present()
    member = is_user_member(interaction.user)
    participant = is_user_in_jam(interaction.user)
    team = is_user_in_jam_team(interaction.user)
    if not jam:
        raise JamNotPresentException()
    if not member:
        raise YoureNotVerifiedException()
    elif not participant:
        raise YouMustJoinJamException()
    elif team:
        raise YouMustNotBeInJamTeamException()
    return True

def check_can_user_jam_submit(interaction: Interaction) -> bool: # DONE
    team = is_user_jam_team_leader(interaction.user)
    if not is_jam_present():
        raise JamNotPresentException()
    if not is_user_member(interaction.user):
        raise YoureNotVerifiedException()
    elif not is_user_in_jam(interaction.user):
        raise YouMustJoinJamException()
    elif not is_user_in_jam_team(interaction.user):
        raise YouMustBeInJamTeamException()
    elif not team:
        raise YouAreNotJamTeamLeaderException()
    elif is_jam_team_submitted(team):
        raise YourJamTeamAlreadySubmittedException()
    return True

                    


def check_can_user_accept_jam_join_request(interaction: Interaction) -> bool:
    member = is_user_member(interaction.user)
    jam = is_jam_present()
    participant = is_user_in_jam(interaction.user)
    team = is_user_in_jam_team(interaction.user)
    if not member:
        raise YoureNotVerifiedException()
    elif not jam:
        raise JamNotPresentException()
    elif not participant:
        raise YouMustJoinJamException()
    elif not team:
        raise YouMustBeInJamTeamException()
    elif not is_user_jam_team_leader(interaction.user):
        raise YouAreNotJamTeamLeaderException()
    return True
#endregion