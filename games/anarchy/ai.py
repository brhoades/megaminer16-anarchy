# This is where you build your AI for the Anarchy game.

from joueur.base_ai import BaseAI

class AI(BaseAI):
    """ the basic AI functions that are the same between games
    """


    def get_name(self):
        """ this is the name you send to the server to play as.

        Returns
            str: the name you want your player to have
        """
        return "Anarchy Python ShellAI" # REPLACE THIS WITH YOUR TEAM NAME


    def start(self):
        """ this is called once the game starts and your AI knows its player.id and game. You can initialize your AI here.
        """


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

        # get my first warehouse
        first_warehouse = self.player.warehouses[0]
        if self.can_be_bribed(first_warehouse) and self.player.bribes_remaining > 0:
            # select the enemy's first building as the target
            target = self.player.other_player.buildings[0]
            # make sure the target isn't a headquarters which can't be ignited directly
            if not target.is_headquarters:
                # bribe my first warehouse to ignite the enemy's first building
                first_warehouse.ignite(target)

        # get my first fire department
        first_fire_department = self.player.fire_departments[0]
        if self.can_be_bribed(first_fire_department) and self.player.bribes_remaining > 0:
            # select my first building
            target = self.player.buildings[0]
            # make sure the target isn't a headquarters which can't be extinguished directly
            if not target.is_headquarters:
                # bribe my first fire department to extinguish my first building
                first_fire_department.extinguish(target)

        # get my first police department
        first_police_department = self.player.police_departments[0]
        if self.can_be_bribed(first_police_department) and self.player.bribes_remaining > 0:
            # select the enemy's first warehouse as the target
            target = self.player.other_player.warehouses[0]
            # bribe my first police station to raid the first warehouse the other player owns
            first_police_department.raid(target)

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

