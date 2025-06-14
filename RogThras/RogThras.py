import numpy as np

# For processing txts from Moxfield
import re

# For determining max available mana
import copy

from tqdm import tqdm
from pprint import pprint

from ManaPool import ManaPool
from GeneralFunctions import *

REV_CARD_TYPES = {
    1          :'creature',
    10         :'sorcery',
    100        :'instant',
    1000       :'artifact',
    10000      :'enchantment',
    100000     :'land',
    }
CARD_TYPES = dict((val, key) for key, val in REV_CARD_TYPES.items())

REV_SPECIAL_TYPES = {
    0       : None,
    1       : 'wincon',
    10      : 'cost_reducer',
    100     : 'ritual',
    200     : 'conditional_ritual',
    1000    : 'creature_tutor',
    2000    : 'conditional_creature_tutor',
    10000   : 'land_tutor',
    100000  : 'other_tutor',
    1000000 : 'recursion',
    }
SPECIAL_TYPES = dict((val, key) for key, val in REV_SPECIAL_TYPES.items())

ALL_CARDS = {
    # Commanders
    "Rograkh, Son of Rohgahh"           : [1, 0, 0, ''], 
    "Thrasios, Triton Hero"             : [1, 0, 2, "ug"], 
    
    # Tokens
    "Creature Token"                    : [1, 0, 0, ''],

    # Creatures
    "Arbor Elf"                         : [1, 0, 1, 'g'], 
    "Biomancer's Familiar"              : [1, 10, 2, 'ug'], 
    "Birds of Paradise"                 : [1, 0, 1, 'g'], 
    "Clever Impersonator"               : [1, 0, 4, 'yyuu'], 
    "Cloud of Faeries"                  : [1, 100, 2, 'yu'], 
    "Delighted Halfling"                : [1, 0, 1, 'g'],
    "Displacer Kitten"                  : [1, 200, 4, 'yyyu'], 
    "Druid of Purification"             : [1, 0, 4, 'yyyg'],
    "Enduring Vitality"                 : [1, 0, 3, 'ygg'], 
    "Eternal Witness"                   : [1, 1000000, 3, 'ygg'], 
    "Faerie Mastermind"                 : [1, 0, 2, 'yu'], 
    "Flesh Duplicate"                   : [1, 0, 2, 'uu'],
    "Gilded Drake"                      : [1, 0, 2, 'yu'],
    "Magus of the Candelabra"           : [1, 0, 1, 'g'], 
    "Mockingbird"                       : [1, 0, 2, 'xu'],
    "Oboro Breezecaller"                : [1, 1, 2, 'yu'], 
    "Phantasmal Image"                  : [1, 0, 2, 'yu'],
    "Phyrexian Metamorph"               : [1, 0, 3, 'yyy'],
    "Seedborn Muse"                     : [1, 0, 5, 'yyygg'], 
    "Sowing Mycospawn"                  : [1, 0, 4, 'yyyg'], 
    "Spellseeker"                       : [1, 0, 3, 'yyu'], 
    "Spellskite"                        : [1, 0, 2, 'yy'],
    "Springheart Nantuko"               : [1, 0, 2, 'yg'], 
    "Thundertrap Trainer"               : [1, 0, 2, 'yu'], 
    "Trinket Mage"                      : [1, 0, 3, 'yyu'], 
    "Valley Floodcaller"                : [1, 0, 3, 'yyu'], 
    "Wall of Roots"                     : [1, 0, 2, 'yg'],

    # Sorceries
    "Chatterstorm"                      : [10, 100, 2,'yg'],
    "Eldritch Evolution"                : [10, 1000, 3, 'ygg'],
    "Finale of Devastation"             : [10, 1000, 10, 'xgg'],
    "Gamble"                            : [10, 100000, 1,'r'],
    "Green Sun's Zenith"                : [10, 1000, 10,'xg'],
    "Malevolent Rumble"                 : [10, 0, 2,'yg'],
    "Nature's Rhythm"                   : [10, 1000, 10,'xgg'],
    "Song of Totentanz"                 : [10, 100, 2,'xr'],
    "Step Through"                      : [10, 1000, 2,'yy'],
    "Sylvan Scrying"                    : [10, 10000, 2,'yg'],
    "Tempt with Discovery"              : [10, 10000, 4,'yyyg'],
    "Traverse the Ulvenwald"            : [10, 0, 1,'g'],

    # Battles
    "Invasion of Ikoria"                : [10, 1000, 10,'xgg'],
    
    # Instants
    "Banishing Knack"                   : [100, 0, 1, 'u'],
    "Borne Upon a Wind"                 : [100, 0, 2, 'yu'],
    "Brain Freeze"                      : [100, 0, 2, 'yu'],
    "Chain of Vapor"                    : [100, 100, 1, 'u'],
    "Chord of Calling"                  : [100, 1000, 10, 'xggg'],
    "Crop Rotation"                     : [100, 10000, 1, 'g'],
    "Cyclonic Rift"                     : [100, 0, 2, 'yu'],
    "Deflecting Swat"                   : [100, 0, 0, 'yyr'],
    "Fierce Guardianship"               : [100, 0, 0, 'yyu'],
    "Flare of Denial"                   : [100, 0, 0, 'yuu'],
    "Flare of Duplication"              : [100, 0, 0, 'urr'],
    "Flusterstorm"                      : [100, 0, 1, 'u'],
    "Force of Will"                     : [100, 0, 0, 'yyyuu'],
    "Frantic Search"                    : [100, 100, 3, 'yyu'],
    "Mental Misstep"                    : [100, 0, 0, 'u'],
    "Mindbreak Trap"                    : [100, 0, 0, 'yyuu'],
    "Noxious Revival"                   : [100, 1000000, 0, 'g'],
    "Pact of Negation"                  : [100, 0, 0, ''],
    "Snap"                              : [100, 100, 1, 'yu'],
    "Swan Song"                         : [100, 0, 0, 'u'],
    "This Town Ain't Big Enough"        : [100, 0, 2, 'yu'],
    "Veil of Summer"                    : [100, 0, 1, 'g'],

    # Artifacts
    "Candelabra of Tawnos"              : [1000, 100, 1, 'y'],
    "Chrome Mox"                        : [1000, 100, 0, ''],
    "Expedition Map"                    : [1000, 10000, 1, 'y'],
    "Lion's Eye Diamond"                : [1000, 100, 0, ''],
    "Lotus Petal"                       : [1000, 100, 0, ''],
    "Machine God's Effigy"              : [1000, 0, 4, 'yyyu'],
    "Mana Vault"                        : [1000, 100, 1, 'y'],
    "Mox Amber"                         : [1000, 100, 0, ''],
    "Mox Diamond"                       : [1000, 200, ''],
    "Sol Ring"                          : [1000, 100, 1, 'y'],
    "Springleaf Drum"                   : [1000, 0, 1, 'y'],
    "The One Ring"                      : [1000, 0, 4, 'yyyy'],

    # Enchantments
    "Cryptolith Rite"                   : [10000,   0, 2, 'yg'],
    "Earthcraft"                        : [10000, 200, 2, 'yg'],
    "Growing Rites of Itlimoc"          : [10000,   0, 3, 'yyg'],
    "Mystic Remora"                     : [10000,   0, 1, 'u'],
    "Rhystic Study"                     : [10000,   0, 3, 'yyu'],
    "Song of Creation"                  : [10000,   0, 4, 'yrug'],
    "Stormchaser's Talent"              : [10001,   0, 1, 'u'],
    "Training Grounds"                  : [10000,  10, 1, 'u'],
    "Underworld Breach"                 : [10000,   0, 2, 'yr'],
    "Wild Growth"                       : [10000, 200, 1, 'g'],

    # Lands
    "Alchemist's Refuge"                : [100000, 0, 0, '', ['c'],],
    "Ancient Tomb"                      : [100000, 0, 0, '', [{'cc':{'life':2}}],],
    "Boseiju, Who Endures"              : [100000, 0, 0, '', ['g'],],
    "Breeding Pool"                     : [100000, 0, 0, '', ['g', 'u'],],
    "Cephalid Coliseum"                 : [100000, 0, 0, '', [{'u':{'life':1}}],],
    "Command Tower"                     : [100000, 0, 0, '', ['c', 'u', 'r'],],
    "Deserted Temple"                   : [100000, 0, 0, '', ['c'],],
    "Dryad Arbor"                       : [100001, 0, 0, '', [{'g':{'summoning_sickness':False}}],],
    "Emergence Zone"                    : [100000, 0, 0, '', ['c'],],
    "Flooded Grove"                     : [100000, 0, 0, '', ['g', 'u'],],
    "Flooded Strand"                    : [100000, 0, 0, '', [''],],
    "Forest"                            : [100000, 0, 0, '', ['g'],],
    "Gaea's Cradle"                     : [100000, 0, 0, '', ['special'],],
    "Gemstone Caverns"                  : [100000, 0, 0, '', ['c'],],
    "Island"                            : [100000, 0, 0, '', ['u'],],
    "Mana Confluence"                   : [100000, 0, 0, '', ['w', 'u', 'b', 'r', 'g'],],
    "Minamo, School at Water's Edge"    : [100000, 0, 0, '', ['u'],],
    "Mistrise Village"                  : [100000, 0, 0, '', ['u'],],
    "Misty Rainforest"                  : [100000, 0, 0, '', [''],],
    "Otawara, Soaring City"             : [100000, 0, 0, '', ['u'],],
    "Polluted Delta"                    : [100000, 0, 0, '', [''],],
    "Prismatic Vista"                   : [100000, 0, 0, '', [''],],
    "Scalding Tarn"                     : [100000, 0, 0, '', [''],],
    "Shifting Woodland"                 : [100000, 0, 0, '', ['g'],],
    "Snow-Covered Forest"               : [100000, 0, 0, '', ['g'],],
    "Snow-Covered Island"               : [100000, 0, 0, '', ['u'],],
    "Taiga"                             : [100000, 0, 0, '', ['g','r'],],
    "Talon Gates of Madara"             : [100000, 1, 0, '', ['c'],],
    "Tropical Island"                   : [100000, 0, 0, '', ['u','g'],],
    "Urza's Cave"                       : [100000, 0, 0, '', ['c'],],
    "Urza's Saga"                       : [100000, 0, 0, '', ['c'],],
    "Verdant Catacombs"                 : [100000, 0, 0, '', [''],],
    "Volcanic Island"                   : [100000, 0, 0, '', ['u','r'],],
    "Windswept Heath"                   : [100000, 0, 0, '', [''],],
    "Wooded Foothills"                  : [100000, 0, 0, '', [''],],
    "Yavimaya, Cradle of Growth"        : [100000, 0, 0, '', ['g'],],
    }

