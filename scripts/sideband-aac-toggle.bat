@echo off

for /f "delims=" %%A in ('git config --global --get sideband.allowControlCharacters 2^>nul') do set "enabled=%%A"

if "%enabled%"=="true" (
    git config --global --unset sideband.allowControlCharacters
    if errorlevel 1 (
        echo Failed to disable sideband.allowControlCharacters.
    ) else (
        echo sideband.allowControlCharacters has been disabled.
    )
) else (
    git config --global sideband.allowControlCharacters true
    if errorlevel 1 (
        echo Failed to enable sideband.allowControlCharacters.
    ) else (
        echo sideband.allowControlCharacters has been enabled.
    )
)
