class WindAI:
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
            # stalemate
            if hq.building_south is None and f != "north":
                return self.change_wind("north")
            else:
                return
            if hq.building_north is None and f != "south":
                return self.change_wind("south")
            else:
                return

            # Bingo. We want to make sure the wind always covers our ass
            if hq.building_east is None:
                return self.change_wind("west")
            if hq.building_west is None:
                return self.change_wind("east")
            return # don't break something optimal

        if sides == 2:
            #############################
            # in corner
            #############################
            #FIXME: uh, these should be ours. no wonder directions are backwards :>
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
                #FIXME: what are they going to extinguish? Make this take the most moves for them
                if f == "east" or f == "west":
                    if hq.building_east is None or hq.building_east.fire <= hq.building_west.fire:
                        return self.change_wind("north")
                    else:
                        return self.change_wind("south")
            if ohq.building_west is None and ohq.building_east is None:
                #north->south tunnel
                if f == "east" or f == "west":
                    if hq.building_north is None or hq.building_north.fire <= hq.building_south.fire:
                        return self.change_wind("east")
                    else:
                        return self.change_wind("west")
            return # don't break something optimal

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

    def wind_to_text(self, f):
        if f == "north":
            return "N"
        elif  f == "south":
            return "S"
        elif f == "east":
            return "E"
        else:
            return "W"
