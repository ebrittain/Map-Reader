import pytest

from Map_Reader.MouseController import MouseController

@pytest.fixture
def mouseController():
    mouseController = MouseController()
    return mouseController

def test_1(mouseController):
    orig = mouseController.getSpeed()
    mouseController.setSpeed(20)

    assert mouseController.getSpeed() == 20

    mouseController.setSpeed(orig)

def test_2(mouseController):
    with pytest.raises(ValueError):
        mouseController.setSpeed(-1)

def test_3(mouseController):
    orig = mouseController.getAcceleration()
    mouseController.setAcceleration(False)

    assert mouseController.getAcceleration() == False

    mouseController.setAcceleration(orig)

def test_4(mouseController):
    orig = mouseController.getAcceleration()
    mouseController.setAcceleration(True)

    assert mouseController.getAcceleration() == True

    mouseController.setAcceleration(orig)