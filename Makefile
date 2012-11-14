
all : protocol/lobby.py protocol/game.py


protocol/lobby.py : protocol/lobby.wld
	./waldo/bin/wcompile.py -f protocol/lobby.wld -e protocol/lobby.py

protocol/game.py : protocol/game.wld
	./waldo/bin/wcompile.py -f protocol/game.wld -e protocol/game.py
