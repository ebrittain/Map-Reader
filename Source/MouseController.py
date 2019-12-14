import ctypes as ct
import ctypes.wintypes as cw

#https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-systemparametersinfoa            

class MouseController():
    def setSpeed(self, speed):
        #   1 - slow
        #   10 - standard
        #   20 - fast

        if speed not in range(1, 21):
            raise ValueError
        
        set_mouse_speed = 113   # 0x0071 for SPI_SETMOUSESPEED
        ct.windll.user32.SystemParametersInfoA(set_mouse_speed, 0, speed, 0)

    def getSpeed(self):
        get_mouse_speed = 112   # 0x0070 for SPI_GETMOUSESPEED
        speed = ct.c_int()
        ct.windll.user32.SystemParametersInfoA(get_mouse_speed, 0, ct.byref(speed), 0)

        return speed.value 

    def setAcceleration(self, b):
        arr = [0, 0, int(b)]
        mouse_params = (ct.c_int * len(arr))(*arr)
        set_mouse = 4   # 0x0004 for SPI_SETMOUSE
        ct.windll.user32.SystemParametersInfoA(set_mouse, 0, mouse_params, 0)

    def getAcceleration(self):
        mouse_params = (ct.c_int * 3)()
        get_mouse = 3   # 0x0003 for SPI_GETMOUSE
        ct.windll.user32.SystemParametersInfoA(get_mouse, 0, mouse_params, 0)
        
        return bool(mouse_params[2])