from discord import Member,Interaction
from collections.abc import Mapping

class UnogMember(Mapping):

    _data : dict

    def __init__(self,
                 id : int,
                 newName : str = None,
                 eMail : str = None,
                 birthday : str = None,
                 info1 : str = None,
                 info2 : str = None):
        self._data = dict({'name':newName,
                           'email':eMail,
                           'birthday':birthday,
                           'info1':info1,
                           'info2':info2,
                           'id':id})
    
    def __getitem__(self, key):
        return self._data[key]
    
    def __iter__(self):
        return iter(self._data)
    
    def __len__(self):
        return len(self._data)

class ApproveRecord(Mapping):

    _data : dict

    def __init__(self,approvedID : int,approverID : int):
        self._data = dict({'approvedID':approvedID,'approverID':approverID})
    
    def __getitem__(self, key):
        return self._data[key]
    
    def __iter__(self):
        return iter(self._data)
    
    def __len__(self):
        return len(self._data)

class Jam(Mapping):
    _data : dict

    def __init__(self,
                 shortName : str, longName : str, categoryID : int = None ,
                    generalTextChannelID : int = None, generalVoiceChannelID : int = None,
                    participantRoleID : int = None, jammerRoleID : int = None,
                    startUnix : int = None, endUnix : int = None, url : str = None
                    ):
        self._data = dict({'_type':"meta",
                            'shortName':shortName,
                            'longName':longName,
                            'categoryID':categoryID,
                            'generalTextChannelID':generalTextChannelID,
                            'generalVoiceChannelID': generalVoiceChannelID,
                            'participantRoleID': participantRoleID,
                            'jammerRoleID': jammerRoleID,
                            'startUnix': startUnix,
                            'endUnix': endUnix,
                            'url': url})
    
    def __getitem__(self, key):
        return self._data[key]
    
    def __iter__(self):
        return iter(self._data)
    
    def __len__(self):
        return len(self._data)
