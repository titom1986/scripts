#!/bin/sh

# CONFIGURATION
DIR="/home/titom/torrents"
DISCARD="OPEN,ISDIR"
EVENTS="open"
FIFO="/tmp/inotify2.fifo"
LAST_FILE=""

# FUNCTIONS
on_exit() {
    python /home/titom/scripts/push.py "Script Torrents Shutdown !" "Need Restart ?"
    kill $INOTIFY_PID
    rm $FIFO
    exit
}

on_event() {
    local file="$1"
    python /home/titom/scripts/push.py "Torrent" "$(date) : $file"
}

# MAIN
if [ ! -e "$FIFO" ]
then
    mkfifo "$FIFO"
fi

inotifywait -m -r -e "$EVENTS" --timefmt '%d/%m/%Y %H:%M:%S' --format '%T %e %w %f' "$DIR" > "$FIFO" &
inotify_pid=$!

trap "on_exit" 2 3 15

#ifs=''
while read date time event dir file
do
    ret=$(echo \"${event}\" | grep \"${DISCARD}\")
    if [ -z "$ret" ] && [ "$last_file" != "$dir$file" ];
    then
        last_file=$dir$file
        on_event "$last_file" &
    fi
done < "$FIFO"

on_exit
