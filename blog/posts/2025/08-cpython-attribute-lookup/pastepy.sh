#!/bin/bash

xclip -selection clipboard $1

{
  sleep 0.1
  xdotool key --window "$win_id" ctrl+shift+v
} &

python -q -E
