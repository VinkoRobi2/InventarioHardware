
const { json } = require("react-router-dom")
const url = 'https://pokeapi.co/api/v2/pokemon/ditto';

fetch(url)
.then(response =>{
    if(response.ok){
        return response.json()
    }else{
        throw new Error('Ha ocurrido un error')
}})
.then(data =>{
    data.abilities.forEach(ability => {
        console.log(ability.ability.name)
    });
}

)