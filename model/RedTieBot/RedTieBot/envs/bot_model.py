import numpy as np
import gym.spaces.box as b
#we need numpy and Gym present here.

class BotModel(gym.env):
    def __init__(self):
        self.w=1
        #width of robot
        self.t=0.5
        #round to the nearest .5 seconds when dealing with time
        self.x0=0
        #robot's starting x-position
        self.y0=0
        #robot's starting y-position
        self.x=self.x0
        #robot's current x-position.
        self.y=self.y0
        #robot's current y-position.
        self.facing=0
        #the direction that the robot is facing in radians, in standard position
        self.l_speed=0
        #left wheel speed
        self.r_speed=0
        #right wheel speed
        self.is_over=False
        #the game is not over yet.
        self.minShootDist = 5 #This is the MINIMUM Distance from away the target
        self.maxShootDist = 10 #This is the MAXIMUM Distance away from the target
        self.reward = 0#the points rewarded to the robot during the simulation


        self.observation_space = b.Box(0, 1.0, shape=(int(821/10), int(1598/10),36))
        #The structure of the data that will be returned by the environment. It's the dimensions of the field (without obstacles at the moment)
        #The box is technically a 1x1x1 cube.
        self.action_space = b.Box(0, 1.0, shape=(int(-128/2), int(127/2)))
        #The range of speeds that the wheel can have.

    def step(self, action):
        self.l_speed += action[0]
        #in the list "action", the first value is the left wheel speed.
        self.r_speed += action[1]
        #in the list "action", the second value is the right wheel speed.
        if self.l_speed > 127:
            self.l_speed = 127
        elif self.l_speed < -128:
            self.l_speed = -128
        if self.r_speed > 127:
            self.r_speed = 127
        elif self.r_speed < -128:
            self.r_speed = -128
        #above lines limit the speed of the wheels to 128 cm/s backwards or 127 cm/s forward.

        if self.l_speed == self.r_speed:
          distance = l_speed * t
          #calculate the distance traveled.
          self.x = self.x + (distance * np.sin(facing))
          self.y = self.y + (distance * np.cos(facing))
          #update my x and y positions, now that I know how far I've traveled.

        else:
            radius = (self.w/2)*(self.l_speed+self.r_speed)/(self.l_speed-self.r_speed)
            #this is the physical radius of the robot.
            z = (self.l_speed-self.r_speed)*self.t/self.w
            self.x = self.x+(radius*np.sin(facing))-(radius*np.sin(facing-z))
            self.y = self.y-(radius*np.cos(facing))+(radius*np.cos(facing-z))
            self.facing -= z
            #see desmos link on slack for explanation of above three lines. It's essentially direction calculations
        
            while z<0:
                z+=2*np.pi
                
            while z>2*np.pi:
                z-=2*np.pi

            while self.facing<0:
                self.facing+=2*np.pi

            while self.facing>2*np.pi:
                self.facing-=2*np.pi
            #making sure that the z-angle measurement doesn't go below 0 or above 2pi
                
        ob = dict(x=self.x, y=self.y, facing=self.facing, l_speed=self.l_speed, r_speed=self.r_speed)
        #when it's training, it takes the data from the environment and says "I have this to use now."
        reward = self.checkreward()
        #returns the amount of reward achieved.
        episode_over = self.is_over()
        #checks to see if it's over.
        info = dict(3)
        #openai needs that line to be happy. means nothing
        return ob, reward, episode_over, info
        #spit back all that data.
        
    def reset(self):
        self.x=self.x0
        self.y=self.y0
        #reset my position. Where I am now is now (0,0) from my perspective.
        self.facing=np.pi/2
        #I am facing forward.
        self.l_speed=0
        #stop the left wheel
        self.r_speed=0
        #stop the right wheel
        return dict(x=self.x, y=self.y, facing=self.facing, l_speed=self.l_speed, r_speed=self.r_speed)
        #spit back all the data about what I'm doing right now.

    def checkreward(self):
        if self.l_speed == 0.0 and self.r_speed == 0.0 and ((58 - self.x) ** 2 - (159 - self.y) ** 2 >= self.minShootDist ** 2 and (58 - self.x) ** 2 - (159 - self.y) ** 2 <= self.maxShootDist ** 2 and self.y <= self.x + 101 and y <= -self.x + 217):
        #If I'm in position in front of the goal and facing the right way,
            if np.round(self.facing,1) == np.round(np.tan((1598-self.y)/(638-self.x)),3):
            #If I'm in position in front of the goal and facing the right way (but with extra parameters)
                self.is_over = True
                #end the game!
                self.reward += 100
                #i get a lot of points
                
        if self.y <= -0.364 * self.x + 6.255 or self.y <= 0.364 * self.x - 23.626 or self.y >= 0.364 * self.x = 153.545 or self.y >= -0.364 * self.x + 183.426:
            self.reward -= 100
            #robot ran into the triangles in the corners and loses points

        if self.y > 87.526 and self.y < 95.146 and self.x > 0 and self.x < 14.1:
            self.reward -= 100
            #robot ran into the north spinner and loses points

        if self.y > 64.68 and self.y < 72.3 and self.x > 68 and self.x < 82.1:
            self.reward -= 100
            #robot ran into the south spinner and loses points
            
        if self.x > 82.1 or self.y > 159.8 or self.x < 0 or self.y<0:
            self.is_over = True
            self.reward -= 100
            #robot went outside the barrier

        if (self.y-105.979)>=((106.403-105.979)/(50.871-49.91))*(self.x-49.91) and (self.y-106.936)<=((107.36-106.936)/(50.439-49.478))*(self.x-49.478):
          if (self.y-105.979)>=((106.936-105.979)/(49.478-49.91))*(self.x-49.91) and (self.y-106.403)<=((107.36-106.403)/(50.439-50.871))*(self.x-50.871):
            self.reward -= 100
            #robot ran into the top right pillar of the rendezvous point
        if (self.y-52.469)>=((52.883-52.469)/(32.604-31.666))*(self.x-31.666) and (self.y-53.403)<=((53.817-53.403)/(32.182-31.244))*(self.x-31.244):
          if (self.y-52.469)>=((53.403-52.469)/(31.244-31.666))*(self.x-31.666) and (self.y-52.883)<=((53.817-52.883)/(32.182-32.604))*(self.x-32.604):
            self.reward -= 100
            #robot ran into the bottom left pillar of the rendezvous point
        if (self.y-90.379)>=((90.799-90.379)/(15.42-14.529))*(self.x-14.529) and (self.y-91.336)<=((91.76-91.336)/(15.056-14.097))*(self.x-14.097):
          if (self.y-90.379)>=((91.336-90.379)/(14.097-14.529))*(self.x-14.529) and (self.y-90.799)<=((91.76-90.799)/(15.056-15.42))*(self.x-15.42):
            self.reward -= 100
            #robot ran into the top left pillar of the rendezvous point
        if (self.y-68.07)>=((68.494-68.07)/(68-67.039))*(self.x-67.039) and (self.y-69.027)<=((69.451-69.027)/(67.568-66.607))*(self.x-66.607):
           if (self.y-68.07)>=((69.027-68.07)/(66.607-67.039))*(self.x-67.039) and (self.y-68.494)<=((69.451-68.494)/(67.568-68))*(self.x-68)
             self.reward -= 100
else:
  print("Out")

    def render(self, mode='human'):
        #graphics; nothing yet
        return

    def close(self):
        #closing the graphics; nothing yet
        return
