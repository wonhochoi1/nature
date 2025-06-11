@echo off
echo Setting up nature-env conda environment...

REM Check if conda is available
where conda >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo conda could not be found. Please install Anaconda or Miniconda first.
    exit /b 1
)

REM Create the conda environment
echo Creating conda environment 'nature-env'...
call conda create -y -n nature-env python=3.9

REM Activate the environment
echo Activating environment...
call conda activate nature-env

REM Install pip packages from requirements.txt
echo Installing dependencies...
pip install -r requirements.txt

REM Print success message and instructions
echo.
echo Nature environment setup complete!
echo.
echo To activate the environment, run:
echo conda activate nature-env
echo.
echo To run the web sandbox, run:
echo cd sandbox
echo python app.py
echo.
echo Don't forget to set your OpenAI API key:
echo set OPENAI_API_KEY=your_api_key_here
echo. 