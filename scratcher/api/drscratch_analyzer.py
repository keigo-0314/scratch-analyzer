# 引用元リポジトリ : https://github.com/AngelaVargas/drscratchv3
# Analyzer of projects sb3, the new version Scratch 3.0
import sys
import json
from collections import Counter
import os


class Mastery: 

    """Analyzer of projects sb3, the new version Scratch 3.0"""

    def __init__(self):

        self.mastery_dicc = {}		#New dict to save punctuation
        self.total_blocks = [] #List with blocks
        self.blocks_dicc = Counter()		#Dict with blocks
        self.concepts = ['Abstraction', 'Parallelism', 'Logic', 'Synchronization', 'FlowControl', 'UserInteractivity', 'DataRepresentation']


    """Start the analysis."""
    def process(self, rf_path):
        
        self.write_fname = rf_path.split('/')[-1].replace('.json', '')
        
        # jsonファイルの読み込み
        json_project = json.loads(open(rf_path).read())

        for key, value in iter(json_project.items()):
            if key == 'targets':
                for dicc in value:
                    for dicc_key, dicc_value in iter(dicc.items()):
                        if dicc_key == 'blocks':
                            for blocks, blocks_value in iter(dicc_value.items()):
                                if type(blocks_value) is dict:
                                    self.total_blocks.append(blocks_value)

        for block in self.total_blocks:
            for key, value in iter(block.items()):
                if key == 'opcode':
                    self.blocks_dicc[value] += 1
        

    """Run and return the results of Mastery. """
    def analyze(self, wf_path):
    
        self.logic() 
        self.flow_control()
        self.synchronization()
        self.abstraction()
        self.data_representation()
        self.user_interactivity()
        self.parallelism()
        self.ct_score()
        self.total_score()
        
        save_dir = wf_path.replace(wf_path.split('/')[-1], '')
        os.makedirs(save_dir, exist_ok=True)  # 保存先となるフォルダが存在しない場合は新たに作成する
        fw = open(wf_path, 'w')
        json.dump(self.mastery_dicc, fw, indent=4)


    """Assign CT Score (0-21)"""
    def ct_score(self):
        
        ctscore = 0
        for concept in self.concepts:
            ctscore += self.mastery_dicc[concept]['MaxScore']
        self.mastery_dicc['CTScore'] = ctscore


    """Assign Total Score (0-42)"""
    def total_score(self):
        
        total = 0
        for concept in self.concepts:
            for score in [1, 2, 3]:
                if self.mastery_dicc[concept][score]:
                    total += score
        self.mastery_dicc['Total'] = total
            

    """Assign the Logic skill result"""
    def logic(self):
        
        self.mastery_dicc['Logic'] = {1: False, 2: False, 3: False}
        
        operations = {'operator_and', 'operator_or', 'operator_not'}
        
        # -----------------------------------
        # 3点の計測処理
        # -----------------------------------
        for operation in operations:
            if self.blocks_dicc[operation]:
                self.mastery_dicc['Logic'][3] = True

        # -----------------------------------
        # 2点の計測処理
        # -----------------------------------
        if self.blocks_dicc['control_if_else']:
            self.mastery_dicc['Logic'][2] = True

        # -----------------------------------
        # 1点の計測処理
        # -----------------------------------
        if self.blocks_dicc['control_if']:
            self.mastery_dicc['Logic'][1] = True
        
        # -----------------------------------
        # 最高点数の計測処理
        # -----------------------------------
        max_score = 0
        for i in range(3, 0, -1):
            if self.mastery_dicc['Logic'][i]:
                max_score = i
                break
        self.mastery_dicc['Logic']['MaxScore'] = max_score


    """Assign the Flow Control skill result"""     
    def flow_control(self):

        self.mastery_dicc['FlowControl'] = {1: False, 2: False, 3: False}

        # -----------------------------------
        # 3点の計測処理
        # -----------------------------------
        if self.blocks_dicc['control_repeat_until']:
            self.mastery_dicc['FlowControl'][3] = True
        
        # -----------------------------------
        # 2点の計測処理
        # -----------------------------------
        if (self.blocks_dicc['control_repeat'] or self.blocks_dicc['control_forever']):
            self.mastery_dicc['FlowControl'][2] = True

        # -----------------------------------
        # 1点の計測処理
        # -----------------------------------
        for block in self.total_blocks:
            for key, value in iter(block.items()):
                if key == "next" and value != None:
                    self.mastery_dicc['FlowControl'][1] = True
                    break
                
        # -----------------------------------
        # 最高点数の計測処理
        # -----------------------------------
        max_score = 0
        for i in range(3, 0, -1):
            if self.mastery_dicc['FlowControl'][i]:
                max_score = i
                break
        self.mastery_dicc['FlowControl']['MaxScore'] = max_score
        

    """Assign the Syncronization skill result"""
    def synchronization(self):

        self.mastery_dicc['Synchronization'] = {1: False, 2: False, 3: False}

        # -----------------------------------
        # 3点の計測処理
        # -----------------------------------
        if self.blocks_dicc['control_wait_until'] or self.blocks_dicc['event_whenbackdropswitchesto'] or self.blocks_dicc['event_broadcastandwait']:
            self.mastery_dicc['Synchronization'][3] = True

        # -----------------------------------
        # 2点の計測処理
        # -----------------------------------
        if self.blocks_dicc['event_broadcast'] or self.blocks_dicc['event_whenbroadcastreceived'] or self.blocks_dicc['control_stop']:
            self.mastery_dicc['Synchronization'][2] = True
        
        # -----------------------------------
        # 1点の計測処理
        # -----------------------------------
        if self.blocks_dicc['control_wait']:
            self.mastery_dicc['Synchronization'][1] = True

        # -----------------------------------
        # 最高点数の計測処理
        # -----------------------------------
        max_score = 0
        for i in range(3, 0, -1):
            if self.mastery_dicc['Synchronization'][i]:
                max_score = i
                break
        self.mastery_dicc['Synchronization']['MaxScore'] = max_score


    """Assign the Abstraction skill result"""
    def abstraction(self):
            
        self.mastery_dicc['Abstraction'] = {1: False, 2: False, 3: False}
                
        # -----------------------------------
        # 3点の計測処理
        # -----------------------------------
        if self.blocks_dicc['control_start_as_clone']:
            self.mastery_dicc['Abstraction'][3] = True
        
        # -----------------------------------
        # 2点の計測処理
        # -----------------------------------
        if self.blocks_dicc['procedures_definition']:
            self.mastery_dicc['Abstraction'][2] = True

        # -----------------------------------
        # 1点の計測処理
        # -----------------------------------
        count = 0
        for block in self.total_blocks:
            for key, value in iter(block.items()):
                if key == "parent" and value == None:
                    count += 1
        if count > 1 :
            self.mastery_dicc['Abstraction'][1] = True

        # -----------------------------------
        # 最高点数の計測処理
        # -----------------------------------
        max_score = 0
        for i in range(3, 0, -1):
            if self.mastery_dicc['Abstraction'][i]:
                max_score = i
                break
        self.mastery_dicc['Abstraction']['MaxScore'] = max_score


    """Assign the Data representation skill result"""
    def data_representation(self):

        self.mastery_dicc['DataRepresentation'] = {1: False, 2: False, 3: False}
        
        modifiers = {
            'motion_movesteps', 'motion_gotoxy', 'motion_glidesecstoxy', 'motion_setx', 'motion_sety', 
            'motion_changexby', 'motion_changeyby', 'motion_pointindirection', 'motion_pointtowards',
            'motion_turnright', 'motion_turnleft', 'motion_goto', 
            'looks_changesizeby', 'looks_setsizeto', 'looks_switchcostumeto', 'looks_nextcostume', 
            'looks_changeeffectby', 'looks_seteffectto', 'looks_show', 'looks_hide', 'looks_switchbackdropto', 
            'looks_nextbackdrop'
        }

        lists = {
            'data_lengthoflist', 'data_showlist', 'data_insertatlist', 'data_deleteoflist', 'data_addtolist',
            'data_replaceitemoflist', 'data_listcontainsitem', 'data_hidelist', 'data_itemoflist'
        }
            
        # -----------------------------------
        # 3点の計測処理
        # -----------------------------------
        for item in lists:
            if self.blocks_dicc[item]:
                self.mastery_dicc['DataRepresentation'][3] = True
                break

        # -----------------------------------
        # 2点の計測処理
        # -----------------------------------
        if self.blocks_dicc['data_changevariableby'] or self.blocks_dicc['data_setvariableto']:
            self.mastery_dicc['DataRepresentation'][2] = True

        # -----------------------------------
        # 1点の計測処理
        # -----------------------------------
        for modifier in modifiers:
            if self.blocks_dicc[modifier]:
                self.mastery_dicc['DataRepresentation'][1] = True

        # -----------------------------------
        # 最高点数の計測処理
        # -----------------------------------
        max_score = 0
        for i in range(3, 0, -1):
            if self.mastery_dicc['DataRepresentation'][i]:
                max_score = i
                break
        self.mastery_dicc['DataRepresentation']['MaxScore'] = max_score


    """Assign the User Interactivity skill result"""
    def user_interactivity(self):

        self.mastery_dicc['UserInteractivity'] = {1: False, 2: False, 3: False}

        proficiency = {
            'videoSensing_videoToggle', 'videoSensing_videoOn', 'videoSensing_whenMotionGreaterThan',
            'videoSensing_setVideoTransparency', 'sensing_loudness'
        }
                
        developing = {
            'event_whenkeypressed', 'event_whenthisspriteclicked', 'sensing_mousedown', 
            'sensing_keypressed', 'sensing_askandwait', 'sensing_answer'
        }

        # -----------------------------------
        # 3点の計測処理
        # -----------------------------------
        for item in proficiency:
            if self.blocks_dicc[item]:
                self.mastery_dicc['UserInteractivity'][3] = True
                break
            
        # -----------------------------------
        # 2点の計測処理
        # -----------------------------------
        for item in developing:
            if self.blocks_dicc[item]:
                self.mastery_dicc['UserInteractivity'][2] = True
                break

        if self.mastery_dicc['UserInteractivity'][2] == False:
            if self.blocks_dicc['motion_goto_menu']:
                if self.check_mouse() == 1:
                    self.mastery_dicc['UserInteractivity'][2] = True
            elif self.blocks_dicc['sensing_touchingobjectmenu']:
                if self.check_mouse() == 1:
                    self.mastery_dicc['UserInteractivity'][2] = True

        # -----------------------------------
        # 1点の計測処理
        # -----------------------------------
        if self.blocks_dicc['event_whenflagclicked']:
            self.mastery_dicc['UserInteractivity'][1] = True
        
        # -----------------------------------
        # 最高点数の計測処理
        # -----------------------------------
        max_score = 0
        for i in range(3, 0, -1):
            if self.mastery_dicc['UserInteractivity'][i]:
                max_score = i
                break
        self.mastery_dicc['UserInteractivity']['MaxScore'] = max_score


    """Check whether there is a block 'go to mouse' or 'touching mouse-pointer?' """
    def check_mouse(self):

        for block in self.total_blocks:
            for key, value in iter(block.items()):
                if key == 'fields':
                    for mouse_key, mouse_val in iter(value.items()):
                        if (mouse_key == 'TO' or mouse_key =='TOUCHINGOBJECTMENU') and mouse_val[0] == '_mouse_':
                                return 1
        return 0


    """Assign the Parallelism skill result"""
    def parallelism (self):
        
        self.mastery_dicc['Parallelism'] = {1: False, 2: False, 3: False}
        
        dict_parall = {}

        dict_parall = self.Parallelism_dict()

        # -----------------------------------
        # 3点の計測処理
        # -----------------------------------
        if self.blocks_dicc['event_whenbroadcastreceived'] > 1:            # 2 Scripts start on the same received message
            if dict_parall['BROADCAST_OPTION']:
                var_list = set(dict_parall['BROADCAST_OPTION'])
                for var in var_list:
                    if dict_parall['BROADCAST_OPTION'].count(var) > 1:
                        self.mastery_dicc['Parallelism'][3] = True
        elif self.blocks_dicc['event_whenbackdropswitchesto'] > 1:           # 2 Scripts start on the same backdrop change
            if dict_parall['BACKDROP']:
                backdrop_list = set(dict_parall['BACKDROP'])
                for var in backdrop_list:
                    if dict_parall['BACKDROP'].count(var) > 1:
                        self.mastery_dicc['Parallelism'][3] = True
        elif self.blocks_dicc['event_whengreaterthan'] > 1:                  # 2 Scripts start on the same multimedia (audio, timer) event
            if dict_parall['WHENGREATERTHANMENU']:
                var_list = set(dict_parall['WHENGREATERTHANMENU'])
                for var in var_list:
                    if dict_parall['WHENGREATERTHANMENU'].count(var) > 1:
                        self.mastery_dicc['Parallelism'][3] = True
        elif self.blocks_dicc['videoSensing_whenMotionGreaterThan'] > 1:     # 2 Scripts start on the same multimedia (video) event
            self.mastery_dicc['Parallelism'][3] = True

        # -----------------------------------
        # 2点の計測処理
        # -----------------------------------
        if self.blocks_dicc['event_whenkeypressed'] > 1:                   # 2 Scripts start on the same key pressed
            if dict_parall['KEY_OPTION']:
                var_list = set(dict_parall['KEY_OPTION'])
                for var in var_list:
                    if dict_parall['KEY_OPTION'].count(var) > 1:
                        self.mastery_dicc['Parallelism'][2] = True
        elif self.blocks_dicc['event_whenthisspriteclicked'] > 1:           # Sprite with 2 scripts on clicked
            self.mastery_dicc['Parallelism'][2] = True

        # -----------------------------------
        # 1点の計測処理
        # -----------------------------------
        if self.blocks_dicc['event_whenflagclicked'] > 1:  # 2 scripts on green flag
            self.mastery_dicc['Parallelism'][1] = True
            
        # -----------------------------------
        # 最高点数の計測処理
        # -----------------------------------
        max_score = 0
        for i in range(3, 0, -1):
            if self.mastery_dicc['Parallelism'][i]:
                max_score = i
                break
        self.mastery_dicc['Parallelism']['MaxScore'] = max_score
        

    def Parallelism_dict(self):
        dicc = {}

        for block in self.total_blocks:
            for key, value in iter(block.items()):
                if key == 'fields':
                    for key_pressed, val_pressed in iter(value.items()):
                        if key_pressed in dicc:
                            dicc[key_pressed].append(val_pressed[0])
                        else:
                            dicc[key_pressed] = val_pressed
        return dicc


if __name__ == '__main__':
        
    try:
        rf_path = sys.argv[1]     # 読み込み先のファイルパス
        wf_path = sys.argv[2]     # 書き込み先のファイルパス
        mastery = Mastery()
        mastery.process(rf_path)
        mastery.analyze(wf_path)
    except Exception as e:
        print(e)