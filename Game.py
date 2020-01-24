"""
Lost Rover Game
Anurag Vaidya
16/10/2019
"""
from gameboard import *
from random import *
from array import *

class Game:
    
    SIZE = 15 # rooms are 15x15
    UID = 0 # keeps room uid
    X = 20 # after how many steps should I generate new task?
    BROKEN = ['engine', 'exhaust', 'cabin', 'wings', 'tail', 'wheels'] # list of things that are broken at the start of the game 
    LIMIT = 100 # after how many steps would a fixed part break again
    
    def __init__(self):
        '''Constructor for the game class, which drives the game
        inputs: self
        return: none
        '''
        
        # initialize Gameboard
        self.gui = GameBoard("Lost Rover", self, Game.SIZE)
        self._check = 100

        # initialize room
        self._current_room = Room(Game.UID)

        # store the rooms in a dictionary and update uid after storing
        self._room_dict = {}
        self._add_room(self._current_room)

        # initialize rover
        self._rover = Rover(self._current_room)

        # set rover location
        self._rover._set_initial_location()

        # define list that holds the linked lists
        self._portal_connections = []

        # inventory list
        self._inventory = InventoryLL()

        # define stack to keep track of way
        self._stack = stack()

        # list of all UIDs
        self._all_UID = list()
        self._all_UID.append(0)

        # initialize task queue
        self._task_queue = Task_Queue()

        # tasks- generate two tasks since game just started, and enqueue them
        self._current_task = ''
        first_task = Task()
        Game.BROKEN.remove(first_task._broken_part)
        self._task_queue.enqueue(first_task)
        second_task = Task()
        Game.BROKEN.remove(second_task._broken_part)
        self._task_queue.enqueue(second_task)

        # keep track of steps
        self._steps = 0

        # keep track of fixed items
        self._fixed = []


    def start_game(self):
        '''Starts the game
        inputs: self
        return: none
        '''
        self.gui.run()

    def get_rover_image(self):
        """ Called by GUI when screen updates.
            Returns image name (as a string) of the rover.
            (Likely 'rover.ppm') """
        return 'rover.ppm'

    def get_rover_location(self):
        """ Called by GUI when screen updates.
            Returns location (as a Point). """
        
        return self._rover._get_location()

    def get_image(self, point):
        """ Called by GUI when screen updates.
            Returns image name (as a string) or None for the
            part, ship component, or portal at the given
            coordinates. ('engine.ppm' or 'cake.ppm' or
            'portal.ppm', etc) """
        if self._current_room._whats_at_XY(point) == None:
            return None
        else:
            return self._current_room._whats_at_XY(point)._get_picture()

    def go_up(self):
        """ Called by GUI when button clicked.
            If legal, moves rover. If the robot lands
            on a portal, it will teleport. """
                
        if self._rover._get_location().getY() == 0: # if @ wall
            if self.get_image(Point(self._rover._get_location().getX(),14)) == 'portal.ppm' or self.get_image(Point(self._rover._get_location().getX(),14)) == 'portal-flashing.ppm': # check if looping will land on portal
                self._rover._set_location(Point(self._rover._get_location().getX(), 14)) # moved onto portal
                self.on_portal()
            else: # just loop
                self._rover._set_location(Point(self._rover._get_location().getX(), 14))
        elif self.get_image(Point(self._rover._get_location().getX(), self._rover._get_location().getY() - 1)) == 'portal.ppm' or self.get_image(Point(self._rover._get_location().getX(), self._rover._get_location().getY() - 1)) == 'portal-flashing.ppm':
            self._rover._set_location(Point(self._rover._get_location().getX(), self._rover._get_location().getY() - 1))
            self.on_portal()
        else:
            self._rover._set_location(Point(self._rover._get_location().getX(), self._rover._get_location().getY() - 1))

        # keep track of steps
        self._steps = self._steps + 1

        # if steps crosses X then add new task
        self._generate_task(self._steps)
            
                                      
    def go_down(self):
        """ Called by GUI when button clicked.
            If legal, moves rover. If the robot lands
            on a portal, it will teleport. """
        
        if self._rover._get_location().getY() == 14: # if @ wall
            if self.get_image(Point(self._rover._get_location().getX(),0)) == 'portal.ppm' or self.get_image(Point(self._rover._get_location().getX(),0)) == 'portal-flashing.ppm': # check if looping will land on portal
                self._rover._set_location(Point(self._rover._get_location().getX(), 0)) # moved onto portal
                self.on_portal()
            else: # just loop
                self._rover._set_location(Point(self._rover._get_location().getX(), 0))
        elif self.get_image(Point(self._rover._get_location().getX(), self._rover._get_location().getY() + 1)) == 'portal.ppm' or self.get_image(Point(self._rover._get_location().getX(), self._rover._get_location().getY() + 1)) == 'portal-flashing.ppm':
            self._rover._set_location(Point(self._rover._get_location().getX(), self._rover._get_location().getY() + 1))
            self.on_portal()
        else:
            self._rover._set_location(Point(self._rover._get_location().getX(), self._rover._get_location().getY() + 1))

        # keep track of steps
        self._steps = self._steps + 1

        # if steps crosses X then add new task
        self._generate_task(self._steps)
        
    def go_left(self):
        """ Called by GUI when button clicked.
            If legal, moves rover. If the robot lands
            on a portal, it will teleport. """
                
        if self._rover._get_location().getX() == 0: # if @ wall
            if self.get_image(Point(14, self._rover._get_location().getY())) == 'portal.ppm' or self.get_image(Point(14, self._rover._get_location().getY())) == 'portal-flashing.ppm': # check if looping will land on portal
                self._rover._set_location(Point(14, self._rover._get_location().getY())) # moved onto portal
                self.on_portal()
            else: # just loop
                self._rover._set_location(Point(14, self._rover._get_location().getY()))
        elif self.get_image(Point(self._rover._get_location().getX() - 1, self._rover._get_location().getY())) == 'portal.ppm' or self.get_image(Point(self._rover._get_location().getX() - 1, self._rover._get_location().getY())) == 'portal-flashing.ppm':
            self._rover._set_location(Point(self._rover._get_location().getX() - 1, self._rover._get_location().getY()))
            self.on_portal()
        else:
            self._rover._set_location(Point(self._rover._get_location().getX() - 1, self._rover._get_location().getY()))
        
        # keep track of steps
        self._steps = self._steps + 1

        # if steps crosses X then add new task
        self._generate_task(self._steps)
        
    def go_right(self):
        """ Called by GUI when button clicked.
            If legal, moves rover. If the robot lands
            on a portal, it will teleport. """
                
        if self._rover._get_location().getX() == 14: # if @ wall
            if self.get_image(Point(0, self._rover._get_location().getY())) == 'portal.ppm' or self.get_image(Point(0, self._rover._get_location().getY())) == 'portal-flashing.ppm': # check if looping will land on portal
                self._rover._set_location(Point(0, self._rover._get_location().getY())) # moved onto portal
                self.on_portal()
            else: # just loop
                self._rover._set_location(Point(0, self._rover._get_location().getY()))
        elif self.get_image(Point(self._rover._get_location().getX() + 1, self._rover._get_location().getY())) == 'portal.ppm' or self.get_image(Point(self._rover._get_location().getX() + 1, self._rover._get_location().getY())) == 'portal-flashing.ppm':
            self._rover._set_location(Point(self._rover._get_location().getX() + 1, self._rover._get_location().getY()))
            self.on_portal()
        else:
            self._rover._set_location(Point(self._rover._get_location().getX() + 1, self._rover._get_location().getY()))

        # keep track of steps
        self._steps = self._steps + 1

        # if steps crosses X then add new task
        self._generate_task(self._steps)

        
    def show_way_back(self):
        """ Called by GUI when button clicked.
            Flash the portal leading towards home. """

        # peek stack to get the room you want to go to. pop if you actually go thru
        if self._stack.size > 0:
            room_to_go = self._stack.peek()
            # find the portal that will lead to the room
            for row in range(15):
                for col in range(15):
                    # find whats at xy
                    curr_loc = Point(row, col)
                    obj_at_xy = self._current_room._whats_at_XY(curr_loc)

                    # check if the object is portal
                    if isinstance(obj_at_xy, Portal):
                        # check if the portal is connected
                        if obj_at_xy._get_connected():
                            # since connected, check which room connected to 
                            # see if the portal is connected to the room_to_go 
                            for ll in self._portal_connections:
                                currNode = ll._head
                                if currNode.item == obj_at_xy:
                                    room_connected_to = currNode.next.item._get_portal_UID()
                                    if room_to_go == room_connected_to:
                                        obj_at_xy._set_picture('portal-flashing.ppm')
                                        obj_at_xy._tag = True
                                        obj_at_xy._flashing = True
                                else:
                                    if currNode.next.item == obj_at_xy:
                                        room_connected_to = currNode.item._get_portal_UID()
                                        if room_to_go == room_connected_to:
                                            obj_at_xy._set_picture('portal-flashing.ppm')
                                            obj_at_xy._tag = True
                                            obj_at_xy._flashing = True

        
    def get_inventory(self):
        """ Called by GUI when inventory updates.
            Returns entire inventory (as a string).
            3 cake
            2 screws
            1 rug
        """
        output = ''
        currNode = self._inventory._head

        if len(self._inventory) > 0:
            
            while currNode.next != None:
                output = output + str(currNode._quantity()) + ' ' + str(currNode._name()) + '\n'
                currNode = currNode.next
            output = output + str(currNode._quantity()) + ' ' + str(currNode._name()) + '\n'

        return output

    def pick_up(self):
        """ Called by GUI when pick up button clicked.
            If rover is standing on a part (not a portal
            or ship component), pick it up and add it
            to the inventory. """

        # get rover location
        currLoc = self.get_rover_location()
        
        # if item is part then do the things
        XY_obj = self._current_room._whats_at_XY(currLoc)

        if isinstance(XY_obj, Parts):

            # check if inventory is empty
            if len(self._inventory) == 0:
                # if empty then add node
                newNode = _InventoryLLNode(XY_obj._get_picture()[0:len(XY_obj._get_picture())-4])
                self._inventory.add(newNode)
                

            # elif len is 1
            elif len(self._inventory) == 1:
                currNode = self._inventory._head
                picture = XY_obj._get_picture()
                if str(currNode._name()) == picture[0:len(picture) - 4]:
                    currNode.quantity = currNode._quantity() + 1
                else:
                    self._inventory.add(_InventoryLLNode(picture[0:len(picture) - 4]))

            # else len > 1
            else:
                picture = XY_obj._get_picture()
                if not self._inventory.__contains__(picture[0:len(picture) - 4]):
                    self._inventory.add(_InventoryLLNode(picture[0:len(picture) - 4]))

            # update current location to blank
            self._current_room._set_item_at_location(currLoc, None)

        
        # Make sure that only items with non-zero quantity are not in the LL
        currNode = self._inventory._head
        
        # if only 1 item
        if currNode.next == None:
            if currNode._quantity() == 0:
                self._inventory.head = None
                self._inventory._size = self._inventory._size - 1 

        else:
            while currNode.next != None:
                nextNode = currNode.next
                if nextNode._quantity() == 0:
                    currNode.next = nextNode.next
                    self._inventory._size = self._inventory._size - 1
                currNode = currNode.next        

    def get_current_task(self):
        """ Called by GUI when task updates.
            Returns top task (as a string).
            'Fix the engine using 2 cake, 3 rugs' or
            'You win!'
        """
        if self._current_task == '':
            self._current_task = self._task_queue.dequeue()
            return str(self._current_task)
        else:
            if self._task_queue.is_empty() and self._current_task._completed:
                self._win()
                return 'You completed all the tasks! You WIN!!!!\nMove Rover now'
            elif not self._any_broken() and self._current_room._get_UID() == 0:
                self._win()
                return 'You fixed all broken parts so your ship is ready to fly \nYou WIN!!!!\nMove Rover now'
            else:
                if self._current_task._completed:
                    self._current_task = self._task_queue.dequeue()
                    return str(self._current_task)
            

    def perform_task(self):
        """ Called by the GUI when button clicked.
            If necessary parts are in inventory, and rover
            is on the relevant broken ship piece, then fixes
            ship piece and removes parts from inventory. If
            we run out of tasks, we win. """        


        # whats the broken part associated with the task?
        broken_part = ' '
        if self._current_task != '':
            broken_part = self._current_task._broken_part

        # whats the object at xy
        obj_at_xy = self._current_room._whats_at_XY(self._rover._get_location())
        pic_at_xy = ''
        if obj_at_xy != None:
            pic_at_xy = obj_at_xy._get_picture()[0:len(obj_at_xy._get_picture())-10]

        # check if rover on correct broken part
        if broken_part == pic_at_xy:
            # what parts and quantities to a require
        
            items_to_fix = self._current_task._parts
            quantities_to_fix = self._current_task._quantities

            # check of items and quantities are empty. If yes, that means the task is completed
            if items_to_fix == [] and quantitieis_to_fix == []:
                self._current_task._completed = True
            else:
                # check if enough times to finish task
                found_items = []
                for i in range(3):
                    break_tag = False
                    curr_item = items_to_fix[i]
                    curr_quantity = quantities_to_fix[i]
                    currNode = self._inventory._head
                    
                    if currNode is not None:
                        
                        while currNode is not None and not break_tag:
                            
                            if str(currNode._name()) == curr_item and currNode._quantity() >= curr_quantity and str(currNode._name()) not in found_items:
                                
                                # use items
                                found_items.append(str(currNode._name()))

                                # update inventory
                                currNode._set_quantity(currNode._quantity() - curr_quantity)
                                
                                if currNode._quantity() <= 0:
                                    self._inventory.remove(currNode._name())

                                # signal break
                                break_tag = True
                                
                            else:
                                # try next node
                                currNode = currNode.next

                if len(found_items) == 3:
                    # task completed
                    self._current_task._completed = True
                    obj_at_xy._set_picture(broken_part + '.ppm')
                    self._fixed.append(broken_part)
                    if broken_part in Game.BROKEN:
                        Game.BROKEN.remove(broken_part)

        
    # Put other methods here as needed
    def on_portal(self):
        """ Called everytime when the rover steps on a portal
        Connect the rover to an appropriate room (new room or previous connection)
        """

        # if any of the flashing portals are not visited, then change their image 
        for row in range(15):
            for col in range(15):
                curr_loc = Point(row, col)
                obj_at_xy = self._current_room._whats_at_XY(curr_loc)
                if isinstance(obj_at_xy, Portal) and obj_at_xy._get_picture() == 'portal-flashing.ppm':
                    obj_at_xy._set_picture('portal.ppm') 
        
        # if portal tag is true, then create a new room
        
        if self._current_room._whats_at_XY(self._rover._get_location())._get_tag():
            # tag is true
            if self._current_room._whats_at_XY(self._rover._get_location())._get_connected():
                # portal connected to a room
                current_portal = self._current_room._whats_at_XY(self._rover._get_location())
                UID = 0 # room I am going to 
                location = Point(0,0) # location of rover in the new room
                for ll in self._portal_connections:
                    # get what room the portal is connected to and the portal location
                    if ll.__contains__(current_portal):
                        currNode = ll._head
                        if currNode.item == current_portal:
                            currNode = currNode.next
                            UID = currNode.item._get_portal_UID()
                            location = currNode.item._get_location()     
                        else:
                            UID = currNode.item._get_portal_UID()
                            location = currNode.item._get_location()

                # if going to a room with lower UID then do nothing, else add UID to stack. If going to a room
                # that is at the top of the stack then pop the stack
                
                if Game.UID < UID:
                    self._stack.push(Game.UID)
                elif UID == self._stack.peek():
                   
                    self._stack.pop()

                # if flashing then change tag and picture
                if current_portal._flashing:
                    current_portal._flashing = False
                    current_portal._set_picture('portal.ppm')
                    
                # set up new room
                
                self._current_room = self._get_room(UID)
                self._rover._set_location(location)
                Game.UID = UID
                
            else:
                
                # going to a new room because portal not conencted to other room
                portal_list = PortalLL()
                portal_list.add(self._current_room._whats_at_XY(self._rover._get_location()))
                self._current_room._whats_at_XY(self._rover._get_location())._set_connected(True)
                self._portal_connections.append(portal_list)

                # if going to new room, add old UID to stack
                self._stack.push(Game.UID)
                
                # update UID
                Game.UID = self._all_UID[-1] + 1
                self._all_UID.append(Game.UID)

                # create a new room
                self._current_room = Room(Game.UID)

                # add room to room dictionary
                self._add_room(self._current_room)

                # set rover on top of a portal
                while True:
                    point_temp = Point(randint(0,14), randint(0,14))
                    if self._current_room._whats_at_XY(point_temp) != None:
                        if self._current_room._whats_at_XY(point_temp)._get_picture() == 'portal.ppm':
                            self._rover._set_location(point_temp)
                            portal_list.add(self._current_room._whats_at_XY(point_temp))
                            self._current_room._whats_at_XY(point_temp)._set_connected(True)
                            break
                        
        # else just set tag to true and do nothing
        else:
            self._current_room._whats_at_XY(self._rover._get_location())._set_tag(True)

    def _add_room(self, room):
        ''' Called everytime a new room is created and stores the new room with its UID in a dictionary
        '''
        self._room_dict[room._get_UID()] = room

    def _get_room(self, UID):
        ''' Returns the room that corresponds to the UID
        '''
        return self._room_dict[UID]

    def _generate_task(self, steps):
        ''' called every time the rover moves
        Every Limit steps, a fixed part is broken
        Every X steps, a new task is added to the queue
        '''
        if steps%Game.LIMIT == 0 and self._fixed != []:
            self._break_something_fixed()
        elif steps%Game.X == 0 and Game.BROKEN != []:
            new_task = Task()
            Game.BROKEN.remove(new_task._broken_part)
            self._task_queue.enqueue(new_task)

    def _any_broken(self):
        '''
        Checks if there are any broken ship compoenents present on the game board
        '''
        for row in range(15):
            for col in range(15):
                obj_at_xy = self._current_room._whats_at_XY(Point(row, col))
                if obj_at_xy is not None:
                    pic_at_xy = obj_at_xy._get_picture()
                    if pic_at_xy in ['enginebroken.ppm', 'exhaustbroken.ppm', 'cabinbroken.ppm', 'tailbroken.ppm', 'wingsbroken.ppm', 'wheelsbroken.ppm']:
                        return True
        return False
                
    def teleport(self):
        ''' check if all items to complete the task are present in the inventory. If yes, then go to room with UID 0 (home)
        '''
        # check of items and quantities are empty. If yes, that means the task is completed
        if self._current_task == '':
            pass
        else:
            items_to_fix = self._current_task._parts
            quantities_to_fix = self._current_task._quantities
            # check if enough times to finish task
            found_items = []
            for i in range(3):
                break_tag = False
                curr_item = items_to_fix[i]
                curr_quantity = quantities_to_fix[i]
                currNode = self._inventory._head
                
                if currNode is not None:
                    
                    while currNode is not None and not break_tag:
                        
                        if str(currNode._name()) == curr_item and currNode._quantity() >= curr_quantity and str(currNode._name()) not in found_items:
                            
                            # use items
                            found_items.append(str(currNode._name()))

                            # signal break
                            break_tag = True
                            
                        else:
                            # try next node
                            currNode = currNode.next

                if len(found_items) == 3 and Game.UID != 0:
                    # task completed so teleport to home room
                    self._current_room = self._get_room(0)
                    Game.UID = 0

                    # set rover location in room 0
                    while True:
                        loc = Point(randint(0,14), randint(0,14))
                        if self._current_room._whats_at_XY(loc) == None:
                            self._rover._set_location(loc)
                            break

                    # clear stack
                    for i in range(len(self._stack)):
                        self._stack.pop()

    def _break_something_fixed(self):
        '''
        Called everytime the rover traverses Limit steps. The method breaks an already fixed object
        '''
        # choose component to break
        
        to_break = self._fixed[randint(0, len(self._fixed) - 1)]

        # find image of component
        for row in range(15):
            for col in range(15):
                if self._current_room._whats_at_XY(Point(row, col)) != None and self._current_room._whats_at_XY(Point(row, col))._get_picture() == to_break + '.ppm':
                    self._current_room._whats_at_XY(Point(row, col))._set_picture(to_break + 'broken.ppm')
                    Game.BROKEN.append(to_break)
                    self._fixed.remove(to_break)
                    
    def _win(self):
        '''
        Does a funny and creative thing when the player wins the game
        '''
        for row in range(15):
            for col in range(15):
                if self._current_room._whats_at_XY(Point(row, col)) == None:
                    dancy_item = Item('dancy.ppm', Point(row, col))
                    self._current_room._set_item_at_location(Point(row, col), dancy_item)
                else:
                    self._current_room._whats_at_XY(Point(row, col))._set_picture('dancy.ppm')
        
