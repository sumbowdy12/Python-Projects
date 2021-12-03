# Pandemic Simulation Python Project
# Author: Boris Le
# Date: 12/2/2021
# Tkinter simulations that simulates a covid pandemic and prints out the results.
# Also can perform a parameter study with the parameter study function
# Each person also moves in a way that simulates social distancing

import tkinter
import random
import matplotlib.pyplot as plt
WIDTH = 40                  # How many cells wide the region is
HEIGHT = 30                 # How many cells tall the region is
                            # Note that going larger makes each day take longer.
                            # If you want to go bigger than 150 x 100 or so,
                            # do it in steps so that you can gauge how slow your
                            # computer gets
CELL_PIXEL_SIZE = 12        # Size of each cell on screen, in pixels

SCREEN_UPDATE_FREQUENCY = 1 # How often to redraw the screen.  Making this 5 or 10
                            # will cause the screen to redraw only every 5 or 10
                            # days, speeding up the run-time, slightly.

STARTING_INFECTED = 4       # How many "patient zero"s are there in your population?

POPULATION_DENSITY = .9    # Fraction of cells have a person in them

SYMPTOM_CHANCE = .4        # Chance that people who are infected will develop
                           # symptoms (per day)

MORTALITY_RATE = .02       # Fraction of people (with symptoms) who will die from it
    
INFECTION_LENGTH = 6       # How many days the infection lasts

CONTAGION_FACTOR = .2       # If you come into contact with someone who is contagious,
                            # how likely are you to get it?
