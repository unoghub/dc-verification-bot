from discord import Member,Interaction
from collections.abc import Mapping
from tinydb.table import Document

class UnogMember(Mapping):

    _data : dict

    @property
    def id(self) -> int:
        return self._data['id']
    
    @id.setter
    def id(self,value : int):
        self._data['id'] = value

    @property
    def name(self) -> str:
        return self._data['name']

    @name.setter
    def name(self,value : str):
        self._data['name'] = value.strip().title()

    @property
    def email(self) -> str:
        return self._data['email']
    
    @email.setter
    def email(self,value : str):
        self._data['email'] = value.strip()

    @property
    def birthday(self) -> str:
        return self._data['birthday']
    
    @birthday.setter
    def birthday(self,value : str):
        self._data['birthday'] = value

    @property
    def info1(self) -> str:
        return self._data['info1']
    
    @info1.setter
    def info1(self,value : str):
        self._data['info1'] = value.strip()
    
    @property
    def info2(self) -> str:
        return self._data['info2']
    
    @info2.setter
    def info2(self,value : str):
        self._data['info2'] = value.strip()
    
    def __init__(self,
                 id : int,
                 name : str = None,
                 email : str = None,
                 birthday : str = None,
                 info1 : str = None,
                 info2 : str = None,
                 data : dict = None):
        if data:
            self._data = data
        else:
            self._data = dict()
            self.name = name
            self.email = email
            self.birthday = birthday
            self.info1 = info1
            self.info2 = info2
            self.id = id
    
    def __getitem__(self, key):
        return self._data[key]
    
    def __iter__(self):
        return iter(self._data)
    
    def __len__(self):
        return len(self._data)

class ApproveRecord(Mapping):

    _data : dict
    @property
    def approvedID(self) -> int:
        return self._data['approvedID']
    
    @approvedID.setter
    def approvedID(self, value : int):
        self._data['approvedID'] = value

    @property
    def approverID(self) -> int:
        return self._data['approverID']

    @approverID.setter
    def approverID(self, value : int):
        self._data['approverID'] = value

    
    def __init__(self,approvedID : int,approverID : int, data : dict = None):
        if data:
            self._data = data
        else:
            self._data = dict()
            self.approvedID = approvedID
            self.approverID = approverID
    
    def __getitem__(self, key):
        return self._data[key]
    
    def __iter__(self):
        return iter(self._data)
    
    def __len__(self):
        return len(self._data)

class Jam(Mapping):
    _data : dict

    @property
    def shortName(self) -> str:
        return self._data['shortName']

    @shortName.setter
    def shortName(self,value : str):
        self._data['shortName'] = value

    @property
    def longName(self) -> str:
        return self._data['longName']

    @longName.setter
    def longName(self,value : str):
        self._data['longName'] = value

    @property
    def categoryID(self) -> int:
        return self._data['categoryID']

    @categoryID.setter
    def categoryID(self,value : int):
        self._data['categoryID'] = value

    @property
    def generalTextChannelID(self) -> int:
        return self._data['generalTextChannelID']

    @generalTextChannelID.setter
    def generalTextChannelID(self,value : int):
        self._data['generalTextChannelID'] = value

    @property
    def generalVoiceChannelID(self) -> int:
        return self._data['generalVoiceChannelID']

    @generalVoiceChannelID.setter
    def generalVoiceChannelID(self,value : int):
        self._data['generalVoiceChannelID'] = value

    @property
    def participantRoleID(self) -> int:
        return self._data['participantRoleID']

    @participantRoleID.setter
    def participantRoleID(self,value : int):
        self._data['participantRoleID'] = value

    @property
    def jammerRoleID(self) -> int:
        return self._data['jammerRoleID']

    @jammerRoleID.setter
    def jammerRoleID(self,value : int):
        self._data['jammerRoleID'] = value

    @property
    def startUnix(self) -> int:
        return self._data['startUnix']

    @startUnix.setter
    def startUnix(self,value : int):
        self._data['startUnix'] = value

    @property
    def endUnix(self) -> int:
        return self._data['endUnix']

    @endUnix.setter
    def endUnix(self,value : int):
        self._data['endUnix'] = value

    @property
    def url(self) -> str:
        return self._data['url']

    @url.setter
    def url(self,value : str):
        self._data['url'] = value
    
    @property
    def description(self) -> str:
        return self._data['description']

    @description.setter
    def description(self,value : str):
        self._data['description'] = value
    
    def __init__(self,
                 shortName : str = None, longName : str = None, categoryID : int = None ,
                    generalTextChannelID : int = None, generalVoiceChannelID : int = None,
                    participantRoleID : int = None, jammerRoleID : int = None,
                    startUnix : int = None, endUnix : int = None, url : str = None, description : str = None,
                    data : dict = None):
        if data:
            self._data = data
        else:
            self._data = dict()
            self.shortName = shortName
            self.longName = longName
            self.categoryID = categoryID
            self.generalTextChannelID = generalTextChannelID
            self.generalVoiceChannelID = generalVoiceChannelID
            self.participantRoleID = participantRoleID
            self.jammerRoleID = jammerRoleID
            self.startUnix = startUnix
            self.endUnix = endUnix
            self.url = url
            self.description = description
        self._data['_type'] = 'meta'

    def __getitem__(self, key):
        return self._data[key]
    
    def __iter__(self):
        return iter(self._data)
    
    def __len__(self):
        return len(self._data)