# Put other classes here or in other files as needed.
class PortalLL:
    '''
    Linked list class to store the portal connections
    '''

    def __init__(self):
        '''
        Initializes the linked list object
        '''
        self._head = None
        self._size = 0

    # Returns the number of items in the list
    def __len__(self):
        ''' returns the size of the linked list '''
        return self._size

    # Adds a new item to the portal LL
    def add(self, item):
        ''' adds the supplied item (not a node) to the portal linked list'''

        newNode = _PortalListNode(item)
        
        if self._head == None:
            self._head = newNode
        else:
            tempNode = self._head
            
            while tempNode.next != None:
                tempNode = tempNode.next
                
            tempNode.next = newNode
            
        self._size += 1

    def __iter__(self):
        ''' iterator for the portal linked list'''
        
        return _PortalLLIterator(self._head)

    def __contains__( self, target ):
        ''' returns True if the target is present in the portal linked list '''
        
        Pointer = self._head
        while True:
            if Pointer.item == target:
                return True
            elif (Pointer.next != None):
                Pointer = Pointer.next
            else:
                return False
    
class _PortalListNode(object):
    ''' Private class for the portal linked list nodes '''
    
    # class for list nodes. Private class
    def __init__( self, item ):
        ''' initializes the node object. attributes are item and size '''
        self.item = item
        self.next = None

