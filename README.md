**This software is only for educational purposes, as Discord's terms and conditions don't allow this practices**

# DiscordMirror
DiscordMirror is a software that clones X server in real time and resend all the messages and embes to another server to which you specify.     

# Firsts steps
(I recommemd to doing this on a virtual enviroment)

You need to install the requirements with the next command in the terminal `pip install -r requirements.txt`

After you have done the previous step, you will need to edit the `gateway.py` source from the discord library and find the line:

`if state._intents is not None:
     payload['d']['intents'] = state._intents.value`
     
and change it to:

`if state._intents is not None and self._connection.is_bot == True:
     payload['d']['intents'] = state._intents.value`

# Configuration
You need to fill `config.json` file with the correct information

- filter_file: you can leave it as default
- server_a: server's ID which you want to clon
- server_b: server's ID where server_a is going to be cloned
- discord_token: your personal discord's token

Then, in the `filter.txt` you need to input the categories ID that you want to clone on your server, the bot will create all the channels and categories it self and delete channels and categories that are not in the filter.

Once you have done all the steps, now just run the software and it will be running ;)
