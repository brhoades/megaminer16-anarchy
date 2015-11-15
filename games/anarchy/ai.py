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
        self._fireAllotment = 0.50
        self.other_player = self.player.other_player

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

        print("")
        print("NEW TURN: bribes={0}\t\t".format(self.player.bribes_remaining), end="")

        self.set_fires(self.decide_wind())
        # self.purge_fire_departments()
        self.fire_safety_check()
        #FIXME: ^ spot

        # purge any buildings, starting with hq, which may be easy kills
        self.purge_max_exposed_building()

        # light their fire departments with remaining points
        self.purge_fire_departments()

        if self.player.bribes_remaining > 0:
            print("{0}".format(self.player.bribes_remaining), end="")

        return True

    def decide_wind(self):
        """Change wind if needed
            
            Returns fire target tile. None if there isn't one.
        """
        ohq = self.other_player.headquarters
        hq = self.player.headquarters
        sides = 0
        f = self.game.next_forecast.direction

        for s in ohq.get_sides():
            if s is not None:
                sides += 1

        #############################
        # in cover
        #############################
        if sides == 1:
            if ohq.building_south is None and (f == "north" or f == "south"):
                if hq.building_west is None or hq.building_west.fire <= hq.building_east.fire:
                    self.change_wind_direction("east")
                    return ohq.building_west
                else:
                    self.change_wind_direction("west")
                    return ohq.building_east
                #FIXME: Is it ever worth it to go south?
            if ohq.building_east is None and (f == "east" or f == "west"):
                if hq.building_south is None or hq.building_south.fire <= hq.building_north.fire:
                    self.change_wind_direction("north")
                    return ohq.building_south
                else:
                    self.change_wind_direction("south")
                    return ohq.building_north

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
                        #FIXME: It's more advantageous to protect ourselves with 2 moves if we canc

                        if f == "south":
                            self.change_wind("east")
                            return ohq.building_west
                        if f == "west":
                            self.change_wind("north")
                            return ohq.building_south

                    if i == 1:
                        #southeast
                        if f == "north":
                            self.change_wind("east")
                            return ohq.building_west
                        if f == "west":
                            self.change_wind("south")
                            return ohq.building_north

                    if i == 2:
                        #southwest
                        if f == "north":
                            self.change_wind("west")
                            return ohq.building_east
                        if f == "east":
                            self.change_wind("south")
                            return ohq.building_north

                    if i == 3:
                        #northwest
                        if f == "south":
                            self.change_wind("west")
                            return ohq.building_east
                        if f == "east":
                            self.change_wind("north")
                            return ohq.building_south
            #############################
            # in tunnel
            #############################
            if ohq.building_north is None and ohq.building_south is None:
                #east->west tunnel
                if f == "east" or f == "west":
                    if hq.building_east is None or hq.building_east.fire <= hq.building_west.fire:
                        self.change_wind("west")
                        return ohq.building_east
                    else:
                        self.change_wind("east")
                        return ohq.building_west
            if ohq.building_west is None and ohq.building_east is None:
                #north->south tunnel
                if f == "east" or f == "west":
                    if hq.building_north is None or hq.building_north.fire <= hq.building_south.fire:
                        self.change_wind("south")
                        return ohq.building_north
                    else:
                        self.change_wind("next")
                        return ohq.building_south



        if sides == 3:
            for s in ohq.get_sides():
                if s is not None:
                    return s

        #############################
        # in open / sides don't matter
        #############################
        if f == "north":
            return ohq.building_south
        if f == "south":
            return ohq.building_north
        if f == "east":
            return ohq.building_west
        if f == "west":
            return ohq.building_east
        

        return None

    def change_wind(self, dir):
        if self.game.next_forecast.direction == dir:
            return
        f = self.game.next_forecast.direction
        dirs = ["north", "west", "south", "east", "north"]

        for w in self.player.weather_stations:
            if w.is_usable:
                ws = w
                break
        
        for i in range(0,len(dirs)-1):
            if dirs[i] == f:
                if dirs[i+1] == dir:
                    return ws.rotate(True)
                if i > 0 and dirs[i-1] == dir:
                    return ws.rotate()
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

    def fire_safety_check(self):
        """
        Fire safety check
        Put out fire in direction wind blows
        """
        b = self.player.headquarters.get_building_by_wind(self.game.current_forecast.direction)
        if b is None:
            return
        while b.fire > 0 and self.player.bribes_remaining > 0:
            b.put_out_fire(self)
            
    
    def set_fires(self, target):
        if target is None:
            print("?", end="")
            return

        for wh in self.player.warehouses:
            if wh.is_headquarters or not wh.is_usable:
                continue
            if self.player.bribes_remaining > 0 and target.fire < 20:
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