class _PortalLLIterator:

    ''' Iterator for the portal linked list class '''
    
    def __init__( self, listHead ):
        self._curNode = listHead

    def __iter__( self ):
        return self

    def __next__( self ):
        if self._curNode is None :
            raise StopIteration
        else :
            item = self._curNode.item
            self._curNode = self._curNode.next

        return item    

class InventoryLL:
    ''' class for the inventory linked list '''

    def __init__(self):
        ''' constructor for the inventory linked list class '''
        self._head = None
        self._size = 0

    # Returns the number of items in the list
    def __len__(self):
        ''' returns the length of the incentory linked list '''
        return self._size

    # Adds a new item to the inventory LL
    def add(self, item):
        ''' adds the inventory item to the inventory linked list '''

        newNode = _InventoryLLNode(item)
        
        if self._head == None:
            self._head = newNode
        else:
            tempNode = self._head
            
            while tempNode.next != None:
                tempNode = tempNode.next
                
            tempNode.next = newNode
            
        self._size += 1

    def __iter__(self):
        ''' iterator for the inventory linked list class '''
        return _InventoryLLIterator(self._head)

    def __contains__( self, target ):
        ''' checks if the target is present in the inventory linked list '''
        Pointer = self._head
        while True:
            if str(Pointer._name()) == target:
                Pointer.quantity = Pointer.quantity + 1
                return True
            elif (Pointer.next != None):
                Pointer = Pointer.next
            else:
                return False

    def remove(self, n):
        ''' removes the supplied node from the inventory linked list '''
        
        predNode = None
        curNode = self._head
        while curNode is not None and curNode._name() != n:
            predNode = curNode
            curNode = curNode.next


        # Unlink the node and return the item.
        self._size = self._size - 1
        if curNode is self._head:
            self._head = curNode.next
        else :
            predNode.next = curNode.next
        
    
