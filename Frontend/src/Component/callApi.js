import React, { useState, useMemo } from "react";
import ReactTooltip from 'react-tooltip';
import { COLUMNS } from "./columns";
import { useTable } from "react-table";
import axios from 'axios'
import MyImage from '../img/SimCompaniesCalculator_Logo.png'


export const CallApi = () => {

const [buildingLevel, setBuildingLevel] = useState('');
const [productionModifierPercentage, setProductionModifier] = useState('');
const [adminCostPercentage, setAdminCostPercentage] = useState('');
const [DATA, setDATA] = useState({});
const [buildingNameDropdownValue, setBuildingNameDropdownValue] = useState('Building Name');
const [phaseDropDownValue, setPhaseDropDownValue] = useState('Normal');
const [shown, setShown] = useState(false);
const buildingNameDropdownOptions = ["Building Name", "Plantation","Water reservoir","Power plant","Oil rig","Refinery","Shipping depot","Farm","Beverage factory","Mine","Factory","Electronics factory","Fashion factory","Car factory","Plant research center","Physics laboratory","Breeding laboratory","Chemistry laboratory","Software R&D","Automotive R&D","Fashion & Design","Launch pad","Propulsion factory","Aerospace factory","Aerospace electronics","Vertical integration facility","Hangar","Quarry","Concrete plant","Construction factory"]
const columns = useMemo(() => COLUMNS, []);
const data = useMemo(() => { // Because our nested dictionary returned from fastAPI is an array of one element object, which contains more objects we need to transform this into an array using .map
  const rawData = DATA;
  if (rawData !== undefined && rawData !== null){
    console.log('rawData is no longer undefined or null, now is: '+JSON.stringify(rawData))
    console.log('rawData mapped is returning: '+JSON.stringify(Object.keys(rawData).map((key) => rawData[key])))
  return Object.keys(rawData).map((key) => rawData[key]);
  }
}, [DATA]);

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
        let encodedName = encodeURI(buildingNameDropdownValue)
        let targetURI = `http://localhost:8000/api/calculate_profit_per_hour{}?buildingName=${encodedName}&buildingLevel=${buildingLevel}&productionModifierPercentage=${productionModifierPercentage}&administrationCostPercentage=${adminCostPercentage}&phase=${phaseDropDownValue}`
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

const HandleClick = () => {
  if (buildingNameDropdownValue === 'Building Name') {
    alert("Please Select A Building Name From The Dropdown!")}
  else if (buildingLevel === '' || isNaN(buildingLevel)){
    alert("Please Enter A Valid Building Level!")
  }
  else if (productionModifierPercentage === '' || isNaN(productionModifierPercentage)){
    alert("Please Enter A Valid Production Modifier %!")
  }
  else if (adminCostPercentage === '' || isNaN(adminCostPercentage)){
    alert("Please Enter A Valid Administration Cost %!")
  }
  else {      
    setShown(false)
    populateTable()
    setShown(true)
    console.log("The type of buildingLevel is: "+(parseInt(buildingLevel)).type)
  }
}

const handlePhaseChange = (event) => {
  setPhaseDropDownValue(event.target.value)
}
const handleBuildingNameChange = (event) => {
  setBuildingNameDropdownValue(event.target.value)
}




return(
    <>
    <div id='mainDiv'>
        <div id='logoDiv'>
          <img id='logoImg' src={MyImage} alt={'Logo!'}></img>
        </div>
        <p id='textBoxes'>
        <label data-tip data-for='bldgNameTip'>
          <select className='inputBox' onChange={handleBuildingNameChange}>
            {buildingNameDropdownOptions.map(buildingN => (
              <option key={buildingN} value={buildingN}>
                {buildingN}
              </option>
            ))}
          </select>
        </label>
        <ReactTooltip id='bldgNameTip' place='top' effect='solid' resizeHide={false}>Select Building</ReactTooltip>
        <input className='inputBox' type="text" name="buildingLevel" id="buildingLevel" placeholder="Lvl ex: 3" onChange={e => setBuildingLevel(e.target.value)} data-tip data-for='bldgLvlTip' ></input>
        <ReactTooltip id='bldgLvlTip' place='top' effect='solid' resizeHide={false}>Enter Building Level - ex: 3</ReactTooltip>
        <input className='inputBox' type="text" name="productionModifier" id="productionModifier" placeholder="Modifier% ex: 0.01" onChange={e => setProductionModifier(e.target.value)} data-tip data-for='prodTip' ></input>
        <ReactTooltip id='prodTip' place='top' effect='solid' resizeHide={false}>Enter Production Modifier % In Decimal Form - ex: 0.01</ReactTooltip>
        <input className='inputBox' type="text" name="adminCost" id="adminCost" placeholder="AdminCost% ex: 0.01" onChange={e => setAdminCostPercentage(e.target.value)} data-tip data-for='adminTip' ></input>
        <ReactTooltip id='adminTip' place='top' effect='solid' resizeHide={false}>Enter Administration Cost Percentage In Decimal Form - ex: 0.02</ReactTooltip>
        <label data-tip data-for='phaseTip'>
          <select className='inputBox' value={phaseDropDownValue} onChange={handlePhaseChange}>
            <option value="Booming">Booming</option>
            <option value="Recession">Recession</option>
            <option value="Normal">Normal</option>
          </select>
        </label>
        <ReactTooltip id='phaseTip' place='top' effect='solid' resizeHide={false}>Select Economy Phase</ReactTooltip>
        </p>
        <p id='Button'>
        <button type='button' id="getDBinfo" className='block' onClick={()=>HandleClick()}>Get Profit Per Hour</button> 
        </p>
    </div>

    <div id='tableDiv'>
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
                      if(cell.value >= 0){
                        return <td  {...cell.getCellProps()} style={{color:"green"}}> {cell.render("Cell")}</td>;
                        }
                      else if( cell.value < 0){
                        return <td  {...cell.getCellProps()} style={{color:"red"}}> {cell.render("Cell")}</td>;
                      }
                      else{
                        return <td  {...cell.getCellProps()}> {cell.render("Cell")}</td>;
                      }
                    })}
                  </tr>
                );
              })}
            </tbody>
          </table>
          :null}
    </div>
    </>

) 

};
