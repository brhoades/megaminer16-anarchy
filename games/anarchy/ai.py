# This is where you build your AI for the Anarchy game.

from joueur.base_ai import BaseAI
import random

class AI(BaseAI):
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

        self._red     = '\033[91m'
        self._green   = '\033[92m'
        self._yellow  = '\033[93m'
        self._lpurple = '\033[94m'
        self._purple  = '\033[95m'
        self._blue    = '\033[34m'
        self._bold_red    = '\033[31m'
        self._black   = '\033[0m'

        # print header, newline is provided by the run_turn func
        print(self._green + "WA/FD/PD/WS\t" + self._red + "WA/FD/PD/WS\t" + self._black + "BRIBES\t" + self._green + "HQ\t" + self._red +"HQ\t" + self._black + "|PHASE|ACTIONS|PHASE|...")

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

        p = self.player
        #structure info
        print(self._green + "{0}/{1}/{2}/{3}\t".format(len(p.warehouses), 
            len(p.fire_departments), len(p.police_departments), len(p.weather_stations)), end="")
        p = self.other_player
        print(self._red + "{0}/{1}/{2}/{3}\t".format(len(p.warehouses), 
            len(p.fire_departments), len(p.police_departments), len(p.weather_stations)), end="")
        print((self._black + "{0}\t" + self._green + "{1}\t" + self._red \
                + "{2}" + self._black + "\t").format(self.player.bribes_remaining, \
                self.player.headquarters.health, self.other_player.headquarters.health), end="")

        ####################################################
        # change the wind in our favor
        # if we don't do this here, we may never get a chance
        print("|W|", end="")
        self.decide_wind()

        # priority to burning them this turn, since they can't avoid it
        self.print_title("I1", self._black, self._red)
        self.set_fires(self.game.current_forecast.direction)

        # burn them next turn if we can
        self.print_title("I2", self._black, self._red)
        self.set_fires(self.game.next_forecast.direction)
        
        # our safety, this turn
        self.print_title("E1", self._black, self._blue)
        self.fire_safety_check(self.game.current_forecast.direction)

        # protect us, next turn
        self.print_title("E2", self._black, self._blue)
        self.fire_safety_check(self.game.next_forecast.direction)

        #panic the shell AIs
        #self.ignite_useless_tiles()

        #TODO: If low fires, increase intensity?

        self.print_title("RHQ", self._black, self._purple)
        # purge any buildings, starting with hq, which may be easy kills
        self.purge_max_exposed_building()

        self.print_title("IF", self._black, self._yellow)
        self.purge_fire_departments()
        print(self._black, end="")

        #end even strat
        ####################################################

        if self.player.bribes_remaining > 0:
            print(self._bold_red + "{0}".format(self.player.bribes_remaining), end="")

        print("")

        return True

    def decide_wind(self):
        """Change wind if needed
        """
        ohq = self.other_player.headquarters
        hq = self.player.headquarters
        sides = 0
        f = self.game.next_forecast.direction

        for s in ohq.get_sides():
            if s is not None:
                sides += 1

        # current_forecast (which is applied regardless) is applied
        # at the end of turn. This function lets us decide where the wind blows at 
        # the end of the opponent's turn.
        # below is for handling "all cases are equal" scenarios (ie first turn)

        #############################
        # in cover
        #############################
        if sides == 1:
            if ohq.building_south is None and (f == "north" or f == "south"):
                if hq.building_west is None or hq.building_west.fire <= hq.building_east.fire:
                    return self.change_wind("east")
                else:
                    return self.change_wind("west")

            # Bingo. We want to make sure the wind always covers our ass
            if ohq.building_east is None:
                return self.change_wind("west")
            if ohq.building_west is None:
                return self.change_wind("east")

        if sides == 2:
            #############################
            # in corner
            #############################
            dirs = [ohq.building_north, ohq.building_east, ohq.building_south, \
                    ohq.building_west, ohq.building_north]
            for i in range(0,len(dirs)-1):
                if dirs[i] is None and dirs[i+1] is None:
                    if i == 0:
                        #northeast
                        # they'll have northwest, so we want wind blowing east always
                        return self.change_wind("east")

                    if i == 1:
                        #southeast
                        # they'll have southwest, so we want wind blowing east always
                        return self.change_wind("east")

                    if i == 2:
                        #southwest
                        # they'll have southeast, so we want wind blowing west always
                        return self.change_wind("west")

                    if i == 3:
                        #northwest
                        # they'll have northeast, so we want wind blowing west always
                        return self.change_wind("west")

            #############################
            # in tunnel
            #############################
            if ohq.building_north is None and ohq.building_south is None:
                #east->west tunnel
                if f == "east" or f == "west":
                    if hq.building_east is None or hq.building_east.fire <= hq.building_west.fire:
                        return self.change_wind("west")
                    else:
                        return self.change_wind("east")
            if ohq.building_west is None and ohq.building_east is None:
                #north->south tunnel
                if f == "east" or f == "west":
                    if hq.building_north is None or hq.building_north.fire <= hq.building_south.fire:
                        return self.change_wind("south")
                    else:
                        self.change_wind("north")

        #### can we do /anything/ to help ourselves? ############
        # point the wind where the fires are lowest on our side and highest on theirs
        ohqs = [x for x in ohq.get_sides_true()]
        hqs = [x for x in hq.get_sides_true()]

        maxdiff = 0
        maxdiffx = -1
        maxdiffy = -1
        for x in hqs:
            for y in ohqs:
                if x is None or y is None or x.is_headquarters or y.is_headquarters:
                    continue
                if x.fire < y.fire and y.fire-x.fire > maxdiff:
                    maxdiffx = x
                    maxdiffy = y
                    maxdiff  = abs(x.fire-y.fire)

        # relate direction back to hq
        if maxdiff != 0:
            if maxdiffy is ohq.building_north:
                return self.change_wind("south") #it will take care of "already north"
            if maxdiffy is ohq.building_south:
                return self.change_wind("north")
            if maxdiffy is ohq.building_east:
                return self.change_wind("west")
            if maxdiffy is ohq.building_west:
                return self.change_wind("east")

        
    def change_wind(self, dir):
        if self.game.next_forecast.direction == dir:
            return
        f = self.game.next_forecast.direction
        dirs = ["north", "west", "south", "east", "north"]

        for w in self.player.weather_stations:
            if w.is_usable:
                ws = w
                break
        
        for i in range(0,len(dirs)):
            if dirs[i] == f:
                if i < len(dirs)-1 and dirs[i+1] == dir:
                    ws.rotate(True)
                    return
                if i > 0 and dirs[i-1] == dir:
                    ws.rotate()
                    return
        # it's 2 away
        ws.rotate()
        for w in self.player.weather_stations:
            if w.is_usable:
                w.rotate()
                break


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
            while b.fire > 0 and self.player.bribes_remaining > 0 and not b.is_headquarters:
                b.put_out_fire(self)
            
    
    # always relative to enemy hq
    def set_fires(self, f):
        if self.player.bribes_remaining <= 0:
            return

        for wh in self.player.warehouses:
            if wh.is_headquarters or not wh.is_usable:
                continue
            target = self.other_player.headquarters.get_building_by_wind(f)

            if target is None:
                return

            if self.player.bribes_remaining > 0 and target.fire < 18 and not target.is_headquarters: #18 as, ideally, we could be spending our shit better somewhere else
                wh.ignite(target)
            else:
                break


    def purge_max_exposed_building(self):
        corruption = sorted(self.player.other_player.warehouses, key=lambda warehouses: warehouses.exposure)
        if corruption[-1].exposure > 20:
            for pd in self.player.police_departments:
                if pd.is_usable and self.player.bribes_remaining > 0:
                    pd.raid(corruption[-1])
                    break


    def purge_fire_departments(self):
        for fd in self.player.other_player.fire_departments:
            if self.player.bribes_remaining <= 0:
                return
            warehouse_by_dist = dict()
            for wh in self.player.warehouses:
                if not wh.is_headquarters:
                    warehouse_by_dist[wh] = abs(wh.x - fd.x) + abs(wh.y - fd.y)
            for wh in sorted(warehouse_by_dist, key=warehouse_by_dist.get, reverse=True):
                if wh.is_usable and fd.fire < 18:
                    wh.ignite(fd)
                    break

    def ignite_useless_tiles(self):
        """
        In a vain attempt to scare shellai-like ais, let's light the enemy hq's surrounding tiles where possible
        """
        warehouse_by_dist = dict()
        for wh in self.player.warehouses:
            if not wh.is_headquarters:
                warehouse_by_dist[wh] = abs(wh.x - self.player.headquarters.x) + abs(wh.y - self.player.headquarters.y)
        for wh in sorted(warehouse_by_dist, key=warehouse_by_dist.get, reverse=True):
            if not wh.is_usable:
                continue
            for t in self.other_player.headquarters.get_sides():
                if t.is_headquarters or t.fire >= 18 or not wh.is_usable or self.player.bribes_remaining <= 0:
                    continue
                wh.ignite(t)

    def print_title(self, title, color, after):
        print(color+"|"+title+"|"+after, end="")
