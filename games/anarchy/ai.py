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
        print("")
        print("NEW TURN: bribes={0}\t\t".format(self.player.bribes_remaining), end="")

        self.fire_safety_check()
        self.set_fires()

        # get my first fire department
        first_fire_department = self.player.fire_departments[0]
        if self.can_be_bribed(first_fire_department) and self.player.bribes_remaining > 0:
            # select my first building
            target = self.player.buildings[0]
            # make sure the target isn't a headquarters which can't be extinguished directly
            if not target.is_headquarters:
                # bribe my first fire department to extinguish my first building
                first_fire_department.extinguish(target)

        first_police_department = self.player.police_departments[0]
        if self.can_be_bribed(first_police_department) and self.player.bribes_remaining > 0:
            # select the enemy's first warehouse as the target
            self.get_max_exposed_building()
            # bribe my first police station to raid the first warehouse the other player owns

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
        
        return True

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
        tokensLeft = 100 #FIXME: count tokens left. Each bribe remaining is a token.

        # Biggest deal is hq safety
        for building in self.player.headquarters.get_sides():
            # for some reason we get hq in here sometimes
            if not building.is_headquarters and building.fire > 1: # hardcoded, any fire
                building.put_out_fire(self)
        
        # Order here dictates who gets priority
        buildings = [self.player.fire_departments, self.player.weather_stations] #police_departments, warehouses

        for bs in buildings:
            for b in bs:
                if b.needs_extinguish():
                     b.put_out_fire(self)
    
    def set_fires(self):
        warehouse_by_dist = dict()
        enemy_hq = self.player.other_player.headquarters
        
        for wh in self.player.warehouses:
            warehouse_by_dist[wh] = abs(wh.x + enemy_hq.x) + abs(wh.y + enemy_hq.y)
        for wh in sorted(warehouse_by_dist, key=warehouse_by_dist.get):
            if self.player.bribes_remaining > 0 and self.can_be_bribed(wh):
                # select random building next to enemy headquarter
                target = random.choice(self.player.other_player.headquarters.get_sides())
                wh.ignite(target)


    def get_max_exposed_building(self):
        corruption = sorted(self.player.other_player.warehouses, key=lambda warehouses: warehouses.exposure)
        if corruption[-1].exposure > 20:
            #FIXME: change to next available police department
            self.player.police_departments[0].raid(corruption[-1])
