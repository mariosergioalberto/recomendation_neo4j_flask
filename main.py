import json
import neo4j
from Person import Person
from neo4j import GraphDatabase
from flask import Flask,jsonify, request
from datetime import *
from Preference import Preference
from LifeStyle import LifeStyle
from State import State
import requests


app = Flask(__name__)
@app.route('/',methods=['GET'])
def index():
    """ con = RecomendationApi()
    jsonodes = con._get_allNodes()
    con.close() """
    jsonodes = "TEST OK"
    print("test ok get ")
    return jsonodes


@app.route('/api/recomendation/<id>',methods=['GET'])
def recomendation(id):
    success = True
    message = "Users recomended"
    error = None
    con = RecomendationApi()
    personas = con._get_peopleRecomendation(id)
    con.close()
    personas_json = []


    for person in personas:
        con2 = RecomendationApi()
        preferences = con2.get_sports(person.id_person)
        print(person.id_person)
        prefe = Preference()
        # lifestyle = LifeStyle(1,1,1,1,1,1)
        # person.lifestyle = lifestyle
        for preference in preferences:
            if(preference['tipo'] == 'state'):
                person.state = preference['idNode']
            if (preference['tipo'] == 'city'):
                person.city = preference['idNode']
            if (preference['tipo'] == 'genremovies'):
                x = {"id": preference['idNode'], "name": preference['name']}
                prefe.genremovies.append(x)
            if(preference['tipo'] == 'genremusic'):
                x = {"id": preference['idNode'], "name": preference['name']}
                prefe.genremusic.append(x)
            if (preference['tipo'] == 'hobby'):
                x = {"id": preference['idNode'], "name": preference['name']}
                prefe.hobbies.append(x)
            if (preference['tipo'] == 'deporte'):
                x = {"id": preference['idNode'], "name": preference['name']}
                prefe.sport.append(x)
            if (preference['tipo'] == 'mascota'):
                x = {"id": preference['idNode'],"name":preference['name']}
                prefe.pets.append(x)
            if (preference['tipo'] == 'career'):
                person.career = (preference['idNode'])
            if (preference['tipo'] == 'convivencia'):
                x = {"id": preference['idNode'], "name": preference['name'],"weight": preference['weight']}
                person.lifestyle.append(x)


        person.preferences = prefe


        con2.close


    for person in personas:
        dict_preferences = json.loads(json.dumps(person.preferences.__dict__))
        person.preferences = dict_preferences
        personas_json.append(json.loads(json.dumps(person.__dict__)))
    json_data = {
        "data": personas_json
        ,
        "success": success,
        "message": message,
        "error": error
    }

    return json_data

@app.route('/api/create/<id>',methods=['POST'])
def createPerson(id):
    success = True
    message = "Person Created"
    error = None
    con0 = RecomendationApi()
    existe = con0.exist_person(int(id))
    if(existe):
        print("La persona existe")
        print(existe)
        success = False
        message = "Failed Create  person."
        error = "Error Person exist with that id"
    else:
        print("La persona no existe")
        request_data = request.get_json()
        con = RecomendationApi()
        person = con.create_nodesPerso(int(id), request_data)
        if (isinstance(person, Person)):
            try:
                print("Id de persona recien agregada")
                print(person.id_person)
                resp1 = con.create_relationPerson(person)
                con.close()
                con2 = RecomendationApi()
                resp2 = con2.create_projectGraph()
                con2.close()
            except():
                success = False
                message = "Failed Create relationalship person."
                error = "Error to Create relationalship."
        else:
            success = False
            message = "Failed Create Person."
            error = "Error to Create node person."
        # json_out = json.dumps(person.__dict__)



    json_data = {
                "data": [
                ],
                "success": success,
                "message": message,
                "error": error
            }
    #json_data['data'].append(json_out)
    json_dict = json.dumps(json_data)



    return json_dict#,resp1,resp2

