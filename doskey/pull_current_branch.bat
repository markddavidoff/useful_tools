@echo off
for /f "tokens=*" %%x in ('git branch ^| sed -n "/\* /s///p"') do set "var=%%x"
echo pulling from origin / %var%
::for /f "tokens=*" %%x in ('%var%') do (git pull origin %%x)
for /f "tokens=*" %%x in ('git branch ^| sed -n "/\* /s///p"') do (git pull origin %%x )
@echo on