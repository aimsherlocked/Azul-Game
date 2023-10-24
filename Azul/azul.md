# Azul : A Competitive Game Environment for COMP90054, Semester 2, 2023
---------------------------------------------------------------------------

### Table of contents

  * [Introduction](#introduction)
     * [Key files to read:](#key-files-to-read)
     * [Other supporting files (do not modify):](#other-supporting-files-do-not-modify)
  * [Rules ](#rules-of-yinsh)
     * [Layout:](#layout)
     * [Scoring:](#scoring)
     * [Winning:](#winning)
     * [Computation Time:](#computation-time)
  * [Getting Started](#getting-started)
     * [Restrictions:](#restrictions)
     * [Warning:](#warning)
     * [Ranking](#ranking)
  
## Introduction

For COMP90054 this semester, you will be competing against agent teams in Azul, a strategic board game.
There are many files in this package, most of them implementing the game itself. The **only** file that you should change is `myTeam.py`. You can use additional files in your team folder (agents/t_XXX/), which is the **only** directory that we will copy from your repository. 

### Key files to read:

* [azul_model.py](azul_model.py): The model file that generates game states and valid actions. Start here to understand how everything is structured, and what is passed to your agent. In particular, ```getLegalActions()``` will provide a concise rundown of what a turn consists of, and how that is encapsulated in an action.
* [../agents/generic/single_lookahead.py](../agents/generic/single_lookahead.py): Example code that defines the skeleton of a basic planning agent. You are not required to use any of the filled in code, but your agent submitted in `myTeam.py` will at least need to be initialised with __init__(self, _id), and implement SelectAction(self, actions, rootstate) to return a valid action when asked.

### Other supporting files (do not modify):

* `general_game_runner.py`: Support code to setup and run games. See the loadParameter() function for details on acceptable arguments.

* `azul_utils.py`: Stores important constants, such as the integer values used to represent each game piece.

Of course, you are welcome to read and use any and all code supplied. For instance, if your agent is trying to simulate future gamestates, it might want to appropriate code from `azul_model.py` in order to do so.


## Game details

### GUI Layout: 

Upon loading Azul, both **Game** and **Activity Log** windows will appear. The Activity Log window will remain in front, tracking each agent's move. At the end of the game, you are able to click on actions in this window and watch the state reload in Game window accordingly (close the Game window to proceed forward).

The Game window will display the game board, with each agent's pieces counter to display the current score as the game progresses.

### How to play:

Please read the rules or play a sample game here: https://www.ultraboardgames.com/azul/game-rules.php

You can also watch [this video from game expert Becca Scott](https://youtu.be/y0sUnocTRrY)


### Computation Time:

Each agent has 1 second to return each action. Each move which does not return within one second will incur a warning. After three warnings, or any single move taking more than 3 seconds, the game is forfeit. 

There will be an initial start-up allowance of 15 seconds. During this time, your agent can do start-up computation, such as loading a policy. Your agent will need to keep track of turns if it is to make use of this allowance. 


## Getting Started

**Make sure the version of Python used is >= 3.8, and that you have installed the following packages:**
```
func-timeout
GitPython
pytz
```
You can install them by running the following command:
```bash
$ python -m pip install func_timeout pytz GitPython
```

By default, you can run a game against two random agents with the following:

```bash
$ python general_game_runner.py -g Azul
```

There are two agents, you can specify them as a list:

```bash
$ python general_game_runner.py -g Azul -a [agents.generic.random,agents.generic.random]
```

<!-- If the game renders at a resolution that doesn't fit your screen, try using the argument --half-scale. -->

### Debugging

There are many options when running the game, you can view them by:
```bash
$ python general_game_runner.py -h
```
A few options that are commonly used: 
* `-g Azul`: must specify the game is Azul
* `-t`: using text displayer (must use in docker)
* `-p`: print the sys.out and sys.err in the terminal
* `-s`: save the game replay
* `-l`: save the log
<!-- * `--half-scale`: scales the window to half size. -->

Have a look at other options to see how to run the game without the GUI, how to change names, and how to run multiple games.

### Restrictions: 

You are free to use any techniques you want, but will need to respect the provided APIs to have a valid submission. Agents which compute during the opponent's turn will be disqualified. In particular, any form of multi-threading is disallowed, because we have found it very hard to ensure that no computation takes place on the opponent's turn.

### Warning (the output of your code is public): 

If one of your agents produces any stdout/stderr output during its games in the any tournament (preliminary or final), that output will be included in the contest results posted on the website. Additionally, in some cases a stack trace may be shown among this output in the event that one of your agents throws an exception. You should design your code in such a way that this does not expose any information that you wish to keep confidential.

### Ranking: 

Rankings are determined according to [ELO score](https://en.wikipedia.org/wiki/Elo_rating_system) received in tournaments, where a win is worth 3 points, a tie is worth 1 point, and losses are worth 0 (Ties are not worth very much to discourage stalemates). Marks will be awarded according to the rank in the final competition against our staff teams, but participating early in the pre-competitions will increase your learning and feedback. Staff members have entered the tournament with their own devious agents, seeking fame and glory. These agents have team names beginning with `staff-`.