class _InventoryLLNode:
    '''class for list nodes. Private class'''
    
    def __init__( self, item, quantity = 1 ):
        self.name = item
        self.quantity = quantity
        self.next = None

    def _quantity(self):
        ''' return the quantity of the node '''
        return self.quantity

    def _set_quantity(self, new_q):
        ''' sets the quanity of the node'''
        self.quantity = new_q

    def _name(self):
        ''' return the name of the node '''
        return self.name

    def __str__(self):
        ''' string method for the private class '''
        return str(self.name)


class _InventoryLLIterator:
    ''' inventory linked list iterator class '''
    def __init__( self, listHead ):
        self._curNode = listHead

    def __iter__( self ):
        return self

    def __next__( self ):
        if self._curNode is None :
            raise StopIteration
        else :
            item = self._curNode.item
            self._curNode = self._curNode.next

        return item
    
class Item:
    ''' parent class for ship components, portals, and parts '''
    
    # parent class
    def __init__(self, image, point):
        ''' constructor for the Item class. Takes in location of the item and the image '''
        self._image = image
        self._location = point

    def _get_picture(self):
        ''' return the picture attribute of the item '''
        return self._image
    
    def _get_location(self):
        ''' return the location of the item '''
        return self._location

    def _set_location(self, new_location):
        ''' set the location of the item '''
        self._location = new_location

    def _set_picture(self, new_pic):
        ''' set the picture of the item '''
        self._image = new_pic

         