@app.route('/api/update/<id>',methods=['PUT'])
def updatePerson(id):
    success = True
    message = "Modified Person preference"
    error = None
    request_data = request.get_json()
    try:
        con = RecomendationApi()
        resp = con.update_Person(int(id),request_data)
        con.close()
    except():
        success = False
        message = "Error to Modified Person preference"
        error = None
    try:
        con2 = RecomendationApi()
        resp2 = con2.create_projectGraph()
        con2.close()
    except():
        success = True
        message = "Error in create projection Data Science"
        error = None

    json_data = {
        "data": [
        ],
        "success": success,
        "message": message,
        "error": error
    }

    return json_data

class RecomendationApi:
    def __init__(self):
        uri = "bolt://neo4j:7687"
        user = "neo4j"
        password = "1234"
        self.driver = GraphDatabase.driver(uri,auth=(user, password))

    def close(self):
        self.driver.close()

    def _get_allNodes(self):
        with self.driver.session() as session:
            nodes = session.execute_read(self.print_get_allNodes)
        return nodes

    def print_get_allNodes(self, tx):
        result = tx.run("MATCH (n:person) RETURN n.name")
        result_json = json.dumps([r.data() for r in result])
        print(result_json)
        return result_json

    def _get_peopleRecomendation(self, id_person):
        try:
            with self.driver.session() as session:
                personas = session.execute_read(self.print_get_peopleRecomendation, id_person)
            return personas
        except():
            error = "Error al realizar la busqueda de recomendaciones"
            return error

    def print_get_peopleRecomendation(self, tx, id_person):
        url = 'https://sh-hasura-api.herokuapp.com/v1/graphql/'
        id_person = int(id_person)
        print("Leega hasta la query de data science")
        query3 = """CALL gds.nodeSimilarity.stream('myGraph')
                    YIELD node1, node2, similarity
                    WHERE gds.util.asNode(node1).id = %i
                    RETURN  gds.util.asNode(node2).id AS idPerson,gds.util.asNode(node2).name AS fullname,
                    gds.util.asNode(node2).username AS username,gds.util.asNode(node2).age AS age,gds.util.asNode(node2).gender AS gender, gds.util.asNode(node2).bio AS bio, similarity
                    ORDER BY similarity DESCENDING, idPerson LIMIT 3"""%(id_person)
        result = tx.run(query3)
        #result_json = json.dumps([r.data() for r in result])
        personas = []
        for record in result:
            
            idpersonrec = record["idPerson"]
            fullname = record['fullname']
            username = record['username']
            age = record['age']
            gender = record['gender']
            state = 0
            city = 0
            bio = record['bio']
            similarity = record['similarity']
            person = Person(idpersonrec, fullname, username, age, gender, state, city, bio)
            person.similarity = similarity
            query = """query GetUserAvatar {
            sh_users(where: {persons_id: {_eq: %i}}) {
		    avatar
                }
            }
            """%(id_person)
            print(f"query = {query}")
            r = requests.post(url, json={'query': query}, headers={'Content-Type': 'application/json', 'x-hasura-admin-secret': 'sh123hasura'}) ## esta clave leerla desde un archivo de entorno
            json_data = r

            print("RESPUESTA DE HEROKU")
            print(json_data)
            print(r.status_code)
            #print(json_data['data']['sh_users'])  # agregar a cada obj persona de la respuesta su avatar
            #personas.avatar = json_data['data']['sh_users']
            personas.append(person)

        #print(result_json)
        return personas
    def get_sports(self,id_person):
        try:
            with self.driver.session() as session:
                query = "MATCH (p:person {id:%i})-[r]->(n) WHERE labels(n)[0] <> 'person' RETURN labels(n)[0] as tipo, n.id as idNode, n.name as name, r.weight as weight"%id_person
                sports = session.run(query)
                preferences = []
                for record in sports:
                  preferences.append(record.data())
                return preferences
        except():
            error = "Error al realizar la busqueda de recomendaciones"
            return error
        
    # def runtx_get_sports(self,tx):
    #     preferences = []
    #     querygetsports = """MATCH (p:person {id:$id_person})-->(n) RETURN labels(n)[0] as tipo, n.id as idNode, n.name as name"""
    #     result = tx.run(querygetsports, id_person=1)
    #     for record in result:
    #         preferences.append(record.data())
    #     return preferences

    def create_projectGraph(self):
        test = "ok"
        with self.driver.session() as session:
            result = session.execute_write(self.runtx_projectGraph,test)
        print("llega hasta create_projectGraph")
        return result

    def runtx_projectGraph(self,tx,test):
        projectGraph_delete = "CALL gds.graph.drop('myGraph', false) YIELD graphName;"
        print(projectGraph_delete)
        resultprojectdelete = tx.run(projectGraph_delete)

        projectGraph_create = """CALL gds.graph.project(
                                        'myGraph',
                                        ['person','career','convivencia','deporte','genremovies','genremusic','hobby','mascota','state','city'],
                                        {
                                            PREFERENCES: {
                                                properties: {
                                                    weight: {
                                                        property: 'weight',
                                                        defaultValue: 0
                                                    }
                                                }
                                            }
                                        }
                                    );"""
        print(projectGraph_create)
        resultprojectcreate = tx.run(projectGraph_create)
        return test

    def update_Person(self,id_person,data_json):
        #pulcro,visitas,salidas,estudiar,fumador,mascotas
        lifestyle = data_json['lifestyles']
        preferences = data_json['preferences']
        with self.driver.session() as session:
            result = session.execute_write(self.runtx_relationUpdatePerson,id_person, preferences,lifestyle)
        return result

    def runtx_relationUpdatePerson(self,tx,id_person,preferences,lifestyle):
        id_person = id_person

        sports = preferences['sports']
        pets = preferences['pets'] # "pets": [1,2],
        movies = preferences['genremovies']
        musics = preferences['genremusic']
        hobbies = preferences['hobbies']

        querydel = "MATCH (p:person {id: %i})-[r]->(n) WHERE labels(n)[0] <> 'city' and labels(n)[0] <> 'career' DELETE r"%id_person
        print(querydel)
        querydelete = """MATCH (p:person {id: $id_person})-[r]->(n) WHERE labels(n)[0] <> 'city' and labels(n)[0] <> 'career'  DELETE r"""
        result = tx.run(querydelete, id_person=id_person)



        querypulcro = "MATCH (p:person {id: $id_person}), (pulcro:convivencia {id:1}),(visita:convivencia {id:2}),(estudia:convivencia {id:3}),(salir:convivencia {id:4}),(fumar:convivencia {id:5}),(mascotas:convivencia {id:6}) " \
                      "CREATE (p)-[:PREFERENCES {weight:%s}]->(pulcro) " \
                      "CREATE (p)-[:PREFERENCES {weight:%s}]->(visita) " \
                      "CREATE (p)-[:PREFERENCES {weight:%s}]->(salir) " \
                      "CREATE (p)-[:PREFERENCES {weight:%s}]->(estudia) " \
                      "CREATE (p)-[:PREFERENCES {weight:%s}]->(fumar) " \
                      "CREATE (p)-[:PREFERENCES {weight:%s}]->(mascotas) "%(lifestyle[0],lifestyle[1],lifestyle[2],lifestyle[3],lifestyle[4],lifestyle[5])

        result = tx.run(querypulcro, id_person=id_person)

        for sport in sports:
            query = "MATCH (p:person {id: $id_person}) MATCH (sport:deporte {id: $sport}) " \
                    "CREATE (p)-[:PREFERENCES {weight:1}]->(sport)"

            result = tx.run(query, id_person=id_person, sport=sport)

        for pet in pets:
            query = "MATCH (p:person {id: $id_person}) MATCH (pet:mascota {id: $pet}) " \
                    "CREATE (p)-[:PREFERENCES {weight:1}]->(pet)"

            result = tx.run(query, id_person=id_person, pet=pet)

        for movie in movies:
            query = "MATCH (p:person {id: $id_person}) MATCH (movie:genremovies {id: $movie}) " \
                    "CREATE (p)-[:PREFERENCES {weight:1}]->(movie)"

            result = tx.run(query, id_person=id_person, movie=movie)

        for music in musics:
            query = "MATCH (p:person {id: $id_person}) MATCH (music:genremusic {id: $music}) " \
                    "CREATE (p)-[:PREFERENCES {weight:1}]->(music)"

            result = tx.run(query, id_person=id_person, music=music)

        for hobby in hobbies:
            query = "MATCH (p:person {id: $id_person}) MATCH (hob:hobby {id: $hobby}) " \
                    "CREATE (p)-[:PREFERENCES {weight:1}]->(hob)"

            result = tx.run(query, id_person=id_person, hobby=hobby)


        result_json = "OK"
        return result_json

    def getEdad(self,birth_date):
        date_issue = datetime.strptime(birth_date, '%Y-%m-%d').date()
        date_today = date.today()
        if date_today.__ge__(date_issue):
            age_calc = date_today.__sub__(date_issue).days // 365
        return age_calc

    def exist_person(self,id_person):
        with self.driver.session() as session:
            result = session.execute_write(self.runtx_exist_person, id_person)
        return result

    def runtx_exist_person(self,tx,id_person):
        query = "MATCH(p:person {id:$id_person}) return p"
        person = []
        try:
            result = tx.run(query,id_person=id_person)

        except():
            print("No se ha podido buscar a la Persona")
        for r in result:
            person.append(r)
        result_json = json.dumps([r.data() for r in result])
        return person


    def create_nodesPerso(self,id,data_json):
        id_person = id
        fullname = data_json['fullname']
        username = data_json['username']
        age = data_json['age']
        gender = data_json['gender']
        state = data_json['state']
        city = data_json['city']
        bio = data_json['bio']
        career = data_json['career']
        lifestyles = data_json['lifestyles']
        person = Person(id_person,fullname,username,age,gender,state,city,bio)
        pref_request = data_json['preferences']
        preference = Preference()
        preference.sport = pref_request['sports']
        preference.genremovies = pref_request['genremovies']
        preference.genremusic = pref_request['genremusic']
        preference.hobbies = pref_request['hobbies']
        preference.pets = pref_request['pets']
        person.preferences = preference
        person.lifestyle = lifestyles
        person.career = career
        error = ""

        try:
            with self.driver.session() as session:
                result = session.execute_write(self.runtx_create, person)
            print(person)
        except():
            error = "Error al crear la persona."
        if(error == ""):
            return person
        else:
            return error

    def runtx_create(self,tx,person):
        query = "CREATE (%s:person {id:$id_person,username:$username,name: $fullname, age:$age, gender:$gender,bio:$bio}) " %(person.username)

        try:
            result = tx.run(query,id_person=person.id_person,username=person.username,fullname=person.fullname,age=person.age,gender=person.gender,bio=person.bio)

        except():
            print("Ha ocurrido un error al crear el nodo persona...")
        result_json = json.dumps([r.data() for r in result])
        # print (result_json)
        return result_json

    def create_relationPerson(self,person):

        with self.driver.session() as session:
            result = session.execute_write(self.runtx_relationPerson, person)
        return result


    def runtx_relationPerson(self,tx,person):

        querycity = "MATCH (p:person {id: $id_person}), (city:city {id:$id_city}) " \
                    "CREATE (p)-[:PREFERENCES {weight:1}]->(city) "
        querycareer = "MATCH (p:person {id: $id_person}), (career:career {id:$id_career}) " \
                    "CREATE (p)-[:PREFERENCES {weight:1}]->(career) "
        print(querycity)
        result = tx.run(querycity, id_person=person.id_person,id_city=person.city)
        result = tx.run(querycareer, id_person=person.id_person,id_career=person.career)
        print("PERSON --------------------------")
        print(person.lifestyle)

        #
        # queryconvivencia = "MATCH (p:person {id: %i}), (pulcro:convivencia {id:1}),(visita:convivencia {id:2}),(estudia:convivencia {id:3}),(salir:convivencia {id:4}),(fumador:convivencia {id:5}),(mascotas:convivencia {id:6}) " \
        #               "CREATE (p)-[:PREFERENCES {weight:%s}]->(pulcro) " \
        #               "CREATE (p)-[:PREFERENCES {weight:%s}]->(visita) " \
        #               "CREATE (p)-[:PREFERENCES {weight:%s}]->(salir) " \
        #               "CREATE (p)-[:PREFERENCES {weight:%s}]->(estudiar) " \
        #               "CREATE (p)-[:PREFERENCES {weight:%s}]->(mascotas) " % (person.id_person, person.lifestyle[0], person.lifestyle[1], person.lifestyle[3], person.lifestyle[2], person.lifestyle[4])
        querypulcro = "MATCH (p:person {id: $id_person}), (pulcro:convivencia {id:1}),(visita:convivencia {id:2}),(estudia:convivencia {id:3}),(salir:convivencia {id:4}),(fumar:convivencia {id:5}),(mascotas:convivencia {id:6}) " \
                      "CREATE (p)-[:PREFERENCES {weight:%s}]->(pulcro) " \
                      "CREATE (p)-[:PREFERENCES {weight:%s}]->(visita) " \
                      "CREATE (p)-[:PREFERENCES {weight:%s}]->(salir) " \
                      "CREATE (p)-[:PREFERENCES {weight:%s}]->(estudia) " \
                      "CREATE (p)-[:PREFERENCES {weight:%s}]->(fumar) " \
                      "CREATE (p)-[:PREFERENCES {weight:%s}]->(mascotas) "%(person.lifestyle[0],person.lifestyle[1],person.lifestyle[2],person.lifestyle[3],person.lifestyle[4],person.lifestyle[5])
        print(querypulcro)
        result = tx.run(querypulcro, id_person=person.id_person)
        result_json = json.dumps([r.data() for r in result])

        for sport in person.preferences.sport:

            query = "MATCH (p:person {id: $id_person}) MATCH (sport:deporte {id: $sport}) " \
                    "CREATE (p)-[:PREFERENCES {weight:1}]->(sport)"

            result = tx.run(query, id_person=person.id_person, sport=sport)


        for pet in person.preferences.pets:
            query = "MATCH (p:person {id: $id_person}) MATCH (pet:mascota {id: $pet}) " \
                    "CREATE (p)-[:PREFERENCES {weight:1}]->(pet)"

            result = tx.run(query, id_person=person.id_person, pet=pet)
            #result_json = json.dumps([r.data() for r in result])

        for movie in person.preferences.genremovies:
            query = "MATCH (p:person {id: $id_person}) MATCH (movie:genremovies {id: $movie}) " \
                    "CREATE (p)-[:PREFERENCES {weight:1}]->(movie)"
            print(query)
            result = tx.run(query, id_person=person.id_person, movie=movie)
            #result_json = json.dumps([r.data() for r in result])

        for music in person.preferences.genremusic:
            query = "MATCH (p:person {id: $id_person}) MATCH (music:genremusic {id: $music}) " \
                    "CREATE (p)-[:PREFERENCES {weight:1}]->(music)"

            result = tx.run(query, id_person=person.id_person, music=music)
            #result_json = json.dumps([r.data() for r in result])

        for hobby in person.preferences.hobbies:
            query = "MATCH (p:person {id: $id_person}) MATCH (hob:hobby {id: $hobby}) " \
                    "CREATE (p)-[:PREFERENCES {weight:1}]->(hob)"

            result = tx.run(query, id_person=person.id_person, hobby=hobby)
            #result_json = json.dumps([r.data() for r in result])

        result_json = "OK"
        return result_json



if __name__ == "__main__":
    #con = RecomendationApi("bolt://localhost:7687","neo4j","123456")
    #greeter.print_greeting("Hola Mundo")
    #con._get_nodes()
    app.run(host="0.0.0.0", port=5000,debug=True)
    #con.friends_recomendation("Sergio")
    #con.create_nodesPerso()
    #con.close()
