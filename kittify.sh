#!/bin/bash

infocmp -a xterm-kitty | ssh $1 tic -x -o .terminfo /dev/stdin