class Portal(Item):
    ''' subclass of the item class'''
    
    def __init__(self, image, point, room_UID):
        ''' constructor for the portal class. Need UID because each portal needs to know which room it is in'''
        # call super
        super().__init__(image, point)

        # tag is specific to portals. True = portal is open, False = portal is closed
        self._tag = True

        # portals need to know which room they are in
        self._portal_UID = room_UID

        # portal needs a tag to check if it is connected
        self._connected = False

        # flashing tag
        self._flashing = False

    # methods specific to Portals
    def _set_tag(self, tag):
        ''' set the open close tag for portals '''
        self._tag = tag

    def _get_tag(self):
        ''' get the open close tag for portals ''' 
        return self._tag

    def _get_portal_UID(self):
        ''' return the portal UID '''
        return self._portal_UID

    def _set_portal_UID(self, new_UID):
        ''' set the portal UID '''
        self._portal_UID = new_UID

    def _get_connected(self):
        ''' see if the portal is previously connected to another room '''
        return self._connected

    def _set_connected(self, tag):
        ''' set the connected tag to True/ False '''
        self._connected = tag

    

class ShipComponent(Item):
    ''' subclass of item class. Holds the ship components'''

    def __init__(self, component, point):
        ''' constructor for the ship components '''
        super().__init__(component, point)


