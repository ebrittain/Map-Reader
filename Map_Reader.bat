FOR /F "tokens=* USEBACKQ" %%F IN (`where pythonw.exe`) DO (
SET pythonw_path=%%F
)
FOR /F "tokens=* USEBACKQ" %%F IN (`where python.exe`) DO (
SET python_path=%%F
)
"%python_path%" -m pip install pyqt5 --user
"%python_path%" -m pip install geopy --user
"%python_path%" -m pip install pandas --user
"%python_path%" -m pip install PyQtWebEngine --user
start "Starting Map Reader" "%pythonw_path%" "%~dp0Source\Starter.py"