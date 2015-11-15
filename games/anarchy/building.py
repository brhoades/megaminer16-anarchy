# Generated by Creer at 08:40PM on November 07, 2015 UTC, git hash: '1b69e788060071d644dd7b8745dca107577844e1'
# This is a simple class to represent the Building object in the game. You can extend it by adding utility functions here in this file.

from games.anarchy.game_object import GameObject

# <<-- Creer-Merge: imports -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
# you can add addtional import(s) here
# <<-- /Creer-Merge: imports -->>

class Building(GameObject):
    """ The class representing the Building in the Anarchy game.

    A basic building. It does nothing besides burn down. Other Buildings inherit from this class.
    """

    def __init__(self):
        """ initializes a Building with basic logic as provided by the Creer code generator
        """
        GameObject.__init__(self)

        # private attributes to hold the properties so they appear read only
        self._bribed = False
        self._building_east = None
        self._building_north = None
        self._building_south = None
        self._building_west = None
        self._fire = 0
        self._health = 0
        self._is_headquarters = False
        self._owner = None
        self._x = 0
        self._y = 0
        self._sides = None


    @property
    def bribed(self):
        """when true this building has already been bribed this turn and cannot be bribed again this turn.
        """
        return self._bribed


    @property
    def building_east(self):
        """The Building directly to the east of this building, or null if not present.
        """
        return self._building_east


    @property
    def building_north(self):
        """The Building directly to the north of this building, or null if not present.
        """
        return self._building_north


    @property
    def building_south(self):
        """The Building directly to the south of this building, or null if not present.
        """
        return self._building_south


    @property
    def building_west(self):
        """The Building directly to the west of this building, or null if not present.
        """
        return self._building_west


    @property
    def fire(self):
        """How much fire is currently burning the building, and thus how much damage it will take at the end of its owner's turn. 0 means no fire.
        """
        return self._fire


    @property
    def health(self):
        """How much health this building currently has. When this reaches 0 the Building has been burned down
        """
        return self._health


    @property
    def is_headquarters(self):
        """true if this is the Headquarters of the owning player, false otherwise. Burning this down wins the game for the other Player.
        """
        return self._is_headquarters


    @property
    def owner(self):
        """The player that owns this building. If it burns down (health reaches 0) that player gets an additional bribe(s).
        """
        return self._owner


    @property
    def x(self):
        """The location of the Building along the x-axis
        """
        return self._x


    @property
    def y(self):
        """The location of the Building along the y-axis
        """
        return self._y

    @property
    def is_alive(self):
        return self.health > 0

    @property
    def is_usable(self):
        return self.is_alive and not self.bribed

    @property
    def time_until_death(self):
        if self.health <= 0:
            return 0
        if self.fire == 0:
            return 1000000000

        return self.health/self.fire # integer division?

    def get_sides(self):
        """List of adjacent buildings
        """
        return [x for x in [self._building_east,self._building_north,self._building_south,self._building_west] if x is not None]

    def get_sides_true(self):
        """List of adjacent buildings
        """
        return [x for x in [self._building_east,self._building_north,self._building_south,self._building_west]]

    def needs_extinguish(self):
        """Has building met threshold for putting out?
        """
        return self.time_until_death <= self._firethreshold
    
    def get_building_by_dir(self, dir):
        if dir == "north":
            return self.building_north
        if dir == "south":
            return self.building_south
        if dir == "west":
            return self.building_west
        if dir == "east":
            return self.building_east

    def get_building_by_wind(self, dir):
        if dir == "north":
            return self.building_south
        if dir == "south":
            return self.building_north
        if dir == "west":
            return self.building_east
        if dir == "east":
            return self.building_west
    
    # <<-- Creer-Merge: functions -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
    # if you want to add any client side logic (such as state checking functions) this is where you can add them
    # <<-- /Creer-Merge: functions -->>
    
    def put_out_fire(self, ai):
        """ Finds the first available fire department and calls extinguish on current building
            
        Args:
            fire_departments: List of player owned fire departments
        """
        for dep in ai.player.fire_departments:
            if self.needs_extinguish and dep.is_usable \
                and ai.player.bribes_remaining > 0:
                dep.extinguish(self)
