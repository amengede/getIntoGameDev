class Door:
    """
        A door in the scene, links two rooms
    """


    def __init__(self, coordinate):
        """
            Create a new door.

            Parameters:
                coordinate (tuple (row,col)) grid coordinate on which the door sits
        """

        self.coordinate = coordinate
        self.planes = []