from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.responses import HTMLResponse
import schemas, items, base, buildings
from base import SessionLocal, engine
from sqlalchemy.orm import Session
from items import getItem, getLowestMarketPrice, getMarketData, getNeededForItems, getProducedAtItems, getProducedFromItems, getResourceData, splitProducedFromString, Item
from time import sleep
from recessionAndBoom import recession, boom
items.Base.metadata.create_all(bind=engine)

#App object
app = FastAPI()


origins = ['simcompaniescalculator.com']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials = True,
    allow_methods = ["GET"],
    allow_headers = ["*"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()





@app.get("/") #empty route
def read_root():
    return {"Ping":"Pong"}


@app.get("/api/All_Items")
def getAllItems(db: Session = Depends(get_db)):
    holder = db.query(items.Item).all()
    return holder # return all items and all data associated with them

@app.get("/api/Items/{item_name}") # Return all item data from given string, looks like 
def getThisItem(item_name:str, db: Session = Depends(get_db)):
    holder = db.query(items.Item).all()
    for item in holder:
        if item.name == str(item_name):
            return item


@app.get("/api/calculateProfitPerHourOf{}")
def calculateProfitPerHourPerItem(buildingName:str, buildingLevel:int, productionModifierPercentage:float, administrationCostPercentage:float, phase:str,db:Session = Depends(get_db)):
    allItems = db.query(items.Item).all()
    buildingsTable = db.query(buildings.Building).all()
    id = 1
    profitDict2= {
    }
    if phase == 'Normal':
        for item in allItems: 
            if item.producedAt == buildingName:
                print(item.name)
                producedFromStringList = splitProducedFromString(item.name) # passes item.name to function that will split the items producedFrom property by "-" ex: ['seeds+4','water+1']
                print('producedFromStringList = '+str(producedFromStringList))
                totalResourceSourcingCost = 0
                for listItem in producedFromStringList: # ex: [seeds+1,water+4] resourceName+amountNeeded
                    if listItem != "": # gets rid of the empty string which all lists contain
                        resourceNameAndAmount = listItem.split("+") # ex: [seeds, 1] [water, 4]
                        resourceName = resourceNameAndAmount[0]
                        resourceAmountNeeded = resourceNameAndAmount[1]
                        print("resourceName: "+resourceName)
                        print("amount needed: "+str(resourceAmountNeeded))
                        print("lowest market price found: " + str(getLowestMarketPrice(resourceName)))
                        lowestMarketPriceWith3Fee = (float(getLowestMarketPrice(resourceName))+(float(getLowestMarketPrice(resourceName))*0.03))
                        print("Lowest Market Price Accounting For 3 Fee: "+str(lowestMarketPriceWith3Fee))
                        marketCostOfSourcingResource = lowestMarketPriceWith3Fee * float(resourceAmountNeeded) # lowest market price * amount needed to produce item = total sourcing cost from market of this resource for producing 1 unit of item, including 3% market fee on purchase (haven't factored in transportaiton)
                        totalResourceSourcingCost = totalResourceSourcingCost + marketCostOfSourcingResource
                #if totalResourceSourcingCost == 0:
                print("costPerHour to source all resources needed to produce "+str(item.producedAnHour*buildingLevel)+" units of "+ item.name + " = " + str(totalResourceSourcingCost))
                # get wages from building and use sourcing cost to find profit per item
                for building in buildingsTable:
                    if building.name == buildingName:
                        print("FOUND: "+building.name)
                        print("BUILDING WAGES: "+str(building.wages*buildingLevel))
                        productionCosts = ((totalResourceSourcingCost + (building.wages * buildingLevel)) + ((building.wages*buildingLevel)*administrationCostPercentage))
                        print("Sourcing Costs +  Wages/h + Admin Overhead: "+str(productionCosts))
                        print("Items Produced An Hour: "+str(item.producedAnHour*buildingLevel))
                        lowestMarketPrice = getLowestMarketPrice(item.name)
                        profitPerHour = (lowestMarketPrice*(item.producedAnHour*buildingLevel)) - productionCosts
                        print("(Lowest Market Price "+str(lowestMarketPrice)+" * (items produced an hour*buildingLevel)) ["+str(item.producedAnHour)+"*"+str(buildingLevel)+"] - productionCosts("+str(productionCosts)+") ="+str(profitPerHour))
                        profitDict2[id] = {'itemName':item.name, 'profitPerHour':profitPerHour}
                        id = id + 1
                        print("profitDict2 "+str(profitDict2))
                        break
        return profitDict2 #currently one indent in too far, only returning on the first loop through. However when one indent back it's returning an empty array as jsx cannot render an object with multiple properties*?, need to convert to array or some other datastructure Ig 
    elif phase == 'Recession':
        for item in allItems: 
            if item.producedAt == buildingName:
                print(item.name)
                producedFromStringList = splitProducedFromString(item.name) # passes item.name to function that will split the items producedFrom property by "-" ex: ['seeds+4','water+1']
                print('producedFromStringList = '+str(producedFromStringList))
                totalResourceSourcingCost = 0
                for listItem in producedFromStringList: # ex: [seeds+1,water+4] resourceName+amountNeeded
                    if listItem != "": # gets rid of the empty string which all lists contain
                        resourceNameAndAmount = listItem.split("+") # ex: [seeds, 1] [water, 4]
                        resourceName = resourceNameAndAmount[0]
                        resourceAmountNeeded = resourceNameAndAmount[1]
                        print("resourceName: "+resourceName)
                        print("amount needed: "+str(resourceAmountNeeded))
                        print("lowest market price found: " + str(getLowestMarketPrice(resourceName)))
                        lowestMarketPriceWith3Fee = (float(getLowestMarketPrice(resourceName))+(float(getLowestMarketPrice(resourceName))*0.03))
                        print("Lowest Market Price Accounting For 3 Fee: "+str(lowestMarketPriceWith3Fee))
                        marketCostOfSourcingResource = lowestMarketPriceWith3Fee * float(resourceAmountNeeded) # lowest market price * amount needed to produce item = total sourcing cost from market of this resource for producing 1 unit of item, including 3% market fee on purchase (haven't factored in transportaiton)
                        totalResourceSourcingCost = totalResourceSourcingCost + marketCostOfSourcingResource
                #if totalResourceSourcingCost == 0:
                print("costPerHour to source all resources needed to produce "+str(item.producedAnHour*buildingLevel)+" units of "+ item.name + " = " + str(totalResourceSourcingCost))
                # get wages from building and use sourcing cost to find profit per item
                for building in buildingsTable:
                    if building.name == buildingName:
                        adjustedWages = building.wages - (building.wages * recession[building.name])
                        print("FOUND: "+building.name)
                        print("BUILDING WAGES: "+str(adjustedWages*buildingLevel))
                        productionCosts = ((totalResourceSourcingCost + (adjustedWages * buildingLevel)) + ((adjustedWages*buildingLevel)*administrationCostPercentage))
                        print("Production Cost of Sourcing AND Wages AND Admin Overhead Percentage: "+str(productionCosts))
                        print("Items Produced An Hour: "+str(item.producedAnHour*buildingLevel))
                        profitPerHour = (getLowestMarketPrice(item.name)*(item.producedAnHour*buildingLevel)) - productionCosts
                        profitDict2[id] = {'itemName':item.name, 'profitPerHour':profitPerHour}
                        id = id + 1
                        print("profitDict2 "+str(profitDict2))
                        break
        return profitDict2 #currently one indent in too far, only returning on the first loop through. However when one indent back it's returning an empty array as jsx cannot render an object with multiple properties*?, need to convert to array or some other datastructure Ig 
    else:
        for item in allItems: 
            if item.producedAt == buildingName:
                print(item.name)
                producedFromStringList = splitProducedFromString(item.name) # passes item.name to function that will split the items producedFrom property by "-" ex: ['seeds+4','water+1']
                print('producedFromStringList = '+str(producedFromStringList))
                totalResourceSourcingCost = 0
                for listItem in producedFromStringList: # ex: [seeds+1,water+4] resourceName+amountNeeded
                    if listItem != "": # gets rid of the empty string which all lists contain
                        resourceNameAndAmount = listItem.split("+") # ex: [seeds, 1] [water, 4]
                        resourceName = resourceNameAndAmount[0]
                        resourceAmountNeeded = resourceNameAndAmount[1]
                        print("resourceName: "+resourceName)
                        print("amount needed: "+str(resourceAmountNeeded))
                        print("lowest market price found: " + str(getLowestMarketPrice(resourceName)))
                        lowestMarketPriceWith3Fee = (float(getLowestMarketPrice(resourceName))+(float(getLowestMarketPrice(resourceName))*0.03))
                        print("Lowest Market Price Accounting For 3 Fee: "+str(lowestMarketPriceWith3Fee))
                        marketCostOfSourcingResource = lowestMarketPriceWith3Fee * float(resourceAmountNeeded) # lowest market price * amount needed to produce item = total sourcing cost from market of this resource for producing 1 unit of item, including 3% market fee on purchase (haven't factored in transportaiton)
                        totalResourceSourcingCost = totalResourceSourcingCost + marketCostOfSourcingResource
                #if totalResourceSourcingCost == 0:
                print("costPerHour to source all resources needed to produce "+str(item.producedAnHour*buildingLevel)+" units of "+ item.name + " = " + str(totalResourceSourcingCost))
                # get wages from building and use sourcing cost to find profit per item
                for building in buildingsTable:
                    if building.name == buildingName:
                        adjustedWages = building.wages + (building.wages * recession[building.name])
                        print("FOUND: "+building.name)
                        print("Why am I running 3x?")
                        print("BUILDING WAGES: "+str(adjustedWages*buildingLevel))
                        productionCosts = ((totalResourceSourcingCost + (adjustedWages * buildingLevel)) + ((adjustedWages*buildingLevel)*administrationCostPercentage))
                        print("Production Cost of Sourcing AND Wages AND Admin Overhead Percentage: "+str(productionCosts))
                        print("Items Produced An Hour: "+str(item.producedAnHour*buildingLevel))
                        profitPerHour = (getLowestMarketPrice(item.name)*(item.producedAnHour*buildingLevel)) - productionCosts
                        profitDict2[id] = {'itemName':item.name, 'profitPerHour':profitPerHour}
                        id = id + 1
                        print("profitDict2 "+str(profitDict2))
                        break
        return profitDict2 #currently one indent in too far, only returning on the first loop through. However when one indent back it's returning an empty array as jsx cannot render an object with multiple properties*?, need to convert to array or some other datastructure Ig 


@app.get("/api/Buildings")
async def getAllBuildings():
    return 1