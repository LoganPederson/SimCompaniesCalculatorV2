import React, { useState, useEffect, useMemo } from "react";
import { COLUMNS } from "./columns";
import { useAsyncDebounce, useTable } from "react-table";
import axios from 'axios'



export const CallApi = () => {

const [buildingName, setBuildingName] = useState('');
const [buildingLevel, setBuildingLevel] = useState('');
const [productionModifierPercentage, setProductionModifier] = useState('');
const [adminCostPercentage, setAdminCostPercentage] = useState('');
const [DATA, setDATA] = useState({});
const [dropDownValue, setDropDownValue] = useState('Normal');
const [shown, setShown] = useState(true);

const columns = useMemo(() => COLUMNS, []);
const data = useMemo(() => { // Because our nested dictionary returned from fastAPI is an array of one element object, which contains more objects we need to transform this into an array using .map
  const rawData = DATA;
  if (rawData != undefined && rawData != null){
    console.log('rawData is no longer undefined or null, now is: '+JSON.stringify(rawData))
    console.log('rawData mapped is returning: '+JSON.stringify(Object.keys(rawData).map((key) => rawData[key])))
  return Object.keys(rawData).map((key) => rawData[key]);
  }
}, [DATA]);

useEffect (() => {
  ToggleShown();
},[])

const tableInstance = useTable({
    columns,
    data
});

const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    rows,
    prepareRow
  } = tableInstance;

const populateTable = async () => {
    try{
        let encodedName = encodeURI(buildingName)
        let targetURI = `3.132.177.230/api/calculateProfitPerHourOf{}?buildingName=${encodedName}&buildingLevel=${buildingLevel}&productionModifierPercentage=${productionModifierPercentage}&administrationCostPercentage=${adminCostPercentage}&phase=${dropDownValue}`
        let res = await axios.get(targetURI);
        let arr = res.data;
        console.log('arr = '+arr)
        console.log('arr stringified = '+JSON.stringify(arr))
        setDATA(arr)
        return (arr)
        
    } catch(e) {
        console.log(e)
    }
}



const ToggleShown = () => {
  setShown(!shown)
}
const HandleClick = () => {
  setShown(false)
  populateTable().then (() => {
    console.log('this happened after pouplateTable completed the promise')
  })
  setShown(true)
}
const whatIsSetShown = async () => {
  ToggleShown();
  console.log('Stringified data: '+String(JSON.stringify(data)))
  console.log('data: '+String(data))
  console.log('DATA = '+DATA)
  console.log('DATA stringified = '+JSON.stringify(DATA))
}
const handleChange = (event) => {
  setDropDownValue(event.target.value)
}




return(
    <div id='mainDiv'>
        <p id='textBoxes'>
        <input type="text" name="buildingName" id="buildingName" placeholder="Building Name" onChange={e => setBuildingName(e.target.value)}></input>
        <input type="text" name="buildingLevel" id="buildingLevel" placeholder="Building Level" onChange={e => setBuildingLevel(e.target.value)}></input>
        <input type="text" name="productionModifier" id="productionModifier" placeholder="Production Modifier %" onChange={e => setProductionModifier(e.target.value)}></input>
        <input type="text" name="adminCost" id="adminCost" placeholder="Administration Cost %" onChange={e => setAdminCostPercentage(e.target.value)}></input>
        <label>
          <select value={dropDownValue} onChange={handleChange}>
            <option value="Booming">Booming</option>
            <option value="Recession">Recession</option>
            <option value="Normal">Normal</option>

          </select>
        </label>
        </p>
        <p id='Button'>
        <button type='button' id="getDBinfo" className='block' onClick={()=>HandleClick()}>Get DB Info</button>
        <button type='button' id="getDBinfo" className='block' onClick={()=>whatIsSetShown()}>Print State of setShown</button>
        
        </p> 
        {(shown && DATA) ?
          <table id='outputTable' {...getTableProps()}>
            <thead>
              {headerGroups.map((headerGroup) => (
                <tr {...headerGroup.getHeaderGroupProps()}>
                  {headerGroup.headers.map((column) => (
                    <th {...column.getHeaderProps()}>{column.render("Header")}</th>
                  ))}
                </tr>
              ))}
            </thead>
            <tbody {...getTableBodyProps()}>
              {rows.map((row) => {
                prepareRow(row);
                return (
                  <tr {...row.getRowProps()}>
                    {row.cells.map((cell) => {
                      return <td {...cell.getCellProps()}>{cell.render("Cell")}</td>;
                    })}
                  </tr>
                );
              })}
            </tbody>
          </table>
          :null}
    </div> 

) 

};
