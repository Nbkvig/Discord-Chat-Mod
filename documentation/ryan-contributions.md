# Ryan's Contributions

## 10/22/25
### What I did: 
* Moved the reaction roles implementation into a cog. 
* `async def on_ready` was defined three times. Put everything into one spot to avoid confusion. 

### What's next: 
* Create basic moderation tools. 
* Create an audit logger. 
* Implement into front end. 

### **What broke or Got Weird**
* moderation.py has no implementation, so it will say that it wasn't loaded correctly everytime the bot boots. This is ok for now, since the bot will still run.

## 10/17/25
### What I did: 
* Completed basic reaction roles command. Bot embeds a message for color roles, looks for reactions, and assigns roles accordingly. 

### What's next: 
* Need to hook it up to flask so that the front end can see the roles. 
* Change the reaction roles to be adaptable, meaning, I want custom reaction roles if the stakeholder wants there to be custom ones. 
* Move everything into a separate file reaction_roles.py in folder cogs. Additionally, should start moving all modules into the cogs folder. 

### **What broke or Got Weird**
* Nothing broken with the new commit


## 10/16/25
### What I did: 
* Working on reaction roles. Bot currently uses an embed adds reactions to a message. 

### What's next:
* Need to configure reaction roles so that it actually assigns the role to the person that reacts to it.
* After this, configure the reaction roles code so that someone can make it say whatever they want it to, ideally using the front end. 
* Upon completion of the reaction roles function, I would like to move it all to a separate file to keep things organized here.

### **What broke or Got Weird**
* Bot does not assign roles to anything at the moment. 
* Learned today that there is only 3 seconds between when a command is sent, and the bot reacting to the command. If the bot doesn't send something to discord within that 3 seconds, discord passes an error and moves on.


## 10/15/25
### What I did: 
* Abandoned the idea of a webscraper, doesn't really relate to a discord bot + existing tools are shake + twitter API costs thousands of dollars to use a year. Not worth spending an entire semester's tuition plus some change on an API. 
* Instead, now using React in a separate repository. Will merge when significant process is made. Working with existing components libraries to minimize workload. 
* Added a file flask_app.py, and configured a very basic API for a dashboard. Used an API template from a youtube video. 

### What's next:
* More backend functions for the bot. Going to pull from existing libraries to add reactions roles and some basic server statistics to display on the dashboard.
* Connect backend functions to front end using flask.
* More front end development. Probably going to do this last. 

### **What broke or Got Weird**
* Flask only uses port 5000, and this gets weird when you close one instance and open another. The port is still in use after exiting the program. 

## 10/10/25 
### What I did: 
* Created a basic webpage to use as a dashboard for the bot, using React, Node.js, and tailwindcss, and all underlying dependencies. 

### What's next:
* Need a data base to connect this front end to. This front end is useless without a proper backend.  

### **What broke or Got Weird**
* Using example data for now. Tailwindcss4 is not compatible with OSX, so I am using Tailwindcss3 for now. Hopefully this doesn't break anything later on...

## 9/23/25 
### What I did: 
* Configured main.py to talk to discord. Basic I/O to test if users could interact with the bot. 

### What's next:
* Time to add functions! The bot works just fine, now its time to brainstorm and see what we want to add to it. 

### **What broke or Got Weird**
* Since everything is in such a barebonens state, there's nothing that needs to be fixed yet.