class Parts(Item):
    ''' subclass of item class. Holds the parts '''

    def __init__(self, part, point):
        ''' constructor for the parts '''
        super().__init__(part, point)
        

class Room:
    ''' class that sets up each individual room '''
    
    # set up the room. Dictionary of key (point) and value (image file name)

    def __init__(self, UID):

        ''' constructor to create new rooms. UID required because the room needs to be identified '''

        # set attributes
        self._room = []
        self._UID = UID
        self._num_parts = 0
        self._num_portals = 0
        self._num_components = 0

        # set quantities
        self._set_quantities()

        # set up the room, which is a 2D array of None type rn
        for row in range(15):
            self._room.append([])
            for col in range(15):
                self._room[row].append(None)

        # place items in the room
        self._set_items()

    def _set_quantities(self):
        ''' hard codes or randomly sets the quantities of ship components, parts, and portals in the specific room '''
        
        # define number of portals
        self._num_portals = randint(2, 6)

        # define number of parts and types
        self._num_parts = randint(5,10)

        # define number of components
        if self._UID == 0:
            self._num_components = 7


    def _set_items(self):

        ''' sets up the room with pre-defined quantities of components, parts, and portals '''

        ## determining components and parts
        
        # determine final parts
        all_parts = ['screw.ppm', 'gear.ppm', 'lettuce.ppm', 'cake.ppm', 'bagel.ppm', 'gas.ppm']
        final_parts = ['screw.ppm', 'gear.ppm', 'bagel.ppm', 'gas.ppm']
        for i in range(randint(5,7)):
            final_parts.append(all_parts[randint(0,5)])

        # determine final components
        if self._UID == 0:
            components_location = [(4,6), (5,6),(6,6),(7,6),(5,7),(6,7),(7,7)]
            
            # ship components broken as ppm files
            components_unbroken = ['cabin.ppm', 'engine.ppm', 'exhaust.ppm', 'wheels.ppm', 'tail.ppm', 'wings.ppm']
    
            # set final items
            components_final = ['cabinbroken.ppm', 'enginebroken.ppm', 'exhaustbroken.ppm', 'wingsbroken.ppm', 'tailbroken.ppm', 'wheelsbroken.ppm', 'engine.ppm']

        else:
            components_final = []

        ## set up components, parts, portals

        # set up the components first since their location is hardcoded
        for i in range(self._num_components):
            self._room[components_location[i][0]][components_location[i][1]] = ShipComponent(components_final[i], Point(components_location[i][0],components_location[i][1]))
        
        # set up parts next. They cannot overlap with components or portals
        for part in final_parts:
            not_empty = True
            while not_empty:
                row = randint(0,14)
                col = randint(0,14)
                if self._room[row][col] == None:
                    self._room[row][col] = Parts(part, Point(row, col))
                    not_empty = False
        
        # set up portals
        for i in range(self._num_portals):
            not_empty = True
            while not_empty:
                row = randint(0,14)
                col = randint(0,14)
                if self._room[row][col] == None:
                    self._room[row][col] = Portal('portal.ppm', Point(row, col), self._get_UID())
                    not_empty = False
    
    def _whats_at_XY(self, point):
        ''' given a point, returns the object or None at the Point '''
        return self._room[point.getX()][point.getY()]

    def _get_UID(self):
        ''' returns the UID of the room '''
        return self._UID

    def _set_item_at_location(self, location, item):
        ''' sets an item at a specific location'''
        # location is a point object
        # item is an item object or None
        self._room[location.getX()][location.getY()] = item
                                                                                                
                                                                                        
                                                                                                
