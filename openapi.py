from flask_restx import Api, Resource, fields
from flask import Blueprint, jsonify, url_for

def create_openapi_spec(app):
    # Główny blueprint dla API
    api_blueprint = Blueprint('api', __name__, url_prefix='/api')
    
    # Inicjalizacja API
    api = Api(api_blueprint, 
              version='1.0', 
              title='BRSP Web API',
              description='API dla systemu BRSP Web',
              doc='/docs/')
    
    # Model danych dla odpowiedzi
    example_model = api.model('ExampleModel', {
        'id': fields.Integer(description='ID rekordu'),
        'name': fields.String(description='Nazwa rekordu'),
        'created_at': fields.DateTime(description='Data utworzenia')
    })
    
    # Namespace dla przykładu
    ns = api.namespace('examples', description='Operacje na przykładach')
    
    @ns.route('/')
    class ExampleList(Resource):
        @ns.doc('list_examples')
        @ns.marshal_list_with(example_model)
        def get(self):
            """Pobiera listę przykładów"""
            # Tutaj Twoja logika biznesowa
            examples = [{'id': 1, 'name': 'Przykład 1', 'created_at': '2023-01-01'}]
            return examples
    
    @ns.route('/<int:id>')
    @ns.response(404, 'Nie znaleziono rekordu')
    class Example(Resource):
        @ns.doc('get_example')
        @ns.marshal_with(example_model)
        def get(self, id):
            """Pobiera konkretny przykład"""
            # Tutaj Twoja logika biznesowa
            return {'id': id, 'name': f'Przykład {id}', 'created_at': '2023-01-01'}
    
    # Rejestracja blueprinta
    app.register_blueprint(api_blueprint)
    
    # Endpoint dla specyfikacji OpenAPI w formacie JSON
    @app.route('/openapi.json')
    def openapi_json():
        return jsonify(api.__schema__)
    
    return api