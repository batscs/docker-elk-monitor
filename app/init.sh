#!/bin/bash

#echo "* * * * * python3.11 /app/app.py -v $elastic_domain $elastic_api_key $elastic_index_name > /app/data/app.log" > /app/app.cron
#crontab /app/app.cron
#cron -f

# Set the command to be executed periodically
COMMAND="python3.11 /app/app.py $elastic_domain $elastic_api_key $elastic_index_name"

# Set the time interval between each execution (in seconds)
if [ -n "$interval" ]; then
    INTERVAL=$interval
else
    INTERVAL=10
fi

echo "Interval=$INTERVAL"

# Function to execute the command in a new shell
execute_command() {
    bash -c "$COMMAND" &
}

# Infinite loop to periodically execute the command
while true; do
    execute_command
    sleep $INTERVAL
done
