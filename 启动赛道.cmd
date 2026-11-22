@echo off
setlocal
set "engine=%GODOT_EXE%"
if not defined engine set "engine=D:\godot\Godot_v4.7.2-stable_win64.exe\Godot_v4.7.2-stable_win64.exe"
if not exist "%engine%" (
    for %%G in (godot.exe) do set "engine=%%~$PATH:G"
)
if not exist "%engine%" (
    echo Open project.godot in Godot 4.7, or set GODOT_EXE to the editor executable.
    pause
    exit /b 1
)
pushd "%~dp0"
if not exist ".godot\imported\Kestrel_R9.glb-*.scn" (
    start "" /wait "%engine%" --headless --editor --import --path .
    if errorlevel 1 (
        echo Godot could not import the project.
        pause
        popd
        exit /b 1
    )
)
start "" "%engine%" --path .
popd