FETCH_LIST = [
    "Arid Mesa",
    "Flooded Strand",
    "Misty Rainforest",
    "Polluted Delta",
    "Prismatic Vista",
    "Scalding Tarn",
    "Verdant Catacombs",
    "Windswept Heath",
    "Wooded Foothills",
    ]

'''
TO DO:

- Special Cards
    x Cloud of Faeries
    x Springheart Nantuko
    - Thundertrap Trainer

    x Chatterstorm
    - Malevolent Rumble
    
    - Snap
    - Frantic Search

- Tutors are wincons. 
    - Land Tutors
        - Crop Rotation
        x Sylvan Scrying
        x Tempt with Discovery
        - Traverse the Ulvenwald
    
    - Creature Tutors 
        x Nature's Rhythm
            x Initiates a spellseeker line if possible, otherwise,
            - tries to get a cost reducer
        x Finale of Devastation
            x Initiates a spellseeker line if possible, otherwise,
            - tries to get a cost reducer
            - can also get from bin
        x Spellseeker
            Initiates either the Crop rotation or the Sylvan Scrying line
        - Chord of Calling
            - Convoke is not handled
    
    - Other Tutors
        - Gamble
            Gamble should be sent for a mycospawn line. If we can't afford the 
            mycospawn line, get Talon Gates Directly and pray to RNGesus.

- Check for playable cards in hand
    Less important, but i think adding an initial step to check for "playable" 
    cards in hand, and playing them if you have enough mana (including thras spin + 
    oboro) would help the odds. Currently, my understanding is that finding a dork 
    when you are low on resources means the dork is just stuck in your hand.,

    - Rocks / Rituals
        - Candelabra of Tawnos


- Mana pool


- Would be nice to get a way to change the initial conditions without having to 
  update the underlying code. Not critical though.,

- Would be nice to get a line at the end that says success or failed,

- And lastly, how do we run this 10000x?


POTENTIAL BUGS
x Confirm we still have enough mana to win if TGoM gets thrasios'ed into play

x When determining if we go for a line that uses crop rot we need to use a 
  max_mana_remaining that leaves one non-cradle land in play.
    - I think this bug is quashed with the addition of the LEAVE_ONE_FLAG 
      portion of the calc_max_mana function and its inclusion in the logic
      for crop rot lines.

- When we cast Chatterstom we should check to see if we can up the storm count
  with any cards that thrasios put into our hand.

'''
#-------------------------------------------------------------------------------
def read_decklist_file(path):
    '''
    '''
    decklist = []
    EXIT_FLAG = False
    with open(str(path), 'r') as f:
        for line in f:
            line = line.strip()
            if line != '': 
                match = re.match(r"^(\d+)\s+(.*)", line)
                if match:
                    qty = int(match.group(1))
                    card_name = match.group(2)

                    
                    for _ in range(qty):
                        decklist.append(card_name)
                    
                    # Check that we have info on the card
                    if card_name not in list(ALL_CARDS.keys()):
                        print(
                            f'Please add {card_name} to the ALL_CARDS dictionary'
                            )
                        EXIT_FLAG = True
    if EXIT_FLAG:
        raise SystemExit

    return decklist
