import numpy as np

import copy

class ManaPool:
    #---------------------------------------------------------------------------
    def __init__(self,
        initial_mana = {
            'w' : 0,
            'u' : 0,
            'b' : 0,
            'r' : 0,
            'g' : 0,
            'c' : 0,
            },
        default_spending_priority:list = 'wbcgru',
        default_adding_priority:list = 'urgbwc',
        ):
        
        self.colors = 'wubrgc'
        self.default_spending_priority = default_spending_priority
        self.default_adding_priority = default_adding_priority
   
        self.mana_pool = self.process_mana(initial_mana)

    #---------------------------------------------------------------------------
    def process_mana(self, mana = 'rr'):
        '''
        PURPOSE
        '''
        output_mana = {
            'w' : 0,
            'u' : 0,
            'b' : 0,
            'r' : 0,
            'g' : 0,
            'c' : 0,
            }

        if isinstance(mana, dict):
            for pip, amount in mana.items():
                try:
                    output_mana[pip] += amount
                except KeyError:
                    output_mana[pip] = amount

        elif isinstance(mana, str):
            for pip in mana:
                try:
                    output_mana[pip] += 1
                except KeyError:
                    output_mana[pip] = 1
        
        return output_mana
    
    #---------------------------------------------------------------------------
    def add(self, add_mana:dict):
        if isinstance(add_mana, dict):
            for pip, amount in add_mana.items():
                try:
                    self.mana_pool[pip] += amount
                except KeyError:
                    self.mana_pool[pip] = amount

        elif isinstance(add_mana, str):
            for pip in add_mana:
                output_mana[pip] += 1
    #---------------------------------------------------------------------------
    def spend(self, 
        mana_cost:dict, 
        spending_priority:str='default',
        LEAVE_ONE_FLAG:bool = True,
        ):
        '''
        PURPOSE
        Spends mana from mana pool
        '''
        #-----------------------------------------------------------------------
        def spend_mana(mana_pool, mana_cost, LEAVE_ONE_FLAG):
            try:
                due = mana_cost['y']
            except KeyError:
                due = 0
            
            remaining_mana = {}
            for pip in spending_priority:
                ck0 = mana_pool[pip]
                ck1 = mana_cost[pip]
                
                if LEAVE_ONE_FLAG and pip != 'c': 
                    remainder = 1
                else:
                    remainder = 0

                ck2 = np.min([(ck0 - ck1) - np.min([ck0 - ck1, remainder]), due])
                due -= ck2    
                
                remaining_mana[pip] = int(ck0 - ck1 - ck2)
                
            mana_due = self.process_mana({'y':due})
            return remaining_mana, mana_due
        
        #-----------------------------------------------------------------------
        if spending_priority == 'default':
            spending_priority = self.default_spending_priority
        
        mana_cost = self.process_mana(mana_cost)
        try:
            unspecified_cost = mana_cost['y']
        except KeyError:
            unspecified_cost = 0

        # Check if we have enough pips, if so, PIP_FLAG = 1
        PIPS_FLAG = 1
        CAST_FLAG = False
        remaining_mana = 0
        
        missing_pips = {}
        comment = ''
        for pip in 'wubrgc':
            if self.mana_pool[pip] >= mana_cost[pip]:
                remaining_mana += self.mana_pool[pip] - mana_cost[pip]
                pass
            else:
                PIPS_FLAG *= 0
                missing_pips[pip] = mana_cost[pip] - self.mana_pool[pip]
                comment = comment + f'Insufficient {pip} pips. '
                CAST_FLAG = False

        if remaining_mana < unspecified_cost:
            PIPS_FLAG *= 0
            comment = 'Insufficient mana after pips are assigned'
            CAST_FLAG = False
            missing_pips['y'] = unspecified_cost - remaining_mana

        if not PIPS_FLAG:
            return CAST_FLAG, missing_pips

        elif LEAVE_ONE_FLAG:
            remaining_mana, mana_due = spend_mana(self.mana_pool, mana_cost, LEAVE_ONE_FLAG)
            
            if mana_due['y'] == 0:
                self.mana_pool = remaining_mana
                CAST_FLAG = True 
                return CAST_FLAG, missing_pips
            else:
                remaining_mana, mana_due = spend_mana(remaining_mana, mana_due, False)
                self.mana_pool = remaining_mana
                comment =  'Unable to leave one pip of each color'
                CAST_FLAG = True 
                return CAST_FLAG, missing_pips
        else:
            remaining_mana, mana_due = spend_mana(self.mana_pool, mana_cost, LEAVE_ONE_FLAG)
            if mana_due['y'] == 0:
                self.mana_pool = remaining_mana
                
                CAST_FLAG = True 
                return CAST_FLAG, missing_pips
    
    #---------------------------------------------------------------------------
    def total(self):
        '''
        PURPOSE

        '''
        count = 0
        for pip, amount in self.mana_pool.items():
            if pip != 'y':
                count += amount

        return count

    #---------------------------------------------------------------------------
    def check_castable(self, 
        mana_cost,
        spending_priority:str='default',
        LEAVE_ONE_FLAG:bool = True,
        ):
        copy_mp = copy.deepcopy(self)
        
        mana_cost = self.process_mana(mana_cost)
        
        CAST_FLAG, missing_pips = copy_mp.spend(
            mana_cost,
            spending_priority,
            LEAVE_ONE_FLAG,
            )
        
        return CAST_FLAG, missing_pips

#-------------------------------------------------------------------------------
if __name__ == "__main__":
    pass


