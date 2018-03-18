from magicbot import AutonomousStateMachine, state, timed_state
from components.PathFinder import PathFinder
from components.OperateArm import OperateArm
from components.OperateGrabber import OperateGrabber
from components.DriveTrain import DriveTrain
from wpilib import DriverStation
from networktables import NetworkTables

table = NetworkTables.getTable('SmartDashboard')

class RightPathFinder(AutonomousStateMachine):

    MODE_NAME = "Right Pathfinder"
    DEFAULT = False

    pathFinder = PathFinder
    driveTrain = DriveTrain
    operateArm = OperateArm
    operateGrabber = OperateGrabber

    def __init__(self):
        self.gameData = None
        self.supportLeftAlliance =False
        self.supportMiddleAlliance = False
        self.supportRightAlliance = False

    @state(first=True)
    def startAutonomous(self):
        self.gameData = DriverStation.getInstance().getGameSpecificMessage()
        self.supportLeftAlliance = table.getBoolean('supportLeftAlliance', False)
        self.supportMiddleAlliance = table.getBoolean('supportMiddleAlliance', False)
        self.supportRightAlliance = table.getBoolean('supportRightAlliance', False)
        if self.gameData[0] == 'L':
            if self.supportLeftAlliance:
                self.next_state('supportSwitchAlliance1')
            else:
                self.next_state('crossAutoLine')
        else:
            self.next_state('openAndLowerArm')

    @state
    def supportSwitchAlliance1(self, initial_call):
        if initial_call:
            self.pathFinder.setTrajectory('RightSwitchLeft1', False)
        if not self.pathFinder.running:
            self.next_state('supportSwitchAlliance2')

    @state
    def supportSwitchAlliance2(self, initial_call):
        if initial_call:
            self.pathFinder.setTrajectory('RightSwitchLeft2', False)
        if not self.pathFinder.running:
            self.next_state('supportcloseGrabber')

    @timed_state(duration=0.5, next_state='supportLiftArm')
    def supportcloseGrabber(self):
        self.operateGrabber.setGrabber(True)

    @timed_state(duration=0.3, next_state='driveToSwitch')
    def supportLiftArm(self):
        self.operateArm.setArm(True)

    @timed_state(duration=0.3, next_state='supportLowerArm')
    def driveToSwitch(self):
        self.driveTrain.moveAuto(1, 0)

    @timed_state(duration=0.5, next_state='supportDropCube')
    def supportLowerArm(self):
        self.operateArm.setArm(False)

    @timed_state(duration=0.3)
    def supportDropCube(self):
        self.operateGrabber.setGrabber(False)

    @state
    def crossAutoLine(self, initial_call):
        if initial_call:
            self.pathFinder.setTrajectory('RightGoForward', False)

    @timed_state(duration=0.8, next_state='closeGrabber')
    def openAndLowerArm(self):
        self.operateGrabber.setGrabber(False)
        self.operateArm.setArm(False)

    @timed_state(duration=0.5, next_state='liftArm')
    def closeGrabber(self):
        self.operateGrabber.setGrabber(True)

    @timed_state(duration=0.3, next_state='goToSwitch')
    def liftArm(self):
        self.operateArm.setArm(True)

    @state
    def goToSwitch(self, initial_call):
        if initial_call:
            self.pathFinder.setTrajectory('RightSwitchRight', False)
        if not self.pathFinder.running:
            self.next_state('lowerArmToSwitch')

    @timed_state(duration=0.3, next_state='dropCube')
    def lowerArmToSwitch(self):
        self.operateArm.setArm(False)

    @timed_state(duration=0.3, next_state='liftArmOutSwitch')
    def dropCube(self):
        self.operateGrabber.setGrabber(False)

    @timed_state(duration=0.2, next_state='readyForScale')
    def liftArmOutSwitch(self):
        self.operateArm.setArm(True)

    @state
    def readyForScale(self, initial_call):
        if initial_call:
            self.pathFinder.setTrajectory('RightSwitchBack', True)
        if not self.pathFinder.running:
            self.next_state('takeCubeRightSwitch')

    @state
    def takeCubeRightSwitch(self, initial_call):
        if initial_call:
            self.pathFinder.setTrajectory('TakeCubeRightSwitch', False)
