# Kalman Filter Study
# by: Brian Huffman

#Libraries used, Numpy for Linear Algebra of Recursive Kalman Algorithm
# and Matplotlib to produce a graphical representation of the results
import numpy as np
import matplotlib.pyplot as myplot
from matplotlib.pyplot import Slider
#<Notes>#
# I've kept the notation the sames as the Kalman Filter Wikipedia Page F = State Transition, H = Observation Model,
# Q = Covariance of process noise, R = Covariance of the observation noise,
# n = control vector, B = input-control model (both n and B and not used since there is to control input)

class KalmanFilter(object):
    #The Kalman Constructor, I'm initializing all necessary variables as empty "None" by default
    def __init__(self, F = None, B = None, H = None, Q = None, R = None, x0 = None, P = None):
        #Error handeling if State Transition or Observation Models remain empty
        if(F is None or H is None):
            raise ValueError("Set proper system dynamics. {F} & {H} Required !")
        #Matrix Dimensions n and m will be defined automatically by the F and H matrices row size
        self.n = F.shape[1]
        self.m = H.shape[1]

        self.F = F
        self.H = H
        self.B = 0 if B is None else B
        self.Q = np.eye(self.n) if Q is None else Q
        self.R = np.eye(self.n) if R is None else R
        self.P = np.eye(self.n) if P is None else P
        #Set initial condition vector to zero if not defined
        self.x = np.zeros((self.n, 1)) if x0 is None else x0
    #Defining the prediction phase of the Kalman filter
    def predict(self, u = 0):
        #Predicted state estimate {x}k-1
        self.x = np.dot(self.F, self.x) + np.dot(self.B, u)
        #Predicted estimate covariance {P}k-1
        self.P = np.dot(np.dot(self.F, self.P), self.F.T) + self.Q
        return self.x
    #Defining the update phase of the Kalman filter
    def update(self, z):
        #Calculate the Innovation {y} or (difference in observed value {z} and the calculated prediction {H} dot {x})
        y = z - np.dot(self.H, self.x)
        #Calculate the Innovation Covariance {S}
        S = self.R + np.dot(self.H, np.dot(self.P, self.H.T))
        #Calculate Kalman gain {K}
        K = np.dot(np.dot(self.P, self.H.T), np.linalg.inv(S))
        #Calculate Update state estimate {x}k
        self.x = self.x + np.dot(K, y)
        #Define Identity Matrix from dimension n
        I = np.eye(self.n)
        #Calculate Updated estimate covariance {P}k (estimated accuracy of the state estimate)
        self.P = np.dot(np.dot(I - np.dot(K, self.H), self.P),
        	(I - np.dot(K, self.H)).T) + np.dot(np.dot(K, self.R), K.T)

def KalmanExample():
    #Assuming a measurement sample rate of one millisecond (1/60 seconds)
    dt = 1.0/60
    #Defining the matrices for the filter
    #Simple Dynamics state model {F} for a ball free-falling to the ground (y = yprev + vprev*dt)
    # where y is height position,v is velocity, dt is incremental change in time
    F = np.array([[1, dt, 0], [0, 1, dt], [0, 0, 1]])
    H = np.array([1, 0, 0]).reshape(1, 3)
    #Q is normally calculated by a series of standard deviations of known sources of process noise
    #instead I've chosen a small value of 0.05 as we don't expect any external noise in the system
    Q = np.array([[0.05, 0.05, 0.0], [0.05, 0.05, 0.0], [0.0, 0.0, 0.0]])
    #R is a grade of uncertainty in the measurements received larger numbers reflect an inaccurate sensor
    R = np.array([0.5]).reshape(1, 1)
    #x0 is an initial condition for the filter to reach an accurate prediction faster, we could use a vector of zeroes
    #here the filter will still eventually reach accurate predictions. However we know constant acceleration
    #due to gravity (9.81 meters/sec^2) then we can assume a starting height of 2000 meters and initially not moving
    #(initial velocity = 0 meters/sec)
    x0 = np.array([2000, 0, 9.81]).reshape(3, 1)
    # Passing the defined matrices into our constructor for our Kalman model object
    kf = KalmanFilter(F=F, H=H, Q=Q, R=R, x0=x0)
    # Initialize an empty array for our calculated values
    predictions = []
    # Setup for Graphical Plot of Measurements vs. Predictions
    fig, axis = myplot.subplots(num='Kalman Plot')
    fig.subplots_adjust(left = 0.15, bottom = 0.2)
    # Define Graph plot space 100 evenly spaced values between 0 and 20 (20 seconds total)
    time = np.linspace(0, 20, 100)
    # Simulated measurements that would normally be from an analog signal generated by a sensor
    # that would be tracking the ball ie. laser, ultrasonic sensor, computer vision etc.
    # A simple inverse parabola (-9.81t^2 + 200) with added random noise at each input simulated by a normal distribution
    # the amount of noise can be adjusted by changing the scale of the normal distribution
    initNoise = 50
    measurements = -1*(9.81 * time ** 2 - 2000) + np.random.normal(0, initNoise, 100)
    # Loop to calculate predicted values
    for y in measurements:
        predictions.append(np.dot(H, kf.predict())[0])
        kf.update(y)
    # Plot initial data on the graph
    mLine, = axis.plot(range(len(measurements)), measurements, label='Measurements')
    pLine, = axis.plot(range(len(predictions)), predictions, label='Predictions')
    # Create an interactive slider to control the "Noise" value
    noiseAxis = fig.add_axes([0.2, 0.05, 0.65, 0.03])
    noiseSlider = Slider(noiseAxis, 'Noise', 0, 200, initNoise)
    # Note actual units are arbitrary here
    axis.set_xlabel("Time in milliseconds")
    axis.set_ylabel("Height in Meters")
    #Defining event to recalculate and update plot based on current "Noise" value when changed
    def sliderEvent(val):
        #Reset initial conditions
        kf.x = x0
        newPredictions = []
        newNoise = noiseSlider.val
        newMeasurements = -1*(9.81 * time ** 2 - 2000) + np.random.normal(0, newNoise, 100)
        mLine.set_ydata(newMeasurements)
        for y in newMeasurements:
            newPredictions.append(np.dot(H, kf.predict())[0])
            kf.update(y)
        pLine.set_ydata(newPredictions)
    noiseSlider.on_changed(sliderEvent)
    #Display Legend and plot
    axis.legend()
    myplot.show()

if __name__ == '__main__':
    KalmanExample()