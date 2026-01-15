from discord import Member,Interaction
from collections.abc import Mapping
from tinydb.table import Document

class UnogMember(dict):

    @property
    def id(self) -> int:
        return self.get('id')
    
    @id.setter
    def id(self,value : int):
        self['id'] = int(value)

    @property
    def name(self) -> str:
        return self.get('name')

    @name.setter
    def name(self,value : str):
        self['name'] = str(value).strip().title()

    @property
    def email(self) -> str:
        return self.get('email')
    
    @email.setter
    def email(self,value : str):
        self['email'] = str(value).strip().lower()

    @property
    def birthday(self) -> str:
        return self.get('birthday')
    
    @birthday.setter
    def birthday(self,value : str):
        self['birthday'] = str(value).strip()

    @property
    def info1(self) -> str:
        return self.get('info1')
    
    @info1.setter
    def info1(self,value : str):
        self['info1'] = str(value).strip()
    
    @property
    def info2(self) -> str:
        return self.get('info2')
    
    @info2.setter
    def info2(self,value : str):
        self['info2'] = str(value).strip()
    
    def __init__(self,
                 id : int | None,
                 name : str | None = None,
                 email : str | None = None,
                 birthday : str | None = None,
                 info1 : str | None = None,
                 info2 : str | None = None,
                 *,
                 mapping : Mapping | None = None):
        if mapping is not None:
            super().__init__(mapping)
        else:
            super().__init__({})
            if name is not None:
                self.name = name
            if email is not None:
                self.email = email
            if birthday is not None:
                self.birthday = birthday
            if info1 is not None:
                self.info1 = info1
            if info2 is not None:
                self.info2 = info2
            if id is not None:
                self.id = id

class ApproveRecord(dict):

    @property
    def approvedID(self) -> int:
        return self.get('approvedID')
    
    @approvedID.setter
    def approvedID(self, value : int):
        self['approvedID'] = int(value)

    @property
    def approverID(self) -> int:
        return self.get('approverID')

    @approverID.setter
    def approverID(self, value : int):
        self['approverID'] = int(value)

    
    def __init__(self,approvedID : int | None = None,
                 approverID : int | None = None,
                 *,
                 mapping : Mapping | None = None):
        if mapping is not None:
            super().__init__(mapping)
        else:
            super().__init__({})
            if approvedID is not None:
                self.approvedID = approvedID
            if approverID is not None:
                self.approverID = approverID

class Jam(dict):

    @property
    def shortName(self) -> str:
        return self.get('shortName')

    @shortName.setter
    def shortName(self,value : str):
        self['shortName'] = str(value).strip().upper()

    @property
    def longName(self) -> str:
        return self.get('longName')

    @longName.setter
    def longName(self,value : str):
        self['longName'] = str(value).strip().title()

    @property
    def categoryID(self) -> int:
        return self.get('categoryID')

    @categoryID.setter
    def categoryID(self,value : int):
        self['categoryID'] = int(value)

    @property
    def generalTextChannelID(self) -> int:
        return self.get('generalTextChannelID')

    @generalTextChannelID.setter
    def generalTextChannelID(self,value : int):
        self['generalTextChannelID'] = int(value)

    @property
    def generalVoiceChannelID(self) -> int:
        return self.get('generalVoiceChannelID')

    @generalVoiceChannelID.setter
    def generalVoiceChannelID(self,value : int):
        self['generalVoiceChannelID'] = int(value)

    @property
    def participantRoleID(self) -> int:
        return self.get('participantRoleID')

    @participantRoleID.setter
    def participantRoleID(self,value : int):
        self['participantRoleID'] = int(value)

    @property
    def jammerRoleID(self) -> int:
        return self.get('jammerRoleID')

    @jammerRoleID.setter
    def jammerRoleID(self,value : int):
        self['jammerRoleID'] = int(value)

    @property
    def startUnix(self) -> int:
        return self.get('startUnix')

    @startUnix.setter
    def startUnix(self,value : int):
        self['startUnix'] = int(value)

    @property
    def endUnix(self) -> int:
        return self.get('endUnix')

    @endUnix.setter
    def endUnix(self,value : int):
        self['endUnix'] = int(value)

    @property
    def url(self) -> str:
        return self.get('url')

    @url.setter
    def url(self,value : str):
        self['url'] = str(value)
    
    @property
    def description(self) -> str:
        return self.get('description')

    @description.setter
    def description(self,value : str):
        self['description'] = str(value)
    
    def __init__(self,
                 shortName : str | None = None,
                 longName : str | None = None,
                 categoryID : int | None = None,
                 generalTextChannelID : int | None = None,
                 generalVoiceChannelID : int | None = None,
                 participantRoleID : int | None  = None,
                 jammerRoleID : int | None = None,
                 startUnix : int | None = None,
                 endUnix : int | None = None,
                 url : str | None = None,
                 description : str | None = None,
                 *,
                 mapping : Mapping | None = None):
        if mapping is not None:
            super().__init__(mapping)
        else:
            super().__init__({})
            if shortName is not None:
                self.shortName = shortName
            if longName is not None:
                self.longName = longName
            if categoryID is not None:
                self.categoryID = categoryID
            if generalTextChannelID is not None:
                self.generalTextChannelID = generalTextChannelID
            if generalVoiceChannelID is not None:
                self.generalVoiceChannelID = generalVoiceChannelID
            if participantRoleID is not None:
                self.participantRoleID = participantRoleID
            if jammerRoleID is not None:
                self.jammerRoleID = jammerRoleID
            if startUnix is not None:
                self.startUnix = startUnix
            if endUnix is not None:
                self.endUnix = endUnix
            if url is not None:
                self.url = url
            if description is not None:
                self.description = description
        self['_type'] = 'meta'