class Person:
    # There are five states a person can be in:
    #   Susceptable:  They've never had it, and can get it
    #   Infected:   They have it and are contagious, but don't know it
    #   Symptomatic: They have it, and have symptoms, so they move around less
    #   Recovered:  They're over it, no longer contagious, and can't get it again
    #   Dead:  They died of the virus
    
    # Each person object needs to "know" (have stored) their region, and
    # where in their region (row, column) they are located
    def __init__(self, region, row, col):
        self.state = "susceptable"
        self.region = region
        self.my_row = row
        self.my_col = col
    
    # How many neighbors within a certain distance are infected or symptomatic?
    # Rather than pythagorian distance, I'm just doing an n x n square from
    # the grid.  So, if distance is 2, I'm counting how many people in the two
    # rows above, two rows below, two columns to the left, and two-columns to 
    # the right are contagious.    
    def count_infected_neighbors(self, distance):
        infected_neighbors = 0
        for r in range(self.my_row - distance, self.my_row + distance + 1):
            for c in range(self.my_col - distance, self.my_col + distance + 1):
                # Check if the neighbor I'm looking at is off the grid
                if r < 0 or c < 0 or r >= HEIGHT or c >= WIDTH:
                    continue
                # Check if the "neighbor" I'm looking at is actually me
                if r == self.my_row and c == self.my_col:
                    continue
                # Only check if that location in the grid is contagious if it's 
                # not "empty". (Because, if it's the string "empty", it won't 
                # have a .state variable to check, and trying would cause an 
                # error.)
                if self.region.grid[r][c] != "empty" \
                        and self.region.grid[r][c].state in ["infected", "symptomatic"]:
                    infected_neighbors += 1
        return infected_neighbors
        
        
    # This function gets called once per clock (day) for each person object
    def update(self):
        
        # Move around (How far? based on how healthy you feel.)
        if self.state == "susceptable" or self.state == "infected"  or \
                    self.state == "recovered":
            # Healthy-feeling people move 5 "steps"
            for i in range(5):
                self.move()
        elif self.state == "symptomatic":
            # Sick-feeling people mostly stay home -- move 1 step
            for i in range(1):
                self.move()
        
        # If you're sick, you're one day closer to getting better
        if self.state == "infected" or self.state == "symptomatic":
            self.days_left -= 1
            
            # If you're sick but have no days left to be sick, you're recovered.
            # Congratulations!
            if self.days_left <= 0:
                self.state = "recovered"

        # If you're infected, you have a chance of developing symptoms
        if self.state == "infected":
            if random.random() < SYMPTOM_CHANCE:
                self.state = "symptomatic"
                
        # If you're symptomatic, you have a chance of dying.
        if self.state == "symptomatic":
            if random.random() < (MORTALITY_RATE / INFECTION_LENGTH):
                self.state = "dead"
            
        # If you're susceptable, you have a chance of getting infected
        if self.state == "susceptable":
            # x is how likely you are to get it from someone at a given distance.
            # We're assuming that the chance of getting it is cut in half with 
            # each additional step away.  That is, if you have a 30% chance of 
            # getting it if you're next to an infected person, you'll have a 15% 
            # chance of getting it for each infected person 2 steps away
            # and a 7.5% chance for each infected person 3 steps away, etc...
            contagion_chance = CONTAGION_FACTOR
            # Calculating for up to 4 places out.  Kind of arbitrary how far to check.
            for distance in range(4):
                # count how many infected people are within a certain distance
                num_infected_people = self.count_infected_neighbors(distance)
                for i in range(num_infected_people):
                    if random.random() < contagion_chance:
                        self.state = "infected"
                        self.days_left = INFECTION_LENGTH
                        
                # Divide chance of contagion by 2 for each step away from the
                # nearest infected person
                contagion_chance = contagion_chance / 2
    # Social distance function to replace the random move by the person. Checks each spot next to each person
    # and returns the spot with the most empty neighbors.
    def socialDistance(self, empty_neighbors):
        max_neighbors = 0
        best_spots = []
        for neighbor in empty_neighbors:
            neighbor_count = 0
            for r in range(neighbor[0] - 1, neighbor[0] + 2):
                for c in range(neighbor[1] - 1, neighbor[1] + 2):
                    # If the neighbor I'm looking at is off the grid, skip to the next one
                    if r < 0 or c < 0 or r >= HEIGHT or c >= WIDTH:
                        continue
                    # If the "neighbor" I'm looking at is me, skip to the next one
                    if r == neighbor[0] and c == neighbor[1]:
                        continue
                
                    if self.region.grid[r][c] == "empty":
                        neighbor_count += 1
                        
            #Section of code to simulate social distance
            if neighbor_count > max_neighbors:
                max_neighbors = neighbor_count
                best_spots = [neighbor]
            elif neighbor_count == max_neighbors:
                best_spots.append(neighbor)
        return random.choice(best_spots) #Move to a random one of the most empty spots
    
    def move(self):
        # Make a list of all of the blank cells around me, then pick one to 
        # move to (if any)
        empty_neighbors = []
        for r in range(self.my_row - 1, self.my_row + 2):
            for c in range(self.my_col - 1, self.my_col + 2):
                # If the neighbor I'm looking at is off the grid, skip to the next one
                if r < 0 or c < 0 or r >= HEIGHT or c >= WIDTH:
                    continue
                # If the "neighbor" I'm looking at is me, skip to the next one
                if r == self.my_row and c == self.my_col:
                    continue
                
                if self.region.grid[r][c] == "empty":
                    empty_neighbors.append( (r,c) )
        
        if len(empty_neighbors) > 0:
            
            # Pick an empty neighboring cell at random
            new_row, new_col = self.socialDistance(empty_neighbors)
        
            # To "move" there, replace my current spot in the grid with 
            # "empty", and insert myself in the new, previously empty
            # spot, then update my own record of where I am.
            self.region.grid[self.my_row][self.my_col] = "empty"
            self.region.grid[new_row][new_col] = self
            self.my_row = new_row
            self.my_col = new_col
    
