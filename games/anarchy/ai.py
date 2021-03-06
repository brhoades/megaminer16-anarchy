# This is where you build your AI for the Anarchy game.

from joueur.base_ai import BaseAI
from logic.wind import WindAI
import random

class AI(BaseAI,WindAI):
    """ the basic AI functions that are the same between games
    """

    def get_name(self):
        """ this is the name you send to the server to play as.

        Returns
            str: the name you want your player to have
        """
        return "ᶘ ᵒᴥᵒᶅ WOW"


    def start(self):
        """ this is called once the game starts and your AI knows its player.id and game. You can initialize your AI here.
        """
        # configurable parameters
        self.other_player = self.player.other_player
        self._sides   = 0
        for s in self.other_player.headquarters.get_sides():
            if s is not None:
                self._sides += 1
        self._red     = '\033[91m'
        self._green   = '\033[92m'
        self._yellow  = '\033[33m'
        self._lyellow = '\033[93m'
        self._lpurple = '\033[94m'
        self._purple  = '\033[95m'
        self._blue    = '\033[34m'
        self._bold_red= '\033[31m'
        self._reset   = '\033[0m'
        self._bold   = '\033[1m'

        self._warehouse_from_hq = None

        # print header, newline is provided by the run_turn func
        print(self._green + "WA/FD/PD/WS\t" + self._red + "WA/FD/PD/WS\t" + self._reset + "C/N/BR\t" + self._green + "HQ\t" + self._red +"HQ\t" + self._reset + "|PHASE|ACTIONS|PHASE|...")

    def game_updated(self):
        """ this is called every time the game's state updates, so if you are tracking anything you can update it here.
        """


    def end(self, won, reason):
        """ this is called when the game ends, you can clean up your data and dump files here if need be

        Args:
            won (bool): won == true means you won, won == false means you lost
            reason (str): the reason why you won or lost
        """

    def run_turn(self):
        """ This is called every time the AI is asked to respond with a command during their turn

        Returns:
            bool: represents if you want to end your turn. true means end the turn, false means to keep your turn going and re-call runTurn()
        """
        # Put your game logic here for runTurn
        self._max_bribes = self.player.bribes_remaining

        fc = self.wind_to_text(self.game.current_forecast.direction) 
        fn = self.wind_to_text(self.game.next_forecast.direction) 

        p = self.player
        #structure info
        print(self._green + "{0}/{1}/{2}/{3}\t".format(len([x for x in p.warehouses if x.health > 0]), 
            len([x for x in p.fire_departments if x.health > 0]), 
            len([x for x in p.police_departments if x.health > 0]), 
            len([x for x in p.weather_stations if x.health > 0])), end="")
        p = self.other_player
        print(self._red + "{0}/{1}/{2}/{3}\t".format(len([x for x in p.warehouses if x.health > 0]), 
            len([x for x in p.fire_departments if x.health > 0]), 
            len([x for x in p.police_departments if x.health > 0]), 
            len([x for x in p.weather_stations if x.health > 0])), end="")
        print((self._reset + "{0}/{1}/{2}\t" + self._green + "{3}\t" + self._red \
                + "{4}" + self._reset + "\t").format(fc, fn, self.player.bribes_remaining, \
                self.player.headquarters.health, self.other_player.headquarters.health), end="")

        ####################################################
        # change the wind in our favor
        # if we don't do this here, we may never get a chance
        self.print_title("W", self._bold, self._reset)
        self.decide_wind()

        # attack enemy HQ if they have 15 exposure or more
        self.attack_enemy_hq()

        # priority to burning them this turn, since they can't avoid it
        self.print_title("I1", self._bold, self._red)
        self.set_fires(self.game.current_forecast.direction)

        # burn them next turn if we can
        self.print_title("I2", self._bold, self._red)
        self.set_fires(self.game.next_forecast.direction)
        
        # our safety, this turn
        self.print_title("E1", self._bold, self._blue)
        self.fire_safety_check(self.game.current_forecast.direction)

        # protect us, next turn
        self.print_title("E2", self._bold, self._blue)
        self.fire_safety_check(self.game.next_forecast.direction)

        #TODO: If low fires for us, increase intensity?

        tries = len([x for x in p.police_departments if x.health > 0])
        while self.player.bribes_remaining > 0 and tries > 0:
            if self._sides == 0:
                self.ignite_useless_tiles()
            else:
                self.print_title("RHQ", self._bold, self._purple)
                self.purge_max_exposed_building()
            tries -= 1

        self.print_title("IF", self._bold, self._yellow)
        print(self._reset, end="")

        #end even strat
        ####################################################

        if self.player.bribes_remaining > 0:
            print(self._bold_red + "{0}".format(self.player.bribes_remaining), end="")

        print("")

        return True

    def can_be_bribed(self, building):
        """ This is an example of a utility function you could create.

        Returns:
            bool: determines whether the building can be bribed. True for yes, False for no
        """

        # building can only be bribed if health is greater than 0, it hasn't already been bribed, and you own it
        return (building.health > 0 and not building.bribed and building.owner == self.game.current_player)

    def fire_safety_check(self, f):
        """
        Fire safety check
        Put out fire in direction wind blows
        pass it which forecast to "fix"
        """
        if self.player.bribes_remaining <= 0:
            return

        b = self.player.headquarters.get_building_by_wind(f)
        if b is not None:
            if b.fire > 0 and self.player.bribes_remaining > 0 and not b.is_headquarters:
                b.put_out_fire(self)
            
    
    # always relative to enemy hq
    def set_fires(self, f):
        if self.player.bribes_remaining <= 0:
            return
        target = self.other_player.headquarters.get_building_by_wind(f)
        if target is not None:
            warehouse_by_dist = dict()
            for wh in self.player.warehouses:
                if not wh.is_headquarters:
                    warehouse_by_dist[wh] = abs(wh.x - target.x) + abs(wh.y - target.y)
            for wh in sorted(warehouse_by_dist, key=warehouse_by_dist.get, reverse=False):
                if wh.is_usable and target.fire <= 18 and not target.is_headquarters:
                    wh.ignite(target)
                    break
        # for wh in self.player.warehouses:
        #     if wh.is_headquarters or not wh.is_usable:
        #         continue
        #     target = self.other_player.headquarters.get_building_by_wind(f)

        #     if target is None:
        #         return

        #     if self.player.bribes_remaining > 0 and target.fire < 18 and not target.is_headquarters: #18 as, ideally, we could be spending our shit better somewhere else
        #         wh.ignite(target)
        #     else:
        #         break

    def attack_enemy_hq(self):
        ohq = self.player.other_player.headquarters
        if ohq.exposure >= 1:
            for pd in self.player.police_departments:
                if pd.is_usable and self.player.bribes_remaining > 0:
                    pd.raid(ohq)
                    self.print_title("IHQ", self._bold, self._yellow)
                    return


    def purge_max_exposed_building(self, num=-1):
        corruption = sorted(self.player.other_player.warehouses, key=lambda warehouses: warehouses.exposure, reverse=True)
        for b in corruption:
            for pd in self.player.police_departments:
                if pd.is_usable and self.player.bribes_remaining > 0 and num != 0:
                    pd.raid(b)
                    num -= 1
                    break


    def purge_fire_departments(self):
        for fd in self.player.other_player.fire_departments:
            if self.player.bribes_remaining <= 0:
                return
            warehouse_by_dist = dict()
            for wh in self.player.warehouses:
                if not wh.is_headquarters:
                    warehouse_by_dist[wh] = abs(wh.x - fd.x) + abs(wh.y - fd.y)
            for wh in sorted(warehouse_by_dist, key=warehouse_by_dist.get, reverse=False):
                if wh.is_usable and fd.fire < 18:
                    wh.ignite(fd)
                    break

    def ignite_useless_tiles(self):
        """
        In a vain attempt to scare shellai-like ais, let's light the enemy hq's surrounding tiles where possible
        """
        warehouse_by_dist = dict()
        if self._warehouse_from_hq is None:
            self._warehouse_from_hq = {}
            for wh in self.player.warehouses:
                if not wh.is_headquarters and wh.is_usable:
                    self._warehouse_from_hq[wh] = abs(wh.x - self.player.headquarters.x) + abs(wh.y - self.player.headquarters.y)
        for wh in sorted(self._warehouse_from_hq, key=self._warehouse_from_hq.get, reverse=True):
            if not wh.is_usable:
                continue
            for t in self.other_player.headquarters.get_sides():
                if t.is_headquarters or t.fire >= 18 or not wh.is_usable or self.player.bribes_remaining <= 0:
                    continue
                wh.ignite(t)

    def print_title(self, title, color, after):
        print(color+"|"+title+"|"+self._reset+after, end="")
