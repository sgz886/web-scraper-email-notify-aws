REM Create a deployment directory
mkdir deployment
cd deployment

REM Install dependencies
pip install -r ..\requirements.txt -t .

REM Copy your project files
copy ..\config.py .
copy ..\db_handler.py .
copy ..\email_sender.py .
copy ..\main.py .
copy ..\scraper.py .
copy ..\services.py .
copy ..\utils.py .
copy ..\.env.example .

REM Create zip file using Windows tar
tar -acf lambda_function.zip *

cd ..