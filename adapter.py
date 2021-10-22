import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dweather_python_client'))

from program_catalog_stub.programs.directory import get_program


class Adapter:
    ''' External Adapter class that implements the evaluation and conditional
        executione of Arbol weather contracts based on weather data on IPFS
    '''
    def __init__(self, input):
        ''' Each call to the adapter creates a new Adapter
            instance to handle the request

            Parameters: input (dict), the received request body
        '''
        self.id = input.get('id', '1')
        self.request_data = input.get('data')
        if self.validate_request_data():
            self.execute_request()
        else:
            self.result_error(f'Bad Request: {self.request_error}')

    def validate_request_data(self):
        ''' Validate that the received request is properly formatted and includes
            all necessary paramters. In the case of an illegal request error
            information is logged to the output

            Returns: bool representing whether the request is valid
        '''
        required_params = ['dataset', 'locations', 'start', 'end', 'strike', 'exhaust', 'limit', 'opt_type']
        if self.request_data is None:
            self.request_error = 'request is None'
            return False
        if self.request_data == {}:
            self.request_error = 'request is empty'
            return False
        program_name = self.request_data.get('program', None)
        if program_name is None:
            self.request_error = 'no program specified'
            return False
        else:
            self.program = get_program(program_name)
        params = self.request_data.get('params', None)
        if params is None:
            self.request_error = 'no parameters specified'
            return False
        self.params = params
        valid, self.request_error = self.program.validate_request(params)
        return valid

    def execute_request(self):
        ''' Get the designated program and determine whether the associated
            contract should payout and if so then for how much
        '''
        try:
            payout = self.program.serve_evaluation(self.params)
            self.request_data['result'] = payout
            self.result_success(payout)
        except Exception as e:
            self.result_error(e)

    def result_success(self, result):
        ''' If the request reaches no errors log the outcome in the result field
            including the payout in the response
        '''
        self.result = {
            'jobRunID': self.id,
            'data': self.request_data,
            'result': result,
            'statusCode': 200,
        }

    def result_error(self, error):
        ''' If the request terminates in an error then log the error details in
            the result field to be returned in the response
        '''
        self.result = {
            'jobRunID': self.id,
            'data': self.request_data,
            'error': f'There was an error: {error}',
            'statusCode': 500,
        }
