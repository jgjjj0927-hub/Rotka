@echo off
title Compile Builder
echo Installing/Updating dependencies...
pip install -r requirements.txt

echo.
echo Compiling builder.py to builder.exe... This may take a while.
python -m nuitka --onefile --windows-disable-console --assume-yes-for-downloads --remove-output --enable-plugin=tk-inter --include-package=customtkinter --windows-company-name="Microsoft Corporation" --windows-product-name="Builder" --output-filename=builder.exe builder.py

echo.
echo Done! Check for builder.exe
pause
