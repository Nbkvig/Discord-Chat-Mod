import {
  Card, 
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle
} from '@/components/ui/card'
import { useEffect, useState } from 'react';


export default function App() {
  const [botStats, setBotStats] = useState(null);
  const [loading, setLoading] = useState(true);   
  const [error, setError] = useState(null);
  const [recentActions, setRecentActions] = useState([]);


  useEffect(() => {
    // Fetch bot stats
    fetch("http://localhost:8005/api/bot-stats")
      .then(res => {
        if (!res.ok) throw new Error('Bot stats endpoint not found');
        return res.json();
      })
      .then(data => {
        setBotStats(data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching bot stats:', error);
        setError(error.message);
        setLoading(false);
      });


      // Fetch recent actions
    fetch("http://localhost:8005/api/recent-actions")
      .then(res => res.json())
      .then(data => {
        setRecentActions(data);
      })
      .catch(error => {
        console.error('Error fetching recent actions:', error);
      });
  }, []);

  
  return (
    <div className="flex h-screen w-full">
      <main className="flex-1 p-6 bg-slate-950 overflow-auto">
        <div className="space-y-6">


          {/* Top Row - 5 cards wide */}
          <div className='grid grid-cols-5 gap-6'>
            

            {/* Users */}
            <Card>
              <CardHeader>
                <CardTitle>Users</CardTitle>
                <CardDescription>Total users in all guilds</CardDescription>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <p>Loading...</p>
                ) : (
                  <p className="text-4xl font-bold">{botStats?.users || 0}</p>
                )}
              </CardContent>
            </Card>


            {/* Guilds */}
            <Card>
              <CardHeader>
                <CardTitle>Guilds</CardTitle>
                <CardDescription>Active servers</CardDescription>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <p>Loading...</p>
                ) : (
                  <p className="text-4xl font-bold">{botStats?.guilds?.length || 0}</p>
                )}
              </CardContent>
            </Card>


            {/* Voice Channels */}
            <Card>
              <CardHeader>
                <CardTitle>Voice Channels</CardTitle>
                <CardDescription>Total voice</CardDescription>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <p>Loading...</p>
                ) : (
                  <p className="text-4xl font-bold">{botStats?.['voice-channels']?.length || 0}</p>
                )}
              </CardContent>
            </Card>


            {/* Text Channels */}
            <Card>
              <CardHeader>
                <CardTitle>Text Channels</CardTitle>
                <CardDescription>Total text</CardDescription>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <p>Loading...</p>
                ) : (
                  <p className="text-4xl font-bold">{botStats?.['text-channels']?.length || 0}</p>
                )}
              </CardContent>
            </Card>


            {/* Bot Status */}
            <Card>
              <CardHeader>
                <CardTitle>Status</CardTitle>
                <CardDescription>Bot status</CardDescription>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <p>Loading...</p>
                ) : (
                  <p className="text-4xl font-bold capitalize">{botStats?.status || 'offline'}</p>
                )}
              </CardContent>
            </Card>
          </div>


      {/* Bottom Row - 2 giant cards */}
          

          {/* Server List */}
          <div className='grid grid-cols-2 gap-6'>
            <Card className="min-h-[400px]">
              <CardHeader>
                <CardTitle>Server List</CardTitle>
                <CardDescription>Discord servers your bot is active in</CardDescription>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <p>Loading...</p>
                ) : botStats?.guilds?.length === 0 ? (
                  <p className="text-slate-400">No servers found</p>
                ) : (
                  <div className="space-y-3">
                    {botStats?.guilds?.map((guild, index) => (
                      <div key={index} className="border-b pb-3 last:border-b-0">
                        <p className="text-sm">{guild.name || guild}</p>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>


             {/* Recent Actions */}
            <Card className="min-h-[400px]">
              <CardHeader>
                <CardTitle>Recent Actions</CardTitle>
                <CardDescription>Latest bot activity</CardDescription>
              </CardHeader>
              <CardContent>
                {recentActions.length === 0 ? (
                  <p className="text-slate-400">No recent actions</p>
                ) : (
                  <div className="space-y-3">
                    {recentActions.map((action, index) => (
                      <div key={index} className="border-b pb-3 last:border-b-0">
                        <p className="">{action.message}</p>
                        <p className="text-xs">{action.time}</p>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>


          </div>
        </div>
      </main>
    </div>
  );
}