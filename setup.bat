powershell -Command "(New-Object Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.6.3/python-3.6.3.exe', 'python.exe')"
START python.exe
@echo off
echo.
echo --------------------------------------------------------------
echo ----Python Installation----
echo.
echo The python installer window should be up on your screen
echo Run Custom Installation
echo Check ALL on Optional Features
echo Click Next
echo Advanced Options: Check Associate files with Python, Add Python to Environment Variables
echo Make sure path is C:/Users/{Username}/AppData/Local/Programs/Python/Python36-32
echo Click Install
echo.
echo Once python is successfully installed, press enter to continue...
echo.
pause

pip.exe install selenium
echo.
echo if an error occurred:
echo Open up CMD.exe (Command Prompt) : Can be done by hitting start and typing cmd then press enter
echo Type pip.exe install selenium (has to be done off the vpn)
echo Wait for installation process
echo Close CMD
pause

powershell -Command "(New-Object Net.WebClient).DownloadFile('https://chromedriver.storage.googleapis.com/2.33/chromedriver_win32.zip', 'chromedriver_win32.zip')"
echo.
echo This should add the file (chromedriver_win32.zip) to the location the setup file is located.
echo Unzip this file, and place the folder (chromedriver_win32) in this path: C:/Users/{Username}/AppData/Local/Programs/Python/Python36-32/selenium/webdriver/
echo Last this to do is to edit the Config file with your information.
echo To do this right click the file and edit with Notepad++ or notepad or the IDLE editor that was installed with Python
pause
