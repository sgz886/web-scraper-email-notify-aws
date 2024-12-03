REM Create a deployment directory
mkdir deployment
cd deployment

REM Install dependencies
pip install -r ..\requirements-prod.txt -t .

REM Create src directory structure
@REM mkdir src
mkdir data
mkdir notification
mkdir scraper
mkdir service
mkdir util

REM Copy your project files
copy ..\src\*.py .
copy ..\src\data\*.py data\
copy ..\src\notification\*.py notification\
copy ..\src\scraper\*.py scraper\
copy ..\src\service\*.py service\
copy ..\src\util\*.py util\
copy ..\.env.example .

REM Create zip file using Windows tar
tar --exclude "*.zip" -acf ..\crawler_for_lambda.zip *

cd ..
pause