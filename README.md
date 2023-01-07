# 🔍️ Pipespector

Pipespector is a pretty shitty tool for debugging and tracing pipes. 

With pipespector it is possible to stepping through each item passing the pipe, and at any time change the values output values. 
By using the 'exec' command to execute any python script to interact and change values before passing it to stdout.

```console
(pipespector)> help

Documented commands (type help <topic>):
========================================
break  close  curr  exec  exit  help  info  open  prev  seq  step

```

## Install
Via pip
```console
python3 -m venv venv
source venv/bin/activate
python -m pip install git+https://github.com/mumubebe/pipespector.git

# Test
seq 5 | pipespector > res.txt

```
Clone:
```console
git clone https://github.com/mumubebe/pipespector.git
cd pipespector

# Test
seq 5 | python -m pipespector > res.txt
```

[![asciicast](https://asciinema.org/a/S0Kqov6Cqt5sMzm75WB4qmCEX.svg)](https://asciinema.org/a/S0Kqov6Cqt5sMzm75WB4qmCEX)