class Region:
    def __init__(self,runCanvas=True):
        # Variable to keep track of max symptomatics
        self.maxsymp = 0
        # Need a "master" window.  tkinter.Tk is a class that makes and 
        # controls an on-screen window for us.
        self.master = tkinter.Tk()
        if not runCanvas:
            self.master.withdraw()
        
        # Make a clock to keep track of how many turns (days) the
        # simulation has run
        self.clock = 0
        
        # Update the window title (at top of window) to show time
        self.master.title("Pandemic Day " + str(self.clock))

        # Create a Canvas object on the window.  The beauty of abstraction
        # is that you don't have to understand what this really means to 
        # be able to use it!  (A "canvas" is an object for putting other
        # visible objects on, so they show up on the screen.)
        self.canvas = tkinter.Canvas(self.master, width=WIDTH*CELL_PIXEL_SIZE, height=HEIGHT*CELL_PIXEL_SIZE)
        self.canvas.pack()

        # A list of people objects
        self.person_list = []
        
        # Create a grid (2-D list) of where the people are
        self.grid = []
        for row in range(HEIGHT):
            self.grid.append([])
            for col in range(WIDTH):
                if random.random() < POPULATION_DENSITY:
                    person = Person(self, row, col)
                    self.grid[row].append(person)
                    self.person_list.append(person)
                else:
                    self.grid[row].append("empty")
        
        # Start off with a handful a "patient zero"s.
        for x in range(STARTING_INFECTED):
            unlucky_person = random.choice(self.person_list)
            unlucky_person.state = "infected"
            unlucky_person.days_left = INFECTION_LENGTH
            
        # A parallel grid (2-D list) for storing "canvas rectangle" objects.
        # Again, you don't need to understand this part very well to use it.
        # It will paint each "cell" on the screen
        self.canvas_grid = []
        for row in range(HEIGHT):
            self.canvas_grid.append([])
            for col in range(WIDTH):
                rectangle = self.canvas.create_rectangle(col*CELL_PIXEL_SIZE,row*CELL_PIXEL_SIZE,\
                    (col+1)*CELL_PIXEL_SIZE,(row+1)*CELL_PIXEL_SIZE, fill="grey", outline="black")
                self.canvas_grid[row].append(rectangle)
        self.canvas.update()

    def update_grid(self):
        # Want to update the people in random order each time.
        # (Otherwise, if they're always getting updated starting in the
        # upper-left corner, they tend to all drift up and to the left over 
        # time.)
        random.shuffle(self.person_list)
        
        # Go through all of the person objects and call their update method.
        # This will check all of the things that can happen to a person
        # (Get better, develop symptoms, die, get infected, move around)
        for p in self.person_list:
            p.update()
    
    def update_canvas_grid(self):
        # This function goes through each entry in the grid (either 
        # the string "empty" or a Person object) and paints the associated
        # cell the correct color based on their status.
    
        for row in range(HEIGHT):
            for col in range(WIDTH):
                if self.grid[row][col] == "empty":
                    color = "black"
                else:
                    state = self.grid[row][col].state
                    if state == "infected":
                        color = "red"
                    elif state == "symptomatic":
                        color = "brown"
                    elif state == "recovered":
                        color = "green"
                    elif state == "dead":
                        color = "yellow"
                    else:
                        color = "white"
                # Now that I know what color, I can update the "rectangle" object
                # I created in the __init__ method to show up that color on 
                # the canvas.  You don't need to understand this part to use it.
                self.canvas.itemconfig(self.canvas_grid[row][col], \
                                  fill=color, outline=color)
        self.canvas.update()
        
    #Function used to plot individual plots on each simulation day
    def plotSIRDgraph(self,dct):
        x = self.clock
        y1 = dct["susceptable"]
        y2 = dct["infected"] + dct["symptomatic"]
        y3 = dct["recovered"]
        y4 = dct["dead"]             
        plt.scatter(x, y1, c="b", label="susceptable")
        plt.scatter(x, y2, c="r", label = "infectious")
        plt.scatter(x, y3, c="g", label = "recovered")
        plt.scatter(x, y4, c="y", label = "dead")
        if x == 1:
            plt.legend(loc="best")
            
    def update_loop(self, runCanvas=True):
        # update the clock
        self.clock += 1
        self.master.title("Pandemic Day " + str(self.clock))
        dict_count = {
            "infected": 0,
            "symptomatic": 0,
            "recovered": 0,
            "dead": 0,
            "susceptable": 0,
            }
        # Call the update_grid method to go through each person object and 
        # update their status, move around, etc...
        self.update_grid()
        
        # Setting Screen_update_frequency (at top) to 5 or 10 will make it run
        # (slightly) faster, for large simulations, but then you can't see
        # the daily changes
        if self.clock % SCREEN_UPDATE_FREQUENCY == 0:
            self.update_canvas_grid()
        
        
        #Code to count state of each person
        for row in range(HEIGHT):
            for col in range(WIDTH):
                if self.grid[row][col] != "empty":
                    dict_count[self.grid[row][col].state] += 1      
        
        #Call to plot graph on each day
        self.plotSIRDgraph(dict_count)
        
        # This function will ask the canvas to call the update_loop function
        # again in 10 milliseconds.  It's a GUI way of entering an infinite 
        # loop.  If you want to exit the program after a while, put this line 
        # in an if statement so that it only runs while the clock is less than
        # some amount, or while there are still infected people, etc...       
        # While loop that finishes once there are no infected
        if dict_count["infected"] or dict_count["symptomatic"] > 0:
            if dict_count["symptomatic"] > self.maxsymp:
                self.maxsymp = dict_count["symptomatic"]
            if runCanvas:
                self.canvas.after(10, self.update_loop())
            else:
                self.canvas.after(10, self.update_loop(False))
        elif not runCanvas:
            return
        else:
            print("The max number of symptomatics at one time was {} people".format(self.maxsymp))
            total_people = dict_count["recovered"] + dict_count["dead"] + dict_count["susceptable"]
            print("{:0.2f}% of people recovered from the pandemic and {:0.2f}% of people died from the pandemic".format(
            dict_count["recovered"]/total_people*100, dict_count["dead"]/total_people*100))
            self.master.withdraw()     
            