class JamParticipant(dict):

    @property
    def discordID(self) -> int:
        return self.get('discordID')
    
    @discordID.setter
    def discordID(self,value : int):
        self['discordID'] = int(value)

    @property
    def teamID(self) -> int:
        return self.get('teamID')
    
    @teamID.setter
    def teamID(self,value : int):
        self['teamID'] = int(value)

    def __init__(self,
                discordID : int = -1,
                teamID : int = -1,
                *,
                mapping : Mapping | None = None):
        if mapping is not None:
            super().__init__(mapping)
        else:  
            super().__init__({})
            
            self.discordID = discordID
            self.teamID = teamID

class JamTeam(dict):

    @property
    def isEmpty(self) -> bool:
        if len(self.members) < 1 and self.leader == -1:
            return True
        return False

    @property
    def textChannelID(self) -> int:
        return self.get('textChannelID')
    
    @textChannelID.setter
    def textChannelID(self,value : int):
        self['textChannelID'] = int(value)

    @property
    def voiceChannelID(self) -> int:
        return self.get('voiceChannelID')
    
    @voiceChannelID.setter
    def voiceChannelID(self,value : int):
        self['voiceChannelID'] = int(value)

    @property
    def leader(self) -> int:
        return self.get('leader')

    @leader.setter
    def leader(self, value: int):
        self['leader'] = int(value)

    @property
    def members(self) -> list[int]:
        return self.get('members')
    
    @members.setter
    def members(self, value: list[int]):
        self['members'] = list(map(int, value))

    def add_participant(self,new_participant_id : int):

        if self.leader == -1:
            self.leader = new_participant_id
        else:
            self.members.append(new_participant_id)

    def remove_participant(self,removed_participant_id : int):
        if self.leader == removed_participant_id:
            if len(self.members) > 0:
                self.leader = self.members[0]
                self.members.pop(0)
            else:
                self.leader = -1
        elif removed_participant_id in self.members:
            self.members.remove(removed_participant_id)

    def change_leader(self,new_leader_participant_id : int):
        raise NotImplementedError()

    @property
    def submitted(self) -> bool:
        return self.get('submitted')

    @submitted.setter
    def submitted(self,value : bool):
        self['submitted'] = bool(value)

    @property
    def teamName(self) -> str:
        return self.get('teamName')

    @teamName.setter
    def teamName(self,value : str):
        self['teamName'] = str(value)

    @property
    def gameURL(self) -> str:
        return self.get('gameURL')
    
    @gameURL.setter
    def gameURL(self,value : str):
        self['gameURL'] = str(value)

    @property
    def joinRequests(self) -> list[int]:
        return self.get('joinRequests')
    
    @joinRequests.setter
    def joinRequests(self, value : list[int]):
        self['joinRequests'] = list(map(int,value))

    def addJoinRequest(self,participant_id : int):
        if self.joinRequests is not None:
            self.joinRequests.append(int(participant_id))
        else:
            self.joinRequests = [int(participant_id)]

    def removeJoinRequest(self,participant_id : int):
        if self.joinRequests is not None and self.joinRequests.count(participant_id) > 0:
            self.joinRequests.remove(participant_id)

    def __init__(self,
                 teamName : str = "",
                 submitted : bool = False,
                 gameURL : str = "",
                 leader : int = -1,
                 members : list[int] = [],
                 textChannelID : int = -1,
                 voiceChannelID : int = -1,
                 joinRequests : list[int] = [],
                 *,
                 mapping : Mapping | None = None):
        if mapping is not None:
            super().__init__(mapping)
        else:
            super().__init__({})
            self.joinRequests = joinRequests
            self.teamName = teamName
            self.submitted = submitted
            self.gameURL = gameURL
            self.leader = leader
            self.members = members
            self.voiceChannelID = voiceChannelID
            self.textChannelID = textChannelID