class JamParticipant(Mapping):

    _data : dict

    @property
    def discordID(self) -> int:
        return self._data['discordID']
    
    @discordID.setter
    def discordID(self,value : int):
        self._data['discordID'] = value

    @property
    def teamID(self) -> int:
        return self._data['teamID']
    
    @teamID.setter
    def teamID(self,value : int):
        self._data['teamID'] = value

    def __init__(self, discordID : int = -1, teamID : int = -1,data : dict = None):
        if data:
            self._data = data
        else:  
            self._data = dict()
            self.discordID = discordID
            self.teamID = teamID

    def __getitem__(self, key):
        return self._data[key]
    
    def __iter__(self):
        return iter(self._data)
    
    def __len__(self):
        return len(self._data)
    pass

class JamTeam(Mapping):
    _data : dict

    @property
    def textChannelID(self) -> int:
        return self._data['textChannelID']
    
    @textChannelID.setter
    def textChannelID(self,value : int):
        self._data['textChannelID'] = value

    @property
    def voiceChannelID(self) -> int:
        return self._data['voiceChannelID']
    
    @voiceChannelID.setter
    def voiceChannelID(self,value : int):
        self._data['voiceChannelID'] = value

    @property
    def leader(self) -> int:
        return self._data('leader')

    @leader.setter
    def leader(self, value: int):
        self._data['leader'] = value

    @property
    def members(self) -> list[int]:
        return self._data['members']
    
    @members.setter
    def members(self, value: list[int]):
        self._data['members'] = value

    def add_member(self,newMemberId : int):
        self._data['members'].append(newMemberId)

    def remove_member(self,removedMemberId : int):
        members : list[int] = self._data['members']
        if removedMemberId in members:
            members.remove(removedMemberId)

    @property
    def submitted(self) -> bool:
        return self._data['submitted']

    @submitted.setter
    def submitted(self,value : bool):
        self._data['submitted'] = value

    @property
    def teamName(self) -> str:
        return self._data['teamName']

    @teamName.setter
    def teamName(self,value : str):
        self._data['teamName'] = value

    @property
    def gameURL(self) -> str:
        return self._data['gameURL']
    
    @gameURL.setter
    def gameURL(self,value : str):
        self._data['gameURL'] = value

    def __init__(self,teamName : str = "",
                 submitted : bool = False,
                 gameURL : str = "",
                 leader : int = -1,
                 members : list[int] = [],
                 textChannelID : int = -1,
                 voiceChannelID : int = -1,
                 data : dict = None):
        if data:
            self._data = data
        else:
            self._data = dict()
            self.teamName = teamName
            self.submitted = submitted
            self.gameURL = gameURL
            self.leader = leader
            self.members = members
            self.voiceChannelID = voiceChannelID
            self.textChannelID = textChannelID
        
    def __getitem__(self, key):
        return self._data[key]
    
    def __iter__(self):
        return iter(self._data)
    
    def __len__(self):
        return len(self._data)