# studyParameter function that studies the cases for different values of POPULATION_DENSITY and SYMPTON_CHANCE. 
# Implemented runCanvas argument to Region constructor and some methods in order to run regions in background
def studyParameter():
    global POPULATION_DENSITY
    global SYMPTON_CHANCE
    global SCREEN_UPDATE_FREQUENCY
    #Speed up background simulations by increasing frequency
    SCREEN_UPDATE_FREQUENCY = 100
    maxSymp = 0
    minSymp = 10000
    maxI = 0
    maxK = 0
    minI = 0
    minK = 0
    index = 0
    
    #Loading statements
    print("Studying Parameters...")
    
    for i in range(1,10):
        #Checks each neighborhood
        for k in range(1,10):
            POPULATION_DENSITY = i/10
            SYMPTON_CHANCE = k/10
            n = Region(False)
            n.update_loop(False)
            print("The maximum symptomatics for population density {} and sympton chance {} is {}".format(i/10,k/10,n.maxsymp))
            if n.maxsymp > maxSymp:
                maxSymp = n.maxsymp
                maxI = i/10
                maxK = k/10
            if n.maxsymp < minSymp:
                minSymp = n.maxsymp
                minI = i/10
                minK = i/10
    #Print results
    print("The max amount of symptomatics are: {}".format(maxSymp))
    print("The Population Density for the max is {} and the Sympton Chance for the max is {}".format(maxI,maxK))
    print("The Population Density for the min is {} and the Sympton Chance for the min is {}".format(minI,minK))

#Function to construct the graph
def constructGraph():
    plt.title("SIRD graph")
    plt.xlabel("Days")
    plt.ylabel("No. people")
    plt.show()
    
# Create the region (call its init method), which will also create
# the list of Person objects.
            
n = Region()

# Call the update_loop function for the first time, which will then take care 
# of scheduling the next update call.

n.update_loop()

#Call to construct the graph after simulation

constructGraph()

#Call for parameter study

studyParameter()

# This line asks the Window to enter a "waiting loop", which will wait until 
# you close the application window, allowing on-screen updates to keep 
# occuring until you do.  Without this, the window would update the first
# time, and then exit the program.
tkinter.mainloop()

    
    
