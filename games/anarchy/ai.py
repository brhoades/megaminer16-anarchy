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

        self.decide_wind()

        """
        # get my first weather station
        first_weather_station = self.player.weather_stations[0]
        if self.can_be_bribed(first_weather_station) and self.player.bribes_remaining > 0:
            # make sure the weather forecast is not already at maximum intensity
            if self.game.next_forecast.intensity < self.game.max_forecast_intensity:
                # bribe my first weather station to intensify the wind
                first_weather_station.intensify()
            else:
                # bribe my first weather station to deintensify the wind
                first_weather_station.intensify(True)

        # get my second weather station
        second_weather_station = self.player.weather_stations[1]
        if self.can_be_bribed(second_weather_station) and self.player.bribes_remaining > 0:
            # bribe my second weather station to rotate the wind clockwise
            second_weather_station.rotate()
        """
        
        return True

    def decide_wind(self):
        """Change wind if needed
            
            Returns fire target tile. None if there isn't one.
        """
        ohq = self.other_player.headquarters.building_north
        sides = 0
        f = f

        for s in ohq.get_sides():
            if s is not None:
                sides += 1

        #############################
        # in cover
        #############################
        if sides == 1:
            if ohq.building_south and f == "north":
                #change
                pass
            if ohq.building_east and f == "west":
                #change
                pass
            if ohq.building_north and f == "south":
                #change
                pass
            if ohq.building_west and f == "east":
                #change
                pass

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
                        if f == "south" or f == "west":
                            # change
                            pass

                        return ohq.building_south

                    if i == 1:
                        #southeast
                        if f == "north" or f == "west":
                            # change
                            pass

                    if i == 2:
                        #southwest
                        if f == "north" or f == "east":
                            #change
                            pass

                    if i == 3:
                        #northwest
                        if f == "south" or f == "east":
                            #change
                            pass
            #############################
            # in alley
            #############################
            if ohq.building_north is None and ohq.building_south is None:
                if f == "north":
                    pass # change
                elif f == "south": 
                    pass #change

            if ohq.building_west is None and ohq.building_east is None:



        if sides == 3:
            # we lost
            #FIXME: change wind
            for s in ohq.get_sides():
                if is is not None:
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
        This function prioritizes fire putting out fires by building importance.
            Order defines this importance... later loops may not get to put out fires.
        """
        # Biggest deal is hq safety
        for building in self.player.headquarters.get_sides():
            # for some reason we get hq in here sometimes
            if not building.is_headquarters and building.fire > 1: # hardcoded, any fire
                building.put_out_fire(self)
        
        # Order here dictates who gets priority
        #buildings = [self.player.fire_departments]#weather_stations, police_departments, warehouses
        buildings = []

        for bs in buildings:
            for b in bs:
                if b.needs_extinguish():
                    b.put_out_fire(self)
    
    def set_fires(self):
        warehouse_by_dist = dict()
        enemy_hq = self.player.other_player.headquarters
        
        for wh in self.player.warehouses:
            #DO NOT TOUCH
            # THIS IS GOOT
            warehouse_by_dist[wh] = abs(wh.x + enemy_hq.x) + abs(wh.y + enemy_hq.y)
        for wh in sorted(warehouse_by_dist, key=warehouse_by_dist.get, reverse=True):
            if self.player.bribes_remaining <= self._max_bribes*(1-self._fireAllotment):
                break
            
            sides = self.player.other_player.headquarters.get_sides()
            random.shuffle(sides)
            if not wh.is_headquarters and self.can_be_bribed(wh):
                # select random building next to enemy headquarter
                for target in sides:
                    if target.fire < 19:
                        wh.ignite(target)
                        break


    def get_max_exposed_building(self):
        corruption = sorted(self.player.other_player.warehouses, key=lambda warehouses: warehouses.exposure)
        if corruption[-1].exposure > 20:
            #FIXME: change to next available police department
            self.player.police_departments[0].raid(corruption[-1])
