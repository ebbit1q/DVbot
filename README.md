# DV-bot
a Discord bot to roll d10s with

## Description
DV is a bot to assist in playing the Cyberpunk RED tabletop role playing game.
The bot is able to roll checks and damage using simple triggers anywhere in
messages, it is useful to restrict the channel access of the bot in order to
prevent false positives.

## Actions
DV responds to certain keywords within a message, each trigger in a message
will generate a field in the reponse.
The bot recognizes the following actions:

#### Check
A check is a basic skill test in CPR, they use a single d10 roll with any
amount of modifiers.
Checks can have one critical failure or success roll added or subtracted:
- when a natural 1 is rolled, a second d10 is rolled and subtracted
- when a natural 10 is rolled, a second d10 is rolled and added

They are recognized by the following format:
- check [+|-] `modifier` [[+|-] `modifier` ...] [x`multiple`]
  - modifier is an integer to add to the result
  - multiple is an optional amount to repeat the action up to 9

Checks require a modifier, to roll a check without modifiers use 0.
A - is used to signify a modifier is negative and it will be detracted.
It is not required to use + signs but they can be used to separate modifiers.
Whitespace is ignored but can be used to separate modifiers as well.
Modifiers with a value of 0 do not show up in the output.
If multiple is 0 nothing happens and the entire trigger is ignored.

The following messages will have the bot reply with a check:
- Alice opens a jar, check +11 -2
- check5+6x2 Bob shoots Jim with their sidearm!
- check 0
- check-13 -- -+++- -- 42     -0           +      +           9        x9

#### Damage
Damage in CPR is based on an amount of d6, from simple knifes dealing 1d6 to
rocket launchers dealing 8d6.
When 2 or more of the dice land on 6 a critical injury is inflicted, the bot
will note this in its reply.

They are recognized by the following format:
- damage `amount`[d6] [[+|-] `modifier` ...] [x`multiple`]
  - amount is how many dice to roll in the integer range 1 to 8, inclusive
  - modifier is an optional integer to add to the result
  - multiple is an optional amount to repeat the action up to 9

Damage actions require an amount, it is not possible to roll 0 dice.
The modifiers are optional and processed the same way as on checks.
If multiple is 0 nothing happens and the entire trigger is ignored.

The following messages will have the bot reply with a damage roll:
- Alice's metal fist strikes the statue (20HP), damage 2d6
- damage3x2 Bob's pistol punches a hole in Jim's torso!
- damage 8+11  -2-------------------------------------0            x3
- damage 4 x4 check 4

## Reactions to messages
Each user can interact with their most recently rolled result.
The bot will place a few emoji reactions on each most recent result.
Other users are not allowed to interact with your results.
Users can add the same reaction in order to have the bot change its message:

#### Die emoji / Reroll
Adding this emoji will have the bot reinterpret your message and update its
result.
This is useful if you made a typo or are otherwise unsatisfied with the
result.

#### Put litter in its place emoji / Trashcan
Adding this emoji will have the bot delete this reply.
This is useful if the bot triggered accidentally.

#### Clock emoji / Patience
The bot will place this reaction on mesages it could not interpret before it
was done sending a reply.
This means you might have to send this message again.

## Starting the bot
Running DV requires Python version 3.8 or higher.
To install the dependencies using pip use: `pip install -r requirements.txt`
To invoke the bot run: `python -m DVbot` from outside the repository.
The bot will by default try to open the .token file that contains your bot's
Discord token (and nothing else).
To create a bot token, check this guide:
https://discordpy.readthedocs.io/en/stable/discord.html
Note that the correct token is in the "Bot" tab, not the "OAuth2" tab.

I like to copy the token and then use this bash comand to pipe it to a file:
`xclip -o -se c >.token`
This requires the xclip tool which can be installed with the xclip package on
most distros.
Alternatively you can paste it into an editor and save the file as `.token`.
