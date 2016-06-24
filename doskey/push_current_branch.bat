@echo off
for /f "tokens=*" %%x in ('git branch ^| sed -n "/\* /s///p"') do set "var=%%x"
echo pushing to origin / %var%
::for /f "tokens=*" %%x in ('%var%') do (git push origin %%x)
for /f "tokens=*" %%x in ('git branch ^| sed -n "/\* /s///p"') do (git push origin %%x )
@echo on