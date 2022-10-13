import itertools
from operator import index
from sqlalchemy import Column, String, Integer, Boolean, Float, inspect
from base import Base, Session, engine
from buildings import Building
import json, requests
from time import time

#- Item class for sqlalchemy Object Relational Mapper (ORM) to translate into postgres database Table. 
class Item(Base): 
    
    __tablename__ = 'Items'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    db_letter = Column(String)
    transportation = Column(Float)
    retailable = Column(Boolean)
    research = Column(Boolean)
    realmAvailable = Column(Boolean)
    producedAnHour = Column(Float)
    averageRetailPrice = Column(Float)
    marketSaturation = Column(Float)
    marketSaturationLabel = Column(String)
    retailModeling = Column(String)
    neededFor = Column(String)
    producedFrom = Column(String)
    producedAt = Column(String)
    lowestMarketPrice = Column(Float)

    def __init__(self, name, db_letter, transportation, retailable, research, realmAvailable, producedAnHour, averageRetailPrice,marketSaturation,marketSaturationLabel,retailModeling, neededFor, producedFrom, producedAt, lowestMarketPrice):
        self.name = name
        self.db_letter = db_letter
        self.transportation = transportation
        self.retailable = retailable
        self.research = research
        self.realmAvailable = realmAvailable
        self.producedAnHour = producedAnHour
        self.averageRetailPrice = averageRetailPrice
        self.marketSaturation = marketSaturation
        self.marketSaturationLabel = marketSaturationLabel
        self.retailModeling = retailModeling
        self.neededFor = neededFor
        self.producedFrom = producedFrom
        self.producedAt = producedAt
        self.lowestMarketPrice = lowestMarketPrice


session = Session()
inspector = inspect(engine)


# GET resource game data from SimCompanies API for specified resource db_letter
def get_resource_data(db_letter):
    timeStart = time()
    url = "https://www.simcompanies.com/api/v4/en/0/encyclopedia/resources/0/{}/".format(db_letter)
    response = requests.get(url)
    resource_data = json.loads(response.text)
    print(url+" Response Time: "+str(time()-timeStart))
    if(time()-timeStart > 1):
        print("Long response time detected, possible rate limiting")
    return resource_data


# GET market pricing list from SimCompanies API for specified resource db_letter
def get_market_data(db_letter):
    url = "https://www.simcompanies.com/api/v3/market/0/{}/".format(db_letter) 
    response = requests.get(url)
    market_data = json.loads(response.text)
    return market_data


def create_new_item(resource_data,market_data):
    needed_for_string = ""
    if "neededFor" in resource_data:
        for item in resource_data["neededFor"]:
            if item["name"]:
                needed_for_string = needed_for_string + item["name"] + '-'
    produced_from_string = ""
    if 'producedFrom' in resource_data:
        if len(resource_data["producedFrom"]) > 0:
            amountToPrint = len(resource_data["producedFrom"])
            x = 0
            for item in resource_data["producedFrom"]:
                if x < amountToPrint:
                    produced_from_string = produced_from_string + resource_data["producedFrom"][x]["resource"]["name"] + "+"+str(resource_data["producedFrom"][x]["amount"])+"-"
                    x = x + 1
    produced_at_string = ""
    if 'producedAt' in resource_data:
        produced_at_string = produced_at_string + resource_data["producedAt"]["name"]
    new_item = Item(resource_data["name"], resource_data["db_letter"], resource_data["transportation"], resource_data["retailable"], resource_data["research"], resource_data["realmAvailable"], resource_data["producedAnHour"], resource_data["averageRetailPrice"], resource_data["marketSaturation"], resource_data["marketSaturationLabel"], resource_data["retailModeling"], needed_for_string, produced_from_string, produced_at_string, market_data[0]["price"])
    return new_item


index_ranges = (
    range(1, 36), # SimCompanies API uses index db_letter associated with each unique item 
    range(40, 90), # however there are big gaps in the indexing for an unknown reason.
    [98], # This is why we have the index_ranges with seemingly random indexes. 
    range(100, 114) 
) 


'''

populate_items_table() checks for existing table and deletes it if one exists,
then for every resource db_letter that exists calls get_resource_data(db_letter) 
and adds the returned data as a row in the Items table. 

'''
def populate_items_table():
    if(inspector.has_table('Items')):
        print("Table Items exists!")
        Item.__table__.drop(engine)
        session.commit()
        Base.metadata.create_all(engine)
        print("Items table dropped, session commited, then schema recreated")
    else:
        print("No table named Items found, creating Schema")
        Base.metadata.create_all(engine)

    for sim_api_db_letter in itertools.chain(*index_ranges):
        resource_data = get_resource_data(sim_api_db_letter)
        market_data = get_market_data(sim_api_db_letter)
        new_item = create_new_item(resource_data, market_data)
        session.add(new_item)
        session.commit()

def get_produced_from_items(): 
    producedFromItems = session.query(Item).all()
    for item in producedFromItems:
        print(item.name + ' is producedFrom: '+item.producedFrom)

def get_produced_at_items():
    producedAtItems = session.query(Item).all()
    for item in producedAtItems:
        print(item.name + ' is producedAt: '+item.producedAt)

def split_produced_from_string(itemName):
    #print itemNames producedFrom
    item = session.query(Item).all()
    for items in item:
        if items.name == itemName:
            splitByMinus = items.producedFrom.split('-')
            #print(splitByMinus) # for loop and check for empty string within list of tuples to split item names and cost
            return(splitByMinus)

def get_lowest_market_price(itemName):
    itemTable = session.query(Item).all()
    for item in itemTable:
        if item.name == itemName:
            return item.lowestMarketPrice
                    

# removes items table
def remove_items_table():
    session.query(Item).delete()
    session.commit()

def get_item():
    items = session.query(Item).all()
    for item in items:
        if item.name == "Mining research":
            print(item.name)
            print(item.producedAnHour)


#removeItemsTable()
#populate_items_table()

session.close()

