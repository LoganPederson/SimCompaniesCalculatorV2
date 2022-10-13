from sqlalchemy import Column, String, Integer, Boolean, inspect
from base import Base, Session, engine
import json, requests


#- Building class for sqlalchemy Object Relational Mapper (ORM) to translate into postgres database Table. 
class Building(Base):

    __tablename__ = 'Buildings'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    image = Column(String)
    cost = Column(Integer)
    costUnits = Column(Integer)
    wages = Column(Integer)
    secondsToBuild = Column(Integer)
    category = Column(String)
    kind = Column(String)
    robotsNeeded = Column(Integer)
    realmAvailable = Column(Boolean)

    def __init__(self, name, image, cost, costUnits, wages, secondsToBuild, category, kind, robotsNeeded, realmAvailable):
        self.name = name
        self.image = image
        self.cost = cost
        self.costUnits = costUnits
        self.wages = wages
        self.secondsToBuild = secondsToBuild
        self.category = category
        self.kind = kind
        self.robotsNeeded = robotsNeeded
        self.realmAvailable = realmAvailable

session = Session()
inspector = inspect(engine)

'''
pouplateBuildingTable acts as both Create & Update in CRUD, 
the table data should be static unless SimCompanies updates the vales.

inspector checks to see if table exists, if it does the table is deleted.
A new Table is created and populated by calling the SimCompanies API for current data. 
'''
def populate_buildings_table():

    if(inspector.has_table('Buildings')):
        print("Table Buildings already exists!")
        Building.__table__.drop(engine)
        session.commit()
        Base.metadata.create_all(engine)
        print("Buildings table dropped, session commited, then schema recreated.")
    else:
        print("No table named Buildings found, creating schema.")
        Base.metadata.create_all(engine)

    url = "https://www.simcompanies.com/api/v3/0/buildings/1/"
    response = requests.get(url)
    building_data = json.loads(response.text)
    for building in building_data:
        name = building['name']
        image = building['image']
        cost = building['cost']
        costUnits = building['costUnits']
        wages = building['wages']
        secondsToBuild = building['secondsToBuild']
        category = building['category']
        kind = building['kind']
        robotsNeeded = building['robotsNeeded']
        realmAvailable = building['realmAvailable']
        building = Building(name, image, cost, costUnits, wages, secondsToBuild, category, kind, robotsNeeded, realmAvailable)
        session.add(building)
        session.commit()

#populate_buildings_table()

session.close()