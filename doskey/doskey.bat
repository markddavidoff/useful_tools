@echo off
DOSKEY open_sidebar=(adb shell am startservice --user 0 -n com.android.systemui/.SystemUIService)
DOSKEY ip=ipconfig $b grep IPv4
DOSKEY get=git pull origin master
DOSKEY branch=git checkout -b $1
DOSKEY branchp=git checkout -b POSMON-$1
DOSKEY push = C:\doskey\push_current_branch.bat
DOSKEY pull = C:\doskey\pull_current_branch.bat
DOSKEY switchl=(git checkout live)
DOSKEY live=(git checkout live)
DOSKEY switch=(git checkout $1)
DOSKEY switchp=(git checkout POSMON-$1)
DOSKEY shortcuts= (type C:\doskey\shortcuts.txt)
DOSKEY cuts= (type C:\doskey\shortcuts.txt)
DOSKEY cut= (type C:\doskey\shortcuts.txt)
@echo on
