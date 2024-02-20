@echo off
REM 生成一个日志路径
set LOG_FILE="C:\Users\krdw\CMD\.log\%date:~0,4%\%date:~5,2%\%~nn0.log"

REM 创建年份和月份的目录
if not exist "C:\Users\krdw\CMD\.log\%date:~0,4%\%date:~5,2%" (
    md "C:\Users\krdw\CMD\.log\%date:~0,4%\%date:~5,2%"
)

REM 根据 LOG_FILE 创建日志文件
if not exist %LOG_FILE% (
    copy nul %LOG_FILE%
)

REM 使用 rclone 挂载到 E:
rclone mount onedav: E: ^
--poll-interval 0 ^
--cache-dir C:\Users\krdw\CMD\.cache\onedav ^
--vfs-cache-mode full ^
--vfs-cache-max-age 1h0m0s ^
--log-file %LOG_FILE% ^
--log-level INFO ^
--rc