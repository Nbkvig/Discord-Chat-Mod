import {
    Card, 
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle
  } from '@/components/ui/card'

  import {
    NativeSelect,
    NativeSelectOptGroup,
    NativeSelectOption,
  } from "@/components/ui/native-select"

  import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
  
  /* Will need this later for dashboard. 
  
  
  async function getData(): Promise<Data[]> {
    const result = await fetch('http://localhost:4000/data')
  
    return result.json()
  }
  */
  
  
  
  export default function XP() {
      // const data = await getData()

      const channels = [
        { id: '123456789', name: 'general' },
        { id: '987654321', name: 'announcements' },
        { id: '555555555', name: 'bot-commands' },
      ];

      return (
        <div className='grid grid-cols-2 gap-8'>
          <Card>
            <CardHeader>
              <div>
                <CardTitle> XP  </CardTitle>
                <CardDescription> Card Description</CardDescription>
              </div>
            </CardHeader>
            <CardContent>
            <NativeSelect>
                <NativeSelectOption value="">Select a channel</NativeSelectOption>
                    {channels.map((channel) => (
                        <NativeSelectOption key={channel.id} value={channel.id}>
                        {channel.name}
                </NativeSelectOption>
            ))}
            </NativeSelect>

            <Textarea placeholder="Type the message for leveling up here!" />


            </CardContent>
            <CardFooter>
            <div className="grid w-full gap-2"><Button>Apply Changes</Button></div>
            </CardFooter>
          </Card>
        </div>
      );
    }