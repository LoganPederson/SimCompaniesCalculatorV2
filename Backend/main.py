from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.responses import HTMLResponse
import items, buildings, schemas, base
from base import SessionLocal, engine
from sqlalchemy.orm import Session
from items import get_lowest_market_price, split_produced_from_string, Item
from recessionAndBoom import recession, boom
items.Base.metadata.create_all(bind=engine)

#App object
app = FastAPI()


origins = ['http://localhost:3000','http://simcompaniescalculator.com','https://simcompaniescalculator.com']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials = True,
    allow_methods = ["GET"],
    allow_headers = ["*"]
)
# create database instance with SessionLocal()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/") # Test route
def read_root():
    return {"Ping":"Pong"}
    

@app.get("/api/calculate_profit_per_hour{}")
def calculate_profit_per_hour(buildingName:str, buildingLevel:int, productionModifierPercentage:float, administrationCostPercentage:float, phase:str,db:Session = Depends(get_db)):
    all_items = db.query(items.Item).all()
    buildings_table = db.query(buildings.Building).all()
    id = 1
    profit_dictionary= {}
    for item in all_items: 
        if item.producedAt == buildingName:
            print('Item to produce: '+item.name)
            produced_from_string_list = split_produced_from_string(item.name) # Splits the item.producedFrom property by "-" ex: ['seeds+4','water+1']
            total_resource_sourcing_cost = 0
            produced_per_hour = item.producedAnHour+(item.producedAnHour*productionModifierPercentage)
            print(item.name+' is produced from [resource+quantity]= '+str(produced_from_string_list))
            print('Current total resource sourcing cost: 0'+"\n")
            for list_item in produced_from_string_list: # ex: [seeds+1,water+4] resource_name+amountNeeded
                if list_item != "": # gets rid of the empty string which all lists contain
                    resource_name_and_amount = list_item.split("+") # ex: [seeds, 1] [water, 4]
                    resource_name = resource_name_and_amount[0]
                    resource_amount_needed = resource_name_and_amount[1]
                    print("resource_name: "+resource_name)
                    print("amount needed: "+str(resource_amount_needed))
                    resource_lowest_market_price = get_lowest_market_price(resource_name)
                    print("lowest market price found for 1 unit of "+resource_name+": " + str(resource_lowest_market_price))
                    market_cost_of_sourcing_resource = resource_lowest_market_price * float(resource_amount_needed) 
                    print("Cost of sourcing "+str(resource_amount_needed)+" of resource "+resource_name+" at market cost of "+str(resource_lowest_market_price)+" = "+str(market_cost_of_sourcing_resource))
                    total_resource_sourcing_cost = total_resource_sourcing_cost + market_cost_of_sourcing_resource
                    print('Current total resource sourcing cost: '+str(total_resource_sourcing_cost)+"\n\n")
            #if total_resource_sourcing_cost == 0:
            print("costPerHour to source all resources needed to produce "+str(produced_per_hour*buildingLevel)+" units of "+ item.name + " = " + str(total_resource_sourcing_cost*(produced_per_hour*buildingLevel))+"\n\n\n")
            # get wages from building and use sourcing cost to find profit per item
            for building in buildings_table:
                if building.name == buildingName:
                    if phase == 'Recession':
                        building_wages = building.wages-(building.wages*recession[building.name])
                    elif phase == 'Booming':
                        building_wages = building.wages+(building.wages*boom[building.name])
                    else:
                        building_wages = building.wages

                    print("Production Building: "+building.name)
                    print("Building Wages: "+str(building_wages*buildingLevel))
                    production_costs = (((total_resource_sourcing_cost*(produced_per_hour*buildingLevel)) + (building_wages * buildingLevel)) + ((building_wages*buildingLevel)*administrationCostPercentage))
                    print("Sourcing Costs "+str(total_resource_sourcing_cost*(produced_per_hour*buildingLevel))+" + Total Wages/h "+str(building_wages*buildingLevel)+" accouting for Admin Overhead of "+str(administrationCostPercentage)+" = "+ str(production_costs))
                    print("Items Produced An Hour: "+str(produced_per_hour*buildingLevel))
                    lowest_market_price = get_lowest_market_price(item.name)
                    transportation_market_price = get_lowest_market_price('Transport')
                    trasnportation_cost = ((item.transportation * transportation_market_price) * (produced_per_hour*buildingLevel))
                    accounting_for_three = lowest_market_price*(produced_per_hour*buildingLevel)- ((lowest_market_price*(produced_per_hour*buildingLevel)*0.03))
                    profit_per_hour = (accounting_for_three -(production_costs+trasnportation_cost))
                    print("(Lowest Market Price Of One "+item.name+' = '+str(lowest_market_price)+" * "+item.name+" produced an hour: "+str(produced_per_hour*buildingLevel)+"= "+str(lowest_market_price*(produced_per_hour*buildingLevel))+" - 3 percent fee: "+str((lowest_market_price*(produced_per_hour*buildingLevel)*0.03))+" = "+str(accounting_for_three)+ "- production_costs+trasnportation_cost: "+str(production_costs)+" "+str(trasnportation_cost)+"("+str(production_costs+trasnportation_cost)+") = "+str(profit_per_hour))
                    print("")
                    profit_dictionary[id] = {'itemName':item.name, 'profit_per_hour':profit_per_hour}
                    print("Adding to profit_dictionary: "+str(profit_dictionary[id])+"\n")
                    id = id + 1
                    break
    db.close()
    return profit_dictionary  