#!/usr/bin/env python3

import wpilib
from wpilib import Spark, Joystick, DoubleSolenoid, Compressor, SpeedControllerGroup, drive, CameraServer, ADXRS450_Gyro, Encoder
from robotpy_ext.common_drivers import navx
from magicbot import MagicRobot, tunable
from components.DriveTrain import DriveTrain
from components.OperateGrabber import OperateGrabber
from components.PathFinder import PathFinder
from components.OperateArm import OperateArm
import math, RobotMap
from networktables import NetworkTables

# Gamepad Axis
leftStick_X = 0
leftStick_Y = 1
shoulderAxisLeft = 2
shoulderAxisRight = 3
rightStick_X = 4
rightStick_Y = 5
dpadAxis = 6

# Gamepad Buttons
BUTTON_A = 1
BUTTON_B = 2
BUTTON_X = 3
BUTTON_Y = 4
BUTTON_L_SHOULDER = 5
BUTTON_R_SHOULDER = 6
BUTTON_BACK = 7
BUTTON_START = 8
BUTTON_LEFTSTICK = 9
BUTTON_RIGHTSTICK = 10

if wpilib.RobotBase.isSimulation():
    rightStick_Y = 3

class MyRobot(MagicRobot):

    pathFinder = PathFinder
    driveTrain = DriveTrain
    operateGrabber = OperateGrabber
    operateArm = OperateArm

    dothing = tunable(False)
    doangle = tunable(0)
    gyro_angle = tunable(0)


    def createObjects(self):
        self.table = NetworkTables.getTable('SmartDashboard')
        self.table.putBoolean('supportLeftAlliance', False)
        self.table.putBoolean('supportMiddleAlliance', False)
        self.table.putBoolean('supportRightAlliance', False)

        self.leftFront = Spark(2)
        self.leftBack = Spark(3)
        self.rightFront = Spark(0)
        self.rightBack = Spark(1)
        self.rightFront.setInverted(True)
        self.rightBack.setInverted(True)
        self.leftFront.setInverted(True)
        self.leftBack.setInverted(True)

        self.m_left = SpeedControllerGroup(self.leftFront, self.leftBack)
        self.m_right = SpeedControllerGroup(self.rightFront, self.rightBack)
        self.myDrive = drive.DifferentialDrive(self.m_left, self.m_right)
        self.myDrive.setSafetyEnabled(False)

        self.compressor = Compressor()
        self.grabber = DoubleSolenoid(0, 1)
        self.armSolenoid = DoubleSolenoid(2, 3)

        self.gamepad = Joystick(0)

        self.gyro = navx.AHRS.create_spi()

        self.leftEncoder = Encoder(0, 1, False, Encoder.EncodingType.k4X)
        self.rightEncoder = Encoder(2, 3, False, Encoder.EncodingType.k4X)
        self.leftEncoder.setDistancePerPulse((1/360.0)*RobotMap.WHEEL_DIAMETER*math.pi)
        self.rightEncoder.setDistancePerPulse((1/360.0)*RobotMap.WHEEL_DIAMETER*math.pi)

        CameraServer.launch()

        self.boost = False

    def autonomous(self):
        self.compressor.start()
        super().autonomous()

    def teleopInit(self):
        self.compressor.start()

    def teleopPeriodic(self):
        if self.gamepad.getRawButtonPressed(BUTTON_B):
            self.boost = not self.boost

        if not self.boost:
            self.driveTrain.moveTank(self.gamepad.getRawAxis(leftStick_Y) * (7.5/10), self.gamepad.getRawAxis(rightStick_Y)*7.5/10)
        else:
            self.driveTrain.moveTank(self.gamepad.getRawAxis(leftStick_Y), self.gamepad.getRawAxis(rightStick_Y))

        if self.gamepad.getRawAxis(shoulderAxisLeft):
            self.operateGrabber.setGrabber('close')
        elif self.gamepad.getRawButton(BUTTON_L_SHOULDER):
            self.operateGrabber.setGrabber('open')

        if self.gamepad.getRawButton(BUTTON_R_SHOULDER):
            self.operateArm.setArm('up')
        elif self.gamepad.getRawAxis(shoulderAxisRight):
            self.operateArm.setArm('down')

        if self.dothing:
            turn, _, _ = self.pathFinder.gotoAngle(self.doangle, self.pathFinder.gp)
            self.driveTrain.moveAuto(0, turn)
        else:
            self.pathFinder.angle_error = 0

        self.gyro_angle = -self.gyro.getAngle()


if __name__ == '__main__':
    wpilib.run(MyRobot)
