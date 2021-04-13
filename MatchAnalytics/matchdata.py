import riotwatcher
import pandas as pd
import urllib as url 
api = 'YOUR API KEY HERE'


############################################################################


class Match(): 
    

    """ A class to get match statistics in a pandas DF for any given league of legends post game url using the package riotwatcher """
    
    
    
    def __init__(self, key, matchurl, region= "na1") : 
           
      
      self.matchid = url.parse.urlsplit(matchurl).fragment.split(sep="/")[2]  
      
      self.key = key 
      
      self.lolwatch = riotwatcher.LolWatcher(self.key)
      
      self.region = region
      
      self.info = self.lolwatch.match.by_id(self.region, self.matchid)
      
      self.versions = self.lolwatch.data_dragon.versions_for_region(region)
      
      self.match_timeline = self.lolwatch.match.timeline_by_match(self.region, self.matchid)
      
      
      """ Riot does not put Ornn's upgraded items in thier data dragon so we read them in here """ 
      
    
      self.ornn_items = {'7000': 	'Sandshrikes Claw',
      '7001' :	'Syzygy',
      '7002' :	'Draktharrs Shadowcarver',
      '7003' :	'Turbocharged Hexperiment',
      '7004' :	'Forgefire Crest',
      '7005' :	'Rimeforged Grasp',
      '7006' :	'Typhoon',
      '7007' :	'Wyrmfallen Sacrifice',
      '7008' :	'Bloodward',
      '7009' :	'Icathias Curse',
      '7010' :	'Vespertide',
      '7011' :	'Upgraded Aeropack',
      '7012' :	'Liandrys Lament',
      '7013' :	'Eye of Luden',
      '7014' :	'Eternal Winter',
      '7015' :	'Ceaseless Hunger',
      '7016' :	'Dreamshatter',
      '7017' :	'Deicide',
      '7018' :	'Infinity Force',
      '7019' :	'Reliquary of the Golden Dawn',
      '7020' :	'Shurelyas Requiem',
      '7021' :	'Starcaster',
      '7022' :	'Seat of Command'}
    
    
   
    def timeline(self): 
        
        
        return self.match_timeline
    
    
    
    def _get_data(self, data): #get information from Riot's Data Dragon 
    
    
      if data == 'champs':
          return pd.DataFrame(self.lolwatch.data_dragon.champions(self.versions['n']['champion'])['data'])
      
      elif data == 'items':
          return pd.DataFrame(self.lolwatch.data_dragon.items(self.versions['n']['item'])['data'])
      
      else:
          print('Error: select items or champs')
          
          
   
    def _get_names(self): # Riot Stores items and champions as a numerical value this function changes that value into the item/champion name 
    
        ornn_items = pd.Series(self.ornn_items)
        
        item_names = self._get_data('items').transpose()['name']
        
        item_names['0'] = 'None'
        
        item_names = pd.concat([item_names, ornn_items])
        
        champion_names =  self._get_data('champs').transpose().set_index('key')['name']
        
        gamestats = self.info['participants']
        
        for player in range(10):
            for item_num in range(7):
                gamestats[player]['stats']['item' + str(item_num)] = item_names.loc[str(gamestats[player]['stats']['item' + str(item_num)])]
        
        for player in range(10):
            gamestats[player]['championId'] = champion_names.loc[str(gamestats[player]['championId'])]
           
        return pd.DataFrame(gamestats)
    
   
    
   
    def _make_tidy(self):
        
        
        cols_list = ['participantId', 'teamId','championId','spell1Id','spell2Id']
        
        data  = self._get_names()
        
        participants = data[cols_list]
        
        stats = data['stats'].to_dict()
        
        timeline = data['timeline'].to_dict()
        
        stats_df = pd.DataFrame.from_dict(stats).transpose()
        
        timeline_df = pd.DataFrame.from_dict(timeline).transpose()
        
        match_wide= participants.merge(stats_df, on='participantId').merge(timeline_df, on='participantId')
        
        return match_wide     
    
    
    
    
    def stats(self):
        
        
        meta = self.info
        
        data = self._make_tidy()
        
            
                  
            
        data['kpm'] = (data['kills'])/ (meta['gameDuration'] / 60)
        
        data['dpm'] = data['totalDamageDealtToChampions'] / (meta['gameDuration'] / 60)
        
        data['gmp'] = data['goldEarned'] / (meta['gameDuration'] / 60)
        
        return data
    
    
    
    
    def teamstats(self):
        
        
        team_data = self.info['teams']
        
        champs = self._get_data('champs').transpose().set_index('key')
        
        for i in range(5): 
            team_data[0]['bans'][i]['championId'] = champs.loc[str(team_data[0]['bans'][i]['championId'])]['id']
        
        for i in range(5):
            team_data[1]['bans'][i]['championId'] = champs.loc[str(team_data[1]['bans'][i]['championId'])]['id']
            
        return team_data
        
   
        
