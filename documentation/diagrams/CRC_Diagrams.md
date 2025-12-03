# CRC Diagrams

## main.py
| Collaboators            | Purpose                                                                |
| ----------------- | ------------------------------------------------------------------ |
| `discord.commands.Bot` | Core bot functionality and command handling |
| `discord.Guild` | Access server information, members, roles, channels |
| `discord.Member` | User operations (kick, ban, voice state |
| `discord.VoiceClient` | Voice channel connection and audio |
| `discord.Embed` | Format level info and music displays |
| `flask_app` | Basic API layer for bot stats |
| `threading.Thread` |  Runs flask server concurrently |


## /cogs/reaction_roles.py
| Collaboators            | Purpose                                                                |
| ----------------- | ------------------------------------------------------------------ |
| `discord.Client` | Access bot instance and shared state |
| `discord.Interaction` | Recieve and respond to commands |
| `discord.Embed` | Create formatted reaction role messages |
| `discord.Role` | Reference roles to assign/remove from members |
| `discord.Member` | Modify role assignments for users |
| `discord.Guild` | Access specific server and server roles |
| `discord.Message` | Fetch messages, add reactions |
| `discord.RawReactionActionEvent` | Process reaction events when bot is offline |
| JSON | Store configuration data |
| File system | Read/Write to `data/reaction_roles.json` |

## /cogs/moderation.py

| Collaboators            | Purpose                                                                |
| ----------------- | ------------------------------------------------------------------ |
| `discord.Client` | Access bot instance |
| `discord.Message` | Access message content, author, channel, and delete messages |
| `discord.Member` | Apply timouts and change permissions for members |
| `discord.Guild` | Access specific server and channels for muting |
| `discord.TextChannel` | Send warning messages and modify permissions |
| `discord.Interaction` | Recieve and respond to slash commands |
| `commands.CooldownMapping` | Track rate limits and violations per member |
| `commands.BucketType` | Define individual member rate limiting |
| `datetime.timedelta` | Define timeout durations |
| File System | Read/Write to `data/bad_words.txt` |