#-------------------------------------------------------------------------------
class Gamestate:
    def __init__(self,
        decklist,
        specific:dict = {
            # location : [list of cards]
            'battlefield' : [
                "Gaea's Cradle", 
                "Rograkh, Son of Rohgahh",
                "Thrasios, Triton Hero", 
                "Oboro Breezecaller",
                ],
            },
        random_adds:dict = {
            # location : card type : [amount, [cards to exclude]]
            'battlefield' : {
                'creature': [1, ["Dryad Arbor", "Biomancer's Familiar"]],
                'land': [3, ["Dryad Arbor", "Talon Gates of Madara"]],
                },
            },
        mana_pool:str = 'uur',
        storm_count:int = 0,
        ):
        '''
        PURPOSE
        This class is designed to model the non-deterministic loop formed
        by Oboro Breezecaller and Thrasios, Triton Hero. 
        As inputs it requires a decklist, and allows you to specify where 
        individual cards are located or randomly place cards of a certain or 
        random type in a particular location. Cards may be excluded from this
        random selection.

        To place a specific card somewhere, use the specific dictionary input.
        '''
        self.battlefield    = []
        self.exile          = []
        self.graveyard      = []
        self.hand           = []
        self.library        = decklist
        self.mana_pool      = ManaPool(initial_mana = mana_pool)
        
        self.thrasios_cost  = 4
        self.oboro_cost     = 2
        self.storm_count    = storm_count

        self.SPRINGHEART_FLAG   = False
        self.FIZZLE_FLAG        = False
        self.WIN_FLAG           = False

        self.LOC_TYPES = {
            'battlefield'   : self.battlefield,
            'exile'         : self.exile,
            'graveyard'     : self.graveyard,
            'hand'          : self.hand,
            'library'       : self.library,
            }
        

        # Add specified cards to the indicated location
        for location, card_list in specific.items():
            self.move_specific(
                cards_to_move = card_list,
                source = self.library,
                dest = self.LOC_TYPES[location],
                )

        # Add random cards to the indicated location
        for location, d in random_adds.items():
            for card_type, [qty, exclusions] in d.items():
                self.move_random(
                    card_type = card_type,
                    source = self.library,
                    dest = self.LOC_TYPES[location],
                    count = qty,
                    exclusions = exclusions,
                    verbose = False
                    )

        self.shuffle_deck()
        
        # Initial Metrics
        num_battlefield_lands, _ = self.count_types(
            card_type = 'land', 
            source = self.battlefield,
            )
        
        num_battlefield_creatures, _ = self.count_types(
            card_type = 'creature', 
            source = self.battlefield,
            )

        # The current max mana that can be produced is given by:
        #   mana_pool + mana netted from oboro activations
        init_max_mana = self.calc_max_mana()  
        
        self.INIT_LAND_COUNT        = num_battlefield_lands
        self.INIT_CREATURE_COUNT    = num_battlefield_creatures
        self.INIT_MAX_MANA          = init_max_mana

        # Metrics to keep track of
        self.THRAS_ACTS             = 0
        self.THRAS_LANDS_HIT        = 0
        
        self.COST_REDUCERS          = 0
        self.LANDFALL_TRIGGERS      = 0
        self.WIN_CON                = 'None'
        
        self.CHATTERSTORM_COUNT     = 0

        # Check if cost reducers are initially present
        cost_reducers = ["Biomancer's Familiar", "Training Grounds"]
        for cost_red in cost_reducers:
            self.update_activation_costs()
            self.COST_REDUCERS += 1

    #----------------------------------------------------------------------------
    def print_log(self):
        '''
        PURPOSE
        '''
        num_battlefield_lands, _ = self.count_types(
            card_type = 'land', 
            source = self.battlefield,
            )
        
        num_battlefield_creatures, _ = self.count_types(
            card_type = 'creature', 
            source = self.battlefield,
            )

        # The current max mana that can be produced is given by:
        #   mana_pool + mana netted from oboro activations
        current_max_mana = self.calc_max_mana()  

        print(f'Hand: {len(self.hand)} | Mana Pool: {self.mana_pool.pool}, Max: {current_max_mana}' +\
                f' | Battlefield: Lands {num_battlefield_lands}, Creatures {num_battlefield_creatures}')
        print('\n')
    
    #----------------------------------------------------------------------------
    def calc_max_mana(self, 
        leave_one_land:bool = False,
        ):
        '''
        PURPOSE
        The purpose of this function is to calculate the maximum amount of mana
        that is currently available to the player from the current boardstate. 
        It assumes that all mana is from either

            1) Mana currently in the mana pool or
            2) can be produced from Oboro/cradle activations
        
        When the leave_one_land is set to True, this function calculates the max
        mana that can be generated leaving one (non-cradle) land in play.
        
        With the incoporation of pips, we need to expand this function to obtain
        the max_mana available under several scenarios
            1) Where one non-cradle land needs to remain in play
            2) A specific minimum set of pips is required for a combo.
                2.1) This is complicated when the current pips are not in the 
                     mana pool and need to be generated from oboro activations
                

        '''
        # Create a temporary instance of the current boardstate
        gamestate_copy = copy.deepcopy(self)
        if not leave_one_land:
            while not gamestate_copy.FIZZLE_FLAG:
                gamestate_copy.activate_oboro(verbose = False)
        
        else:
            # Get Oboro Activations remaining
            _, copy_battlefield_lands = gamestate_copy.count_types(
                card_type = 'land', 
                source = gamestate_copy.battlefield,
                )
            copy_oboro_lands = []
            for land in copy_battlefield_lands:
                if land not in ["Gaea's Cradle"]:
                    copy_oboro_lands.append(land)
            
            # Activate oboro but leave one
            for _ in range(len(copy_oboro_lands) - 1):
                gamestate_copy.activate_oboro(verbose = False)
    
        return gamestate_copy.mana_pool.total()
    #---------------------------------------------------------------------------
    def check_mana_state(self,
        target_mana,
        verbose:bool = False,
        ):
        '''
        PURPOSE
        The purpose of this function is to check if a target mana state is 
        achievable from the current mana pool, lands, and oboro activations.

        FUTURE IMPLEMENTATIONS
        Concievably we could have a mana dork that produces the color we need. 
        Adding non-land mana producers to the mix would be more correct though
        requires tracking summoning sickness/haste.
        '''
        gamestate_copy = copy.deepcopy(self)
        
        # Check if we already have enough pips
        in_mana_pool_flag, missing_pips = gamestate_copy.mana_pool.check_castable(
            mana_cost = target_mana
            )
        
        if in_mana_pool_flag:
            if verbose: print('Requested mana in mana pool')
            return True

        # Check if we have a land that can produce the required pips
        #   Check different pips that can be produced
        num_battlefield_lands, battlefield_lands = gamestate_copy.count_types(
            card_type = 'land', 
            source = self.battlefield,
            )

        #   Remove cradle and Dryad Arbor
        exclude = ["Gaea's Cradle", "Dryad Arbor"]
        for land in exclude:
            try:
                battlefield_lands.remove(land)
            except ValueError:
                # Land isnt on battlefield
                pass

        #   Get the number of mana combinations
        mana_production_info = {}
        non_mana_producers = []
        
        for card in battlefield_lands:
            pip_options = ALL_CARDS[card][4]
            
            tmp = []
            for pip in pip_options:
                if isinstance(pip, dict):
                    tmp.append(list(pip.keys())[0])
                elif pip != '':
                    tmp.append(pip)
            if len(tmp) != 0:
                mana_production_info[card] = tmp
            else:
                non_mana_producers.append(card)
        
        missing_producers = {}
        keepers = []
        for pip, amount_missing in missing_pips.items():
            if pip != 'y':
                curr_keepers = []
                desp = []
                for land, pip_options in mana_production_info.items():
                    if pip in pip_options:
                        curr_keepers.append(land)
                if not curr_keepers:
                    missing_producers[pip] = amount_missing
                else:
                    keepers.append(curr_keepers)
        
        # Get the best lands to keep
        best_keepers = shortest_hitting_set(keepers)
       
        if missing_producers:
            # We cannot make one of the pips with the current lands.
            if verbose: 
                print(
                    f'Current lands cannot produce: {missing_producers}.'
                    )
            return False

        #
        # Now we need to check if we can make the missing pips with oboro 
        # activations
        #   To generate a pip from a tapped land, we need to spend 
        #   oboro_cost unspecified pips and return a land to hand.
        #
        bounceable_lands = battlefield_lands
        for land in best_keepers:
            bounceable_lands.remove(land)
        
        if bounceable_lands:
            gamestate_copy.move_specific(
                cards_to_move = [bounceable_lands[0]],
                source  = gamestate_copy.battlefield,
                dest    = gamestate_copy.hand,
                )
            gamestate_copy.mana_pool.spend({'y':gamestate_copy.oboro_cost})
            gamestate_copy.check_mana_state(target_mana = target_mana)

            print(f'Current mana: {gamestate_copy.mana_pool.mana_pool}')
            print(f'Missing mana: {missing_pips}')
        else:
            return False
        
        pprint(mana_production_info)
        print(keepers)
        print(best_keepers)

    #----------------------------------------------------------------------------
    def shuffle_deck(self):
        np.random.shuffle(self.library)

    #----------------------------------------------------------------------------
    def update_activation_costs(self):
        '''
        PURPOSE
        After a cost reducer is cost, we need to update the activation costs of 
        our creatures.
        '''
        self.thrasios_cost -= 2
        if self.thrasios_cost <= 1:
            self.thrasios_cost = 1

        self.oboro_cost -= 2
        if self.oboro_cost <= 1:
            self.oboro_cost = 1
    
    #----------------------------------------------------------------------------
    def count_types(self,
        card_type:str,
        source,
        ):
        '''
        PURPOSE
        This function calculates the number of cards of a specified card_type in
        a given location.

        USAGE
        -   Used to determine cradle counts
        '''
        if card_type == 'all':
            matches = source
        
        else:
            matches = []
            target_card_type_id = CARD_TYPES[card_type] 
            for card in source:
                card_type_id_k = ALL_CARDS[card][0]
                
                if int(card_type_id_k / target_card_type_id) % 10 > 0:
                    matches.append(card)
        
        return len(matches), matches

    #----------------------------------------------------------------------------
    def move_specific(self,
        cards_to_move:list,
        source,
        dest,
        ):
        '''

        POTENTIAL BUGS
        This function may fail to perform as desired when trying to move a 
        token from the battlefield to any other location where it should cease to 
        exist
        '''
        for card in cards_to_move:
            if 'Token' not in card:
                source.remove(card)
                dest.append(card)

            else:
                dest.append(card)
                if card in source:
                    source.remove(card)

        return None
    #----------------------------------------------------------------------------
    def move_random(self, 
        card_type:str,
        source,
        dest,
        count:int = 1,
        exclusions:list = [],
        verbose:bool = False,
        ):
        '''
        PURPOSE
        Move random cards of a certain type from one location to another.

        USAGE
        -   Used in setup of a gamestate to place creatures and lands onto the 
            battlefield.
        -   Used by oboro_activation to return a random land to hand
        '''
        total_count, matches = self.count_types(
            card_type = card_type,
            source = source,
            )
        
        for exclusion in exclusions:
            if exclusion in matches:
                matches.remove(exclusion)
        
        moved = []
        for move_id in range(count):
            random_card = str(np.random.choice(matches))
            matches.remove(random_card)
            source.remove(random_card)
            
            dest.append(random_card)
            moved.append(random_card)

            if verbose:
                print(f'Moved {random_card}')
        
        return moved
    #----------------------------------------------------------------------------
    def activate_thrasios(self,
        verbose = True,
        ):
        '''
        PURPOSE
        Models an activation of Thrasios
        '''
        #----------------------------------------------------------------------- 
        def assess_card(position):
            '''
            PURPOSE
            The purpose of this function is to unify the logic used to decide
            whether or not to keep a card with thrasios.
            '''

            # Look at top card
            card = self.library[0]

            card_type_id    = ALL_CARDS[card][0]
            card_spec_id    = ALL_CARDS[card][1]        
            card_mv         = ALL_CARDS[card][2]
            card_mana_cost  = ALL_CARDS[card][3]
            
            # Get Oboro Activations remaining
            num_battlefield_lands, battlefield_lands = self.count_types(
                card_type = 'land', 
                source = self.battlefield,
                )
            oboro_lands = []
            mana_producing_lands = 0
            for land in battlefield_lands:
                if land not in ["Gaea's Cradle", "Dryad Arbor"]:
                    oboro_lands.append(land)
                
                if land not in FETCH_LIST + ["Dryad Arbor"]:
                    mana_producing_lands += 1
            
            # Update cradle count
            num_battlefield_creatures, _ = self.count_types(
                card_type = 'creature', 
                source = self.battlefield,
                )
            
            oboro_acts_remaining = len(oboro_lands)
            desperate_oboro_acts_remaining = oboro_acts_remaining + \
                ("Dryad Arbor" in battlefield_lands) 
            
            current_max_mana = self.calc_max_mana()
            penult_max_mana = self.calc_max_mana(leave_one_land = True)
            TGOM_FLAG = "Talon Gates of Madara" in self.library
            CASTABLE_FLAG, missing_pips = \
                self.mana_pool.check_castable(mana_cost = card_mana_cost)

            #print(TGOM_FLAG, penult_max_mana,'/',current_max_mana, desperate_oboro_acts_remaining) 

            #-------------------------------------------------------------------
            if card == 'Talon Gates of Madarda':
                '''
                The top card is Talon Gates, choose to put into play
                '''
                self.move_specific(
                    cards_to_move = [card],
                    source = self.library,
                    dest = self.battlefield,
                    )

                if verbose:
                    if (self.calc_max_mana() >= 1): 
                        print(f'Win! {card} > battlefield')
                        self.WIN_FLAG = True
                        self.WIN_CON = card
                    else:
                        print(f'Close but no cigar.')
                        self.FIZZLE_FLAG = True

                return True
            
            #-------------------------------------------------------------------
            elif (int(card_spec_id/10) % 10 == 1) and (CASTABLE_FLAG)\
                (
                    (
                        (self.mana_pool.total() - card_mv >= 1) and \
                        (oboro_acts_remaining >= 1)
                    ) or \
                    (
                        (self.mana_pool.total() >= self.oboro_cost) and \
                        (oboro_acts_remaining >= 2)
                    )
                ):
                '''
                Top card is a cost reducer, choose to put into hand if we 
                either 
                1) have enough mana to activate oboro afterwards or 
                2) can activate oboro, cast the cost reducer, then activate 
                   oboro again
                '''
                if verbose: print(f'Cost Reducer! {card} > battlefield')

                if (self.mana_pool.total() - card_mv <= 0):
                    # Activate oboro then cast creature
                    self.activate_oboro(verbose = True)
                
                # Cast it
                self.move_specific(
                    cards_to_move = [card],
                    source = self.library,
                    dest = self.battlefield,
                    )
                
                self.mana_pool.spend(card_mana_cost)
                self.update_activation_costs()
                self.storm_count += 1
                
                self.COST_REDUCERS += 1
                return True

            #-------------------------------------------------------------------
            elif (
                (card == "Crop Rotation")
                and \
                CASTABLE_FLAG
                and \
                (penult_max_mana >= 1)
                and \
                (desperate_oboro_acts_remaining >= 1)
                # ensures that we have a land to sac
                and \
                (num_battlefield_creatures >= 6)
                and \
                TGOM_FLAG
                ):
                '''
                Crop Rot for win
                '''
                self.move_specific(
                    cards_to_move = [card],
                    source = self.library,
                    dest = self.graveyard,
                    )
                
                self.storm_count += 1
                if verbose: 
                    print(f'Win! {card} line is available.')
                
                self.WIN_FLAG = True
                self.WIN_CON = card
                return True
            #-------------------------------------------------------------------
            elif (
                (card == "Trinket Mage") and CASTABLE_FLAG
                and \
                (num_battlefield_creatures >= 5)
                and \
                TGOM_FLAG
                and \
                ("Expedition Map" in self.library)
                and \
                (current_max_mana >= 11)
                ):
                '''
                '''
                self.move_specific(
                    cards_to_move = [card],
                    source = self.library,
                    dest = self.graveyard,
                    )
                
                self.storm_count += 1
                if verbose: print(f'Win! {card} line is available.')
                
                self.WIN_FLAG = True
                self.WIN_CON = card
                return True
            #-------------------------------------------------------------------
            elif (
                (card == 'Spellseeker')
                and \
                (num_battlefield_creatures >= 5)
                and \
                TGOM_FLAG
                and \
                (
                    (
                        (desperate_oboro_acts_remaining >= 1) and \
                        ("Crop Rotation" in self.library) and \
                        (penult_max_mana >= 4)
                    ) or \
                    (
                        ("Sylvan Scrying" in self.library) and \
                        (current_max_mana >= 10)
                    )
                )
                ):
                '''
                '''
                self.move_specific(
                    cards_to_move = [card],
                    source = self.library,
                    dest = self.graveyard,
                    )
                
                self.storm_count += 1
                if verbose: 
                    print(f'Win! {card} line is available.')
                
                self.WIN_FLAG = True
                self.WIN_CON = card
                return True
            #-------------------------------------------------------------------
            elif (
                (card == "Step Through")
                and \
                (num_battlefield_creatures >= 5)
                and \
                (TGOM_FLAG)
                and \
                ("Spellseeker" in self.library)
                and \
                (
                    (
                        (desperate_oboro_acts_remaining >= 1) and \
                        ("Crop Rotation" in self.library) and \
                        (penult_max_mana >= 6)
                    ) or \
                    (
                        ("Sylvan Scrying" in self.library) and \
                        (current_max_mana >= 12)
                    )
                )
                ):
                '''
                '''
                self.move_specific(
                    cards_to_move = [card],
                    source = self.library,
                    dest = self.graveyard,
                    )
                
                self.storm_count += 1
                if verbose: 
                    print(f'Win! {card} line is available.')
                
                self.WIN_FLAG = True
                self.WIN_CON = card
                return True
            #-------------------------------------------------------------------
            elif (
                (card in ["Nature's Rhythm", "Finale of Devastation"]) 
                and \
                (num_battlefield_creatures >= 5)
                and \
                (TGOM_FLAG)
                and \
                ("Spellseeker" in self.library)
                and \
                (
                    (
                        (desperate_oboro_acts_remaining >= 1) and \
                        ("Crop Rotation" in self.library) and \
                        (penult_max_mana >= 6)
                    ) or \
                    (
                        ("Sylvan Scrying" in self.library) and \
                        (current_max_mana >= 12)
                    )
                )
                ):
                '''
                '''
                self.move_specific(
                    cards_to_move = [card],
                    source = self.library,
                    dest = self.graveyard,
                    )
                
                self.storm_count += 1
                if verbose: 
                    print(f'Win! {card} line is available.')
                
                self.WIN_FLAG = True
                self.WIN_CON = card
                return True
            #-------------------------------------------------------------------
            elif (
                (card == "Chord of Calling")
                and \
                (num_battlefield_creatures >= 5)
                and \
                TGOM_FLAG
                and \
                ("Spellseeker" in self.library)
                and \
                (
                    (
                        ("Crop Rotation" in self.library) and \
                        (penult_max_mana >= 7)
                        and \
                        (desperate_oboro_acts_remaining >= 1)
                    )
                    or \
                    (
                        ("Sylvan Scrying" in self.library) and \
                        (current_max_mana >= 13)
                    )
                )
                ):
                '''
                Chord > Crop Rot for win
                '''
                self.move_specific(
                    cards_to_move = [card],
                    source = self.library,
                    dest = self.graveyard,
                    )
                
                self.storm_count += 1
                if verbose: 
                    print(f'Win! {card} line is available.')
                
                self.WIN_FLAG = True
                self.WIN_CON = card
                return True
            #-------------------------------------------------------------------
            elif (
                (card in ["Sowing Mycospawn"])
                and \
                (current_max_mana >= 5)
                and \
                (num_battlefield_creatures >= 5)
                and \
                TGOM_FLAG
                ):
                '''
                Sowing Mycospawn tutor for win
                '''
                self.move_specific(
                    cards_to_move = [card],
                    source = self.library,
                    dest = self.graveyard,
                    )
                
                self.storm_count += 1
                if verbose: 
                    print(f'Win! {card} line is available.')
                
                self.WIN_CON = card
                self.WIN_FLAG = True
                return True
            #-------------------------------------------------------------------
            elif (
                (card in ["Expedition Map"])
                and \
                (current_max_mana >= 8)
                and \
                (num_battlefield_creatures >= 6)
                and \
                TGOM_FLAG
                ):
                '''
                '''
                self.move_specific(
                    cards_to_move = [card],
                    source = self.library,
                    dest = self.graveyard,
                    )
                
                self.storm_count += 1
                if verbose: 
                    print(f'Win! {card} line is available.')
                
                self.WIN_FLAG = True
                self.WIN_CON = card
                return True
            #-------------------------------------------------------------------
            elif (
                (card in ["Tempt with Discovery"])
                and \
                (current_max_mana >= 5)
                and \
                (num_battlefield_creatures >= 6)
                and \
                TGOM_FLAG
                ):
                '''
                Tempt with Discovery can tutor for win
                '''
                self.move_specific(
                    cards_to_move = [card],
                    source = self.library,
                    dest = self.graveyard,
                    )
                
                self.storm_count += 1
                if verbose: 
                    print(f'Win! {card} line is available.')
                
                self.WIN_FLAG = True
                self.WIN_CON = card
                return True
            #-------------------------------------------------------------------
            elif (
                (card == "Springheart Nantuko")
                and not \
                (
                    (oboro_acts_remaining  == 0) and \
                    (self.mana_pool <= self.oboro_cost + self.thrasios_cost + \
                        card_mv)
                    )
                ):
                '''
                Springheart Nantuko will almost always be worth casting
                
                ASSUMPTIONS
                Cast Springheart even if we have only cradle and enough mana to
                try and get a lucky flip from thrasios and oboro to untap.
                '''
                self.move_specific(
                    cards_to_move = [card],
                    source = self.library,
                    dest = self.graveyard,
                    )
                
                if (self.mana_pool - card_mv < self.oboro_cost):
                    # Activate oboro then cast creature
                    self.activate_oboro(verbose = True)
                
                self.storm_count += 1
                self.mana_pool -= card_mv
                if verbose: print(f'Start the Landfalls! {card} > battlefield')
                self.SPRINGHEART_FLAG = True 
                return True
            
            #-------------------------------------------------------------------
            elif (
                (card == "Chatterstorm")
                and not \
                (
                    (oboro_acts_remaining  == 0) and \
                    (self.mana_pool <= self.oboro_cost + self.thrasios_cost + \
                        card_mv)
                    )
                ):
                '''
                Chatterstorm will almost always be worth casting
                
                ASSUMPTIONS
                Cast Chatterstorm even if we have only cradle and enough mana to
                try and get a lucky flip from thrasios and oboro to untap.
                '''
                self.move_specific(
                    cards_to_move = [card],
                    source = self.library,
                    dest = self.graveyard,
                    )
                
                if (self.mana_pool - card_mv < self.oboro_cost):
                    # Activate oboro then cast creature
                    self.activate_oboro(verbose = True)
                
                self.storm_count += 1
                self.mana_pool -= card_mv

                for _ in range(self.storm_count):
                    self.battlefield.append("Creature Token")
                
                if verbose: 
                    print(
                        f'Found {card}! Created {self.storm_count} '+\
                        'Creature Tokens.'
                        )
                
                self.CHATTERSTORM_COUNT += self.storm_count
                return True
            
            #-------------------------------------------------------------------
            elif (
                    (card == "Cloud of Faeries")
                and \
                    (
                        (
                        (card_mv <= oboro_acts_remaining) and \
                        (self.mana_pool - card_mv >= self.oboro_cost)
                        ) 
                    or \
                    (card_mv <= oboro_acts_remaining - 1)
                    or \
                    (num_battlefield_lands >= 2)
                    )
                ):
                '''
                Cloud of Faeries has an etb trigger that needs to be handled.
                '''
                if (self.mana_pool - card_mv < self.oboro_cost):
                    # Activate oboro then cast creature
                    self.activate_oboro(verbose = True)
                
                self.move_specific(
                    cards_to_move = [card],
                    source = self.library,
                    dest = self.battlefield,
                    )
                
                # Update cradle count
                num_battlefield_creatures, _ = self.count_types(
                    card_type = 'creature', 
                    source = self.battlefield,
                    )
                
                self.storm_count += 1
                self.mana_pool -= card_mv
                
                # Do we have another land to untap to generate mana?
                if mana_producing_lands > 2:
                    extra = 1
                else:
                    extra = 0

                self.mana_pool += num_battlefield_creatures + extra  
                if verbose: print(f'Cheap Creature! {card} > battlefield')
                
                return True


            #-------------------------------------------------------------------
            elif (
                    (int(card_type_id) % 10 > 0) and \
                    (card != "Dryad Arbor")
                ) and \
                (
                    (
                        (card_mv <= oboro_acts_remaining) and \
                        (self.mana_pool - card_mv >= self.oboro_cost)
                        ) or \
                    (card_mv <= oboro_acts_remaining - 1)
                ):
                '''
                If the top card is a non-dryad arbor creature 
                And  either 
                (1) its mana value is less than the number of remaining Oboro 
                      activations we have and we can cast it with floating mana
                      and still activate oboro afterwards
                OR
                
                (2) its mana value is less than one minus the number of 
                      remaining oboro activations,
                then we should take it and cast it in case we hit another land
                later on.
                
                This should also consider the case where we need to 
                activate the Oboro to have enough mana to case the creature and 
                still have enough remaining Oboro activations to go mana neutral
                from the exchange.
                '''
                if (self.mana_pool - card_mv < self.oboro_cost):
                    # Activate oboro then cast creature
                    self.activate_oboro(verbose = True)
                
                self.move_specific(
                    cards_to_move = [card],
                    source = self.library,
                    dest = self.battlefield,
                    )
                
                self.storm_count += 1
                self.mana_pool -= card_mv
                
                if verbose: print(f'Cheap Creature! {card} > battlefield')
                
                return True

            #-------------------------------------------------------------------
            elif int(card_type_id / 100000)  % 10 > 0:
                '''
                Land found, choose to put into play
                '''
                self.move_specific(
                    cards_to_move = [card],
                    source = self.library,
                    dest = self.battlefield,
                    )

                if verbose: print(f'Land! {card} > battlefield')
                self.THRAS_LANDS_HIT += 1

                if self.SPRINGHEART_FLAG:
                    self.battlefield.append("Creature Token")
                
                    if verbose: 
                        print(f'Landfall Trigger! Created a Creature Token.')
                        self.LANDFALL_TRIGGERS += 1
                return True
            
            #-------------------------------------------------------------------
            elif position == 0:
                # Move card to bottom

                self.library.pop(0)
                self.library.append(card)
                if verbose: print(f'Miss. {card} > bottom')
                return False

            #-------------------------------------------------------------------
            elif position == 1:
                self.move_specific(
                    cards_to_move = [card],
                    source = self.library,
                    dest = self.hand,
                    )
                if verbose: print(f'Miss. {card} > hand')
                return False
        #-----------------------------------------------------------------------
        # check available mana
        if self.mana_pool >= self.thrasios_cost:
            self.mana_pool -= self.thrasios_cost
        else:
            self.FIZZLE_FLAG = True
            return None
        
        PLAYED_FLAG = assess_card(position = 0)
        if not PLAYED_FLAG:
            PLAYED_FLAG = assess_card(position = 1)
    
    #----------------------------------------------------------------------------
    def activate_oboro(self, 
        verbose:bool = False,
        exclusions:list = [],
        ):
        '''
        PURPOSE
        This function models an Oboro Breezecaller activation.
        
        SQUASHED BUGS
        We need to check the number of lands to bounce before we check the 
        available mana so that the mana cost is not paid before fizzling.
        '''
        # check number of lands to bounce. 
        num_battlefield_lands, _ = self.count_types(
            card_type = 'land', 
            source = self.battlefield,
            )
        if num_battlefield_lands < 2:
            self.FIZZLE_FLAG = True
            return None
        
        # check available mana
        if self.mana_pool.total() >= self.oboro_cost:
            self.mana_pool.spend({'y' : self.oboro_cost})
        else:
            self.FIZZLE_FLAG = True
            return None

        if num_battlefield_lands > 2:
            # Assume we will bounce dryad arbor at last possible moment
            # so that the cradle count is maximized.
            # Note, you can remove Dryad Arbor from the following list to relax 
            # this assumption, though if you don't run it, you don't need to.
            exclusions = exclusions + ["Gaea's Cradle", "Dryad Arbor"]
        
        else:
            exclusions = exclusions + ["Gaea's Cradle"]

        bounced = self.move_random(
            card_type = 'land',
            source = self.battlefield,
            dest = self.hand,
            count = 1,
            exclusions = exclusions,
            verbose = False
            )
        
        if verbose:
            print(f"Returned {bounced[0]} to hand to untap Gaea's Cradle")

        # Update cradle count
        num_battlefield_creatures, _ = self.count_types(
            card_type = 'creature', 
            source = self.battlefield,
            )

        self.mana_pool.add({'g':num_battlefield_creatures})

        return None
    
    #----------------------------------------------------------------------------
    def grind(self, max_spins = 50):
        '''
        '''
        # Add our mana from cradle and other lands to the mana pool
        #   Update cradle count
        num_battlefield_creatures, _ = self.count_types(
            card_type = 'creature', 
            source = self.battlefield,
            )
        self.mana_pool.add({'g':num_battlefield_creatures})
        
        self.print_log()
        while (not self.FIZZLE_FLAG) and (not self.WIN_FLAG):
            
            if self.mana_pool.total() >= self.thrasios_cost + self.oboro_cost:
                self.activate_thrasios(verbose = True)
            else:
                self.activate_oboro(verbose = True)

            # Check hand for combos
            # Check hand for any creatures that we may have picked up that 
            # we now have enough mana to cast efficiently

            self.print_log()
        
        if self.calc_max_mana() == 5:
            self.activate_thrasios(verbose = True)
            self.print_log()


        print("END GAME INSTANCE")
        print("-------------------------------------------------------------------")
#-------------------------------------------------------------------------------
if __name__ == "__main__":
    
    max_trials = 10000
    decklist = read_decklist_file(path = 'decklist.txt')
    game = Gamestate(decklist = decklist,
        specific = {
            # location : [list of cards]
            'battlefield' : [
                "Gaea's Cradle", 
                "Rograkh, Son of Rohgahh",
                "Thrasios, Triton Hero", 
                "Oboro Breezecaller",
                ],
            'graveyard' :[
                "Flooded Strand",
                "Misty Rainforest",
                ],
            },
        random_adds = {
            # location : card type : [amount, [cards to exclude]]
            'battlefield' : {
                'creature': [3, ["Dryad Arbor", "Biomancer's Familiar"]],
                'land': [6, ["Dryad Arbor", "Talon Gates of Madara"]],
                },
            },
        mana_pool = 'ggu',
        )

    # Test check_mana_state function
    game.check_mana_state('uuyyygr', verbose = True)
    '''
    for trial in tqdm(range(max_trials), desc='Simulating Games'):
        current_game = copy.deepcopy(game)
        current_game.shuffle_deck()        

        current_game.grind()
    #game.calc_max_mana()
    '''