class Rover:
    ''' class to create and handle the rover '''
    
    def __init__(self, room):
        ''' constructor for the rover '''
        
        # try out an intial position
        self._rover_position = Point(randint(0,14), randint(0,14))
        self._room = room

    def _get_location(self):
        """
        Returns rover location as point object
        """
        return self._rover_position

    def _set_location(self, point):
        """
        Takes in a point object and sets rover location to that object
        """
        self._rover_position = point

    def _set_initial_location(self):
        while self._room._whats_at_XY(self._get_location()) != None:
            self._rover_position._set_location(Point(randint(0,14), randint(0,14)))

class stack:
    ''' generic stack class. Used to store the way back to home '''
    
    def __init__(self):
        ''' constructor for the stack '''
        self.stack = list()
        self.size = 0

    def __len__(self):
        ''' returns the length of the stack '''
        return self.size

    def push(self, item):
        ''' adds an item to the end of the stack '''
        self.stack.append(item)
        self.size = self.size + 1

    def pop(self):
        ''' removes an item from the end of the stack'''
        item = ''
        if self.size > 0:
            item = self.stack.pop()
            self.size = self.size - 1
        return item

    def peek(self):
        ''' returns what the end of the stack '''
        return self.stack[self.size - 1]

    def __str__(self):
        ''' str method for the stack '''
        s = ''
        for i in range(self.size):
            s = s + ' ' + str(self.stack[i])
        if s == '':
            return('empty stack')
        else:
            return s

