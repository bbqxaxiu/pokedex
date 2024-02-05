import { useState, useEffect, useMemo } from 'react'; 
import axios from 'axios';
import './Pokedex.css'; 

export default function Pokedex() {
    const [showFilter, setShowFilter] = useState(false)
    const [filters, setFilters] = useState([])
    const [search, setSearch] = useState("")
    const [pokemonInfo, setPokemonInfo] = useState([])
    const [pokemonTypes, setPokemonTypes] = useState([])

    useEffect(() => {
        fetchPokemonInfo()
    }, [])

    async function fetchPokemonInfo () {
        try {
            const POKEMON_BULK_API = `http://localhost:8000/pokemon/bulk-no-pagination`
            const response_pokemon = await axios.get(POKEMON_BULK_API)
            setPokemonInfo(response_pokemon.data.result)

            const POKEMON_TYPES_API = "https://pokeapi.co/api/v2/type"
            const response_types = await axios.get(POKEMON_TYPES_API)

            const tempPokemonTypes = [] 
            response_types.data.results.map((result) => {
                tempPokemonTypes.push(result.name)
            })
            setPokemonTypes(tempPokemonTypes)
        } catch {
            console.log("couldnt fulfill ur request :(")
        }
    }

    const renderPokemon = (pokemon) => {
        const name = pokemon.name
        const image = pokemon.image
        const type = pokemon.types
        return (
            <div className="pokemon__pokemon_info">
                <div className="pokemon__pokemon_info--biography">
                    <img src={image}/>
                    <div>
                        <div>{type}</div>
                        <span>{name}</span>
                    </div>
                </div>
                <button>View More</button>
            </div>
        )
    }
    
    const handleSearchChange = (e) => {
        setSearch(e.target.value)
    }

    const handleFilterChange = (type) => {
        console.log("in the method againnn")
        if (filters.includes(type)) {
            setFilters(filters.filter((filter) => filter != type))
        } else {
            setFilters([...filters, type])
        }
    }
    
    const renderFilters = () => {
        return (
            <div>
                {pokemonTypes.map((type) => {
                    return (
                        <button id={type} onClick={() => handleFilterChange(type)}>{type}</button>
                    )
                })}
            </div>
        )
    }

    const pokemons = useMemo(() => {
        if (!filters.length > 0 && search == "") {
            return pokemonInfo
        }
        else if (filters.length > 0 && search == "") { // filters set, but no search 
            return pokemonInfo.filter((pokemon) => {
                return filters.includes(pokemon.types)
            })
        } else if (!filters.length > 0 && search != "") { // no filters, but non empty search 
            return pokemonInfo.filter((pokemon) => {
                return pokemon.name.toLowerCase().includes(search.toLowerCase()) 
            })
        } else { // user use input both filters and search 
            return pokemonInfo.filter((pokemon) => {
                return filters.includes(pokemon.types) && pokemon.name.toLowerCase().includes(search.toLowerCase()) 
            })
        }
        
    }, [search, filters, pokemonInfo])

    return (
        <div>
            <div className="pokedex__header">
                Pokemon
            </div>
            <div className="pokedex__search">
                <div className="pokedex__search-input">
                    <input placeholder="Search by Name" type="text" onChange={handleSearchChange}/>
                </div>
                <div className="pokedex__search-filter">
                    <button onClick={() => setShowFilter(!showFilter)}>Filters</button>
                    {showFilter && renderFilters()}
                </div>
            </div>
            <div className="pokedex__pokemon_content">
                {pokemons && pokemons.map((pokemon) => renderPokemon(pokemon))}
            </div>
        </div>
    )
}