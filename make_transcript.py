#!/bin/env python3
import sys
import json
from collections import defaultdict

class Transcript:
  def __init__(self, name, desc, campaign):
    self.name = name
    self.description = desc
    self.campaign = campaign
    self.zones = []
  def add_zones(self, adv):
    area_set_id = adv['area_set_id']
    areas = [x for x in area_sets if x['area_set_id'] == area_set_id]
    lastZoneHadEnd = False
    for area in areas:
      quest = [x for x in quests if x['id'] == area['quest_id']][0]
      cinematics_id = area.get('cinematics_id', None)
      if cinematics_id is not None:
        cinematic = [x for x in cinematics if x['id'] == cinematics_id][0]
      else:
        cinematic = None
      zone = Zone(quest, cinematic, lastZoneHadEnd)
      self.zones.append(zone)
      lastZoneHadEnd = zone.hasEnd()
  def to_wiki(self):
    s = []
    s.append('{| class="article-table mw-collapsible" border="0" cellpadding="1" cellspacing="1";')
    s.append(f'! style="text-align: center;" colspan=6|[[File:Icon {self.name}.png|40px]] [[{self.name}]]')
    s.append('|-')
    s.append(f'| style="text-align: center;" colspan=6|{self.description}')
    s.append('|-')
    s.append('''! style="text-align: left;"|Area
! style="text-align: center;"|Goal
! style="text-align: center;"|
! style="text-align: left;" colspan=3|Quests & Cinematics''')
    for n, zone in enumerate(self.zones):
      wiki = zone.to_wiki(n)
      if wiki:
        s.append(wiki)
    s.append(f'''|-
| style="text-align: left;" colspan=2|[[SOMETHING/Transcript|Previous: SOMETHING]]
| style="text-align: right;" colspan=2|[[SOMETHING_ELSE/Transcript|Next: SOMETHING_ELSE]]
|}}
<noinclude>
[[Category:{self.name}]]
[[Category:Transcript]]
[[Category:{self.campaign}]]
</noinclude>
''')
    return '\n'.join(s)
  def graphic_ids(self):
    ids = defaultdict(set)
    for zone in self.zones:
      for mapping in zone.graphic_id_mapping:
        ids[mapping].update(zone.graphic_id_mapping[mapping])
    return ids


class Zone:
  def __init__(self, quest, cinematic, lastZoneHadEnd):
    self.quest = quest
    self.cinematic = cinematic
    self.lastZoneHadEnd = lastZoneHadEnd
    self.graphic_id_mapping = defaultdict(set)
  def hasEnd(self):
    if self.cinematic is None:
      return False
    ends = [x for x in self.cinematic['details'] if x['type'] == 'end']
    return len(ends) > 0
  def quest_text(self):
    if self.quest['type'] == 1:
      num = self.quest['goal_amount']
      name = self.quest['goal_description']
      return f'Collect {num} {name}'
    if self.quest['type'] == 2:
      num = self.quest['goal_amount']
      name = self.quest['goal_description']
      return f'Defeat {num} {name}'
    if self.quest['type'] == 3:
      name = self.quest['goal_description']
      return f'Defeat the {name}'
    if self.quest['type'] == 4:
      num = self.quest['goal_amount']
      name = self.quest['goal_description']
      return f'Collect {num} {name}'
    if self.quest['type'] == 5:
      num = self.quest['goal_amount']
      name = self.quest['goal_description']
      return f'Defeat {num} {name}'
    raise Exception('Unknown quest text type')
  def cinematics_section(self, section, solid_start):
    s = []
    details = section['sequence']
    assert all('type' not in x or x['type'] in ['npc', 'hero', 'show_quest', 'action'] for x in details)
    relevant_details = [x for x in details if 'type' in x and (x['type'] == 'npc' or x['type'] == 'hero')]
    for n, cine in enumerate(relevant_details):
      first_style = 'solid' if solid_start and n == 0 else 'none'
      third_style = 'solid' if n == len(relevant_details) - 1 else 'none'
      style = f'border-style: {first_style} none {third_style} none;'
      s.append(self.saying(style, cine))
    return '\n'.join(s)
  def saying(self, style, cine):
    text = cine['text']
    s = []
    s.append('|-')
    ctype = cine['type']
    if ctype == 'npc':
      name = cine['name']
      graphic = [x for x in game_details['graphic_defines'] if x['id'] == cine['graphic_id']][0]
      image_name = graphic['graphic'].split('/')[-1]
      s.append(f'| style="{style}" | [[File:{image_name}.png|60px]]<br>{name}:')
      self.graphic_id_mapping[cine['graphic_id']].add(name)
    elif ctype == 'hero':
      hero = [x for x in game_details['hero_defines'] if x['id'] == cine['hero_id']][0]['name']
      s.append(f'| style="{style}" | [[File:Icon {hero}.png|60px]]<br>{hero}:')
    else:
      raise Exception('Unknown cinematic detail type')
    s.append(f'| style="{style}" colspan="3" | {text}')
    return '\n'.join(s)
  def to_wiki(self, index):
    s = []
    if self.cinematic is not None:
      details = self.cinematic['details']
      starts = [x for x in details if x['type'] == 'start']
      ends = [x for x in details if x['type'] == 'end']
      assert len(starts) < 2 
      if len(ends) > 1:
        print(ends)
      #assert len(ends) < 2
      assert len(starts) + len(ends) == len(details)
      if len(starts) > 0:
        start = starts[0]
        s.append(self.cinematics_section(start, self.lastZoneHadEnd))
    s.append(f'''|-
| style="text-align: left;"|{index + 1}
| style="text-align: center;"|{self.quest_text()}
| style="text-align: center;"|
| style="text-align: left;" colspan=4|{self.quest['description']}''')
    if self.cinematic is not None and len(ends) > 0:
      end = ends[0]
      s.append(self.cinematics_section(end, False))
    return '\n'.join(s)

def adv_transcript(adv):
  campaign = [x for x in campaigns if x['id'] == adv['campaign_id']][0]
  tran = Transcript(adv['name'], adv['description'], campaign['name'])
  tran.add_zones(adv)
  print(tran.to_wiki())
  return tran

def main(name):
  global user_details
  global game_details
  global adventures
  global area_sets
  global quests
  global cinematics
  global campaigns

  with open('fulljs.json', 'r') as f:
    game_details = json.loads(f.read())
  with open('user_details.json', 'r') as f:
    user_details = json.loads(f.read())
  defines = user_details['defines']
  adventures = defines['adventure_defines']
  area_sets = defines['adventure_area_defines']
  quests = defines['quest_defines']
  cinematics = defines['cinematics_defines']
  campaigns = defines['campaign_defines']
  adv = [x for x in adventures if x['name'] == name]
  if (len(adv) == 0):
    return
  tran = adv_transcript(adv[0])
  print('---')
  print(tran.graphic_ids())
  print('./get_image.sh ' + ' '.join([str(x) for x in sorted(tran.graphic_ids().keys())]))

if __name__ == '__main__':
  main(sys.argv[1])
