import aiosqlite

# =================================
# Initialize the Database & check
# =================================
async def init_db():
    async with aiosqlite.connect("level.db") as connect:
        
        await connect.execute("""
            CREATE TABLE IF NOT EXISTS Users (
                UserId TEXT PRIMARY KEY,
                Xp INT DEFAULT 0,
                Level INT DEFAULT 1
            )
        """)

        # save the changes
        await connect.commit()

        # check if the table is created
        async with connect.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Users'") as cursor:
            table = await cursor.fetchone()

            if table:
                print("✅ Users table exists")
            else:
                print("❌ Users table not found!")



# =================================
# Add XP to User in Database
# =================================
async def add_xp(UserId, Amount):
    # Open a connection to the database for this operation
    async with aiosqlite.connect("level.db") as connect:

        # retrieve the xp and level using the UserID
        async with connect.execute("SELECT Xp, Level FROM Users WHERE UserId = ?", (UserId,)) as cursor:
            result = await cursor.fetchone()     # fetch one row from the query

            # If the user exists
            if result:
                Xp, Level = result
                Xp += Amount

                # create a level-up depending on the amount of XP required
                while Xp >= 100 * (Level ** 2):
                    Xp -= 100 * (Level ** 2)
                    Level += 1

                # update the database with new XP
                await connect.execute("UPDATE Users SET Xp = ?, Level = ? WHERE UserId = ?", (Xp, Level, UserId))

            else:
                # if the user doesn't exist then add them to DB
                await connect.execute("INSERT INTO Users (UserId, Xp) VALUES (?, ?)", (UserId, Amount))

            await connect.commit()



# Add user to the database
async def auto_user(UserId):
    async with aiosqlite.connect("level.db") as connect:
        
        # Add the user to the data base
        await connect.execute("INSERT INTO Users (UserId) VALUES (?)", (UserId,))

        # save changes
        await connect.commit()


# function to return level and xp for printing
async def print_level(UserId):
    async with aiosqlite.connect("level.db") as connect:
        async with connect.execute("SELECT Xp, Level FROM Users WHERE UserId = ?", (UserId,)) as cursor:
            results = await cursor.fetchone()
            
            if results: 
                xp, level = results
                return xp, level
            else:
                return None, None
            

# function for Resetting level
async def reset_level(UserId):
    async with aiosqlite.connect("level.db") as connect:
        async with connect.execute("SELECT UserId FROM Users WHERE UserId = ?", (UserId,)) as cursor:
        
            # check if the user exists first before updating
            if await cursor.fetchone():
                await connect.execute("UPDATE Users SET Xp = 0, Level = 1 WHERE UserId = ?", (UserId,))

                await connect.commit()
