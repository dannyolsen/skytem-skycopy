# skytem-skycopy

IN ORDER TO RUN SKYCOPY DO FOLLOWING STEPS

1. use microsoft store to install the newest python version avaliable.

2. launch a terminal by clicking windows key and write cmd and hit enter

3. verify python version with "python -V"

4. navigate to the folder containing requirements.txt. ("cd c:\path\to\txt")

5. type "pip install -r requirements.txt". This will install neccesary modules for linebiblebuddy to run.

5.1 your will most likely get a path error - add the paths by
5.2 OPTION1
pressing windows key -> "edit environmental variables for your account" -> "new" and add the paths specified 
when running pip install.
5.2 OPTION2
Use CLI and fill this : setx NEW_VAR "C:\NewPath"


6. run "pip install -r requirements.txt" in terminal window again - this time you should have no errors.

if python has been installed correctly on your windows machine, you should now be able to double click the .py
to execute it.