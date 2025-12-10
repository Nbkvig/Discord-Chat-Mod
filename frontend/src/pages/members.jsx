import {
  Card, 
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle
} from '@/components/ui/card'

/* Will need this later for dashboard. 


async function getData(): Promise<Data[]> {
  const result = await fetch('http://localhost:4000/data')

  return result.json()
}
*/



export default function Members() {
    // const data = await getData()
    return (
      <div className='grid grid-cols-1 gap-8'>
        <Card>
          <CardHeader>
            <div>
              <CardTitle> members </CardTitle>
              <CardDescription> Card Description</CardDescription>
            </div>
          </CardHeader>
          <CardContent>
            <p>Placeholder P-Tag </p>
          </CardContent>
          <CardFooter>
            <button>Placeholder button</button>
          </CardFooter>
        </Card>
      </div>
    );
  }