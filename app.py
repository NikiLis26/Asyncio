import aiohttp
import asyncio
import asyncpg

async def fetch_character_data(session, character_id):
    url = f'https://swapi.dev/api/people/{character_id}/'
    async with session.get(url) as response:
        data = await response.json()
        return {
            'id': character_id,
            'birth_year': data['birth_year'],
            'eye_color': data['eye_color'],
            'films': ', '.join(data['films']),
            'gender': data['gender'],
            'hair_color': data['hair_color'],
            'height': data['height'],
            'homeworld': data['homeworld'],
            'mass': data['mass'],
            'name': data['name'],
            'skin_color': data['skin_color'],
            'species': ', '.join(data['species']),
            'starships': ', '.join(data['starships']),
            'vehicles': ', '.join(data['vehicles'])
        }

async def load_data_to_database(pool, character_data):
    async with pool.acquire() as connection:
        async with connection.transaction():
            await connection.execute('''
                INSERT INTO characters 
                (id, birth_year, eye_color, films, gender, hair_color, height, homeworld, mass, name, skin_color, species, starships, vehicles) 
                VALUES 
                ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
            ''',
            character_data['id'], character_data['birth_year'], character_data['eye_color'], character_data['films'],
            character_data['gender'], character_data['hair_color'], character_data['height'], character_data['homeworld'],
            character_data['mass'], character_data['name'], character_data['skin_color'], character_data['species'],
            character_data['starships'], character_data['vehicles'])

async def main():
    async with aiohttp.ClientSession() as session:
        pool = await asyncpg.create_pool(user='user', password='password', database='database', host='localhost')

        tasks = [fetch_character_data(session, character_id) for character_id in range(1, 11)]
        character_data_list = await asyncio.gather(*tasks)

        load_tasks = [load_data_to_database(pool, character_data) for character_data in character_data_list]
        await asyncio.gather(*load_tasks)

asyncio.run(main())
