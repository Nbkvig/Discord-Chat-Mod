import {
  Card, 
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle
} from '@/components/ui/card'

import {
    Field,
    FieldDescription,
    FieldGroup,
    FieldLabel,
    FieldSet,
  } from "@/components/ui/field"

import {
    NativeSelect,
    NativeSelectOptGroup,
    NativeSelectOption,
  } from "@/components/ui/native-select"

import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import { EmojiPicker } from "frimousse";

/* Will need this later for dashboard. 


async function getData(): Promise<Data[]> {
  const result = await fetch('http://localhost:4000/data')

  return result.json()
}
*/



export default function Roles() {

    const channels = [
        { id: '123456789', name: 'general' },
        { id: '987654321', name: 'announcements' },
        { id: '555555555', name: 'bot-commands' },
      ];

    const roles = [
        { id: '1111', name: 'Admin' },
        { id: '1234', name: 'user' },
    ]

    
    // const data = await getData()
    return (
        <div className='grid grid-cols-2 gap-8'>
        <Card>
          <CardHeader>
            <div>
              <CardTitle>Auto Roles</CardTitle>
              <CardDescription>Assign roles upon joining the server.</CardDescription>
            </div>
          </CardHeader>
          <CardContent>
          
          <NativeSelect className>
                <NativeSelectOption value="">Select a Role</NativeSelectOption>
                    {roles.map((role) => (
                        <NativeSelectOption key={role.id} value={role.id}>
                        {role.name}
                </NativeSelectOption>
            ))}
            </NativeSelect>
          </CardContent>
          
          <CardFooter>
          <div className="grid w-full gap-2"><Button>Deploy Autoroles!</Button></div>
          </CardFooter> 
        </Card>

        <Card>
          <CardHeader>
            <div>
              <CardTitle>Reaction Roles</CardTitle>
              <CardDescription>Allow users to self-assign roles.</CardDescription>
            </div>
          </CardHeader>
          <CardContent>
            <p>Select a channel: </p>
            <div className="grid w-full gap-2">
            <NativeSelect>
                <NativeSelectOption value="">Select a channel</NativeSelectOption>
                    {channels.map((channel) => (
                        <NativeSelectOption key={channel.id} value={channel.id}>
                        {channel.name}
                </NativeSelectOption>
            ))}
            </NativeSelect>

                <Textarea placeholder="Type the message for your reaction roles here." />
                <Button>Add Emoji
                </Button>
                

                <Button>Send Reaction Roles</Button>
            </div>

          </CardContent>
        </Card>
      </div>
    );
  }