class Task:
    ''' class to create new tasks '''
    
    HEADERS = ['Broken Engine! To fix the engine, you will need:', 'Broken Cabin! To fix the cabin, you will need:', 'Broken Exhaust! To fix the exhaust, you will need:', 'Broken Wheels! To fix the wheels, you will need:', 'Broken Tail! To fix the tail, you will need:', 'Broken Wings! To fix the wings, you will need:']
    PARTS = ['screw', 'gear', 'lettuce', 'cake', 'bagel', 'gas']

    def __init__(self):
        ''' constructor for the task class '''
        self._broken_part = Game.BROKEN[randint(0,len(Game.BROKEN) - 1)]
        
        if self._broken_part == 'engine':
            choose_header = 0
        elif self._broken_part == 'cabin':
            choose_header = 1
        elif self._broken_part == 'exhaust':
            choose_header = 2
        elif self._broken_part == 'wheels':
            choose_header = 3
        elif self._broken_part == 'tail':
            choose_header = 4
        else:
            choose_header = 5

        self._task_header = Task.HEADERS[choose_header]

        self._parts = []
        self._quantities = [] # respective for parts
        already_added = []
        for i in range(3):
            while True:
                p = randint(0,5)
                if p in already_added:
                    p = randint(0,5)
                else:
                    self._parts.append(Task.PARTS[p])
                    self._quantities.append(randint(1,3)) 
                    already_added.append(p)
                    break

        self._task = self._task_header
        self._completed = False

        for i in range(len(self._parts)):
            self._task = self._task + '\n' + '- ' + str(self._quantities[i]) + ' ' + self._parts[i]

    def __str__(self):
        ''' string method for the task class '''
        return self._task

class Task_Queue:
    ''' class to store the tasks  in a circular array '''

    def __init__(self, max_size = 1000):
        ''' constructor for the class '''
        self._count = 0
        self._front = 0
        self._back = max_size - 1 # last index
        self._array = Array(max_size)
        self._max_size = max_size

    def __len__(self):
        ''' returns the numbe rof items in the circular array '''
        return self._count

    def is_empty(self):
        ''' returns of the circular array is empty '''
        return self._count == 0

    def is_full(self):
        ''' returns if the circular array is full '''
        return self._count == self._max_size

    def enqueue(self, task):
        '''
        Items that are task objects are added to the circular array
        '''
        assert not self.is_full(), 'You lost the game! :('

        # find current last item --> max_size
        max_size = len(self._array)

        # set item at the back (FIFO)
        self._back = (self._back + 1) % max_size
        self._array[self._back] = task

        # increase size
        self._count = self._count + 1

    def dequeue(self):
        ''' items removed from the circular array '''
        assert not self.is_empty(), 'Empty'

        # get front task 
        task = self._array[self._front]

        # update front pointer
        max_size = len(self._array)
        self._front = (self._front + 1) % max_size

        # reduce size
        self._count = self._count - 1

        return task

    def peek(self):
        ''' returns what is at the front of the circular array '''
        return self._array[self._front]
        
            
""" Launch the game. """
g = Game()
g.start_game() # This does not return until the game is over
