@echo off
echo Starting Market Nutrition API...

REM Create and activate virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt

REM Set environment variables
set PORT=5000
set DATABASE_URL=postgresql://postgres:your_password@localhost:5432/market_nutrition

REM Run the application
echo Starting the application...
python main.py 