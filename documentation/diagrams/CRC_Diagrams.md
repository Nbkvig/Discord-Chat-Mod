# CRC Diagrams

reaction_roles.py
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

| reaction_roles.py             | Collaboators                                                                |
| ----------------- | ------------------------------------------------------------------ |
| `check_spam()` |  |
| `check_mention_spam()` |  |
| `check_bad_words` | `/data/bad_words.txt` |
|  | |
